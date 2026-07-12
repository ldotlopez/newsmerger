from __future__ import annotations

from pathlib import Path

import platformdirs
import pydantic
import yaml

from .consts import PACKAGE_NAME


class SourceConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    name: str
    url: pydantic.HttpUrl
    provider: str


class CacheConfig(pydantic.BaseModel):
    base_dir: Path = pydantic.Field(
        default_factory=lambda: platformdirs.user_cache_path(PACKAGE_NAME)
    )
    expiration: float = 60 * 60


class Config(pydantic.BaseModel):
    sources: list[SourceConfig] = []
    cache: CacheConfig = CacheConfig()

    @classmethod
    def from_file(cls, filepath: str | Path) -> Config:
        if isinstance(filepath, str):
            filepath = Path(filepath)

        return cls.from_text(filepath.read_text())

    @classmethod
    def from_text(cls, text: str) -> Config:
        data = yaml.load(text, yaml.Loader)
        return cls(**data)
