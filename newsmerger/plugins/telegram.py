"""Two sinks sharing one Telegram bot and chat (decision 0007):

- `telegram` posts summarized items (title, summary and link), oldest first,
  at most one per source every `interval` minutes.
- `telegram_artifacts` sends every artifact of the remixers listed in
  `artifacts` (e.g. `[digest]`) as a document.

Each has an optional subsection of options. With none, both are enabled with
their defaults; with some, only those. What was delivered is in the ledger
(`inspect deliveries`), so nothing is ever posted twice unless forced.
"""

import html
import logging
import mimetypes
from datetime import UTC, datetime, timedelta
from typing import Any

import pydantic
import requests
from pydantic import SecretStr

from ..db import Database
from ..models import Artifact, Delivery, SourceItem
from ..sinks import BaseArtifactSink, BaseItemSink, Sink
from . import PluginObjects, PluginOptions, Services

LOGGER = logging.getLogger(__name__)

MAX_CAPTION_LENGTH = 1024


class TelegramError(Exception):
    """A message could not be posted."""


def build_caption(title: str, summary: str, uri: str) -> str:
    escaped_title = html.escape(title)
    escaped_summary = html.escape(summary)
    escaped_uri = html.escape(uri, quote=True)
    footer = f'\n\n<a href="{escaped_uri}">Original article</a>'
    heading = f"<b>{escaped_title}</b>\n\n"
    available_summary_length = MAX_CAPTION_LENGTH - len(heading) - len(footer)

    if available_summary_length <= 0:
        return (heading + footer)[:MAX_CAPTION_LENGTH]

    if len(escaped_summary) > available_summary_length:
        suffix = "..."
        escaped_summary = (
            escaped_summary[: max(0, available_summary_length - len(suffix))] + suffix
        )

    return heading + escaped_summary + footer


class ItemSinkOptions(PluginOptions):
    interval: int = 30  # minutes between posts of the same source
    max_retries: int = 3
    lookback: int = 24  # hours: the candidates without --since or --item


class ArtifactSinkOptions(PluginOptions):
    # Remixers whose artifacts are sent.
    artifacts: list[str] = pydantic.Field(default_factory=list)
    max_retries: int = 3
    lookback: int = 24  # hours: the candidates without --since or --artifact


class Options(PluginOptions):
    bot_token: SecretStr
    chat_id: str
    telegram: ItemSinkOptions = ItemSinkOptions()
    telegram_artifacts: ArtifactSinkOptions = ArtifactSinkOptions()

    @pydantic.field_validator("telegram", "telegram_artifacts", mode="before")
    @classmethod
    def empty_section_takes_defaults(cls, value: Any) -> Any:
        return {} if value is None else value


class TelegramClient:
    """Bot API calls to one chat."""

    def __init__(self, bot_token: SecretStr, chat_id: str) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id

    def post(self, method: str, **request: Any) -> int:
        """Call `method` with `requests.post` keyword arguments; return the
        id of the message sent."""
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{self.bot_token.get_secret_value()}/{method}",
                timeout=30,
                **request,
            )
            result = response.json()
        except requests.RequestException as e:
            # Only the class: the message holds the URL, which embeds the bot token.
            raise TelegramError(type(e).__name__) from None
        if not result.get("ok"):
            raise TelegramError(result.get("description", str(result)))
        return result["result"]["message_id"]


class TelegramSink(BaseItemSink):
    name = "telegram"
    requires = "summary"

    def __init__(self, client: TelegramClient, cfg: ItemSinkOptions) -> None:
        super().__init__(max_retries=cfg.max_retries, lookback=cfg.lookback)
        self.client = client
        self.interval = timedelta(minutes=cfg.interval)

    def select(
        self, db: Database, pending: list[tuple[Delivery, SourceItem]], now: datetime
    ) -> list[tuple[Delivery, SourceItem]]:
        """The head of each source's queue, once it is due and the source's
        last delivery is `interval` old."""
        last_delivery = db.last_delivery_by_source(self.name)
        heads: dict[str, tuple[Delivery, SourceItem]] = {}
        for delivery, item in pending:
            heads.setdefault(item.source.id, (delivery, item))
        never = datetime.min.replace(tzinfo=UTC)
        return [
            (delivery, item)
            for source_id, (delivery, item) in heads.items()
            if self.is_due(delivery, now)
            and now - last_delivery.get(source_id, never) >= self.interval
        ]

    def send(self, db: Database, subject: SourceItem) -> dict[str, int]:
        summaries = db.get_annotation_values([subject], key="summary")
        caption = build_caption(subject.title, str(summaries[subject.key]), subject.uri)
        image = subject.data.get("image")
        if isinstance(image, str) and image.strip():
            payload = {
                "chat_id": self.client.chat_id,
                "photo": image,
                "caption": caption,
                "parse_mode": "HTML",
            }
            message_id = self.client.post("sendPhoto", json=payload)
        else:
            payload = {
                "chat_id": self.client.chat_id,
                "text": caption,
                "parse_mode": "HTML",
            }
            message_id = self.client.post("sendMessage", json=payload)
        return {"message_id": message_id}


class TelegramArtifactSink(BaseArtifactSink):
    """Sends artifacts as documents, which avoids the 4096-character limit
    of messages."""

    name = "telegram_artifacts"

    def __init__(self, client: TelegramClient, cfg: ArtifactSinkOptions) -> None:
        super().__init__(
            cfg.artifacts, max_retries=cfg.max_retries, lookback=cfg.lookback
        )
        self.client = client

    def send(self, db: Database, subject: Artifact) -> dict[str, int]:
        artifact = db.get_artifact(subject.remixer, subject.name)
        if artifact is None or artifact.content is None:
            raise LookupError(f"artifact {subject.remixer}/{subject.name} is gone")
        extension = mimetypes.guess_extension(artifact.content_type) or ".txt"
        filename = f"{artifact.remixer}-{artifact.name.replace('/', '_')}{extension}"
        message_id = self.client.post(
            "sendDocument",
            data={
                "chat_id": self.client.chat_id,
                "caption": f"{artifact.remixer}/{artifact.name}",
            },
            files={
                "document": (
                    filename,
                    artifact.content.encode(),
                    artifact.content_type,
                )
            },
        )
        return {"message_id": message_id}


def __newsmerger_plugin__(services: Services, **options: Any) -> PluginObjects:
    cfg = Options.model_validate(options)
    client = TelegramClient(cfg.bot_token, cfg.chat_id)
    builders = {
        "telegram": lambda: TelegramSink(client, cfg.telegram),
        "telegram_artifacts": lambda: TelegramArtifactSink(
            client, cfg.telegram_artifacts
        ),
    }
    enabled = [name for name in options if name in builders] or list(builders)
    sinks = [builders[name]() for name in enabled]
    return [(sink.name, Sink, sink) for sink in sinks]
