from __future__ import annotations

import dataclasses
import hashlib
from datetime import datetime
from typing import Any, TypeVar

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
    content: str | bytes = ""
    data: JsonCompatible = dataclasses.field(default_factory=lambda: {})
    published_at: datetime | None = None
    modified_at: datetime | None = None

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


class SourceItemData(
    UidFromNameMixin,
    UidFieldMixin,
    BaseModel,
):
    title: str
    uri: str
    content: str
    data: JsonCompatible = {}
    published_at: datetime | None = None
    modified_at: datetime | None = None
