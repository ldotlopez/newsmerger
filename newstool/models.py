from __future__ import annotations

import dataclasses
import hashlib
from datetime import datetime
from typing import Self

from foundation.jsonlib import JsonCompatible
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

# (source id, uid): an item's identity. Each source is its own uid space.
type ItemKey = tuple[str, str]


class SourceData(BaseModel):
    """A configured source. `id` is its identity and must stay stable."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    name: str
    url: HttpUrl
    provider: str
    # Over the provider's `plugins` section, the options its provider is
    # built with. Config only, like `skip_default`: the database stores
    # neither.
    options: dict[str, JsonCompatible] = Field(default_factory=dict)
    # Left out of the `default` workflow; workflows that name it use it.
    skip_default: bool = False

    def __hash__(self) -> int:
        # The id is the identity (decision 0001), and the options are a dict.
        return hash(self.id)


class SourceItemData(BaseModel):
    """A provider's output for one item, validated at the scraping boundary.

    `uid` is derived by the provider; it only has to be deterministic and
    stable within its source.
    """

    uid: str
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


@dataclasses.dataclass(frozen=True, slots=True)
class PreflightSourceItemData[T]:
    """An item as its source's index lists it, before fetching it."""

    uid: str
    ref: T  # what the plugin needs to fetch it; opaque to the core
    # As the index shows it, when it does: lets the core skip unchanged items.
    modified_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.modified_at is not None and self.modified_at.tzinfo is None:
            raise ValueError(
                f"modified_at must be timezone-aware: {self.modified_at!r}"
            )


@dataclasses.dataclass
class SourceItem:
    source: SourceData
    uid: str
    title: str
    uri: str
    # None when read back from the database: load it with Application.get_content().
    content: bytes | None = None
    mimetype: str = "application/octet-stream"
    content_sha256: str | None = None
    data: JsonCompatible = dataclasses.field(default_factory=dict)
    published_at: datetime | None = None
    modified_at: datetime | None = None
    # The database id: None until saved. A local handle, not the identity.
    id: int | None = None

    def __post_init__(self) -> None:
        if self.content is not None:
            self.content_sha256 = hashlib.sha256(self.content).hexdigest()

    @classmethod
    def from_data(cls, source: SourceData, data: SourceItemData) -> SourceItem:
        return cls(source=source, **data.model_dump())

    @property
    def key(self) -> ItemKey:
        return (self.source.id, self.uid)

    def __hash__(self) -> int:
        return hash(self.key)


@dataclasses.dataclass(slots=True)
class Artifact:
    """A remixer output derived from many items (an RSS feed, a newsletter).

    Unique per (remixer, name), where `remixer` holds the remix run's
    key (by default the remixer's name); the timestamps are set by the
    database.
    """

    remixer: str
    name: str
    content: str | None
    content_type: str
    content_sha256: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        if self.content is not None:
            self.content_sha256 = hashlib.sha256(self.content.encode()).hexdigest()


@dataclasses.dataclass(slots=True)
class Delivery:
    """A record of delivering one subject, an item or an artifact
    (decision 0007). `status` is a `db.DeliveryStatus`. `sink` holds the
    ledger key: `<workflow>/<key>`, or the bare key in `default`."""

    sink: str
    status: str
    item_id: int | None = None
    artifact_id: int | None = None
    attempts: int = 0
    last_error: str | None = None
    content_sha256: str | None = None  # the subject's content when delivered
    external_ref: JsonCompatible = None  # e.g. {"message_id": ...}
    created_at: datetime | None = None
    updated_at: datetime | None = None
    artifact_name: str | None = None  # "<remixer>/<name>", read back only
    id: int | None = None


@dataclasses.dataclass(slots=True)
class Annotation:
    """One key a processor stored for an item, with its value."""

    id: int
    item_id: int
    processor: str
    key: str
    updated_at: datetime
    value: JsonCompatible


@dataclasses.dataclass(frozen=True, slots=True)
class ProcessingScope:
    """Which items an operation applies to. Every field is optional and they
    combine; an unset field means no restriction on that axis."""

    source: str | None = None  # source id
    sources: tuple[str, ...] | None = None  # source ids: a workflow's
    since: datetime | None = None  # published_at >=
    until: datetime | None = None  # published_at <
    item_ids: tuple[int, ...] | None = None  # database ids
    limit: int | None = None
