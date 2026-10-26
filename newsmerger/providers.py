import logging
from abc import abstractmethod
from collections.abc import Iterator
from typing import Any, Protocol, runtime_checkable

from .httpclient import HTTPClient
from .models import SourceData, SourceItemData

LOGGER = logging.getLogger(__name__)

type URI = str


@runtime_checkable
class Provider(Protocol):
    """Retrieves a source's items. Sources name it in `provider:` and pass it
    their `provider_options` as keyword arguments, which an implementation
    declares one by one (never `**kwargs`: the core checks them against its
    signature)."""

    def retrieve_items(
        self, source: SourceData, fetcher: HTTPClient, **provider_options: Any
    ) -> Iterator[SourceItemData]: ...


class IndexSiteProvider:
    """A Provider for a site with an index page listing article URLs, one
    item per article."""

    def index_url(self, source: SourceData) -> str:
        return str(source.url)

    @abstractmethod
    def parse_index(
        self, content: bytes, source: SourceData, fetcher: HTTPClient
    ) -> Iterator[URI]: ...

    @abstractmethod
    def parse_item(self, content: bytes) -> SourceItemData: ...

    def retrieve_item(self, url: str, fetcher: HTTPClient) -> SourceItemData:
        """Fetch and parse one item URL."""
        return self.parse_item(fetcher.get(url))

    def retrieve_items(
        self, source: SourceData, fetcher: HTTPClient
    ) -> Iterator[SourceItemData]:
        index = fetcher.get(self.index_url(source))
        for url in self.parse_index(index, source, fetcher):
            try:
                yield self.retrieve_item(url, fetcher)
            except ValueError as e:
                LOGGER.error(f"error '{e}' while parsing '{url}'")
