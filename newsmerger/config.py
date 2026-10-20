from __future__ import annotations

import os
import string
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import platformdirs
import pydantic
import yaml
from dotenv import dotenv_values

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


class Config(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    sources: list[SourceData] = []
    # Plugin module name -> its options, validated by the plugin itself. Only
    # plugins listed here are loaded; an empty section enables its defaults.
    plugins: dict[str, dict[str, Any] | None] = {}
    cache: CacheConfig = CacheConfig()
    db: DatabaseConfig = DatabaseConfig()

    @pydantic.model_validator(mode="after")
    def source_ids_are_unique(self) -> Config:
        ids = [source.id for source in self.sources]
        if len(ids) != len(set(ids)):
            raise ValueError("source ids must be unique")
        return self

    def get_source(self, source_id: str) -> SourceData:
        for source in self.sources:
            if source.id == source_id:
                return source
        raise ConfigError(f"source '{source_id}' is not configured")

    @classmethod
    def from_file(cls, path: Path) -> Config:
        """Load a config file. `${VAR}` takes values from the environment,
        then from a `.env` file next to the config file, if any."""
        dotenv = {
            name: value
            for name, value in dotenv_values(path.parent / ".env").items()
            if value is not None
        }
        return cls.from_text(path.read_text(), environ={**dotenv, **os.environ})

    @classmethod
    def from_text(
        cls, text: str, *, environ: Mapping[str, str] | None = None
    ) -> Config:
        """Parse YAML after expanding `${VAR}` references from `environ`
        (the process environment by default).

        A literal `$` must be written as `$$`.
        """
        try:
            expanded = string.Template(text).substitute(
                os.environ if environ is None else environ
            )
        except KeyError as e:
            raise ConfigError(f"environment variable {e} is not set") from e
        except ValueError as e:
            raise ConfigError(f"invalid ${{VAR}} reference: {e}") from e

        try:
            return cls(**(yaml.safe_load(expanded) or {}))
        except pydantic.ValidationError as e:
            raise ConfigError(str(e)) from e


def plugin_options_error(plugin: str, error: pydantic.ValidationError) -> ConfigError:
    """A plugin's rejected options, one line per error with its config path."""
    lines = [
        f"{'.'.join(map(str, ('plugins', plugin, *detail['loc'])))}: {detail['msg']}"
        for detail in error.errors()
    ]
    return ConfigError("invalid plugin options:\n" + "\n".join(lines))
