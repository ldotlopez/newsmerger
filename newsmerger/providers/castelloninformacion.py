import hashlib
import logging
from collections.abc import Iterator
from datetime import datetime

import bs4
import feedparser
from foundation.scrapelib import (
    drop_selectors,
    head_meta_get_value_by_name,
    head_meta_get_value_by_property,
    prune_to_spine,
)
from pydantic import HttpUrl

from ..httpclient import HTTPClient
from ..models import SourceData, SourceItemData
from . import URI, IndexSiteProvider

LOGGER = logging.getLogger(__name__)


class Provider(IndexSiteProvider):
    NAME = "castelloninformacion"

    def __init__(self, source: SourceData, *, fetcher: HTTPClient) -> None:
        source.url = HttpUrl(str(source.url).rstrip("/") + "/feed/")
        super().__init__(source, fetcher=fetcher)

    def parse_index(self, content: bytes) -> Iterator[URI]:
        feed = feedparser.parse(content.decode("utf-8"))
        for entry in feed.entries:
            yield entry.link

    def parse_item(self, content: bytes) -> SourceItemData:
        html = content.decode("utf-8")

        soup = bs4.BeautifulSoup(html, features="html5lib")

        title = head_meta_get_value_by_property(soup, "og:title")
        image = head_meta_get_value_by_property(soup, "og:image")
        author = head_meta_get_value_by_name(soup, "author")
        url = head_meta_get_value_by_property(soup, "og:url")
        # tags = head_meta_get_value_by_property(soup, "article:tag").split(",")
        # section = head_meta_get_value_by_property(soup, "article:section")
        pub_time = datetime.fromisoformat(
            head_meta_get_value_by_property(soup, "article:published_time")
        )
        mod_time = datetime.fromisoformat(
            head_meta_get_value_by_property(soup, "article:modified_time")
        )

        if (article := soup.select_one("article.post")) is None:
            raise ValueError("Article not found")

        drop_selectors(article, [".td-is-sticky"])
        root = prune_to_spine(article)

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
            },
        )
