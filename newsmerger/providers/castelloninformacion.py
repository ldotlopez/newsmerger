from pydantic import HttpUrl

import bs4

from ..models import SourceItemData

import logging
from datetime import datetime
from typing import Iterator

from readability import Document

from ..models import SourceData
from . import URI, IndexSiteProvider
from ..httpclient import HTTPClient
import feedparser
import hashlib

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

        title = _get_meta_property(soup, "og:title")
        image = _get_meta_property(soup, "og:image")
        author = _get_meta_name(soup, "author")
        url = _get_meta_property(soup, "og:url")
        # tags = _get_meta_property(soup, "article:tag").split(",")
        # section = _get_meta_property(soup, "article:section")
        pub_time = datetime.fromisoformat(
            _get_meta_property(soup, "article:published_time")
        )
        mod_time = datetime.fromisoformat(
            _get_meta_property(soup, "article:modified_time")
        )

        doc = Document(soup.select_one(".tdb_single_content"))
        content = doc.summary()

        return SourceItemData(
            uid=hashlib.sha256(url.encode()).hexdigest(),
            title=title,
            uri=url,
            content=content,
            data={
                "author": author,
                "image": image,
                "pub_date": pub_time,
                "mod_date": mod_time,
            },
        )


def _get_meta_property(soup: bs4.BeautifulSoup, property: str) -> str:
    if (head_tag := soup.find("head")) is None:
        raise ValueError()

    # if (meta_tag := head_tag.find("meta", property=property)) is None:
    if (meta_tag := head_tag.find("meta", attrs={"property": property})) is None:
        raise ValueError()

    try:
        content = meta_tag.attrs["content"]
    except KeyError as e:
        raise ValueError() from e

    return content.strip()


def _get_meta_name(soup: bs4.BeautifulSoup, name: str) -> str:
    if (head_tag := soup.find("head")) is None:
        raise ValueError()

    if (meta_tag := head_tag.find("meta", attrs={"name": name})) is None:
        raise ValueError()

    try:
        content = meta_tag.attrs["content"]
    except KeyError as e:
        raise ValueError() from e

    return content.strip()
