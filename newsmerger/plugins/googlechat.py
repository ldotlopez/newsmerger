"""The `googlechat` sink posts summarized items (title, summary and link) to a
Google Chat space through an incoming webhook, given either as its `url` or
as its `channel` (space id) and `token`. What was delivered is in the ledger
(`inspect deliveries`), so nothing is ever posted twice unless forced.
"""

import html
from typing import Any, Self
from urllib.parse import quote

import pydantic
import requests
from pydantic import SecretStr

from ..db import Database
from ..models import SourceItem
from ..sinks import BaseItemSink, Sink
from . import PluginObjects, PluginOptions, Services

# The API key Google puts in every incoming webhook URL; only the token is secret.
WEBHOOK_KEY = "AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI"


class GoogleChatError(Exception):
    """A message could not be posted."""


def build_text(title: str, summary: str, uri: str) -> str:
    # Chat parses `<url|label>` links and `*bold*`, so the text must escape `<>&`.
    return (
        f"*{html.escape(title, quote=False)}*\n\n"
        f"{html.escape(summary, quote=False)}\n\n"
        f"<{uri}|Original article>"
    )


class Options(PluginOptions):
    url: SecretStr | None = None
    channel: str | None = None
    token: SecretStr | None = None
    max_retries: int = 3
    lookback: int = 24  # hours: the candidates without --since or --item

    @pydantic.model_validator(mode="after")
    def url_or_channel_and_token(self) -> Self:
        parts = (self.channel, self.token)
        if (self.url is None and None not in parts) or (
            self.url is not None and parts == (None, None)
        ):
            return self
        raise ValueError("set either `url` or both `channel` and `token`")

    def webhook_url(self) -> SecretStr:
        if self.url is not None:
            return self.url
        assert self.channel is not None and self.token is not None
        return SecretStr(
            f"https://chat.googleapis.com/v1/spaces/{quote(self.channel)}/messages"
            f"?key={WEBHOOK_KEY}&token={quote(self.token.get_secret_value())}"
        )


class GoogleChatSink(BaseItemSink):
    name = "googlechat"
    requires = "summary"

    def __init__(self, cfg: Options) -> None:
        super().__init__(max_retries=cfg.max_retries, lookback=cfg.lookback)
        self.webhook_url = cfg.webhook_url()

    def send(self, db: Database, subject: SourceItem) -> dict[str, str]:
        summaries = db.get_annotation_values([subject], key="summary")
        text = build_text(subject.title, str(summaries[subject.key]), subject.uri)
        try:
            response = requests.post(
                self.webhook_url.get_secret_value(), json={"text": text}, timeout=30
            )
            result = response.json()
        except requests.RequestException as e:
            # Only the class: the message holds the URL, which embeds the token.
            raise GoogleChatError(type(e).__name__) from None
        if not response.ok:
            raise GoogleChatError(result.get("error", {}).get("message", str(result)))
        return {"message": result["name"]}


def __newsmerger_plugin__(services: Services, **options: Any) -> PluginObjects:
    cfg = Options.model_validate(options)
    sink = GoogleChatSink(cfg)
    return [(sink.name, Sink, sink)]
