import hashlib
import logging
from collections.abc import Iterator
from typing import Any

import feedparser

from ..httpclient import HTTPClient
from ..models import SourceData, SourceItemData
from ..providers import IndexSiteProvider, Provider
from . import PluginObjects, PluginOptions, Services

LOGGER = logging.getLogger(__name__)


class RssParserProvider(IndexSiteProvider):
    def retrieve_items(
        self, source: SourceData, fetcher: HTTPClient
    ) -> Iterator[SourceItemData]:
        content = fetcher.get(url=str(source.url))

        fc = feedparser.parse(content)
        for item in fc["items"]:
            yield SourceItemData(
                uid=hashlib.sha256(item["link"].encode()).hexdigest(),
                title=item["title"],
                uri=item["link"],
                content=item["content"][0]["value"],
                mimetype=item["content"][0]["type"],
                published_at=item["published"],
                modified_at=item["updated"],
                data={
                    "author": ", ".join([x["name"] for x in fc["items"][0]["authors"]]),
                    # "image": image,
                    # "section": section,
                    # "tags": tags,
                },
            )


def __newsmerger_plugin__(services: Services, **options: Any) -> PluginObjects:
    PluginOptions.model_validate(options)
    return [("rssparser", Provider, RssParserProvider())]
