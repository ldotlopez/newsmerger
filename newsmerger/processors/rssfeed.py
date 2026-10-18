"""Example ArtifactProcessor: builds a single RSS feed from scoped items.

Scope (--source/--since/--until/--limit) controls which items go into the
feed. Produces one artifact named "feed".
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from xml.sax.saxutils import escape

from ..db import ProcessingScope
from ..models import SourceItem
from . import ArtifactProcessor


class Processor(ArtifactProcessor):
    NAME = "rssfeed"

    def __init__(
        self, *args, title: str = "newsmerger feed", max_items: int = 100, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.title = title
        self.max_items = max_items

    def produce(self, scope: ProcessingScope) -> Iterator[tuple[str, str, str]]:
        effective_scope = scope
        if scope.limit is None:
            effective_scope = ProcessingScope(
                source=scope.source,
                since=scope.since,
                until=scope.until,
                uids=scope.uids,
                limit=self.max_items,
            )

        items = self.db.get_source_items(effective_scope)
        xml = self._build_feed(items)
        yield "feed", xml, "application/rss+xml"

    def _build_feed(self, items: list[SourceItem]) -> str:
        entries = "\n".join(self._build_entry(item) for item in items)
        now = datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S %z")

        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0"><channel>\n'
            f"<title>{escape(self.title)}</title>\n"
            f"<lastBuildDate>{now}</lastBuildDate>\n"
            f"{entries}\n"
            "</channel></rss>\n"
        )

    def _build_entry(self, item: SourceItem) -> str:
        pub_date = ""
        if item.published_at is not None:
            pub_date = item.published_at.astimezone(UTC).strftime(
                "%a, %d %b %Y %H:%M:%S %z"
            )

        return (
            "<item>\n"
            f"<title>{escape(item.title)}</title>\n"
            f"<link>{escape(item.uri)}</link>\n"
            f"<guid>{escape(item.uid)}</guid>\n"
            + (f"<pubDate>{pub_date}</pubDate>\n" if pub_date else "")
            + "</item>"
        )
