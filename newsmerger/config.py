from __future__ import annotations

from pathlib import Path

import platformdirs
import pydantic
import yaml

from .consts import PACKAGE_NAME
from .models import SourceData


class CacheConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    base_dir: Path = pydantic.Field(
        default_factory=lambda: platformdirs.user_cache_path(PACKAGE_NAME)
    )
    expiration: float = 60 * 60


class DatabaseConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    uri: str = pydantic.Field(
        default_factory=lambda: (
            "sqlite:///" + platformdirs.user_data_dir(PACKAGE_NAME) + "/data.db"
        )
    )


class ProcessorConfigParams(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")


class ProcessorConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    name: str
    # Forwarded as kwargs to the Processor's __init__. `max_retries` and
    # `version` are recognized by BaseProcessor itself (override the
    # class-level MAX_RETRIES/VERSION); anything else is processor-specific
    # (e.g. a model name, a feed title).
    params: ProcessorConfigParams


class Config(pydantic.BaseModel):
    sources: list[SourceData] = []
    processors: list[ProcessorConfig] = []
    cache: CacheConfig = CacheConfig()
    db: DatabaseConfig = DatabaseConfig()

    @classmethod
    def from_file(cls, filepath: str | Path) -> Config:
        if isinstance(filepath, str):
            filepath = Path(filepath)

        return cls.from_text(filepath.read_text())

    @classmethod
    def from_text(cls, text: str) -> Config:
        data = yaml.load(text, yaml.Loader)
        return cls(**data)
