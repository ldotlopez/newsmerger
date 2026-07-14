# ---------------------------------------------------------------------------
# ORM models — persistence shape only. No knowledge of SourceData/SourceItem.
# ---------------------------------------------------------------------------
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.types import TypeDecorator

from ..jsonlib import dump_json_compatible, load_json_compatible

LOGGER = logging.getLogger(__name__)


class CustomJSON(TypeDecorator):
    """JSON column with pluggable encode/decode for non-standard Python types."""

    impl = JSON
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return None
        return dump_json_compatible(value)

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return None
        return load_json_compatible(value)


class Base(DeclarativeBase):
    pass


class DBUidMixin:
    uid: Mapped[str] = mapped_column(String(255), unique=True)


class DBSource(DBUidMixin, Base):
    """Internal DB model for Source"""

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String)
    provider: Mapped[str] = mapped_column(String)

    entries: Mapped[list[DBSourceItem]] = relationship(
        back_populates="source",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<DBSource(id={self.id}, url={self.url[:30]})>"


class DBSourceItem(DBUidMixin, Base):
    """Internal DB model for DBSourceItem"""

    __tablename__ = "source_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    uri: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(String)
    data: Mapped[dict] = mapped_column(CustomJSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    source: Mapped[DBSource] = relationship(back_populates="entries")

    def __repr__(self) -> str:
        return f"<DBSourceItem(id={self.id}, title={self.title})>"
