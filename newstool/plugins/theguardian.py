import hashlib
import logging
import re
from collections.abc import Iterator
from datetime import datetime
from urllib.parse import urljoin

import feedparser
from foundation.scrapelib import (
    drop_selectors,
    find_canonical_url,
    head_meta_get_value,
    soupify,
)

from ..errors import PluginFailure
from ..models import SourceData, SourceItemData
from ..providers import URI, IndexSiteProvider, ProviderType
from . import PluginTypes

LOGGER = logging.getLogger(__name__)

# Live blogs, videos, galleries and podcasts don't use the article body layout
NON_ARTICLE_RE = re.compile(r"/(live|video|gallery|audio|picture)/")


class TheGuardianProvider(IndexSiteProvider):
    def parse_index(self, content: bytes, source: SourceData) -> Iterator[URI]:
        soup = soupify(content.decode("utf-8"))
        tag = soup.select_one('link[rel="alternate"][type="application/rss+xml"]')
        if tag is None or not (href := tag.attrs.get("href")):
            raise PluginFailure("Could not find RSS feed link in index page")

        feed = feedparser.parse(self.fetcher.get(urljoin(self.index_url(source), href)))
        for entry in feed["entries"]:
            if NON_ARTICLE_RE.search(entry["link"]):
                LOGGER.debug(f"Skipping non-article entry '{entry['link']}'")
                continue
            yield entry["link"]

    def parse_item(self, content: bytes) -> SourceItemData:
        soup = soupify(content.decode("utf-8"))

        if (url := find_canonical_url(soup)) is None:
            raise PluginFailure("no canonical URL")
        title = head_meta_get_value(soup, {"property": "og:title"})
        image = head_meta_get_value(soup, {"property": "og:image"})
        section = head_meta_get_value(soup, {"property": "article:section"})
        tags = head_meta_get_value(soup, {"property": "article:tag"}).split(",")
        pub_time = datetime.fromisoformat(
            head_meta_get_value(soup, {"property": "article:published_time"})
        )
        mod_time = datetime.fromisoformat(
            head_meta_get_value(soup, {"property": "article:modified_time"})
        )
        author = ", ".join(
            a.get_text().strip() for a in soup.select('address a[rel="author"]')
        )

        if (body := soup.select_one(".article-body-commercial-selector")) is None:
            raise PluginFailure("Could not find article body container")

        drop_selectors(
            body,
            [
                "#sign-in-gate",
                "gu-island",
                "button",
                'figure[data-spacefinder-type$="NewsletterSignupBlockElement"]',
            ],
        )

        return SourceItemData(
            uid=hashlib.sha256(url.encode()).hexdigest(),
            title=title,
            uri=url,
            content=str(body).encode("utf-8"),
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


def __newstool_plugin__() -> PluginTypes:
    return [("theguardian", ProviderType, TheGuardianProvider)]
