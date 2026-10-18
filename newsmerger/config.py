from __future__ import annotations

import os
import string
from collections.abc import Callable
from pathlib import Path
from typing import Any

import platformdirs
import pydantic
import yaml

from .consts import PACKAGE_NAME
from .models import SourceData


class ConfigError(ValueError):
    """The configuration file cannot be loaded."""


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
            f"sqlite:///{platformdirs.user_data_path(PACKAGE_NAME) / 'data.db'}"
        )
    )
    content_dir: Path = pydantic.Field(
        default_factory=lambda: platformdirs.user_data_path(PACKAGE_NAME) / "content"
    )


class PluginConfig(pydantic.BaseModel):
    """A configured processor or remixer: its module name and constructor params."""

    model_config = pydantic.ConfigDict(extra="forbid")
    name: str
    params: dict[str, Any] = {}


class Config(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    sources: list[SourceData] = []
    processors: list[PluginConfig] = []
    remixers: list[PluginConfig] = []
    cache: CacheConfig = CacheConfig()
    db: DatabaseConfig = DatabaseConfig()

    @pydantic.model_validator(mode="after")
    def names_are_unique(self) -> Config:
        for section, names in (
            ("source ids", [source.id for source in self.sources]),
            ("processor names", [processor.name for processor in self.processors]),
            ("remixer names", [remixer.name for remixer in self.remixers]),
        ):
            if len(names) != len(set(names)):
                raise ValueError(f"{section} must be unique")
        return self

    def get_source(self, source_id: str) -> SourceData:
        return _find(self.sources, source_id, "source", lambda source: source.id)

    def get_processor(self, name: str) -> PluginConfig:
        return _find(self.processors, name, "processor", lambda plugin: plugin.name)

    def get_remixer(self, name: str) -> PluginConfig:
        return _find(self.remixers, name, "remixer", lambda plugin: plugin.name)

    @classmethod
    def from_file(cls, path: Path) -> Config:
        return cls.from_text(path.read_text())

    @classmethod
    def from_text(cls, text: str) -> Config:
        """Parse YAML after expanding `${VAR}` references from the environment.

        A literal `$` must be written as `$$`.
        """
        try:
            expanded = string.Template(text).substitute(os.environ)
        except KeyError as e:
            raise ConfigError(f"environment variable {e} is not set") from e
        except ValueError as e:
            raise ConfigError(f"invalid ${{VAR}} reference: {e}") from e

        try:
            return cls(**(yaml.safe_load(expanded) or {}))
        except pydantic.ValidationError as e:
            raise ConfigError(str(e)) from e


def _find[T](entries: list[T], key: str, kind: str, get_key: Callable[[T], str]) -> T:
    for entry in entries:
        if get_key(entry) == key:
            return entry
    raise ConfigError(f"{kind} '{key}' is not configured")
