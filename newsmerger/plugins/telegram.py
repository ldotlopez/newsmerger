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
from pydantic import SecretStr

from ..db import Database
from ..models import ProcessingScope, SourceItem
from ..remixers import BaseRemixer, Remixer
from . import PluginObjects, PluginOptions

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


class Options(PluginOptions):
    bot_token: SecretStr
    chat_id: str
    interval: int = 30  # minutes between posts of the same source


class TelegramRemixer(BaseRemixer):
    name = "telegram"

    def __init__(self, cfg: Options) -> None:
        self.bot_token = cfg.bot_token
        self.chat_id = cfg.chat_id
        self.interval = timedelta(minutes=cfg.interval)

    def produce(
        self, db: Database, scope: ProcessingScope
    ) -> Iterator[tuple[str, str, str]]:
        now = datetime.now(UTC)
        state = self._load_state(db, now)
        self._enqueue(db, state, scope)
        self._post_due(db, state, now)
        yield "state", json.dumps(state, indent=2), "application/json"

    def _load_state(self, db: Database, now: datetime) -> dict[str, Any]:
        artifact = db.get_artifact(self.name, "state")
        if artifact is None or artifact.content is None:
            return {
                "watermark": now.isoformat(),
                "queue": [],
                "posted": [],
                "last_post": {},
            }
        return json.loads(artifact.content)

    def _enqueue(
        self, db: Database, state: dict[str, Any], scope: ProcessingScope
    ) -> None:
        if scope.since is None and scope.uids is None:
            watermark = datetime.fromisoformat(state["watermark"])
            scope = dataclasses.replace(scope, since=watermark)

        known = {(source_id, uid) for source_id, uid in state["queue"]}
        known |= {(source_id, uid) for source_id, uid, _ in state["posted"]}
        items = [item for item in db.get_items(scope) if item.key not in known]
        summaries = db.get_annotation_values(
            items, processor="summarize", key="summary"
        )
        state["queue"].extend(list(item.key) for item in items if item.key in summaries)

    def _post_due(self, db: Database, state: dict[str, Any], now: datetime) -> None:
        for source_id in dict.fromkeys(source_id for source_id, _ in state["queue"]):
            last_post = state["last_post"].get(source_id)
            if last_post and now - datetime.fromisoformat(last_post) < self.interval:
                continue

            uid = next(uid for queued, uid in state["queue"] if queued == source_id)
            (item,) = db.get_items(ProcessingScope(source=source_id, uids=(uid,)))
            try:
                message_id = self._post(db, item)
            except TelegramError as e:
                LOGGER.warning(f"{self.name}: could not post {source_id}/{uid}: {e}")
                continue

            state["queue"].remove([source_id, uid])
            state["posted"].append([source_id, uid, message_id])
            state["last_post"][source_id] = now.isoformat()

    def _post(self, db: Database, item: SourceItem) -> int:
        summaries = db.get_annotation_values(
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
                f"https://api.telegram.org/bot{self.bot_token.get_secret_value()}/{endpoint}",
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


def __newsmerger_plugin__(**options: Any) -> PluginObjects:
    remixer = TelegramRemixer(Options.model_validate(options))
    return [(remixer.name, Remixer, remixer)]
