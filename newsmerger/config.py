from __future__ import annotations

import os
import re
import string
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import platformdirs
import pydantic
import yaml
from dotenv import dotenv_values
from foundation.jsonlib import JsonCompatible

from .consts import PACKAGE_NAME
from .models import SourceData

# The workflow built from the catalog (`Config.default_workflow`).
DEFAULT_WORKFLOW = "default"
# Ids, workflow names, and remix and delivery keys, which form ledger keys as
# `<workflow>/<key>`.
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


class Entry(pydantic.BaseModel):
    """A configured use of a plugin type: its `options` over the type's
    `plugins` section. `id` names it in the catalog, so that workflows can
    refer to it; the entries of a workflow have none."""

    model_config = pydantic.ConfigDict(extra="forbid", frozen=True)
    id: str | None = None
    options: dict[str, JsonCompatible] = {}

    @pydantic.field_validator("id")
    @classmethod
    def id_is_valid(cls, value: str | None) -> str | None:
        if value is not None and not NAME_PATTERN.fullmatch(value):
            raise ValueError(f"invalid id '{value}'")
        return value

    @property
    def type_name(self) -> str:
        """The plugin type it uses."""
        raise NotImplementedError


class LLMEntry(Entry):
    """An LLM. Objects that use one name it by `id`, or by type; the first
    entry serves those that name none."""

    llm: str

    @pydantic.model_validator(mode="before")
    @classmethod
    def from_name(cls, value: Any) -> Any:
        """A bare type name is the type with its section's options."""
        return {"llm": value} if isinstance(value, str) else value

    @property
    def type_name(self) -> str:
        return self.llm


class ProcessEntry(Entry):
    """A processor run. `key` names the annotation it writes (default: the
    processor's own for its options)."""

    processor: str
    key: str | None = None
    skip_default: bool = False  # catalog only: left out of `default`

    @pydantic.model_validator(mode="before")
    @classmethod
    def from_name(cls, value: Any) -> Any:
        """A bare type name is the type with its section's options."""
        return {"processor": value} if isinstance(value, str) else value

    @property
    def type_name(self) -> str:
        return self.processor


class RemixEntry(Entry):
    """A remixer run, its artifacts under `key` (default: the remixer's
    name), which belongs to one workflow: artifacts are not per source."""

    remixer: str
    key: str | None = None
    skip_default: bool = False  # catalog only: left out of `default`

    @pydantic.model_validator(mode="before")
    @classmethod
    def from_name(cls, value: Any) -> Any:
        """A bare type name is the type with its section's options."""
        return {"remixer": value} if isinstance(value, str) else value

    @property
    def type_name(self) -> str:
        return self.remixer


class DeliveryEntry(Entry):
    """A sink run, its ledger rows under `key` (default: the sink's name),
    which is unique within its workflow."""

    sink: str
    key: str | None = None

    @pydantic.model_validator(mode="before")
    @classmethod
    def from_name(cls, value: Any) -> Any:
        """A bare type name is the type with its section's options."""
        return {"sink": value} if isinstance(value, str) else value

    @property
    def type_name(self) -> str:
        return self.sink


class Workflow(pydantic.BaseModel):
    """Which sources to use and what to run on them, in phase order. A
    string refers to a catalog entry by `id`, or else to a type with its
    section's options; a mapping is an entry of the workflow's own.
    `default`, built from the catalog, has no entries of its own."""

    model_config = pydantic.ConfigDict(extra="forbid", frozen=True)
    name: str
    sources: list[str]  # source ids
    process: list[str | ProcessEntry] = []
    remix: list[str | RemixEntry] = []
    deliver: list[str | DeliveryEntry] = []

    @pydantic.model_validator(mode="after")
    def entries_are_valid(self) -> Workflow:
        if not NAME_PATTERN.fullmatch(self.name):
            raise ValueError(f"invalid workflow name '{self.name}'")
        own: list[tuple[str, int, Entry]] = [
            *own_entries("process", self.process),
            *own_entries("remix", self.remix),
            *own_entries("deliver", self.deliver),
        ]
        for section, index, entry in own:
            if entry.id is not None:
                raise ValueError(
                    f"workflow '{self.name}': {section}.{index} has an id;"
                    " only catalog entries do"
                )
        for section, index, entry in own:
            if isinstance(entry, ProcessEntry | RemixEntry) and entry.skip_default:
                raise ValueError(
                    f"workflow '{self.name}': {section}.{index} sets"
                    " skip_default; only catalog entries do"
                )
        return self

    def ledger_key(self, key: str) -> str:
        """Where a delivery key's rows live: its workflow asked for them."""
        return f"{self.name}/{key}"


def own_entries(
    section: str, entries: Sequence[str | Entry]
) -> list[tuple[str, int, Entry]]:
    """The `(section, index, entry)` of a workflow section's own entries."""
    return [
        (section, index, entry)
        for index, entry in enumerate(entries)
        if not isinstance(entry, str)
    ]


class Config(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    # Used when neither --log-level, -v/-q nor NEWSMERGER_LOG_LEVEL set one.
    log_level: str = "warning"
    # Plugin type name -> the defaults of its options in every use of the
    # type. Nothing is built from a section.
    plugins: dict[str, dict[str, Any] | None] = {}
    # The catalog: every configured use, built when a workflow runs it.
    llms: list[LLMEntry] = []
    sources: list[SourceData] = []
    processors: list[ProcessEntry] = []
    remixers: list[RemixEntry] = []
    sinks: list[DeliveryEntry] = []
    # Workflows, run by name; a list, since YAML drops duplicate keys.
    workflows: list[Workflow] = []
    cache: CacheConfig = CacheConfig()
    db: DatabaseConfig = DatabaseConfig()

    @pydantic.model_validator(mode="after")
    def catalog_ids_are_unique(self) -> Config:
        source_ids = [source.id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source ids must be unique")
        catalog: dict[str, Sequence[Entry]] = {
            "llms": self.llms,
            "processors": self.processors,
            "remixers": self.remixers,
            "sinks": self.sinks,
        }
        for section, entries in catalog.items():
            ids = [entry.id for entry in entries if entry.id is not None]
            if duplicated := sorted({id for id in ids if ids.count(id) > 1}):
                raise ValueError(f"{section}: id(s) {', '.join(duplicated)} used twice")
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

    def default_workflow(self) -> Workflow:
        """The `default` workflow: the sources without `skip_default`. Its
        runs are the catalog's processors and remixers without it; it
        delivers nothing."""
        return Workflow(
            name=DEFAULT_WORKFLOW,
            sources=[source.id for source in self.sources if not source.skip_default],
        )

    def all_workflows(self) -> list[Workflow]:
        """Every workflow, `default` first."""
        return [self.default_workflow(), *self.workflows]

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
