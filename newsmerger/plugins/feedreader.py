import hashlib
import logging
from collections.abc import Iterator, Mapping
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urljoin

import feedparser
from feedparser import FeedParserDict
from foundation.scrapelib import soupify

from ..httpclient import HTTPClient
from ..models import SourceData, SourceItemData
from ..providers import Provider
from . import PluginObjects, PluginOptions, Services, merge_options

LOGGER = logging.getLogger(__name__)


class Options(PluginOptions):
    # CSS selector of the article body, for feeds that only carry a summary:
    # the item's content is then fetched from its link. The default for every
    # source; a source overrides it in its `options`.
    article_selector: str | None = None


class FeedReaderProvider:
    def __init__(self, cfg: Options) -> None:
        self.cfg = cfg

    def use_options(self, overrides: Mapping[str, Any]) -> Options:
        return merge_options(Options, self.cfg, overrides)

    def retrieve_items(
        self, source: SourceData, fetcher: HTTPClient, options: Options
    ) -> Iterator[SourceItemData]:
        feed = fetch_feed(str(source.url), fetcher)
        selector = options.article_selector
        for entry in feed["entries"]:
            try:
                item = parse_entry(entry)
                if selector is not None:
                    item.content = fetch_article(item.uri, selector, fetcher)
                    item.mimetype = "text/html"
                yield item
            except (KeyError, ValueError) as e:
                LOGGER.error(f"error '{e}' while parsing entry '{entry.get('link')}'")


def fetch_feed(url: str, fetcher: HTTPClient) -> FeedParserDict:
    content = fetcher.get(url)
    feed = feedparser.parse(content)
    # No version means HTML: maybe a site's home page advertising its feed.
    if not feed.version and (feed_url := discover_feed_url(content, url)):
        feed = feedparser.parse(fetcher.get(feed_url))
    # An empty but valid feed is fine.
    if not feed["entries"] and (feed.bozo or not feed.version):
        raise ValueError(f"not a valid feed: {feed.get('bozo_exception')}")
    return feed


def discover_feed_url(page: bytes, page_url: str) -> str | None:
    link = soupify(page.decode("utf-8", errors="replace")).select_one(
        'link[rel~="alternate"][type="application/rss+xml"][href],'
        'link[rel~="alternate"][type="application/atom+xml"][href]'
    )
    return urljoin(page_url, str(link["href"])) if link else None


def parse_entry(entry: FeedParserDict) -> SourceItemData:
    link = entry["link"]
    # Full body (content:encoded, atom:content) beats the summary/description.
    body = entry["content"][0] if entry.get("content") else entry["summary_detail"]
    tags = [t["term"] for t in entry.get("tags", []) if t.get("term")]

    return SourceItemData(
        # The guid is the entry identity; links may change (tracking params).
        uid=hashlib.sha256(entry.get("id", link).encode()).hexdigest(),
        title=entry.get("title", ""),
        uri=link,
        content=body["value"].encode("utf-8"),
        mimetype=body["type"],
        published_at=entry_date(entry, "published"),
        modified_at=entry_date(entry, "updated"),
        data={
            "author": ", ".join(
                a["name"] for a in entry.get("authors", []) if a.get("name")
            ),
            "image": find_image(entry, body),
            # RSS has no section; the first category is the closest thing.
            "section": tags[0] if tags else None,
            "tags": tags,
        },
    )


def entry_date(entry: FeedParserDict, key: str) -> datetime | None:
    # Plain dict access skips feedparser's deprecated updated -> published fallback.
    if key not in entry:
        return None
    parsed = dict.get(entry, f"{key}_parsed")
    if parsed is None:
        LOGGER.warning(f"unparseable {key} date '{entry[key]}' in '{entry['link']}'")
        return None
    # feedparser normalizes every *_parsed date to UTC.
    return datetime(*parsed[:6], tzinfo=UTC)


def find_image(entry: FeedParserDict, body: FeedParserDict) -> str | None:
    for media in entry.get("media_content", []):
        if media.get("medium") == "image" or media.get("type", "").startswith("image/"):
            return media["url"]
    for thumbnail in entry.get("media_thumbnail", []):
        return thumbnail["url"]
    for enclosure in entry.get("enclosures", []):
        if enclosure.get("type", "").startswith("image/"):
            return enclosure["href"]
    if body["type"] in ("text/html", "application/xhtml+xml") and (
        img := soupify(body["value"]).select_one("img[src]")
    ):
        return urljoin(entry["link"], str(img["src"]))
    return None


def fetch_article(url: str, selector: str, fetcher: HTTPClient) -> bytes:
    soup = soupify(fetcher.get(url).decode("utf-8"))
    if (article := soup.select_one(selector)) is None:
        raise ValueError(f"no element matches '{selector}'")
    return str(article).encode("utf-8")


def __newsmerger_plugin__(services: Services, **options: Any) -> PluginObjects:
    return [
        ("feedreader", Provider, FeedReaderProvider(Options.model_validate(options)))
    ]
