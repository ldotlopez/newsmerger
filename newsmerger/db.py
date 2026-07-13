from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

from .models import SourceEntry, SourceEntryData, Source

Base = declarative_base()


class DBSource(Base):
    """Internal DB model for Source"""

    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    url = Column(String(255), nullable=False, unique=True)
    provider = Column(String(128), nullable=False)

    entries = relationship(
        "DBSourceEntry", back_populates="source", cascade="all, delete-orphan"
    )

    @classmethod
    def from_data(cls, source: Source) -> "DBSource":
        """Convert from models.Source to DBSource"""
        return cls(url=str(source.url), provider=source.provider)

    def to_data(self) -> Source:
        """Convert from DBSource to models.Source"""
        return Source(url=self.url, provider=self.provider)

    def __repr__(self):
        return f"<DBSource(id={self.id}, provider={self.provider})>"


class DBSourceEntry(Base):
    """Internal DB model for SourceEntry"""

    __tablename__ = "source_entries"

    id = Column(String(255), primary_key=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    title = Column(String(255), nullable=False)
    uri = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    data = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    source = relationship("DBSource", back_populates="entries")

    @classmethod
    def from_data(cls, source_id: int, entry: SourceEntryData) -> "DBSourceEntry":
        """Convert from models.SourceEntryData to DBSourceEntry"""
        return cls(
            id=entry.id,
            source_id=source_id,
            title=entry.title,
            uri=entry.uri,
            content=entry.content,
            data=entry.data if isinstance(entry.data, dict) else {},
        )

    def to_data(self) -> SourceEntryData:
        """Convert from DBSourceEntry to models.SourceEntryData"""
        return SourceEntryData(
            id=self.id,
            title=self.title,
            uri=self.uri,
            content=self.content,
            data=self.data,
        )

    def __repr__(self):
        return f"<DBSourceEntry(id={self.id}, title={self.title})>"


class Database:
    """Database connection and session management"""

    def __init__(self, database_url: str):
        """
        Initialize database connection.

        Args:
            database_url: SQLAlchemy database URL (e.g., 'sqlite:///newsmerger.db')
        """
        self.engine = create_engine(database_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables defined in Base"""
        Base.metadata.create_all(self.engine)

    def drop_tables(self):
        """Drop all tables (use with caution)"""
        Base.metadata.drop_all(self.engine)

    def get_session(self):
        """Get a new database session"""
        return self.Session()

    def close(self):
        """Close all connections"""
        self.engine.dispose()

    # Public methods for SourceEntry operations
    def add_source(self, source: Source) -> int:
        """Add a source and return its ID"""
        session = self.get_session()
        try:
            db_source = DBSource.from_data(source)
            session.add(db_source)
            session.commit()
            source_id = db_source.id
            return source_id
        finally:
            session.close()

    def add_source_entry(self, source: Source, entry: SourceEntryData) -> str:
        """Add a source entry"""
        session = self.get_session()
        try:
            db_source = (
                session.query(DBSource).filter(DBSource.url == str(source.url)).first()
            )
            if not db_source:
                db_source = DBSource.from_data(source)
                session.add(db_source)
                session.flush()

            db_entry = DBSourceEntry.from_data(db_source.id, entry)
            session.add(db_entry)
            session.commit()
            return db_entry.id
        finally:
            session.close()

    def get_source_entries(self, source: Source) -> list[SourceEntry]:
        """Retrieve all entries for a given source"""
        session = self.get_session()
        try:
            db_source = (
                session.query(DBSource).filter(DBSource.url == str(source.url)).first()
            )
            if not db_source:
                return []

            entries = (
                session.query(DBSourceEntry)
                .filter(DBSourceEntry.source_id == db_source.id)
                .all()
            )
            return [SourceEntry.from_data(source, entry.to_data()) for entry in entries]
        finally:
            session.close()

    def get_source_entry(self, entry_id: str) -> SourceEntry | None:
        """Retrieve a specific source entry by ID"""
        session = self.get_session()
        try:
            db_entry = (
                session.query(DBSourceEntry)
                .filter(DBSourceEntry.id == entry_id)
                .first()
            )
            if not db_entry:
                return None

            source_data = db_entry.source.to_data()
            return SourceEntry.from_data(source_data, db_entry.to_data())
        finally:
            session.close()

    def update_source_entry(self, entry_id: str, entry: SourceEntryData) -> bool:
        """Update a source entry"""
        session = self.get_session()
        try:
            db_entry = (
                session.query(DBSourceEntry)
                .filter(DBSourceEntry.id == entry_id)
                .first()
            )
            if not db_entry:
                return False

            db_entry.title = entry.title
            db_entry.uri = entry.uri
            db_entry.content = entry.content
            db_entry.data = entry.data if isinstance(entry.data, dict) else {}
            session.commit()
            return True
        finally:
            session.close()

    def delete_source_entry(self, entry_id: str) -> bool:
        """Delete a source entry"""
        session = self.get_session()
        try:
            db_entry = (
                session.query(DBSourceEntry)
                .filter(DBSourceEntry.id == entry_id)
                .first()
            )
            if not db_entry:
                return False

            session.delete(db_entry)
            session.commit()
            return True
        finally:
            session.close()
