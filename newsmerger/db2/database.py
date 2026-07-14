# ---------------------------------------------------------------------------
# Database — bulk upsert now takes an explicit Mapper instead of relying on
# the DB model itself to know how to build from a DTO.
# ---------------------------------------------------------------------------
from __future__ import annotations

import contextlib
import logging
from pathlib import Path
from typing import Any, Iterable, Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import (
    Session,
    sessionmaker,
)

from .ormmodels import Base, DBSource, DBSourceItem
from .mappers import (
    Mapper,
    SourceItemMapper,
    SourceMapper,
    SourceItem,
    SourceData,
    DBModel,
    DTO,
)
from ..models import SupportsUid

LOGGER = logging.getLogger(__name__)


class Database:
    """Database connection and session management"""

    def __init__(
        self,
        database_url: str,
        create_schema: bool = True,
        engine: Engine | None = None,
    ):
        """
        Initialize database connection.

        Args:
            database_url: SQLAlchemy database URL (e.g., 'sqlite:///newsmerger.db').
                Ignored for engine construction if `engine` is supplied, but still
                used for the sqlite-directory-creation check below.
            create_schema: if True, create all tables defined on Base.metadata
                that don't already exist (no-op for existing tables; does not
                handle migrations of existing schemas — use Alembic for that).
            engine: an existing SQLAlchemy Engine to use instead of creating one
                from `database_url`. Useful for tests.
        """
        self._ensure_sqlite_directory(database_url)

        if engine is not None:
            self.engine = engine
        else:
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

    def close(self) -> None:
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

    def save_source_items(self, items: list[SourceItem]) -> None:
        sources = {item.source for item in items}

        items_by_source: dict[SourceData, list[SourceItem]] = {
            source: [] for source in sources
        }
        for item in items:
            items_by_source[item.source].append(item)

        with self.session_scope() as sess:
            db_sources_map = dict(
                self._get_or_create_bulk(sess, DBSource, SourceMapper, sources)
            )

            for source, source_items in items_by_source.items():
                db_source = db_sources_map[source]
                _ = dict(
                    self._get_or_create_bulk(
                        sess,
                        DBSourceItem,
                        SourceItemMapper,
                        source_items,
                        source_id=db_source.id,
                    )
                )

    def _get_or_create_bulk(
        self,
        session: Session,
        db_model: type[DBModel],
        mapper: type[Mapper[DTO, DBModel]],
        objects: Iterable[SupportsUid],
        **kwargs: Any,
    ) -> list[tuple[SupportsUid, DBModel]]:
        """Get or create DB objects for the given uid-bearing DTOs with a single lookup query."""
        objects = list(objects)
        if not objects:
            return []

        objects_by_uid = {obj.uid: obj for obj in objects}
        objects_uids = list(dict.fromkeys(obj.uid for obj in objects))

        existing_objects = (
            session.query(db_model).filter(db_model.uid.in_(objects_uids)).all()
        )
        db_objects_by_uid = {db_obj.uid: db_obj for db_obj in existing_objects}

        missing_objects = [
            objects_by_uid[uid] for uid in objects_uids if uid not in db_objects_by_uid
        ]
        for obj in missing_objects:
            db_obj = mapper.from_dto(obj, **kwargs)
            session.add(db_obj)
            db_objects_by_uid[obj.uid] = db_obj

        if missing_objects:
            LOGGER.info(
                f"Created {len(missing_objects)} new {db_model.__name__} entries"
            )
            session.flush()  # Ensure IDs are generated for newly created rows.

        return [(obj, db_objects_by_uid[obj.uid]) for obj in objects]
