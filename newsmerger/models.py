from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from pydantic import BaseModel, HttpUrl

type JsonCompatibleType = (
    None
    | bool
    | int
    | float
    | str
    | datetime
    | set["JsonCompatibleType"]
    | list["JsonCompatibleType"]
    | dict[str, "JsonCompatibleType"]
)


class Source(BaseModel):
    url: HttpUrl
    provider: str


class SourceEntry(BaseModel):
    source: Source
    id: str
    title: str
    uri: str
    content: str | bytes = ""
    data: JsonCompatibleType = {}

    @classmethod
    def from_data(cls, source: Source, entry: SourceEntryData) -> SourceEntry:
        return cls(
            source=source,
            id=entry.id,
            title=entry.title,
            uri=entry.uri,
            content=entry.content,
            data=entry.data,
        )


@dataclass(frozen=False)
class SourceEntryData:
    id: str
    title: str
    uri: str
    content: str
    data: JsonCompatibleType = field(default_factory=lambda: {})
