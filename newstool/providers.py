from __future__ import annotations

import logging
from abc import abstractmethod
from collections.abc import Iterator
from typing import Any, Protocol, runtime_checkable

import pydantic

from .httpclient import HTTPClient
from .models import PreflightSourceItemData, SourceData, SourceItemData
from .plugins import NoOptions, Services

LOGGER = logging.getLogger(__name__)

type URI = str


@runtime_checkable
class Provider(Protocol):
    """Retrieves all of a source's items in one go."""

    def retrieve_items(
        self, source: SourceData, fetcher: HTTPClient
    ) -> Iterator[SourceItemData]: ...


@runtime_checkable
class PreflightProvider[T](Protocol):
    """Retrieves a source's items in two stages: lists them, then fetches the
    ones the core asks for. A stored item listed with a `modified_at` that is
    not newer than the stored one is not fetched."""

    def iter_items(
        self, source: SourceData, fetcher: HTTPClient
    ) -> Iterator[PreflightSourceItemData[T]]: ...

    def retrieve_item(
        self, preflight_item: PreflightSourceItemData[T], fetcher: HTTPClient
    ) -> SourceItemData: ...


@runtime_checkable
class ProviderType(Protocol):
    """A Provider class, as plugins register it: each source builds one with
    its options, validated at startup with `options_model`."""

    options_model: type[pydantic.BaseModel]

    def __call__(
        self, options: Any, services: Services
    ) -> Provider | PreflightProvider: ...


class BaseProvider:
    """A Provider or PreflightProvider built with its source's options."""

    options_model: type[pydantic.BaseModel] = NoOptions

    def __init__(self, options: Any, services: Services) -> None:
        self.options = options


class IndexSiteProvider(BaseProvider):
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
