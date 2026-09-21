from __future__ import annotations

import html
import os
from typing import Any

import requests

from ..models import SourceItem
from . import ItemProcessor, PartialFailure

MAX_CAPTION_LENGTH = 1024


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


class Processor(ItemProcessor):
    NAME = "telegram"

    def __init__(
        self,
        *args: Any,
        bot_token: str | None = None,
        chat_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.bot_token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")

    def process_item(self, item: SourceItem) -> dict[str, Any]:
        if not self.bot_token or not self.chat_id:
            raise PartialFailure(
                {},
                {"sended": "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required"},
            )

        annotations = self.db.get_annotations(
            item, processor="summarize", key="summary"
        )
        summary = annotations.get("summarize", {}).get("summary")
        if not summary:
            raise PartialFailure(
                {},
                {"sended": "summary annotation is not available"},
            )

        caption = build_caption(item.title, str(summary), item.uri)
        image = item.data.get("image") if isinstance(item.data, dict) else None
        if isinstance(image, str) and image.strip():
            endpoint = "sendPhoto"
            payload = {
                "chat_id": self.chat_id,
                "photo": image,
                "caption": caption,
                "parse_mode": "HTML",
            }
        else:
            endpoint = "sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": caption,
                "parse_mode": "HTML",
            }

        response = requests.post(
            f"https://api.telegram.org/bot{self.bot_token}/{endpoint}",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
        if not result.get("ok"):
            raise PartialFailure({}, {"sended": str(result)})

        self.db.save_artifact(
            self.NAME,
            f"sended:{item.uid}",
            str(result.get("result", {}).get("message_id", "")),
            "application/json",
        )
        return {"sended": True}
