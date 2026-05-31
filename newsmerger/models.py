from dataclasses import dataclass

from pydantic import BaseModel, HttpUrl

type JsonCompatibleType = (
    None
    | bool
    | int
    | float
    | str
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
    data: JsonCompatibleType

    @classmethod
    def from_data(cls, source: Source, entry: "SourceEntryData") -> "SourceEntry":
        return cls(
            source=source,
            id=entry.id,
            title=entry.title,
            data=entry.data,
        )


@dataclass(frozen=True)
class SourceEntryData:
    id: str
    title: str
    data: JsonCompatibleType
