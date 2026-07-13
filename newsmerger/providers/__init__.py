from newsmerger.httpclient import HTTPClient
from typing import Iterator
from abc import abstractmethod

from ..models import SourceEntryData
import logging

LOGGER = logging.getLogger(__name__)

URI = str


class BaseProvider:
    NAME: str

    @abstractmethod
    def retrieve_items(self) -> Iterator[SourceEntryData]: ...


class IndexSiteProvider(BaseProvider):
    def __init__(self, *, url: URI, fetcher: HTTPClient) -> None:
        self.url = url
        self.fetcher = fetcher

    @abstractmethod
    def parse_index(self, content: bytes) -> Iterator[URI]: ...

    @abstractmethod
    def parse_item(self, content: bytes) -> SourceEntryData: ...

    def retrieve_items(self) -> Iterator[SourceEntryData]:
        content = self.fetcher.get(self.url)
        links = self.parse_index(content)

        for url in links:
            content = self.fetcher.get(url)

            try:
                entry_data = self.parse_item(content)
            except ValueError as e:
                LOGGER.error(f"error '{e}' while parsing '{url}'")
                continue

            yield entry_data
