# ---------------------------------------------------------------------------
# Mappers — own the DTO <-> ORM conversion. DB models don't know this exists;
# mappers import both sides. This is the seam that lets either side change
# shape independently, and the seam that matters for testing DTO<->row
# mapping without spinning up a session.
# ---------------------------------------------------------------------------
from __future__ import annotations

import logging
from typing import Any, Protocol, TypeVar


from ..models import SourceData, SourceItem
from .ormmodels import Base, DBSource, DBSourceItem

LOGGER = logging.getLogger(__name__)


DTO = TypeVar("DTO")
DBModel = TypeVar("DBModel", bound=Base)


class Mapper(Protocol[DTO, DBModel]):
    """Structural contract every mapper follows."""

    @staticmethod
    def from_dto(dto: DTO, **kwargs: Any) -> DBModel: ...

    @staticmethod
    def to_dto(db_obj: DBModel) -> DTO: ...

    @staticmethod
    def update(db_obj: DBModel, dto: DTO) -> None: ...


class SourceMapper:
    """Converts between SourceData and DBSource."""

    @staticmethod
    def from_dto(dto: SourceData, **kwargs: Any) -> DBSource:
        return DBSource(
            uid=dto.uid,
            url=str(dto.url),
            provider=dto.provider,
            name=dto.name,
        )

    @staticmethod
    def to_dto(db_obj: DBSource) -> SourceData:
        return SourceData(
            uid=db_obj.uid, name=db_obj.name, url=db_obj.url, provider=db_obj.provider
        )

    @staticmethod
    def update(db_obj: DBSource, dto: SourceData) -> None:
        db_obj.name = dto.name
        db_obj.url = str(dto.url)
        db_obj.provider = dto.provider


class SourceItemMapper:
    """Converts between SourceItem and DBSourceItem.

    Note: to_dto() reads db_obj.source, a lazy-loaded relationship. Calling
    this over a large, non-eager-loaded batch triggers one SELECT per item
    (N+1). Eager-load with joinedload(DBSourceItem.source) first for bulk
    conversions.
    """

    @staticmethod
    def from_dto(dto: SourceItem, **kwargs: Any) -> DBSourceItem:
        return DBSourceItem(
            uid=dto.uid,
            title=dto.title,
            uri=dto.uri,
            content=dto.content,
            data=dto.data if isinstance(dto.data, dict) else {},
            **kwargs,
        )

    @staticmethod
    def to_dto(db_obj: DBSourceItem) -> SourceItem:
        return SourceItem(
            source=SourceMapper.to_dto(db_obj.source),
            uid=db_obj.uid,
            title=db_obj.title,
            uri=db_obj.uri,
            content=db_obj.content,
            data=db_obj.data,
        )

    @staticmethod
    def update(db_obj: DBSourceItem, dto: SourceItem) -> None:
        db_obj.title = dto.title
        db_obj.uri = dto.uri
        db_obj.content = dto.content
        db_obj.data = dto.data if isinstance(dto.data, dict) else {}
