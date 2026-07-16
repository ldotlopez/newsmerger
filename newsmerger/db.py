from __future__ import annotations

import contextlib
import logging
from abc import abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generic, Iterable, Iterator, Self, TypeVar

from foundation.jsonlib import dump_json_compatible, load_json_compatible
from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship, sessionmaker
from sqlalchemy.types import TypeDecorator

from .models import SourceData, SourceItem, SupportsUid

LOGGER = logging.getLogger(__name__)

Base = declarative_base()


DTO = TypeVar("DTO")


class DtoTransferMixin(Generic[DTO]):
    """Mixin for DB models to provide conversion to/from DTOs"""

    @classmethod
    @abstractmethod
    def from_dto(cls, dto: DTO, **kwargs) -> Self:
        """Convert from DTO to DB model"""
        pass

    @abstractmethod
    def to_dto(self) -> DTO:
        """Convert from DB model to DTO"""
        pass

    @abstractmethod
    def update(self, dto: DTO) -> None:
        """Update DB model from DTO"""
        pass


class CustomJSON(TypeDecorator):
    """JSON column with pluggable encode/decode for non-standard Python types."""

    impl = JSON
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        return dump_json_compatible(value)

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        return load_json_compatible(value)


class UTCDateTime(TypeDecorator):
    """DateTime column that round-trips tz-aware UTC datetimes safely.

    SQLite has no native datetime type: the sqlite3 driver stores it as a
    string and always returns naive datetimes on SELECT, silently dropping
    tzinfo. `DateTime(timezone=True)` alone does not protect against this —
    it's effectively a no-op under the sqlite dialect. This decorator
    normalizes to UTC on write and re-attaches UTC tzinfo on read, so callers
    always get a tz-aware datetime back regardless of backend. Naive
    datetimes are rejected on write to avoid silently assuming a timezone.
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Any) -> Any:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError(f"naive datetime not allowed: {value!r}")
        return value.astimezone(timezone.utc)

    def process_result_value(self, value: Any, dialect: Any) -> datetime | None:
        if value is None:
            return None
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


class DBSource(DtoTransferMixin[SourceData], Base):
    """Internal DB model for Source"""

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    # (provider, url) is expected to be unique in practice, but not enforced
    # here — providers are responsible for deriving correct uids from it.
    url: Mapped[str] = mapped_column(Text)
    provider: Mapped[str] = mapped_column(String(255))

    entries: Mapped[list[DBSourceItem]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )

    @classmethod
    def from_dto(cls, dto: SourceData, **kwargs) -> DBSource:
        """Convert from models.Source to DBSource"""
        return cls(
            uid=dto.uid,
            url=str(dto.url),
            provider=dto.provider,
            name=dto.name,
        )

    def update(self, dto: SourceData) -> None:
        """Update DBSource from models.Source"""
        self.name = dto.name
        self.url = str(dto.url)
        self.provider = dto.provider

    def to_dto(self) -> SourceData:
        """Convert from DBSource to models.Source"""
        return SourceData(
            uid=self.uid, name=self.name, url=self.url, provider=self.provider
        )

    def __repr__(self):
        return f"<DBSource(id={self.id}, name={self.url[:30]})>"


class DBSourceItem(DtoTransferMixin[SourceItem], Base):
    """Internal DB model for DBSourceItem"""

    __tablename__ = "source_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    title: Mapped[str] = mapped_column(Text)
    # Uid is provider-derived (often sha256(uri), but not guaranteed), so
    # uri gets its own real uniqueness/index rather than relying on uid.
    uri: Mapped[str] = mapped_column(Text, unique=True, index=True)
    content: Mapped[str] = mapped_column(Text)
    data: Mapped[dict] = mapped_column(CustomJSON, default=dict)

    # These are the ONLY two datetime columns on this table — they carry
    # dual meaning by convention rather than having separate system-clock
    # columns: sourced from the provider when available, falling back to
    # local time when the provider doesn't supply them (a new row with no
    # provider published_at gets "now"; an update to a row with no provider
    # modified_at gets "now" too). See Database.upsert_source_items for
    # where that decision is actually made — this table just stores the
    # result. Nullable here only as a defensive default; in practice every
    # row should end up with both populated.
    published_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    modified_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)

    source: Mapped[DBSource] = relationship(back_populates="entries")

    __table_args__ = (
        Index("ix_source_items_source_id_published_at", "source_id", "published_at"),
    )

    @classmethod
    def from_dto(cls, dto: SourceItem, **kwargs) -> DBSourceItem:
        """Convert from models.SourceItem to DBSourceItem.

        `published_at`/`modified_at` are read straight off the dto by
        default. Callers that need different values (e.g. a "now" fallback
        when the provider didn't supply one) can pass `published_at=...`/
        `modified_at=...` explicitly via kwargs to override the dto's values.
        """
        fields = {
            "uid": dto.uid,
            "title": dto.title,
            "uri": dto.uri,
            "content": dto.content,
            "data": dto.data if isinstance(dto.data, dict) else {},
            "published_at": dto.published_at,
            "modified_at": dto.modified_at,
        }
        fields.update(kwargs)
        return cls(**fields)

    def update(self, dto: SourceItem) -> None:
        """Update DBSourceItem from models.SourceItem.

        Unconditionally overwrites all mutable fields, including
        published_at/modified_at straight from the dto. This is the
        "no diffing, no comparison" update used by save_source_items's
        create-only path (it's actually never called there today, since
        that path only creates missing rows — see upsert_source_items for
        the diff-aware alternative).
        """
        self.title = dto.title
        self.uri = dto.uri
        self.content = dto.content
        self.data = dto.data if isinstance(dto.data, dict) else {}
        self.published_at = dto.published_at
        self.modified_at = dto.modified_at

    def to_dto(self) -> SourceItem:
        """Convert from DBSourceItem to models.SourceItem"""
        return SourceItem(
            source=self.source.to_dto(),
            uid=self.uid,
            title=self.title,
            uri=self.uri,
            content=self.content,
            data=self.data,
            published_at=self.published_at,
            modified_at=self.modified_at,
        )

    def __repr__(self):
        return f"<DBSourceItem(id={self.id}, title={self.title})>"


class Database:
    """Database connection and session management"""

    def __init__(self, database_url: str, create_schema: bool = True):
        """
        Initialize database connection.

        Args:
            database_url: SQLAlchemy database URL (e.g., 'sqlite:///newsmerger.db')
            create_schema: if True, create all tables defined on Base.metadata
                that don't already exist (no-op for existing tables; does not
                handle migrations of existing schemas — use Alembic for that).
        """
        self._ensure_sqlite_directory(database_url)

        try:
            self.engine = create_engine(database_url)
        except Exception:
            LOGGER.exception(f"Failed to create engine for '{database_url}'")
            raise

        if create_schema:
            try:
                Base.metadata.create_all(self.engine)
            except Exception:
                LOGGER.exception("Failed to create database schema")
                raise

        self.Session = sessionmaker(bind=self.engine)
        LOGGER.info(f"Using database at '{database_url}'")

    @staticmethod
    def _ensure_sqlite_directory(database_url: str) -> None:
        """Create the parent directory for a file-based SQLite URL, if needed."""
        prefix = "sqlite:///"
        if not database_url.startswith(prefix):
            return
        db_path_str = database_url[len(prefix) :]
        if db_path_str in ("", ":memory:") or db_path_str.startswith(":memory:"):
            return

        db_filepath = Path(db_path_str)
        try:
            db_filepath.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            LOGGER.exception(f"Failed to create directory for {db_filepath}")
            raise

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.Session()

    def close(self):
        """Close all connections"""
        self.engine.dispose()

    @contextlib.contextmanager
    def session_scope(self) -> Iterator[Session]:
        """Provide a transactional scope around a series of operations."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def save_source_items(self, items: list[SourceItem]):
        sources = {item.source for item in items}

        items_by_source = {source: [] for source in sources}
        for item in items:
            items_by_source[item.source].append(item)

        with self.session_scope() as sess:
            db_sources_map = dict(self._get_or_create_source_bulk(sess, sources))

            for source, items in items_by_source.items():
                db_source = db_sources_map[source]
                _ = dict(
                    self._get_or_create_bulk(
                        sess, DBSourceItem, items, source_id=db_source.id
                    )
                )

    def upsert_source_items(self, items: list[SourceItem]) -> None:
        """Alternative to `save_source_items`.

        NOT currently called from any active code path (cli.py still uses
        `save_source_items`). This exists as the diff-aware replacement we
        discussed: unlike `save_source_items`, which only ever inserts
        missing rows and silently no-ops on existing uids, this method also
        updates existing rows — but only the fields that actually changed,
        and with deliberate handling of published_at/modified_at:

        - New row: published_at/modified_at come from the provider if
          present, otherwise both default to "now".
        - Existing row: title/uri/content/data are diffed against what's
          stored. If nothing differs, the row is left untouched entirely
          (no write, no modified_at bump).
        - If something differs: modified_at is set to the provider's
          incoming value, UNLESS that incoming value is older than (or equal
          to) what's already stored, in which case the existing modified_at
          is trusted and left alone (an out-of-order/stale re-scrape
          shouldn't regress it). If the provider gave no modified_at at all,
          "now" is used.
        - published_at is only ever filled in when missing; an existing
          published_at is never overwritten by a later update.
        """
        sources = {item.source for item in items}

        items_by_source = {source: [] for source in sources}
        for item in items:
            items_by_source[item.source].append(item)

        with self.session_scope() as sess:
            db_sources_map = dict(self._get_or_create_source_bulk(sess, sources))

            for source, source_items in items_by_source.items():
                db_source = db_sources_map[source]
                self._upsert_source_items_bulk(
                    sess, source_items, source_id=db_source.id
                )

    def _upsert_source_items_bulk(
        self, session: Session, items: list[SourceItem], *, source_id: int
    ) -> None:
        """Get-or-create-or-update DBSourceItems for one source's items."""
        if not items:
            return

        items_by_uid = {item.uid: item for item in items}
        item_uids = list(dict.fromkeys(item.uid for item in items))

        existing_items = (
            session.query(DBSourceItem).filter(DBSourceItem.uid.in_(item_uids)).all()
        )
        existing_by_uid = {db_item.uid: db_item for db_item in existing_items}

        now = datetime.now(timezone.utc)
        created, updated, unchanged = 0, 0, 0

        for uid, item in items_by_uid.items():
            db_item = existing_by_uid.get(uid)

            if db_item is None:
                db_item = DBSourceItem.from_dto(
                    item,
                    source_id=source_id,
                    published_at=item.published_at or now,
                    modified_at=item.modified_at or now,
                )
                session.add(db_item)
                created += 1
                continue

            if self._apply_source_item_changes(session, db_item, item, now=now):
                updated += 1
            else:
                unchanged += 1

        if created:
            LOGGER.info(f"Created {created} new DBSourceItem entries")
        if updated:
            LOGGER.info(f"Updated {updated} existing DBSourceItem entries")
        LOGGER.debug(f"{unchanged} DBSourceItem entries unchanged")

        if created or updated:
            session.flush()

    def _apply_source_item_changes(
        self, session: Session, db_item: DBSourceItem, dto: SourceItem, *, now: datetime
    ) -> bool:
        """Diff `dto` against the stored `db_item` and apply changes in place.

        Returns True if anything was actually written. Only touches
        modified_at when a real content difference is found — a provider
        re-sending identical content should be a complete no-op, not a
        modified_at bump.

        Uses `session.is_modified()` instead of a manual field-by-field
        comparison: SQLAlchemy's unit-of-work already tracks per-attribute
        History, so trust it rather than hand-maintaining an equality check
        that has to be remembered every time a column is added.

        ORDERING IS LOAD-BEARING. title/uri/content/data must be assigned
        BEFORE `session.is_modified()` is called, and modified_at/published_at
        must be assigned AFTER. If modified_at/published_at were set before
        the check, they'd count as "changes" themselves and `is_modified()`
        would return True unconditionally — defeating the whole point of the
        check. Do not reorder these without re-verifying that invariant.
        """
        db_item.title = dto.title
        db_item.uri = dto.uri
        db_item.content = dto.content
        db_item.data = dto.data if isinstance(dto.data, dict) else {}

        # --- checkpoint: nothing below this line until the check itself ---
        content_changed = session.is_modified(db_item, include_collections=False)
        if not content_changed:
            return False
        # --- only modified_at/published_at assignments from here on ---

        if dto.modified_at is None:
            db_item.modified_at = now
        elif db_item.modified_at is None or dto.modified_at > db_item.modified_at:
            db_item.modified_at = dto.modified_at
        # else: incoming modified_at is older than (or equal to) what's
        # stored — trust the database, leave modified_at as-is.

        # published_at is filled once and never moved on subsequent updates.
        if db_item.published_at is None and dto.published_at is not None:
            db_item.published_at = dto.published_at

        return True

    def _get_or_create_source(self, session, source: SourceData) -> DBSource:
        return self._get_or_create_source_bulk(session, [source])[0][1]

    def _get_or_create_source_bulk(
        self, session, sources: Iterable[SourceData]
    ) -> list[tuple[SourceData, DBSource]]:
        return self._get_or_create_bulk(session, DBSource, sources)

        # """Get or create DBSources for the given SourceData list with a single lookup query."""
        # if not sources:
        #     return []

        # source_by_uid = {source.uid: source for source in sources}
        # source_uids = list(dict.fromkeys(source.uid for source in sources))

        # existing_sources = (
        #     session.query(DBSource).filter(DBSource.uid.in_(source_uids)).all()
        # )
        # db_sources_by_uid = {db_source.uid: db_source for db_source in existing_sources}

        # missing_sources = [
        #     source_by_uid[source_uid]
        #     for source_uid in source_uids
        #     if source_uid not in db_sources_by_uid
        # ]
        # for source in missing_sources:
        #     db_source = DBSource.from_dto(source)
        #     session.add(db_source)
        #     db_sources_by_uid[source.uid] = db_source

        # if missing_sources:
        #     session.flush()  # Ensure IDs are generated for newly created rows.

        # return [(source, db_sources_by_uid[source.uid]) for source in sources]

    def _get_or_create_bulk(
        self,
        session: Session,
        DBModel: type[Base],
        objects: Iterable[SupportsUid],
        **kwargs,
    ) -> list[tuple[SupportsUid, Base]]:
        """Get or create DBobjects for the given HasUidMember list with a single lookup query."""
        if not objects:
            return []

        objects_by_uid = {object.uid: object for object in objects}
        objects_uids = list(dict.fromkeys(object.uid for object in objects))

        existing_objects = (
            session.query(DBModel).filter(DBModel.uid.in_(objects_uids)).all()
        )
        db_objects_by_uid = {db_object.uid: db_object for db_object in existing_objects}

        missing_objects = [
            objects_by_uid[object_uid]
            for object_uid in objects_uids
            if object_uid not in db_objects_by_uid
        ]
        for object in missing_objects:
            db_object = DBModel.from_dto(object, **kwargs)
            session.add(db_object)
            db_objects_by_uid[object.uid] = db_object

        if missing_objects:
            LOGGER.info(
                f"Created {len(missing_objects)} new {DBModel.__name__} entries"
            )
            session.flush()  # Ensure IDs are generated for newly created rows.

        return [(object, db_objects_by_uid[object.uid]) for object in objects]
