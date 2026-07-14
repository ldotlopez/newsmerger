from __future__ import annotations
from abc import abstractmethod

import contextlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker
from .jsonlib import load_json_compatible, dump_json_compatible

from .models import SourceData, SourceItem, SupportsUid
from sqlalchemy.types import TypeDecorator
from typing import Any

from sqlalchemy.orm import Mapped, mapped_column

from typing import TypeVar, Generic, Self

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


class DBSource(DtoTransferMixin[SourceData], Base):
    """Internal DB model for Source"""

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String)
    provider: Mapped[str] = mapped_column(String)

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
    uid: Mapped[str] = mapped_column(String(255), unique=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
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

    @classmethod
    def from_dto(cls, dto: SourceItem, **kwargs) -> DBSourceItem:
        """Convert from models.SourceEntryData to DBSourceItem"""
        return cls(
            uid=dto.uid,
            title=dto.title,
            uri=dto.uri,
            content=dto.content,
            data=dto.data if isinstance(dto.data, dict) else {},
            **kwargs,
        )

    def update(self, dto: SourceItem) -> None:
        """Update DBSourceItem from models.SourceEntryData"""
        self.title = dto.title
        self.uri = dto.uri
        self.content = dto.content
        self.data = dto.data if isinstance(dto.data, dict) else {}

    def to_dto(self) -> SourceItem:
        """Convert from DBSourceItem to models.SourceEntryData"""
        return SourceItem(
            source=self.source.to_dto(),
            uid=self.uid,
            title=self.title,
            uri=self.uri,
            content=self.content,
            data=self.data,
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
