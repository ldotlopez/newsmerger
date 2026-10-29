"""Two Telegram sinks (decision 0007):

- `telegram` posts summarized items (title, the `summary` option's annotation
  and link), oldest first.
- `telegram_artifacts` sends every artifact of the remixers listed in
  `artifacts` (e.g. `[digest]`) as a document.

Each use posts with its `bot_token` to its `chat_id`; a type's `plugins`
section, which is optional, holds their defaults, so one bot can post to
many chats and uses can use different bots. What was delivered is in the
ledger (`inspect deliveries`), so nothing is ever posted twice unless forced.
"""

import html
import logging
import mimetypes
from typing import Any

import requests
from pydantic import SecretStr

from ..db import Database
from ..errors import PluginFailure
from ..models import Artifact, SourceItem
from ..sinks import (
    ArtifactDeliveryOptions,
    BaseArtifactSink,
    BaseItemSink,
    DeliveryOptions,
    SinkType,
)
from . import PluginTypes

LOGGER = logging.getLogger(__name__)

MAX_CAPTION_LENGTH = 1024


def build_caption(
    title: str,
    summary: str,
    uri: str,
    link_text: str = "original article",
    markdown: bool = False,
) -> str:
    """The caption in Telegram's HTML or, with `markdown`, in its legacy
    Markdown with the summary unescaped, so that its formatting renders."""
    if markdown:
        # Legacy Markdown cannot escape an entity's delimiter inside it.
        heading = f"*{title.replace('*', '')}*\n\n"
        footer = f"\n\n[{link_text.replace(']', '')}]({uri.replace(')', '%29')})"
        escaped_summary = summary
    else:
        escaped_uri = html.escape(uri, quote=True)
        heading = f"<b>{html.escape(title)}</b>\n\n"
        footer = f'\n\n<a href="{escaped_uri}">{html.escape(link_text)}</a>'
        escaped_summary = html.escape(summary)
    available_summary_length = MAX_CAPTION_LENGTH - len(heading) - len(footer)

    if available_summary_length <= 0:
        return (heading + footer)[:MAX_CAPTION_LENGTH]

    if len(escaped_summary) > available_summary_length:
        suffix = "..."
        escaped_summary = (
            escaped_summary[: max(0, available_summary_length - len(suffix))] + suffix
        )

    return heading + escaped_summary + footer


class ItemDeliveryOptions(DeliveryOptions):
    bot_token: SecretStr
    chat_id: str
    item_image: bool = True  # post the item's image, when it has one, as a photo
    item_url_preview: bool = False  # only for text messages
    item_url_text: str = "original article"
    summary: str = "summary"  # the annotation key posted as the summary
    markdown: bool = False  # post the summary as Markdown, not as plain text


class DocumentDeliveryOptions(ArtifactDeliveryOptions):
    bot_token: SecretStr
    chat_id: str


def post(bot_token: SecretStr, method: str, **request: Any) -> int:
    """Call the Bot API `method` with `requests.post` keyword arguments;
    return the id of the message sent."""
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token.get_secret_value()}/{method}",
            timeout=30,
            **request,
        )
        result = response.json()
    except requests.RequestException as e:
        # Only the class: the message holds the URL, which embeds the bot token.
        raise PluginFailure(type(e).__name__) from None
    if not result.get("ok"):
        raise PluginFailure(result.get("description", str(result)))
    return result["result"]["message_id"]


class TelegramSink(BaseItemSink[ItemDeliveryOptions]):
    name = "telegram"
    options_model = ItemDeliveryOptions

    @classmethod
    def required_key(cls, options: ItemDeliveryOptions) -> str:
        return options.summary

    def send(self, db: Database, subject: SourceItem) -> dict[str, Any]:
        options = self.options
        summaries = db.get_annotation_values([subject], key=options.summary)
        caption = build_caption(
            subject.title,
            str(summaries[subject.key]),
            subject.uri,
            options.item_url_text,
            options.markdown,
        )
        parse_mode = "Markdown" if options.markdown else "HTML"
        image = subject.data.get("image")
        if options.item_image and isinstance(image, str) and image.strip():
            # Uploaded, not by URL: Telegram cannot fetch some URLs, such as
            # its own CDN's (cdn*.telesco.pe) from `telegram_channel`.
            response = requests.get(image, timeout=30)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "image/jpeg")
            extension = mimetypes.guess_extension(content_type) or ".jpg"
            payload = {
                "chat_id": options.chat_id,
                "caption": caption,
                "parse_mode": parse_mode,
            }
            message_id = post(
                options.bot_token,
                "sendPhoto",
                data=payload,
                files={"photo": (f"image{extension}", response.content, content_type)},
            )
        else:
            payload = {
                "chat_id": options.chat_id,
                "text": caption,
                "parse_mode": parse_mode,
                "link_preview_options": {"is_disabled": not options.item_url_preview},
            }
            message_id = post(options.bot_token, "sendMessage", json=payload)
        # A message id is only unique within its chat.
        return {"chat_id": options.chat_id, "message_id": message_id}


class TelegramArtifactSink(BaseArtifactSink[DocumentDeliveryOptions]):
    """Sends artifacts as documents, which avoids the 4096-character limit
    of messages."""

    name = "telegram_artifacts"
    options_model = DocumentDeliveryOptions

    def send(self, db: Database, subject: Artifact) -> dict[str, Any]:
        options = self.options
        artifact = db.get_artifact(subject.remixer, subject.name)
        if artifact is None or artifact.content is None:
            raise LookupError(f"artifact {subject.remixer}/{subject.name} is gone")
        extension = mimetypes.guess_extension(artifact.content_type) or ".txt"
        filename = f"{artifact.remixer}-{artifact.name.replace('/', '_')}{extension}"
        message_id = post(
            options.bot_token,
            "sendDocument",
            data={
                "chat_id": options.chat_id,
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
        return {"chat_id": options.chat_id, "message_id": message_id}


def __newstool_plugin__() -> PluginTypes:
    sinks = [TelegramSink, TelegramArtifactSink]
    return [(sink.name, SinkType, sink) for sink in sinks]
