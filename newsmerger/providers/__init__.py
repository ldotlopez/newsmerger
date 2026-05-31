from abc import abstractmethod

from ..models import SourceEntryData


class BaseProvider:
    name: str

    @abstractmethod
    def parse_listing(self, buffer: bytes) -> list[SourceEntryData]: ...

    @abstractmethod
    def parse_item(self, buffer: bytes) -> SourceEntryData: ...
