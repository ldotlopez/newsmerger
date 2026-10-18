from __future__ import annotations

import contextlib
import dataclasses
import enum
import logging
import sqlite3
from abc import abstractmethod
from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Self, TypeVar

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
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    Mapped,
    Session,
    aliased,
    mapped_column,
    relationship,
    sessionmaker,
)
from sqlalchemy.types import TypeDecorator

from .models import Artifact, SourceData, SourceItem, SupportsUid

LOGGER = logging.getLogger(__name__)

Base = declarative_base()


DTO = TypeVar("DTO")

# The connection settings foundation.dblib.SQLite3DB applies.
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


class DtoTransferMixin[DTO]:
    """Mixin for DB models to provide conversion to/from DTOs"""

    @classmethod
    @abstractmethod
    def from_dto(cls, dto: DTO, **kwargs) -> Self:
        """Convert from DTO to DB model"""

    @abstractmethod
    def to_dto(self) -> DTO:
        """Convert from DB model to DTO"""

    @abstractmethod
    def update(self, dto: DTO) -> None:
        """Update DB model from DTO"""


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
        return value.astimezone(UTC)

    def process_result_value(self, value: Any, dialect: Any) -> datetime | None:
        if value is None:
            return None
        return value if value.tzinfo else value.replace(tzinfo=UTC)


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
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(Text)
    # Uid is provider-derived (often sha256(uri), but not guaranteed), so
    # uri gets its own real uniqueness/index rather than relying on uid.
    uri: Mapped[str] = mapped_column(Text, unique=True, index=True)
    mimetype: Mapped[str] = mapped_column(String(255))
    # Key of the item's content in Database.contents.
    content_sha256: Mapped[str] = mapped_column(String(64), index=True)
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
        CheckConstraint(
            "length(content_sha256) = 64", name="ck_source_items_content_sha256"
        ),
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
            "mimetype": dto.mimetype,
            "content_sha256": dto.content_sha256,
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
        self.mimetype = dto.mimetype
        self.content_sha256 = dto.content_sha256
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
            mimetype=self.mimetype,
            content_sha256=self.content_sha256,
            data=self.data,
            published_at=self.published_at,
            modified_at=self.modified_at,
        )

    def __repr__(self):
        return f"<DBSourceItem(id={self.id}, title={self.title})>"


class ProcessingStatus(str, enum.Enum):
    DONE = "done"
    ERROR = "error"
    IGNORED = "ignored"


@dataclasses.dataclass(frozen=True)
class ProcessingScope:
    """Which items a processor run should apply to. All fields optional /
    combinable; an unset field means "no restriction on this axis"."""

    source: str | None = None  # source name or uid
    since: datetime | None = None  # published_at >=
    until: datetime | None = None  # published_at <
    uids: tuple[str, ...] | None = None
    limit: int | None = None


def _backoff_seconds(
    attempts: int,
    base: float = 60.0,
    factor: float = 2.0,
    max_seconds: float = 24 * 3600,
) -> float:
    """Simple exponential backoff for error retries: base * factor**(attempts-1),
    capped at max_seconds. Just a counter + a timestamp comparison — no
    scheduler, no background machinery."""
    return min(base * (factor ** max(attempts - 1, 0)), max_seconds)


class DBProcessingState(Base):
    """Per-(item, processor) run state.

    Absence of a row means "pending" — never attempted. `error` rows track
    `attempts` for retry/backoff accounting (see `_backoff_seconds`); once
    attempts >= max_retries the item is no longer picked up automatically.
    `ignored` means the processor itself decided the item doesn't apply
    (e.g. wrong language) — a deliberate, permanent skip, distinct from a
    failure, and only reprocessed with `force=True`.
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
    # Bumping a processor's VERSION constant makes previously `done` items
    # eligible again without needing --force (see Database._is_eligible).
    processor_version: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Item content this state was computed from; a different one on the item
    # makes it eligible again (see Database._is_eligible).
    content_sha256: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime)

    source_item: Mapped[DBSourceItem] = relationship()

    __table_args__ = (
        UniqueConstraint("source_item_id", "processor"),
        Index("ix_processing_state_processor_status", "processor", "status"),
    )

    def __repr__(self):
        return f"<DBProcessingState(item={self.source_item_id}, processor={self.processor}, status={self.status})>"


class DBItemAnnotation(Base):
    """One piece of derived data a processor attached to a SourceItem.

    (source_item_id, processor, key) is unique — a processor can write
    several keys per item (e.g. a tagger writing "tags" and "language"),
    but re-running it on the same item updates in place rather than
    duplicating rows. Deliberately separate from DBProcessingState: state
    tracks "did this run succeed", annotations track "what did it produce"
    — a partial failure can leave some keys saved while the item is still
    marked as needing a retry.
    """

    __tablename__ = "item_annotations"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_item_id: Mapped[int] = mapped_column(
        ForeignKey("source_items.id", ondelete="CASCADE")
    )
    processor: Mapped[str] = mapped_column(String(255))
    key: Mapped[str] = mapped_column(String(255))
    value: Mapped[Any] = mapped_column(CustomJSON)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime)

    source_item: Mapped[DBSourceItem] = relationship()

    __table_args__ = (
        UniqueConstraint("source_item_id", "processor", "key"),
        Index("ix_item_annotations_processor", "processor"),
    )

    def __repr__(self):
        return f"<DBItemAnnotation(item={self.source_item_id}, processor={self.processor}, key={self.key})>"


class DBArtifact(DtoTransferMixin[Artifact], Base):
    """A generated output not tied to a single item (e.g. an RSS feed).

    (processor, name) is unique — `name` disambiguates when one processor
    produces several artifacts (e.g. one feed per source).
    """

    __tablename__ = "artifacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    processor: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime)

    __table_args__ = (UniqueConstraint("processor", "name"),)

    @classmethod
    def from_dto(cls, dto: Artifact, **kwargs) -> DBArtifact:
        """Convert from models.Artifact; kwargs override the timestamps."""
        fields = {
            "processor": dto.processor,
            "name": dto.name,
            "content": dto.content,
            "content_type": dto.content_type,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        }
        fields.update(kwargs)
        return cls(**fields)

    def update(self, dto: Artifact) -> None:
        """Update every field but the timestamps, which Database manages."""
        self.processor = dto.processor
        self.name = dto.name
        self.content = dto.content
        self.content_type = dto.content_type

    def to_dto(self) -> Artifact:
        return Artifact(
            processor=self.processor,
            name=self.name,
            content=self.content,
            content_type=self.content_type,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def __repr__(self):
        return f"<DBArtifact(processor={self.processor}, name={self.name})>"


class Database:
    """Database connection and session management"""

    def __init__(
        self, database_url: str, content_dir: Path, create_schema: bool = True
    ):
        """
        Initialize database connection.

        Args:
            database_url: SQLAlchemy database URL (e.g., 'sqlite:///newsmerger.db')
            content_dir: directory holding item contents, keyed by their sha256
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
        if self.engine.dialect.name == "sqlite":
            event.listen(self.engine, "connect", _configure_sqlite_connection)

        if create_schema:
            try:
                Base.metadata.create_all(self.engine)
            except Exception:
                LOGGER.exception("Failed to create database schema")
                raise

        self.Session = sessionmaker(bind=self.engine)
        self.contents = DiskStorage(content_dir)
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
        self.contents.close()

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
        - Existing row: title/uri/mimetype/content_sha256/data are diffed against what's
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

        replaced: set[str] = set()
        with self.session_scope() as sess:
            db_sources_map = dict(self._get_or_create_source_bulk(sess, sources))

            for source, source_items in items_by_source.items():
                db_source = db_sources_map[source]
                replaced |= self._upsert_source_items_bulk(
                    sess, source_items, source_id=db_source.id
                )

        # Only once the rows are committed is it safe to drop old contents.
        self._release_contents(replaced)

    def get_content(self, item: SourceItem) -> bytes:
        """Return the item's stored content.

        Raise foundation.storage.EntryNotFoundError if the storage lost it.
        """
        if item.content_sha256 is None:
            raise ValueError(f"item {item.uid} has no content reference")
        return self.contents.get(item.content_sha256)

    def _store_content(self, item: SourceItem) -> None:
        """Write the item's content before the row that references it."""
        if item.content is None or item.content_sha256 is None:
            raise ValueError(f"item {item.uid} has no content to store")
        self.contents.set(item.content_sha256, item.content)

    def _release_contents(self, sha256s: set[str]) -> None:
        """Delete the contents no item references any more.

        shortcut: an upsert in another process that starts referencing one of
        these between the check and the delete loses its content; add a lock
        if imports ever run concurrently.
        """
        if not sha256s:
            return
        with self.session_scope() as sess:
            referenced = {
                sha256
                for (sha256,) in sess.query(DBSourceItem.content_sha256).filter(
                    DBSourceItem.content_sha256.in_(sha256s)
                )
            }
        for sha256 in sha256s - referenced:
            self.contents.delete(sha256)

    def _upsert_source_items_bulk(
        self, session: Session, items: list[SourceItem], *, source_id: int
    ) -> set[str]:
        """Get-or-create-or-update DBSourceItems for one source's items.

        Returns the sha256 of the contents the updated items stopped using.
        """
        replaced: set[str] = set()
        if not items:
            return replaced

        items_by_uid = {item.uid: item for item in items}
        item_uids = list(dict.fromkeys(item.uid for item in items))

        existing_items = (
            session.query(DBSourceItem).filter(DBSourceItem.uid.in_(item_uids)).all()
        )
        existing_by_uid = {db_item.uid: db_item for db_item in existing_items}

        now = datetime.now(UTC)
        created, updated, unchanged = 0, 0, 0

        for uid, item in items_by_uid.items():
            db_item = existing_by_uid.get(uid)

            if db_item is None:
                self._store_content(item)
                db_item = DBSourceItem.from_dto(
                    item,
                    source_id=source_id,
                    published_at=item.published_at or now,
                    modified_at=item.modified_at or now,
                )
                session.add(db_item)
                created += 1
                continue

            previous_sha256 = db_item.content_sha256
            if previous_sha256 != item.content_sha256:
                self._store_content(item)
                replaced.add(previous_sha256)

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

        return replaced

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

        ORDERING IS LOAD-BEARING. title/uri/mimetype/content_sha256/data must be assigned
        BEFORE `session.is_modified()` is called, and modified_at/published_at
        must be assigned AFTER. If modified_at/published_at were set before
        the check, they'd count as "changes" themselves and `is_modified()`
        would return True unconditionally — defeating the whole point of the
        check. Do not reorder these without re-verifying that invariant.
        """
        db_item.title = dto.title
        db_item.uri = dto.uri
        db_item.mimetype = dto.mimetype
        db_item.content_sha256 = dto.content_sha256
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

    # --- Post-processing: state, annotations, artifacts ---------------------

    def get_unprocessed_items(
        self,
        processor: str,
        *,
        version: str | None = None,
        max_retries: int = 3,
        force: bool = False,
        scope: ProcessingScope | None = None,
        requires: str | None = None,
    ) -> list[SourceItem]:
        """Items a processor should run on, given its current state and scope.

        With `requires`, only items that processor finished on their current
        content are candidates: anything it ignored, failed or has not reached
        yet is left alone rather than attempted and failed here. This holds
        even with `force=True`.

        Eligibility (pending / error-with-backoff-elapsed / done-with-stale-
        version) is evaluated in Python rather than SQL — the candidate set
        is already narrowed by `scope` in the query, and backoff math is
        simple enough that hand-rolling dialect-portable SQL for it isn't
        worth it. `force=True` skips eligibility entirely, including
        `ignored` items. A state computed from older content is always
        eligible again.
        """
        scope = scope or ProcessingScope()
        now = datetime.now(UTC)

        with self.session_scope() as sess:
            query = (
                sess.query(DBSourceItem, DBProcessingState)
                .join(DBSource)
                .outerjoin(
                    DBProcessingState,
                    (DBProcessingState.source_item_id == DBSourceItem.id)
                    & (DBProcessingState.processor == processor),
                )
            )
            if requires is not None:
                upstream = aliased(DBProcessingState)
                query = query.join(
                    upstream,
                    (upstream.source_item_id == DBSourceItem.id)
                    & (upstream.processor == requires)
                    & (upstream.status == ProcessingStatus.DONE.value)
                    & (upstream.content_sha256 == DBSourceItem.content_sha256),
                )
            query = self._apply_scope(query, scope)
            query = query.order_by(DBSourceItem.published_at)

            result = []
            for db_item, state in query.all():
                if not force and not self._is_eligible(
                    state, db_item.content_sha256, version, max_retries, now
                ):
                    continue
                result.append(db_item.to_dto())
                if scope.limit and len(result) >= scope.limit:
                    break

            return result

    def _apply_scope(self, query, scope: ProcessingScope):
        if scope.source:
            query = query.filter(
                (DBSource.uid == scope.source) | (DBSource.name == scope.source)
            )
        if scope.since:
            query = query.filter(DBSourceItem.published_at >= scope.since)
        if scope.until:
            query = query.filter(DBSourceItem.published_at < scope.until)
        if scope.uids:
            query = query.filter(DBSourceItem.uid.in_(scope.uids))
        return query

    def _is_eligible(
        self,
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
            return False  # permanent skip; only --force reprocesses it
        if state.status == ProcessingStatus.DONE:
            return state.processor_version != version  # version bump reprocesses
        if state.status == ProcessingStatus.ERROR:
            if state.attempts >= max_retries:
                return False
            elapsed = (now - state.updated_at).total_seconds()
            return elapsed >= _backoff_seconds(state.attempts)
        return True

    def get_source_items(
        self, scope: ProcessingScope | None = None
    ) -> list[SourceItem]:
        """Scoped item lookup for ArtifactProcessors, which don't consult
        per-item processing state (an artifact isn't "done" or "error" per
        item — it's regenerated wholesale on each run)."""
        scope = scope or ProcessingScope()

        with self.session_scope() as sess:
            query = sess.query(DBSourceItem).join(DBSource)
            query = self._apply_scope(query, scope)
            query = query.order_by(DBSourceItem.published_at)
            if scope.limit:
                query = query.limit(scope.limit)
            return [db_item.to_dto() for db_item in query.all()]

    def record_result(
        self,
        item: SourceItem,
        processor: str,
        status: ProcessingStatus,
        *,
        annotations: dict[str, Any] | None = None,
        error: str | None = None,
        version: str | None = None,
    ) -> None:
        """Save a processor run's annotations and state in one transaction.

        The state records `item.content_sha256`: the content the run used.
        """
        with self.session_scope() as sess:
            db_item = sess.query(DBSourceItem).filter_by(uid=item.uid).one()
            now = datetime.now(UTC)
            if annotations:
                self._save_annotations(sess, db_item.id, processor, annotations, now)
            self._save_state(
                sess, db_item.id, item, processor, status, error, version, now
            )

    def _save_state(
        self,
        session: Session,
        source_item_id: int,
        item: SourceItem,
        processor: str,
        status: ProcessingStatus,
        error: str | None,
        version: str | None,
        now: datetime,
    ) -> None:
        state = (
            session.query(DBProcessingState)
            .filter_by(source_item_id=source_item_id, processor=processor)
            .one_or_none()
        )
        if state is None:
            state = DBProcessingState(
                source_item_id=source_item_id,
                processor=processor,
                attempts=0,
                created_at=now,
            )
            session.add(state)
        elif state.content_sha256 != item.content_sha256:
            state.attempts = 0  # new content gets a full set of retries

        state.status = status
        state.content_sha256 = item.content_sha256
        state.processor_version = version
        state.updated_at = now
        if status == ProcessingStatus.ERROR:
            state.attempts += 1
            state.last_error = error
        else:
            state.attempts = 0
            state.last_error = None

    def _save_annotations(
        self,
        session: Session,
        source_item_id: int,
        processor: str,
        values: dict[str, Any],
        now: datetime,
    ) -> None:
        existing = (
            session.query(DBItemAnnotation)
            .filter_by(source_item_id=source_item_id, processor=processor)
            .filter(DBItemAnnotation.key.in_(values.keys()))
            .all()
        )
        existing_by_key = {row.key: row for row in existing}

        for key, value in values.items():
            row = existing_by_key.get(key)
            if row is not None:
                row.value = value
                row.updated_at = now
            else:
                session.add(
                    DBItemAnnotation(
                        source_item_id=source_item_id,
                        processor=processor,
                        key=key,
                        value=value,
                        created_at=now,
                        updated_at=now,
                    )
                )

    def get_annotations(
        self,
        item: SourceItem,
        *,
        processor: str | None = None,
        key: str | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Annotations saved for a single item, keyed as `{processor: {key: value}}`.

        `processor`/`key` narrow the query but never change the return
        shape. Missing item, no annotations, or a filter matching nothing
        all collapse to `{}` — there's no separate "item not found" signal,
        since callers only ever care whether the annotation they asked for
        is there.
        """
        with self.session_scope() as sess:
            query = (
                sess.query(DBItemAnnotation)
                .join(DBSourceItem, DBItemAnnotation.source_item_id == DBSourceItem.id)
                .filter(DBSourceItem.uid == item.uid)
            )
            if processor is not None:
                query = query.filter(DBItemAnnotation.processor == processor)
            if key is not None:
                query = query.filter(DBItemAnnotation.key == key)

            result: dict[str, dict[str, Any]] = {}
            for row in query.all():
                result.setdefault(row.processor, {})[row.key] = row.value
            return result

    def get_annotation_values(
        self, items: list[SourceItem], *, processor: str, key: str
    ) -> dict[str, Any]:
        """One annotation's value per item uid, in a single query.

        Items without that annotation are absent from the result.
        """
        uids = [item.uid for item in items]
        with self.session_scope() as sess:
            rows = (
                sess.query(DBSourceItem.uid, DBItemAnnotation.value)
                .join(
                    DBItemAnnotation, DBItemAnnotation.source_item_id == DBSourceItem.id
                )
                .filter(
                    DBSourceItem.uid.in_(uids),
                    DBItemAnnotation.processor == processor,
                    DBItemAnnotation.key == key,
                )
            )
            return dict(rows.all())

    def save_artifact(self, artifact: Artifact) -> None:
        """Create or replace the artifact named (processor, name)."""
        with self.session_scope() as sess:
            now = datetime.now(UTC)
            existing = (
                sess.query(DBArtifact)
                .filter_by(processor=artifact.processor, name=artifact.name)
                .one_or_none()
            )
            if existing is not None:
                existing.update(artifact)
                existing.updated_at = now
            else:
                sess.add(DBArtifact.from_dto(artifact, created_at=now, updated_at=now))

    def get_artifact(self, processor: str, name: str) -> Artifact | None:
        with self.session_scope() as sess:
            db_artifact = (
                sess.query(DBArtifact)
                .filter_by(processor=processor, name=name)
                .one_or_none()
            )
            return db_artifact.to_dto() if db_artifact is not None else None

    def _get_or_create_source(self, session, source: SourceData) -> DBSource:
        return self._get_or_create_source_bulk(session, [source])[0][1]

    def _get_or_create_source_bulk(
        self, session, sources: Iterable[SourceData]
    ) -> list[tuple[SourceData, DBSource]]:
        return self._get_or_create_bulk(session, DBSource, sources)

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
