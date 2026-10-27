from __future__ import annotations

import os
import re
import string
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import platformdirs
import pydantic
import yaml
from dotenv import dotenv_values
from foundation.jsonlib import JsonCompatible

from .consts import PACKAGE_NAME
from .models import SourceData

# The workflow whose `sources`, `process`, `remix` and `deliver` are the
# config's root keys.
DEFAULT_WORKFLOW = "default"
# Workflow names and delivery keys, which form ledger keys as `<workflow>/<key>`.
NAME_PATTERN = re.compile(r"[a-z0-9_-]+")


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


class ProcessEntry(pydantic.BaseModel):
    """One run of a processor in the process phase. `key` names the
    annotation it writes (default: the processor's own for `options`), which
    are passed to it as keyword arguments."""

    model_config = pydantic.ConfigDict(extra="forbid", frozen=True)
    processor: str
    key: str | None = None
    options: dict[str, JsonCompatible] = {}

    @pydantic.model_validator(mode="before")
    @classmethod
    def from_name(cls, value: Any) -> Any:
        """A bare processor name runs it with its defaults."""
        return {"processor": value} if isinstance(value, str) else value


class DeliveryEntry(pydantic.BaseModel):
    """One delivery of a workflow: `sink` run with `options` (passed to it),
    its ledger rows under `key` (default: the sink's name), which is unique
    within the workflow."""

    model_config = pydantic.ConfigDict(extra="forbid", frozen=True)
    sink: str
    key: str | None = None
    options: dict[str, JsonCompatible] = {}

    @pydantic.model_validator(mode="before")
    @classmethod
    def from_name(cls, value: Any) -> Any:
        """A bare sink name runs it with its defaults."""
        return {"sink": value} if isinstance(value, str) else value

    @property
    def name(self) -> str:
        return self.key or self.sink


class Workflow(pydantic.BaseModel):
    """Which sources to use and what to run on them, in phase order. The
    config's root keys are the `default` workflow."""

    model_config = pydantic.ConfigDict(extra="forbid", frozen=True)
    name: str
    sources: list[str]  # source ids
    process: list[ProcessEntry] = []
    remix: list[str] = []  # remixer names
    deliver: list[DeliveryEntry] = []

    @pydantic.model_validator(mode="after")
    def names_are_valid(self) -> Workflow:
        if not NAME_PATTERN.fullmatch(self.name):
            raise ValueError(f"invalid workflow name '{self.name}'")
        keys = [entry.name for entry in self.deliver]
        for key in keys:
            if not NAME_PATTERN.fullmatch(key):
                raise ValueError(
                    f"workflow '{self.name}': invalid delivery key '{key}'"
                )
        if duplicated := sorted({key for key in keys if keys.count(key) > 1}):
            raise ValueError(
                f"workflow '{self.name}': delivery key(s) {', '.join(duplicated)}"
                " used twice; give the entries distinct `key`s"
            )
        return self

    def ledger_key(self, key: str) -> str:
        """Where a delivery key's rows live: its workflow asked for them."""
        return key if self.name == DEFAULT_WORKFLOW else f"{self.name}/{key}"


class Config(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    # Used when neither --log-level, -v/-q nor NEWSMERGER_LOG_LEVEL set one.
    log_level: str = "warning"
    sources: list[SourceData] = []
    # Plugin module name -> its options, validated by the plugin itself. An
    # empty section enables its defaults. Providers and processors named by
    # `sources` or `process` but provided by no section load the plugin of
    # the same name with its defaults.
    plugins: dict[str, dict[str, Any] | None] = {}
    # The default workflow's runs, in order; what is not listed never runs.
    process: list[ProcessEntry] = []
    remix: list[str] = []
    deliver: list[DeliveryEntry] = []
    # More workflows, run by name; a list, since YAML drops duplicate keys.
    workflows: list[Workflow] = []
    cache: CacheConfig = CacheConfig()
    db: DatabaseConfig = DatabaseConfig()

    @pydantic.model_validator(mode="after")
    def source_ids_are_unique(self) -> Config:
        ids = [source.id for source in self.sources]
        if len(ids) != len(set(ids)):
            raise ValueError("source ids must be unique")
        return self

    @pydantic.model_validator(mode="after")
    def workflows_are_valid(self) -> Config:
        names = [workflow.name for workflow in self.workflows]
        if DEFAULT_WORKFLOW in names:
            raise ValueError(f"the workflow name '{DEFAULT_WORKFLOW}' is reserved")
        if len(names) != len(set(names)):
            raise ValueError("workflow names must be unique")
        known = {source.id for source in self.sources}
        for workflow in self.workflows:
            if unknown := [s for s in workflow.sources if s not in known]:
                raise ValueError(
                    f"workflow '{workflow.name}': unknown source(s)"
                    f" {', '.join(unknown)}"
                )
        return self

    def all_workflows(self) -> list[Workflow]:
        """Every workflow, `default` (from the root keys) first."""
        default = Workflow(
            name=DEFAULT_WORKFLOW,
            sources=[source.id for source in self.sources if source.default],
            process=self.process,
            remix=self.remix,
            deliver=self.deliver,
        )
        return [default, *self.workflows]

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


def options_error(location: str, error: pydantic.ValidationError) -> ConfigError:
    """Rejected options at `location` in the config, one line per error with
    its config path."""
    lines = [
        f"{'.'.join(map(str, (location, *detail['loc'])))}: {detail['msg']}"
        for detail in error.errors()
    ]
    return ConfigError("invalid options:\n" + "\n".join(lines))
