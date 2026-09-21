import logging
from abc import abstractmethod
from collections.abc import Iterator

from newsmerger.httpclient import HTTPClient

from ..models import SourceData, SourceItemData

LOGGER = logging.getLogger(__name__)

URI = str


class BaseProvider:
    NAME: str

    def __init__(self, source: SourceData) -> None:
        self.source = source

    @abstractmethod
    def retrieve_items(self) -> Iterator[SourceItemData]: ...


class IndexSiteProvider(BaseProvider):
    def __init__(self, source: SourceData, *, fetcher: HTTPClient) -> None:
        super().__init__(source)
        self.fetcher = fetcher

    @abstractmethod
    def parse_index(self, content: bytes) -> Iterator[URI]: ...

    @abstractmethod
    def parse_item(self, content: bytes) -> SourceItemData: ...

    def retrieve_item(self, url: str) -> SourceItemData:
        """Fetch and parse one item URL."""
        return self.parse_item(self.fetcher.get(url))

    def retrieve_items(self) -> Iterator[SourceItemData]:
        content = self.fetcher.get(str(self.source.url))
        links = self.parse_index(content)

        for url in links:
            content = self.fetcher.get(url)

            try:
                entry_data = self.parse_item(content)
            except ValueError as e:
                LOGGER.error(f"error '{e}' while parsing '{url}'")
                continue

            # TODO: is this the right place to do this check? maybe it should be done in parse_item instead
            if entry_data.content is None:
                LOGGER.warning(f"skipping entry with no content: {url}")
                continue

            yield entry_data
