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


class MissingVariableError(ConfigError):
    """A `${VAR}` reference names a variable that is not set."""

    def __init__(self, variable: str, location: str) -> None:
        super().__init__(f"{location}: environment variable '{variable}' is not set")
        self.variable = variable
        self.location = location


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
    # Used when neither --log-level, -v/-q nor NEWSMERGER_LOG_LEVEL set one.
    log_level: str = "warning"
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
        try:
            return cls.from_text(path.read_text(), environ={**dotenv, **os.environ})
        except MissingVariableError as e:
            raise ConfigError(
                f"{path}: {e}\n"
                f"Set {e.variable} in the environment or in {path.parent / '.env'}."
            ) from e

    @classmethod
    def from_text(
        cls, text: str, *, environ: Mapping[str, str] | None = None
    ) -> Config:
        """Parse YAML, then expand `${VAR}` references in its string values
        from `environ` (the process environment by default). Comments and
        keys are never expanded.

        A literal `$` in a value must be written as `$$`.
        """
        parsed = yaml.safe_load(text) or {}
        expanded = expand_variables(
            parsed, os.environ if environ is None else environ, ()
        )
        try:
            return cls(**expanded)
        except pydantic.ValidationError as e:
            raise ConfigError(str(e)) from e


def expand_variables(
    value: Any, environ: Mapping[str, str], location: tuple[str | int, ...]
) -> Any:
    """`value` with `${VAR}` references expanded in every string it holds.
    `location` is its path in the config, for error messages."""
    if isinstance(value, dict):
        return {
            key: expand_variables(item, environ, (*location, key))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [
            expand_variables(item, environ, (*location, index))
            for index, item in enumerate(value)
        ]
    if not isinstance(value, str):
        return value
    try:
        return string.Template(value).substitute(environ)
    except KeyError as e:
        raise MissingVariableError(e.args[0], ".".join(map(str, location))) from e
    except ValueError as e:
        raise ConfigError(
            f"{'.'.join(map(str, location))}: invalid ${{VAR}} reference: {e}"
        ) from e


def plugin_options_error(plugin: str, error: pydantic.ValidationError) -> ConfigError:
    """A plugin's rejected options, one line per error with its config path."""
    lines = [
        f"{'.'.join(map(str, ('plugins', plugin, *detail['loc'])))}: {detail['msg']}"
        for detail in error.errors()
    ]
    return ConfigError("invalid plugin options:\n" + "\n".join(lines))
