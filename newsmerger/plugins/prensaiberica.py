import hashlib
import logging
from collections.abc import Iterator
from datetime import datetime
from typing import Any
from urllib.parse import urljoin

import feedparser
from foundation.scrapelib import (
    drop_selectors,
    find_canonical_url,
    head_meta_get_value,
    prune_to_spine,
    soupify,
)

from ..httpclient import HTTPClient
from ..models import SourceData, SourceItemData
from ..providers import URI, IndexSiteProvider, URLProvider
from . import PluginObjects, PluginOptions, Services

LOGGER = logging.getLogger(__name__)


class PrensaIbericaProvider(IndexSiteProvider):
    def parse_index(
        self, content: bytes, source: SourceData, fetcher: HTTPClient
    ) -> Iterator[URI]:
        soup = soupify(content.decode("utf-8"))

        if not (tag := soup.select_one('html head link[rel="alternate"]')):
            LOGGER.warning("Could not find <link rel='alternate'> in index page")
            return

        href = tag.attrs.get("href")
        if not href:
            LOGGER.warning("Could not find href in <link rel='alternate'>")
            return

        if not href.startswith("/rss/section/"):
            LOGGER.warning(
                f"Unexpected href in <link rel='alternate'>: {href} (expected '/rss/section/...')"
            )
            return

        feed_url = urljoin(str(source.url), href)
        feed_content = fetcher.get(feed_url)
        fc = feedparser.parse(feed_content)
        yield from (entry["link"] for entry in fc["entries"])

    def parse_item(self, content: bytes) -> SourceItemData:
        soup = soupify(content.decode("utf-8"))

        title = head_meta_get_value(soup, {"property": "og:title"})
        image = head_meta_get_value(soup, {"property": "og:image"})
        author = head_meta_get_value(soup, {"name": "author"})
        if (url := find_canonical_url(soup)) is None:
            raise ValueError("no canonical URL")
        tags = head_meta_get_value(soup, {"property": "article:tag"}).split(",")
        section = head_meta_get_value(soup, {"property": "article:section"})
        pub_time = datetime.fromisoformat(
            head_meta_get_value(soup, {"property": "article:published_time"})
        )
        mod_time = datetime.fromisoformat(
            head_meta_get_value(soup, {"property": "article:modified_time"})
        )

        if (main := soup.select_one("#main-content")) is None:
            raise ValueError("Could not find main content container")

        for div in main.find_all("div", recursive=False):
            if div.get_text().find("Lo más leído") != -1:
                div.decompose()  # Remove the "Lo más leído" section

        drop_selectors(
            main,
            [
                "#paywall",
                ".ft-mol-rrss-column",
                ".ft-mol-advice",
                ".ft-ad",
                ".closedContent",
                ".ft-mol-writer",
                ".ft-mol-tagsNews",
                ".ft-mol-related",
                ".ft-mol-related__header",
                ".bloque_bajo_noticia",
                "a#comments",
                ".ft-mol-btnGroup",
                ".disqus_thread",
            ],
        )

        root = prune_to_spine(main)

        return SourceItemData(
            uid=hashlib.sha256(url.encode()).hexdigest(),
            title=title,
            uri=url,
            content=str(root).encode("utf-8"),
            mimetype="text/html",
            published_at=pub_time,
            modified_at=mod_time,
            data={
                "author": author,
                "image": image,
                "section": section,
                "tags": tags,
            },
        )


def __newsmerger_plugin__(services: Services, **options: Any) -> PluginObjects:
    PluginOptions.model_validate(options)
    return [("prensaiberica", URLProvider, PrensaIbericaProvider())]
