"""Persistence: SQLite metadata plus a content-addressed DiskStorage.

Item, annotation and artifact contents live in one `DiskStorage`, keyed by
the sha256 of their bytes; rows only hold that key. SQLAlchemy models never
leave this module: `Database` takes and returns DTOs.
"""

from __future__ import annotations

import contextlib
import dataclasses
import enum
import hashlib
import logging
import sqlite3
from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Self

from foundation.jsonlib import dump_json_compatible, load_json_compatible
from foundation.storage import DiskStorage
from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    event,
    tuple_,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Query,
    Session,
    aliased,
    mapped_column,
    relationship,
    sessionmaker,
)
from sqlalchemy.types import TypeDecorator

from .models import (
    Annotation,
    Artifact,
    Delivery,
    ItemKey,
    ProcessingScope,
    SourceData,
    SourceItem,
)

LOGGER = logging.getLogger(__name__)

SQLITE_PRAGMAS = (
    "foreign_keys = ON",
    "busy_timeout = 5000",
    "journal_mode = WAL",
    "synchronous = NORMAL",
    "temp_store = MEMORY",
)


def _configure_sqlite_connection(
    dbapi_connection: sqlite3.Connection, connection_record: Any
) -> None:
    for pragma in SQLITE_PRAGMAS:
        dbapi_connection.execute(f"PRAGMA {pragma}")


class Base(DeclarativeBase):
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
    """DateTime column that round-trips tz-aware UTC datetimes.

    The sqlite3 driver returns naive datetimes, and `DateTime(timezone=True)`
    does not change that. This normalizes to UTC on write, re-attaches UTC on
    read, and rejects naive datetimes rather than guessing their timezone.
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Any) -> Any:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError(f"naive datetime not allowed: {value!r}")
        return value.astimezone(UTC)

    def process_result_value(self, value: Any, dialect: Any) -> datetime | None:
        if value is None:
            return None
        return value if value.tzinfo else value.replace(tzinfo=UTC)


# Ids are handles the CLI selects rows by (decision 0008): never reuse a
# deleted one.
AUTOINCREMENT = {"sqlite_autoincrement": True}


def _sha256_column() -> Mapped[str]:
    return mapped_column(String(64), index=True)


class DBSource(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(Text)
    provider: Mapped[str] = mapped_column(String(255))

    items: Mapped[list[DBSourceItem]] = relationship(
        back_populates="source", cascade="all, delete-orphan", passive_deletes=True
    )

    @classmethod
    def from_dto(cls, dto: SourceData) -> Self:
        return cls(id=dto.id, name=dto.name, url=str(dto.url), provider=dto.provider)

    def to_dto(self) -> SourceData:
        return SourceData(
            id=self.id, name=self.name, url=self.url, provider=self.provider
        )

    def update(self, dto: SourceData) -> None:
        self.name = dto.name
        self.url = str(dto.url)
        self.provider = dto.provider


class DBSourceItem(Base):
    __tablename__ = "source_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"))
    uid: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(Text)
    uri: Mapped[str] = mapped_column(Text)
    mimetype: Mapped[str] = mapped_column(String(255))
    content_sha256: Mapped[str] = _sha256_column()
    data: Mapped[dict] = mapped_column(CustomJSON, default=dict)
    # From the provider when it gives them, else the import time (see
    # Database._upsert_source_items).
    published_at: Mapped[datetime] = mapped_column(UTCDateTime)
    modified_at: Mapped[datetime] = mapped_column(UTCDateTime)

    source: Mapped[DBSource] = relationship(back_populates="items")

    __table_args__ = (
        UniqueConstraint("source_id", "uid"),
        Index("ix_source_items_source_id_published_at", "source_id", "published_at"),
        CheckConstraint(
            "length(content_sha256) = 64", name="ck_source_items_content_sha256"
        ),
        AUTOINCREMENT,
    )

    @classmethod
    def from_dto(cls, dto: SourceItem) -> Self:
        return cls(
            source_id=dto.source.id,
            uid=dto.uid,
            title=dto.title,
            uri=dto.uri,
            mimetype=dto.mimetype,
            content_sha256=dto.content_sha256,
            data=dto.data,
            published_at=dto.published_at,
            modified_at=dto.modified_at,
        )

    def to_dto(self) -> SourceItem:
        return SourceItem(
            source=self.source.to_dto(),
            uid=self.uid,
            title=self.title,
            uri=self.uri,
            mimetype=self.mimetype,
            content_sha256=self.content_sha256,
            data=self.data,
            published_at=self.published_at,
            modified_at=self.modified_at,
            id=self.id,
        )

    def update(self, dto: SourceItem) -> None:
        """Assign every field but the identity and the timestamps, whose
        no-regression rules live in Database._apply_source_item_changes."""
        self.title = dto.title
        self.uri = dto.uri
        self.mimetype = dto.mimetype
        self.content_sha256 = dto.content_sha256
        self.data = dto.data


class ProcessingStatus(enum.StrEnum):
    DONE = "done"
    ERROR = "error"
    IGNORED = "ignored"


def backoff_seconds(
    attempts: int,
    base: float = 60.0,
    factor: float = 2.0,
    max_seconds: float = 24 * 3600,
) -> float:
    """Exponential backoff between retries: base * factor**(attempts-1), capped."""
    return min(base * (factor ** max(attempts - 1, 0)), max_seconds)


class DBProcessingState(Base):
    """Per-(item, processor) run state; no row means never attempted.

    `ignored` is the processor's own permanent skip for that content.
    `error` rows count attempts for retries with backoff.
    """

    __tablename__ = "processing_state"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_item_id: Mapped[int] = mapped_column(
        ForeignKey("source_items.id", ondelete="CASCADE")
    )
    processor: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50))
    attempts: Mapped[int] = mapped_column(default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    # A different VERSION on the processor makes `done` items eligible again.
    processor_version: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Item content this state was computed from; a different one on the item
    # makes it eligible again.
    content_sha256: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime)

    __table_args__ = (
        UniqueConstraint("source_item_id", "processor"),
        Index("ix_processing_state_processor_status", "processor", "status"),
        CheckConstraint(
            "status IN ('done', 'error', 'ignored')", name="ck_processing_state_status"
        ),
        AUTOINCREMENT,
    )


class DBItemAnnotation(Base):
    """One key a processor produced for an item; the value lives in storage.

    Kept apart from DBProcessingState: a partial failure saves some keys
    while the item is still marked for retry.
    """

    __tablename__ = "item_annotations"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_item_id: Mapped[int] = mapped_column(
        ForeignKey("source_items.id", ondelete="CASCADE")
    )
    processor: Mapped[str] = mapped_column(String(255))
    key: Mapped[str] = mapped_column(String(255))
    content_sha256: Mapped[str] = _sha256_column()
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime)

    __table_args__ = (
        UniqueConstraint("source_item_id", "processor", "key"),
        Index("ix_item_annotations_processor", "processor"),
        AUTOINCREMENT,
    )


class DBArtifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    remixer: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(255))
    content_sha256: Mapped[str] = _sha256_column()
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime)

    __table_args__ = (UniqueConstraint("remixer", "name"), AUTOINCREMENT)

    @classmethod
    def from_dto(cls, dto: Artifact) -> Self:
        return cls(
            remixer=dto.remixer,
            name=dto.name,
            content_type=dto.content_type,
            content_sha256=dto.content_sha256,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def to_dto(self) -> Artifact:
        return Artifact(
            remixer=self.remixer,
            name=self.name,
            content=None,
            content_type=self.content_type,
            content_sha256=self.content_sha256,
            created_at=self.created_at,
            updated_at=self.updated_at,
            id=self.id,
        )

    def update(self, dto: Artifact) -> None:
        self.remixer = dto.remixer
        self.name = dto.name
        self.content_type = dto.content_type
        self.content_sha256 = dto.content_sha256
        self.updated_at = dto.updated_at


class DeliveryStatus(enum.StrEnum):
    QUEUED = "queued"
    SENDING = "sending"  # committed before the external call
    DONE = "done"
    ERROR = "error"


class DBDelivery(Base):
    """The delivery ledger: one row per (sink, subject), the record of an
    external fact, never regenerated (decision 0007)."""

    __tablename__ = "deliveries"

    id: Mapped[int] = mapped_column(primary_key=True)
    sink: Mapped[str] = mapped_column(String(255))
    source_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("source_items.id", ondelete="CASCADE"), nullable=True
    )
    artifact_id: Mapped[int | None] = mapped_column(
        ForeignKey("artifacts.id", ondelete="CASCADE"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(50))
    attempts: Mapped[int] = mapped_column(default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    external_ref: Mapped[Any] = mapped_column(CustomJSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime)

    artifact: Mapped[DBArtifact | None] = relationship()

    __table_args__ = (
        CheckConstraint(
            "(source_item_id IS NULL) != (artifact_id IS NULL)",
            name="ck_deliveries_one_subject",
        ),
        CheckConstraint(
            "status IN ('queued', 'sending', 'done', 'error')",
            name="ck_deliveries_status",
        ),
        UniqueConstraint("sink", "source_item_id"),
        UniqueConstraint("sink", "artifact_id"),
        Index("ix_deliveries_sink_status", "sink", "status"),
        AUTOINCREMENT,
    )

    @classmethod
    def from_dto(cls, dto: Delivery) -> Self:
        return cls(
            sink=dto.sink,
            source_item_id=dto.item_id,
            artifact_id=dto.artifact_id,
            status=dto.status,
            attempts=dto.attempts,
            last_error=dto.last_error,
            content_sha256=dto.content_sha256,
            external_ref=dto.external_ref,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def to_dto(self) -> Delivery:
        return Delivery(
            sink=self.sink,
            status=self.status,
            item_id=self.source_item_id,
            artifact_id=self.artifact_id,
            attempts=self.attempts,
            last_error=self.last_error,
            content_sha256=self.content_sha256,
            external_ref=self.external_ref,
            created_at=self.created_at,
            updated_at=self.updated_at,
            artifact_name=(
                f"{self.artifact.remixer}/{self.artifact.name}"
                if self.artifact is not None
                else None
            ),
            id=self.id,
        )

    def update(self, dto: Delivery) -> None:
        self.sink = dto.sink
        self.source_item_id = dto.item_id
        self.artifact_id = dto.artifact_id
        self.status = dto.status
        self.attempts = dto.attempts
        self.last_error = dto.last_error
        self.content_sha256 = dto.content_sha256
        self.external_ref = dto.external_ref
        self.created_at = dto.created_at
        self.updated_at = dto.updated_at


# Sort keys of the selection queries, by entity: the columns to sort by,
# ascending (oldest first for dates). The row id breaks ties.
ITEM_SORTS = {
    "id": [DBSourceItem.id],
    "source": [DBSourceItem.source_id],
    "published": [DBSourceItem.published_at],
    "updated": [DBSourceItem.modified_at],
    "title": [DBSourceItem.title],
}
ANNOTATION_SORTS = {
    "id": [DBItemAnnotation.id],
    "item": [
        DBItemAnnotation.source_item_id,
        DBItemAnnotation.processor,
        DBItemAnnotation.key,
    ],
    "processor": [DBItemAnnotation.processor, DBItemAnnotation.key],
    "updated": [DBItemAnnotation.updated_at],
}
ARTIFACT_SORTS = {
    "id": [DBArtifact.remixer, DBArtifact.name],
    "type": [DBArtifact.content_type],
    "created": [DBArtifact.created_at],
    "updated": [DBArtifact.updated_at],
}
DELIVERY_SORTS = {
    "id": [DBDelivery.id],
    "sink": [DBDelivery.sink],
    "status": [DBDelivery.status],
    "updated": [DBDelivery.updated_at],
}


def _encode_value(value: Any) -> tuple[str, bytes]:
    """An annotation value as stored: its JSON bytes and their sha256."""
    encoded = dump_json_compatible(value).encode()
    return hashlib.sha256(encoded).hexdigest(), encoded


class Database:
    def __init__(
        self, database_url: str, content_dir: Path, *, create_schema: bool = True
    ) -> None:
        """Open the database and the content storage.

        `create_schema` creates missing tables only; it never alters an
        existing schema.
        """
        self._ensure_sqlite_directory(database_url)
        self.engine = create_engine(database_url)
        if self.engine.dialect.name == "sqlite":
            event.listen(self.engine, "connect", _configure_sqlite_connection)
        if create_schema:
            Base.metadata.create_all(self.engine)

        self._sessionmaker = sessionmaker(bind=self.engine)
        self.contents = DiskStorage(content_dir)
        LOGGER.info(f"Using database at '{database_url}'")

    @staticmethod
    def _ensure_sqlite_directory(database_url: str) -> None:
        """Create the parent directory of a file-based SQLite URL."""
        prefix = "sqlite:///"
        if not database_url.startswith(prefix):
            return
        db_path = database_url.removeprefix(prefix)
        if db_path == "" or db_path.startswith(":memory:"):
            return
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    def close(self) -> None:
        self.engine.dispose()
        self.contents.close()

    @contextlib.contextmanager
    def session_scope(self) -> Iterator[Session]:
        """One transaction: commit on success, roll back on any error."""
        session = self._sessionmaker()
        try:
            yield session
            session.commit()
        except BaseException:
            session.rollback()
            raise
        finally:
            session.close()

    # --- Contents --------------------------------------------------------

    def get_content(self, item: SourceItem) -> bytes:
        """Return the item's stored content.

        Raise foundation.storage.EntryNotFoundError if the storage lost it.
        """
        if item.content_sha256 is None:
            raise ValueError(f"item {item.key} has no content reference")
        return self.get_stored_content(item.content_sha256)

    def get_stored_content(self, sha256: str) -> bytes:
        """Return the stored content with this sha256, whatever references it.

        Raise foundation.storage.EntryNotFoundError if there is none.
        """
        return self.contents.get(sha256)

    def _release_contents(self, sha256s: set[str]) -> None:
        """Delete the contents no row references any more.

        An upsert in another process that started referencing one of these
        between the check and the delete would lose its content: writers take
        `Application.lock()` (decision 0007) so that they never overlap.
        """
        if not sha256s:
            return
        referenced: set[str] = set()
        with self.session_scope() as sess:
            for column in (
                DBSourceItem.content_sha256,
                DBItemAnnotation.content_sha256,
                DBArtifact.content_sha256,
            ):
                referenced.update(
                    sha256
                    for (sha256,) in sess.query(column).filter(column.in_(sha256s))
                )
        for sha256 in sha256s - referenced:
            self.contents.delete(sha256)

    # --- Import ----------------------------------------------------------

    def upsert_source_items(self, items: list[SourceItem]) -> None:
        """Create or update items, and the sources they belong to, and set
        each item's `id`.

        Contents are written before the rows that reference them, so a crash
        leaves an unused file, never a row pointing at nothing. Contents the
        updated rows stopped using are released after the commit.
        """
        items_by_source: dict[SourceData, list[SourceItem]] = {}
        for item in items:
            items_by_source.setdefault(item.source, []).append(item)

        replaced: set[str] = set()
        with self.session_scope() as sess:
            for source, source_items in items_by_source.items():
                self._sync_source(sess, source)
                replaced |= self._upsert_source_items(sess, source, source_items)

        self._release_contents(replaced)

    def _sync_source(self, session: Session, source: SourceData) -> None:
        db_source = session.get(DBSource, source.id)
        if db_source is None:
            session.add(DBSource.from_dto(source))
        else:
            db_source.update(source)
        session.flush()

    def _upsert_source_items(
        self, session: Session, source: SourceData, items: list[SourceItem]
    ) -> set[str]:
        """Returns the sha256 of the contents the updated items stopped using."""
        items_by_uid = {item.uid: item for item in items}
        existing_by_uid = {
            db_item.uid: db_item
            for db_item in session.query(DBSourceItem).filter(
                DBSourceItem.source_id == source.id,
                DBSourceItem.uid.in_(items_by_uid),
            )
        }

        now = datetime.now(UTC)
        replaced: set[str] = set()
        rows: list[tuple[SourceItem, DBSourceItem]] = []
        created = updated = 0

        for uid, item in items_by_uid.items():
            if item.content is None or item.content_sha256 is None:
                raise ValueError(f"item {item.key} has no content to store")

            db_item = existing_by_uid.get(uid)
            if db_item is None:
                self.contents.set(item.content_sha256, item.content)
                db_item = DBSourceItem.from_dto(
                    dataclasses.replace(
                        item,
                        published_at=item.published_at or now,
                        modified_at=item.modified_at or now,
                    )
                )
                session.add(db_item)
                rows.append((item, db_item))
                created += 1
                continue

            rows.append((item, db_item))

            if db_item.content_sha256 != item.content_sha256:
                self.contents.set(item.content_sha256, item.content)
                replaced.add(db_item.content_sha256)

            if self._apply_source_item_changes(session, db_item, item, now=now):
                updated += 1

        session.flush()
        for item, db_item in rows:
            item.id = db_item.id
        LOGGER.info(f"{source.id}: {created} new, {updated} updated item(s)")
        return replaced

    def _apply_source_item_changes(
        self, session: Session, db_item: DBSourceItem, dto: SourceItem, *, now: datetime
    ) -> bool:
        """Apply `dto` to `db_item`; return whether anything changed.

        Ordering is load-bearing: `update()` must run before
        `session.is_modified()` and the timestamps after it, or the
        timestamps themselves would count as changes.
        """
        db_item.update(dto)
        if not session.is_modified(db_item, include_collections=False):
            return False

        if dto.modified_at is None:
            db_item.modified_at = now
        elif dto.modified_at > db_item.modified_at:
            db_item.modified_at = dto.modified_at
        # published_at is set once, on creation, and never moved.
        return True

    # --- Items -------------------------------------------------------------

    def get_items(
        self,
        scope: ProcessingScope | None = None,
        *,
        newest_first: bool = False,
        sort: str = "published",
    ) -> list[SourceItem]:
        """Items in scope, by an `ITEM_SORTS` key, ascending unless
        `newest_first`; `limit` keeps the first ones in that order."""
        scope = scope or ProcessingScope()
        columns = [*ITEM_SORTS[sort], DBSourceItem.id]
        with self.session_scope() as sess:
            query = self._apply_scope(sess.query(DBSourceItem), scope)
            query = query.order_by(
                *(column.desc() if newest_first else column for column in columns)
            )
            if scope.limit:
                query = query.limit(scope.limit)
            return [db_item.to_dto() for db_item in query]

    @staticmethod
    def _apply_scope(query: Query, scope: ProcessingScope) -> Query:
        if scope.source:
            query = query.filter(DBSourceItem.source_id == scope.source)
        if scope.since:
            query = query.filter(DBSourceItem.published_at >= scope.since)
        if scope.until:
            query = query.filter(DBSourceItem.published_at < scope.until)
        if scope.item_ids:
            query = query.filter(DBSourceItem.id.in_(scope.item_ids))
        return query

    @staticmethod
    def _get_item_row(session: Session, item: SourceItem) -> DBSourceItem:
        return (
            session.query(DBSourceItem)
            .filter_by(source_id=item.source.id, uid=item.uid)
            .one()
        )

    # --- Processing state --------------------------------------------------

    def get_unprocessed_items(
        self,
        processor: str,
        *,
        version: str | None,
        max_retries: int,
        force: bool = False,
        scope: ProcessingScope | None = None,
        requires: str | None = None,
    ) -> list[SourceItem]:
        """Items a processor should run on, oldest first.

        With `requires`, only items that processor finished on their current
        content are candidates, even with `force`: the rest wait instead of
        failing here. `force` skips eligibility, including `ignored` items.
        """
        scope = scope or ProcessingScope()
        now = datetime.now(UTC)

        with self.session_scope() as sess:
            query = sess.query(DBSourceItem, DBProcessingState).outerjoin(
                DBProcessingState,
                (DBProcessingState.source_item_id == DBSourceItem.id)
                & (DBProcessingState.processor == processor),
            )
            if requires is not None:
                query = self._join_finished(query, requires)
            query = self._apply_scope(query, scope).order_by(DBSourceItem.published_at)

            result = []
            for db_item, state in query:
                if not force and not self._is_eligible(
                    state, db_item.content_sha256, version, max_retries, now
                ):
                    continue
                result.append(db_item.to_dto())
                if scope.limit and len(result) >= scope.limit:
                    break
            return result

    @staticmethod
    def _join_finished(query: Query, processor: str) -> Query:
        """Keep the items `processor` finished on their current content."""
        upstream = aliased(DBProcessingState)
        return query.join(
            upstream,
            (upstream.source_item_id == DBSourceItem.id)
            & (upstream.processor == processor)
            & (upstream.status == ProcessingStatus.DONE)
            & (upstream.content_sha256 == DBSourceItem.content_sha256),
        )

    @staticmethod
    def _is_eligible(
        state: DBProcessingState | None,
        content_sha256: str,
        version: str | None,
        max_retries: int,
        now: datetime,
    ) -> bool:
        if state is None:
            return True  # never attempted
        if state.content_sha256 != content_sha256:
            return True  # the item's content changed since the last run
        if state.status == ProcessingStatus.IGNORED:
            return False  # permanent for this content; only force revisits it
        if state.status == ProcessingStatus.DONE:
            return state.processor_version != version
        if state.attempts >= max_retries:
            return False
        elapsed = (now - state.updated_at).total_seconds()
        return elapsed >= backoff_seconds(state.attempts)

    def record_result(
        self,
        item: SourceItem,
        processor: str,
        status: ProcessingStatus,
        *,
        annotations: dict[str, Any] | None = None,
        error: str | None = None,
        version: str | None = None,
        reset_attempts: bool = False,
    ) -> None:
        """Save a run's annotations and state in one transaction.

        The state records `item.content_sha256`, the content the run used.
        `reset_attempts` starts the retry count afresh (forced runs).
        """
        replaced: set[str] = set()
        with self.session_scope() as sess:
            db_item = self._get_item_row(sess, item)
            now = datetime.now(UTC)
            if annotations:
                replaced = self._save_annotations(
                    sess, db_item.id, processor, annotations, now
                )
            self._save_state(
                sess, db_item, processor, status, error, version, reset_attempts, now
            )
        self._release_contents(replaced)

    @staticmethod
    def _save_state(
        session: Session,
        db_item: DBSourceItem,
        processor: str,
        status: ProcessingStatus,
        error: str | None,
        version: str | None,
        reset_attempts: bool,
        now: datetime,
    ) -> None:
        state = (
            session.query(DBProcessingState)
            .filter_by(source_item_id=db_item.id, processor=processor)
            .one_or_none()
        )
        if state is None:
            state = DBProcessingState(
                source_item_id=db_item.id,
                processor=processor,
                attempts=0,
                created_at=now,
            )
            session.add(state)
        elif reset_attempts or state.content_sha256 != db_item.content_sha256:
            state.attempts = 0

        state.status = status
        state.content_sha256 = db_item.content_sha256
        state.processor_version = version
        state.updated_at = now
        if status == ProcessingStatus.ERROR:
            state.attempts += 1
            state.last_error = error
        else:
            state.attempts = 0
            state.last_error = None

    # --- Annotations -------------------------------------------------------

    def _save_annotations(
        self,
        session: Session,
        source_item_id: int,
        processor: str,
        values: dict[str, Any],
        now: datetime,
    ) -> set[str]:
        """Store values, then upsert their rows; returns the replaced contents."""
        existing_by_key = {
            row.key: row
            for row in session.query(DBItemAnnotation)
            .filter_by(source_item_id=source_item_id, processor=processor)
            .filter(DBItemAnnotation.key.in_(values))
        }

        replaced: set[str] = set()
        for key, value in values.items():
            sha256, encoded = _encode_value(value)
            self.contents.set(sha256, encoded)

            row = existing_by_key.get(key)
            if row is None:
                session.add(
                    DBItemAnnotation(
                        source_item_id=source_item_id,
                        processor=processor,
                        key=key,
                        content_sha256=sha256,
                        created_at=now,
                        updated_at=now,
                    )
                )
            elif row.content_sha256 != sha256:
                replaced.add(row.content_sha256)
                row.content_sha256 = sha256
                row.updated_at = now
        return replaced

    def _load_value(self, sha256: str) -> Any:
        return load_json_compatible(self.contents.get(sha256).decode())

    def get_annotations(
        self,
        item: SourceItem,
        *,
        processor: str | None = None,
        key: str | None = None,
    ) -> dict[str, dict[str, Any]]:
        """An item's annotations as `{processor: {key: value}}`.

        `processor`/`key` narrow the result; nothing found is `{}`.
        """
        with self.session_scope() as sess:
            query = (
                sess.query(
                    DBItemAnnotation.processor,
                    DBItemAnnotation.key,
                    DBItemAnnotation.content_sha256,
                )
                .join(DBSourceItem, DBItemAnnotation.source_item_id == DBSourceItem.id)
                .filter(
                    DBSourceItem.source_id == item.source.id,
                    DBSourceItem.uid == item.uid,
                )
            )
            if processor is not None:
                query = query.filter(DBItemAnnotation.processor == processor)
            if key is not None:
                query = query.filter(DBItemAnnotation.key == key)
            rows = query.all()

        result: dict[str, dict[str, Any]] = {}
        for row_processor, row_key, sha256 in rows:
            result.setdefault(row_processor, {})[row_key] = self._load_value(sha256)
        return result

    def get_annotation_keys(
        self, item_ids: Iterable[int]
    ) -> dict[int, list[tuple[int, str, str]]]:
        """The `(id, processor, key)` of each item's annotations, by item id,
        read in a single query. Items without annotations are absent."""
        item_ids = list(item_ids)
        if not item_ids:
            return {}
        with self.session_scope() as sess:
            rows = (
                sess.query(
                    DBItemAnnotation.source_item_id,
                    DBItemAnnotation.id,
                    DBItemAnnotation.processor,
                    DBItemAnnotation.key,
                )
                .filter(DBItemAnnotation.source_item_id.in_(item_ids))
                .order_by(DBItemAnnotation.processor, DBItemAnnotation.key)
                .all()
            )
        result: dict[int, list[tuple[int, str, str]]] = {}
        for item_id, annotation_id, processor, key in rows:
            result.setdefault(item_id, []).append((annotation_id, processor, key))
        return result

    def find_annotations(
        self,
        scope: ProcessingScope | None = None,
        *,
        processor: str | None = None,
        key: str | None = None,
        annotation_ids: Iterable[int] | None = None,
        sort: str = "item",
    ) -> list[Annotation]:
        """Annotations of the items in scope, with their values, by an
        `ANNOTATION_SORTS` key. Every filter combines; `limit` counts
        annotations."""
        scope = scope or ProcessingScope()
        with self.session_scope() as sess:
            query = sess.query(DBItemAnnotation).join(
                DBSourceItem, DBItemAnnotation.source_item_id == DBSourceItem.id
            )
            query = self._apply_scope(query, scope)
            if processor is not None:
                query = query.filter(DBItemAnnotation.processor == processor)
            if key is not None:
                query = query.filter(DBItemAnnotation.key == key)
            if annotation_ids is not None:
                query = query.filter(DBItemAnnotation.id.in_(annotation_ids))
            query = query.order_by(*ANNOTATION_SORTS[sort], DBItemAnnotation.id)
            if scope.limit:
                query = query.limit(scope.limit)
            rows = [
                (
                    row.id,
                    row.source_item_id,
                    row.processor,
                    row.key,
                    row.updated_at,
                    row.content_sha256,
                )
                for row in query
            ]
        return [
            Annotation(
                id=annotation_id,
                item_id=item_id,
                processor=row_processor,
                key=row_key,
                updated_at=updated_at,
                value=self._load_value(sha256),
            )
            for annotation_id, item_id, row_processor, row_key, updated_at, sha256 in rows
        ]

    def get_annotation_values(
        self, items: Iterable[SourceItem], *, processor: str, key: str
    ) -> dict[ItemKey, Any]:
        """One annotation's value per item, read in a single query.

        Items without that annotation are absent from the result.
        """
        keys = [item.key for item in items]
        if not keys:
            return {}
        with self.session_scope() as sess:
            rows = (
                sess.query(
                    DBSourceItem.source_id,
                    DBSourceItem.uid,
                    DBItemAnnotation.content_sha256,
                )
                .join(
                    DBItemAnnotation, DBItemAnnotation.source_item_id == DBSourceItem.id
                )
                .filter(
                    tuple_(DBSourceItem.source_id, DBSourceItem.uid).in_(keys),
                    DBItemAnnotation.processor == processor,
                    DBItemAnnotation.key == key,
                )
                .all()
            )
        return {
            (source_id, uid): self._load_value(sha256)
            for source_id, uid, sha256 in rows
        }

    def delete_annotations(
        self, *, processor: str | None = None, item_id: int | None = None
    ) -> int:
        """Delete annotations by processor, by item, or both, together with
        their processing state, so the items become pending again.

        Returns the number of annotations deleted.
        """
        if processor is None and item_id is None:
            raise ValueError("give a processor, an item, or both")

        with self.session_scope() as sess:
            annotations = sess.query(DBItemAnnotation)
            states = sess.query(DBProcessingState)
            if processor is not None:
                annotations = annotations.filter(
                    DBItemAnnotation.processor == processor
                )
                states = states.filter(DBProcessingState.processor == processor)
            if item_id is not None:
                annotations = annotations.filter(
                    DBItemAnnotation.source_item_id == item_id
                )
                states = states.filter(DBProcessingState.source_item_id == item_id)

            released = {row.content_sha256 for row in annotations}
            deleted = annotations.delete(synchronize_session=False)
            states.delete(synchronize_session=False)

        self._release_contents(released)
        return deleted

    def delete_items(self, item_ids: Iterable[int]) -> int:
        """Delete items with everything that references them (processing
        state, annotations, deliveries) and release their contents; return
        how many were deleted."""
        item_ids = list(item_ids)
        if not item_ids:
            return 0
        with self.session_scope() as sess:
            released = {
                sha256
                for (sha256,) in sess.query(DBSourceItem.content_sha256).filter(
                    DBSourceItem.id.in_(item_ids)
                )
            }
            released |= {
                sha256
                for (sha256,) in sess.query(DBItemAnnotation.content_sha256).filter(
                    DBItemAnnotation.source_item_id.in_(item_ids)
                )
            }
            # The foreign keys cascade to state, annotations and deliveries.
            deleted = (
                sess.query(DBSourceItem)
                .filter(DBSourceItem.id.in_(item_ids))
                .delete(synchronize_session=False)
            )
        self._release_contents(released)
        return deleted

    # --- Artifacts ---------------------------------------------------------

    def save_artifact(self, artifact: Artifact) -> None:
        """Create or replace the artifact named (remixer, name)."""
        if artifact.content is None or artifact.content_sha256 is None:
            raise ValueError(f"artifact {artifact.remixer}/{artifact.name} is empty")
        self.contents.set(artifact.content_sha256, artifact.content.encode())

        replaced: set[str] = set()
        with self.session_scope() as sess:
            now = datetime.now(UTC)
            stamped = dataclasses.replace(artifact, created_at=now, updated_at=now)
            existing = (
                sess.query(DBArtifact)
                .filter_by(remixer=artifact.remixer, name=artifact.name)
                .one_or_none()
            )
            if existing is None:
                sess.add(DBArtifact.from_dto(stamped))
            else:
                if existing.content_sha256 != artifact.content_sha256:
                    replaced.add(existing.content_sha256)
                existing.update(stamped)
        self._release_contents(replaced)

    def get_artifact(self, remixer: str, name: str) -> Artifact | None:
        with self.session_scope() as sess:
            db_artifact = (
                sess.query(DBArtifact)
                .filter_by(remixer=remixer, name=name)
                .one_or_none()
            )
            artifact = db_artifact.to_dto() if db_artifact is not None else None

        if artifact is not None and artifact.content_sha256 is not None:
            artifact.content = self.contents.get(artifact.content_sha256).decode()
        return artifact

    def delete_artifacts(self, names: Iterable[tuple[str, str]]) -> int:
        """Delete the `(remixer, name)` artifacts with their deliveries and
        release their contents; return how many were deleted."""
        names = list(names)
        if not names:
            return 0
        with self.session_scope() as sess:
            query = sess.query(DBArtifact).filter(
                tuple_(DBArtifact.remixer, DBArtifact.name).in_(names)
            )
            released = {artifact.content_sha256 for artifact in query}
            deleted = query.delete(synchronize_session=False)
        self._release_contents(released)
        return deleted

    def list_artifacts(
        self,
        remixer: str | None = None,
        *,
        names: Iterable[tuple[str, str]] | None = None,
        limit: int | None = None,
        sort: str = "id",
    ) -> list[Artifact]:
        """Artifacts by an `ARTIFACT_SORTS` key, without their content.
        `names` keeps only these `(remixer, name)` pairs; filters combine."""
        with self.session_scope() as sess:
            query = sess.query(DBArtifact).order_by(
                *ARTIFACT_SORTS[sort], DBArtifact.id
            )
            if remixer is not None:
                query = query.filter(DBArtifact.remixer == remixer)
            if names is not None:
                query = query.filter(
                    tuple_(DBArtifact.remixer, DBArtifact.name).in_(list(names))
                )
            if limit:
                query = query.limit(limit)
            return [db_artifact.to_dto() for db_artifact in query]

    # --- Deliveries --------------------------------------------------------

    def queue_item_deliveries(
        self, sink: str, scope: ProcessingScope, *, requires: str | None = None
    ) -> int:
        """Queue the items in scope that have no row for `sink`; return how
        many. With `requires`, only items that processor finished on their
        current content."""
        now = datetime.now(UTC)
        with self.session_scope() as sess:
            recorded = sess.query(DBDelivery.source_item_id).filter(
                DBDelivery.sink == sink, DBDelivery.source_item_id.is_not(None)
            )
            query = sess.query(DBSourceItem.id).filter(DBSourceItem.id.not_in(recorded))
            if requires is not None:
                query = self._join_finished(query, requires)
            query = self._apply_scope(query, scope).order_by(DBSourceItem.published_at)
            if scope.limit:
                query = query.limit(scope.limit)
            item_ids = [item_id for (item_id,) in query]
            sess.add_all(
                DBDelivery.from_dto(
                    Delivery(
                        sink=sink,
                        status=DeliveryStatus.QUEUED,
                        item_id=item_id,
                        created_at=now,
                        updated_at=now,
                    )
                )
                for item_id in item_ids
            )
        return len(item_ids)

    def queue_artifact_deliveries(
        self,
        sink: str,
        remixers: Iterable[str],
        *,
        since: datetime | None = None,
        names: Iterable[tuple[str, str]] | None = None,
    ) -> int:
        """Queue the artifacts of `remixers` that have no row for `sink`,
        created since `since` and named in `names` when given; return how
        many."""
        now = datetime.now(UTC)
        with self.session_scope() as sess:
            recorded = sess.query(DBDelivery.artifact_id).filter(
                DBDelivery.sink == sink, DBDelivery.artifact_id.is_not(None)
            )
            query = sess.query(DBArtifact.id).filter(
                DBArtifact.remixer.in_(list(remixers)),
                DBArtifact.id.not_in(recorded),
            )
            if since is not None:
                query = query.filter(DBArtifact.created_at >= since)
            if names is not None:
                query = query.filter(
                    tuple_(DBArtifact.remixer, DBArtifact.name).in_(list(names))
                )
            artifact_ids = [artifact_id for (artifact_id,) in query]
            sess.add_all(
                DBDelivery.from_dto(
                    Delivery(
                        sink=sink,
                        status=DeliveryStatus.QUEUED,
                        artifact_id=artifact_id,
                        created_at=now,
                        updated_at=now,
                    )
                )
                for artifact_id in artifact_ids
            )
        return len(artifact_ids)

    def get_item_deliveries(
        self,
        sink: str,
        scope: ProcessingScope | None = None,
        *,
        statuses: Iterable[DeliveryStatus] | None = None,
    ) -> list[tuple[Delivery, SourceItem]]:
        """The sink's rows for items in scope, with their items, oldest item
        first (the FIFO order)."""
        scope = scope or ProcessingScope()
        with self.session_scope() as sess:
            query = (
                sess.query(DBDelivery, DBSourceItem)
                .join(DBSourceItem, DBDelivery.source_item_id == DBSourceItem.id)
                .filter(DBDelivery.sink == sink)
            )
            if statuses is not None:
                query = query.filter(DBDelivery.status.in_(list(statuses)))
            query = self._apply_scope(query, scope).order_by(
                DBSourceItem.published_at, DBSourceItem.id
            )
            return [(row.to_dto(), db_item.to_dto()) for row, db_item in query]

    def get_artifact_deliveries(
        self,
        sink: str,
        *,
        statuses: Iterable[DeliveryStatus] | None = None,
        names: Iterable[tuple[str, str]] | None = None,
    ) -> list[tuple[Delivery, Artifact]]:
        """The sink's rows for artifacts, with their metadata (no content),
        oldest artifact first."""
        with self.session_scope() as sess:
            query = (
                sess.query(DBDelivery, DBArtifact)
                .join(DBArtifact, DBDelivery.artifact_id == DBArtifact.id)
                .filter(DBDelivery.sink == sink)
            )
            if statuses is not None:
                query = query.filter(DBDelivery.status.in_(list(statuses)))
            if names is not None:
                query = query.filter(
                    tuple_(DBArtifact.remixer, DBArtifact.name).in_(list(names))
                )
            query = query.order_by(DBArtifact.created_at, DBArtifact.id)
            return [(row.to_dto(), db_artifact.to_dto()) for row, db_artifact in query]

    def save_delivery(self, delivery: Delivery) -> None:
        """Store a row's new state, stamped now, in its own transaction."""
        if delivery.id is None:
            raise ValueError("only stored deliveries can be saved")
        delivery.updated_at = datetime.now(UTC)
        with self.session_scope() as sess:
            sess.get_one(DBDelivery, delivery.id).update(delivery)

    def last_delivery_by_source(self, sink: str) -> dict[str, datetime]:
        """When `sink` last delivered an item of each source."""
        with self.session_scope() as sess:
            rows = (
                sess.query(DBSourceItem.source_id, DBDelivery.updated_at)
                .join(DBSourceItem, DBDelivery.source_item_id == DBSourceItem.id)
                .filter(
                    DBDelivery.sink == sink,
                    DBDelivery.status == DeliveryStatus.DONE,
                )
                .all()
            )
        # The latest per source in Python: func.max() would bypass UTCDateTime.
        last: dict[str, datetime] = {}
        for source_id, delivered_at in rows:
            if source_id not in last or delivered_at > last[source_id]:
                last[source_id] = delivered_at
        return last

    def find_deliveries(
        self,
        scope: ProcessingScope | None = None,
        *,
        sink: str | None = None,
        status: DeliveryStatus | None = None,
        artifact_names: Iterable[tuple[str, str]] | None = None,
        sort: str = "id",
    ) -> list[Delivery]:
        """Ledger rows by a `DELIVERY_SORTS` key (`id` is creation order).
        Item filters in `scope` keep item rows only and `artifact_names`
        artifact rows only; filters combine and `limit` counts rows."""
        scope = scope or ProcessingScope()
        with self.session_scope() as sess:
            query = (
                sess.query(DBDelivery)
                .outerjoin(DBSourceItem, DBDelivery.source_item_id == DBSourceItem.id)
                .outerjoin(DBArtifact, DBDelivery.artifact_id == DBArtifact.id)
            )
            query = self._apply_scope(query, scope)
            if sink is not None:
                query = query.filter(DBDelivery.sink == sink)
            if status is not None:
                query = query.filter(DBDelivery.status == status)
            if artifact_names is not None:
                query = query.filter(
                    tuple_(DBArtifact.remixer, DBArtifact.name).in_(
                        list(artifact_names)
                    )
                )
            query = query.order_by(*DELIVERY_SORTS[sort], DBDelivery.id)
            if scope.limit:
                query = query.limit(scope.limit)
            return [row.to_dto() for row in query]
