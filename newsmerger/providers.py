import logging
from abc import abstractmethod
from collections.abc import Iterator, Mapping
from typing import Any, Protocol, runtime_checkable

import pydantic

from .httpclient import HTTPClient
from .models import SourceData, SourceItemData
from .plugins import NoOptions

LOGGER = logging.getLogger(__name__)

type URI = str


@runtime_checkable
class Provider[O: pydantic.BaseModel](Protocol):
    """Retrieves a source's items. Sources name it in `provider:`; their
    `options` are validated once, at startup, by `use_options`, and passed to
    every `retrieve_items`."""

    def use_options(self, overrides: Mapping[str, Any]) -> O:
        """A source's options over the plugin section's defaults. Raise
        `pydantic.ValidationError` for options the provider does not take."""
        ...

    def retrieve_items(
        self, source: SourceData, fetcher: HTTPClient, options: O
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

    def use_options(self, overrides: Mapping[str, Any]) -> NoOptions:
        return NoOptions.model_validate(overrides)

    def retrieve_item(self, url: str, fetcher: HTTPClient) -> SourceItemData:
        """Fetch and parse one item URL."""
        return self.parse_item(fetcher.get(url))

    def retrieve_items(
        self, source: SourceData, fetcher: HTTPClient, options: NoOptions
    ) -> Iterator[SourceItemData]:
        index = fetcher.get(self.index_url(source))
        for url in self.parse_index(index, source, fetcher):
            try:
                yield self.retrieve_item(url, fetcher)
            except ValueError as e:
                LOGGER.error(f"error '{e}' while parsing '{url}'")
