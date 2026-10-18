from __future__ import annotations

import dataclasses
import hashlib
from datetime import datetime
from typing import Any, Self, TypeVar

from foundation.jsonlib import JsonCompatible
from pydantic import BaseModel, HttpUrl, model_validator


class UidFieldMixin:
    uid: str


SupportsUid = TypeVar("SupportsUid", bound=UidFieldMixin)


class UidFromNameMixin(UidFieldMixin):
    @model_validator(mode="before")
    @classmethod
    def id_from_name(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        if data.get("uid"):
            return data

        seed = None
        if data.get("provider") and data.get("url"):
            seed = f"{data['provider']}:{data['url']}"
        elif data.get("uri"):
            seed = str(data["uri"])
        elif data.get("name"):
            seed = str(data["name"])
        elif data.get("id"):
            seed = str(data["id"])

        if seed:
            data["uid"] = hashlib.sha256(seed.encode()).hexdigest()

        return data


class SourceData(
    UidFromNameMixin,
    UidFieldMixin,
    BaseModel,
):
    name: str
    url: HttpUrl
    provider: str

    def __hash__(self) -> int:
        return hash(self.uid)


@dataclasses.dataclass(frozen=False)
class SourceItem:
    source: SourceData
    uid: str
    title: str
    uri: str
    # None when read back from the database: load it with Database.get_content().
    content: bytes | None = None
    mimetype: str = "application/octet-stream"
    content_sha256: str | None = None
    data: JsonCompatible = dataclasses.field(default_factory=dict)
    published_at: datetime | None = None
    modified_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.content is not None:
            self.content_sha256 = hashlib.sha256(self.content).hexdigest()

    @classmethod
    def from_data(cls, source: SourceData, data: SourceItemData) -> SourceItem:
        return cls(source=source, **data.model_dump())

        # return cls(
        #     source=source,
        #     id=entry.id,
        #     title=entry.title,
        #     uri=entry.uri,
        #     content=entry.content,
        #     data=entry.data,
        # )

    def __hash__(self) -> int:
        return hash((hash(self.source), self.uid))

    def as_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(slots=True)
class Artifact:
    """A processor output derived from many items (an RSS feed, a newsletter).

    Unique per (processor, name); the timestamps are set by the database.
    """

    processor: str
    name: str
    content: str
    content_type: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SourceItemData(
    UidFromNameMixin,
    UidFieldMixin,
    BaseModel,
):
    title: str
    uri: str
    content: bytes
    mimetype: str
    data: JsonCompatible = {}
    published_at: datetime | None = None
    modified_at: datetime | None = None

    @model_validator(mode="after")
    def text_is_utf8(self) -> Self:
        # Text is always stored as UTF-8, so the mimetype carries no charset.
        if ";" in self.mimetype:
            raise ValueError(f"mimetype must not have parameters: {self.mimetype!r}")
        if self.mimetype.startswith("text/"):
            try:
                self.content.decode("utf-8")
            except UnicodeDecodeError as e:
                raise ValueError(f"{self.mimetype} content is not UTF-8") from e
        return self
