"""Posts summarized items (title, summary and link) to a Telegram chat, at
most one per source every `interval` minutes.

Each source has a FIFO queue. On every run, summarized items that are not
queued or posted yet join their source's queue, oldest first, and the head of
each queue is posted if its source's last post is at least `interval` minutes
old. By default only items published since the remixer's first run are
queued; a scope with `since` or `uids` queues the items it selects instead.
An item is never posted twice; one that fails to post stays queued.

Produces one artifact named "state" (JSON): the first run's time
(`watermark`), the queue, the posted items with their message ids and the
time of each source's last post.
"""

import dataclasses
import html
import json
import logging
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import Any

import requests

from ..db import Database
from ..models import ProcessingScope, SourceItem
from . import BaseRemixer

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


class Remixer(BaseRemixer):
    NAME = "telegram"

    def __init__(
        self, db: Database, *, bot_token: str, chat_id: str, interval: int = 30
    ) -> None:
        super().__init__(db)
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.interval = timedelta(minutes=interval)

    def produce(self, scope: ProcessingScope) -> Iterator[tuple[str, str, str]]:
        now = datetime.now(UTC)
        state = self._load_state(now)
        self._enqueue(state, scope)
        self._post_due(state, now)
        yield "state", json.dumps(state, indent=2), "application/json"

    def _load_state(self, now: datetime) -> dict[str, Any]:
        artifact = self.db.get_artifact(self.NAME, "state")
        if artifact is None or artifact.content is None:
            return {
                "watermark": now.isoformat(),
                "queue": [],
                "posted": [],
                "last_post": {},
            }
        return json.loads(artifact.content)

    def _enqueue(self, state: dict[str, Any], scope: ProcessingScope) -> None:
        if scope.since is None and scope.uids is None:
            watermark = datetime.fromisoformat(state["watermark"])
            scope = dataclasses.replace(scope, since=watermark)

        known = {(source_id, uid) for source_id, uid in state["queue"]}
        known |= {(source_id, uid) for source_id, uid, _ in state["posted"]}
        items = [item for item in self.db.get_items(scope) if item.key not in known]
        summaries = self.db.get_annotation_values(
            items, processor="summarize", key="summary"
        )
        state["queue"].extend(list(item.key) for item in items if item.key in summaries)

    def _post_due(self, state: dict[str, Any], now: datetime) -> None:
        for source_id in dict.fromkeys(source_id for source_id, _ in state["queue"]):
            last_post = state["last_post"].get(source_id)
            if last_post and now - datetime.fromisoformat(last_post) < self.interval:
                continue

            uid = next(uid for queued, uid in state["queue"] if queued == source_id)
            (item,) = self.db.get_items(ProcessingScope(source=source_id, uids=(uid,)))
            try:
                message_id = self._post(item)
            except TelegramError as e:
                LOGGER.warning(f"{self.NAME}: could not post {source_id}/{uid}: {e}")
                continue

            state["queue"].remove([source_id, uid])
            state["posted"].append([source_id, uid, message_id])
            state["last_post"][source_id] = now.isoformat()

    def _post(self, item: SourceItem) -> int:
        summaries = self.db.get_annotation_values(
            [item], processor="summarize", key="summary"
        )
        caption = build_caption(item.title, str(summaries[item.key]), item.uri)
        image = item.data.get("image")
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

        try:
            response = requests.post(
                f"https://api.telegram.org/bot{self.bot_token}/{endpoint}",
                json=payload,
                timeout=30,
            )
            result = response.json()
        except requests.RequestException as e:
            # Only the class: the message holds the URL, which embeds the bot token.
            raise TelegramError(type(e).__name__) from None
        if not result.get("ok"):
            raise TelegramError(result.get("description", str(result)))

        return result["result"]["message_id"]
