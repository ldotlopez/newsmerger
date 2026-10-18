"""Builds an RSS feed from the newest items in scope, newest first, capped at
`max_items` unless the scope sets its own limit.

Produces one artifact named "feed".
"""

import dataclasses
from collections.abc import Iterator
from datetime import UTC, datetime
from xml.sax.saxutils import escape

from ..db import Database
from ..models import ProcessingScope, SourceItem
from . import BaseRemixer

RFC822 = "%a, %d %b %Y %H:%M:%S %z"


class Remixer(BaseRemixer):
    NAME = "rssfeed"

    def __init__(
        self,
        db: Database,
        *,
        title: str = "newsmerger feed",
        link: str | None = None,
        description: str | None = None,
        max_items: int = 100,
    ) -> None:
        super().__init__(db)
        self.title = title
        self.link = link
        self.description = description or title
        self.max_items = max_items

    def produce(self, scope: ProcessingScope) -> Iterator[tuple[str, str, str]]:
        if scope.limit is None:
            scope = dataclasses.replace(scope, limit=self.max_items)
        yield (
            "feed",
            self._build_feed(self.db.get_items(scope, newest_first=True)),
            "application/rss+xml",
        )

    def _build_feed(self, items: list[SourceItem]) -> str:
        entries = "\n".join(self._build_entry(item) for item in items)
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0"><channel>\n'
            f"<title>{escape(self.title)}</title>\n"
            + (f"<link>{escape(self.link)}</link>\n" if self.link else "")
            + f"<description>{escape(self.description)}</description>\n"
            + f"<lastBuildDate>{datetime.now(UTC).strftime(RFC822)}</lastBuildDate>\n"
            + f"{entries}\n"
            + "</channel></rss>\n"
        )

    def _build_entry(self, item: SourceItem) -> str:
        pub_date = ""
        if item.published_at is not None:
            pub_date = f"<pubDate>{item.published_at.astimezone(UTC).strftime(RFC822)}</pubDate>\n"

        return (
            "<item>\n"
            f"<title>{escape(item.title)}</title>\n"
            f"<link>{escape(item.uri)}</link>\n"
            f'<guid isPermaLink="false">{escape(item.source.id)}/{escape(item.uid)}</guid>\n'
            f"{pub_date}"
            "</item>"
        )
