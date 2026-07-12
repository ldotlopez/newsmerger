from typing import Iterator
from abc import abstractmethod

from ..models import SourceEntryData

URI = str


class BaseProvider:
    name: str

    @abstractmethod
    def parse_index(self, buffer: bytes) -> Iterator[URI]: ...

    @abstractmethod
    def parse_listing(self, buffer: bytes) -> Iterator[SourceEntryData]: ...

    @abstractmethod
    def parse_item(self, buffer: bytes) -> SourceEntryData: ...
