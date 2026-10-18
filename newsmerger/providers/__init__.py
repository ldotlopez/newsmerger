import logging
from abc import abstractmethod
from collections.abc import Iterator

from ..httpclient import HTTPClient
from ..models import SourceData, SourceItemData

LOGGER = logging.getLogger(__name__)

type URI = str


class BaseProvider:
    def __init__(self, source: SourceData, *, fetcher: HTTPClient) -> None:
        self.source = source
        self.fetcher = fetcher

    @abstractmethod
    def retrieve_items(self) -> Iterator[SourceItemData]: ...


class IndexSiteProvider(BaseProvider):
    """A site with an index page listing article URLs, one item per article."""

    @property
    def index_url(self) -> str:
        return str(self.source.url)

    @abstractmethod
    def parse_index(self, content: bytes) -> Iterator[URI]: ...

    @abstractmethod
    def parse_item(self, content: bytes) -> SourceItemData: ...

    def retrieve_item(self, url: str) -> SourceItemData:
        """Fetch and parse one item URL."""
        return self.parse_item(self.fetcher.get(url))

    def retrieve_items(self) -> Iterator[SourceItemData]:
        for url in self.parse_index(self.fetcher.get(self.index_url)):
            try:
                yield self.retrieve_item(url)
            except ValueError as e:
                LOGGER.error(f"error '{e}' while parsing '{url}'")
