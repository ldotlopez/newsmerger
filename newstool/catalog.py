"""The configuration resolved against the registered plugin classes
(decision 0010): every configured use of a class as a `Profile`, its options
validated, and every workflow's runs, all checked at startup. Nothing is
built here: `Application` builds a profile's object when a run needs it.
"""

from __future__ import annotations

import dataclasses
import logging
import re
from collections.abc import Mapping, Sequence
from typing import Annotated, Any

import pydantic

from .config import (
    DEFAULT_WORKFLOW,
    NAME_PATTERN,
    Config,
    ConfigError,
    DeliveryEntry,
    Entry,
    ProcessEntry,
    RemixEntry,
    Workflow,
    options_error,
)
from .llms import LLMType
from .plugins import ClassRegister, UsesLLMOptions, merge_options
from .processors import ProcessorType
from .providers import ProviderType
from .remixers import RemixerType
from .sinks import SinkType

LOGGER = logging.getLogger(__name__)

# Annotation keys: lowercase words, optionally in `/`-separated parts.
KEY_PATTERN = re.compile(r"[a-z0-9_]+(/[a-z0-9_]+)*")


@dataclasses.dataclass(frozen=True, slots=True)
class Kind:
    """A kind of plugin type: the Protocol its classes conform to."""

    label: str
    protocol: type


LLM = Kind("llm", LLMType)
PROVIDER = Kind("provider", ProviderType)
PROCESSOR = Kind("processor", ProcessorType)
REMIXER = Kind("remixer", RemixerType)
SINK = Kind("sink", SinkType)


@dataclasses.dataclass(eq=False, slots=True)
class Profile:
    """A configured use of a plugin class (by type name) with its validated
    options, and where it is configured. Equal only to itself: the runs
    that refer to one profile share its object."""

    name: str
    cls: Any
    options: pydantic.BaseModel
    location: str


@dataclasses.dataclass(frozen=True, slots=True)
class Run:
    """A workflow's run of a profile under a key, and where it is named."""

    workflow: Workflow
    key: str
    profile: Profile
    location: str


@dataclasses.dataclass(frozen=True, slots=True)
class Use:
    """A profile under a key, as a catalog entry names it."""

    profile: Profile
    key: str
    location: str


class Catalog:
    """The profiles and runs of a configuration. Every use is validated, run
    or not; a run's options in its profile, the rest in its key and in what
    it reads."""

    def __init__(self, config: Config, register: ClassRegister) -> None:
        self._classes = {
            kind: register.classes(kind.protocol)
            for kind in (LLM, PROVIDER, PROCESSOR, REMIXER, SINK)
        }
        self._sections = {
            name: section or {} for name, section in config.plugins.items()
        }
        self._check_sections()
        self._profiles: list[Profile] = []
        self._type_profiles: dict[tuple[Kind, str], Profile] = {}

        self._llms = self._llm_catalog(config)
        self._default_llm = next(iter(self._llms.values()), None)
        self.sources = {
            source.id: self._profile(
                PROVIDER, source.provider, source.options, f"sources.{source.id}"
            )
            for source in config.sources
        }
        processors = self._catalog(PROCESSOR, config.processors, "processors")
        remixers = self._catalog(REMIXER, config.remixers, "remixers")
        sinks = self._catalog(SINK, config.sinks, "sinks")
        self._ids = {
            PROCESSOR: ids_of(processors),
            REMIXER: ids_of(remixers),
            SINK: ids_of(sinks),
        }

        # By (workflow, key), by key and by ledger key, in configuration order.
        self.process: dict[tuple[str, str], Run] = {}
        self.remix: dict[str, Run] = {}
        self.deliveries: dict[str, Run] = {}
        for workflow in config.all_workflows():
            if workflow.name == DEFAULT_WORKFLOW:
                process = in_default(processors)
                remix = in_default(remixers)
                deliver: list[Use] = []
            else:
                process = self._resolve_all(
                    PROCESSOR, workflow, "process", workflow.process
                )
                remix = self._resolve_all(REMIXER, workflow, "remix", workflow.remix)
                deliver = self._resolve_all(SINK, workflow, "deliver", workflow.deliver)
            for use in process:
                self._add_process(Run(workflow, use.key, use.profile, use.location))
            for use in remix:
                self._add_remix(Run(workflow, use.key, use.profile, use.location))
            for use in deliver:
                self._add_delivery(Run(workflow, use.key, use.profile, use.location))
        self._check_requirements()
        self._check_llms()

    @property
    def processor_names(self) -> list[str]:
        """Every processor type."""
        return list(self._classes[PROCESSOR])

    def llm_profile(self, name: str | None, location: str = "llms") -> Profile:
        """The LLM `name` refers to: an `llms` id, an LLM type, or the first
        `llms` entry for None."""
        if name is None:
            if self._default_llm is None:
                raise ConfigError(f"{location}: uses an llm, and `llms` is empty")
            return self._default_llm
        if name in self._llms:
            return self._llms[name]
        if name in self._classes[LLM]:
            return self._type_profile(LLM, name, location)
        raise ConfigError(f"{location}: no llm has the id or type '{name}'")

    # --- Profiles ----------------------------------------------------------

    def _check_sections(self) -> None:
        """Every `plugins` section names a type and sets options it takes."""
        for name, section in self._sections.items():
            classes = [
                classes[name] for classes in self._classes.values() if name in classes
            ]
            if not classes:
                raise ConfigError(f"plugins.{name}: no plugin provides '{name}'")
            for cls in classes:
                check_section(f"plugins.{name}", cls.options_model, section)

    def _profile(
        self, kind: Kind, name: str, overrides: Mapping[str, Any], location: str
    ) -> Profile:
        """The use of the type `name` with `overrides` over its section."""
        if (cls := self._classes[kind].get(name)) is None:
            raise ConfigError(
                f"{location}: no plugin provides the {kind.label} '{name}'"
            )
        options = merge_options(self._sections.get(name, {}), overrides)
        try:
            validated = cls.options_model.model_validate(options)
        except pydantic.ValidationError as e:
            raise options_error(f"{location}.options", e) from None
        profile = Profile(name, cls, validated, location)
        self._profiles.append(profile)
        return profile

    def _type_profile(self, kind: Kind, name: str, location: str) -> Profile:
        """The type `name` with its section's options: one profile for every
        reference to it."""
        if (kind, name) not in self._type_profiles:
            self._type_profiles[kind, name] = self._profile(kind, name, {}, location)
        return self._type_profiles[kind, name]

    def _llm_catalog(self, config: Config) -> dict[str, Profile]:
        """The `llms` entries' profiles, by id, or by position for those
        without one."""
        llms: dict[str, Profile] = {}
        for index, entry in enumerate(config.llms):
            location = f"llms.{index}"
            self._check_id(LLM, entry, location)
            profile = self._profile(LLM, entry.llm, entry.options, location)
            llms[entry.id or f"#{index}"] = profile
        return llms

    def _catalog(
        self,
        kind: Kind,
        entries: Sequence[ProcessEntry | RemixEntry | DeliveryEntry],
        section: str,
    ) -> list[tuple[Entry, Use]]:
        """A catalog section's entries with their uses."""
        uses: list[tuple[Entry, Use]] = []
        for index, entry in enumerate(entries):
            location = f"{section}.{index}"
            self._check_id(kind, entry, location)
            profile = self._profile(kind, entry.type_name, entry.options, location)
            uses.append(
                (entry, Use(profile, self._key(kind, entry, profile), location))
            )
        return uses

    def _check_id(self, kind: Kind, entry: Entry, location: str) -> None:
        """An id is not a type name, so a reference means one thing."""
        if entry.id is not None and entry.id in self._classes[kind]:
            raise ConfigError(
                f"{location}: the id '{entry.id}' is a {kind.label} type's name"
            )

    @staticmethod
    def _key(
        kind: Kind,
        entry: ProcessEntry | RemixEntry | DeliveryEntry | None,
        profile: Profile,
    ) -> str:
        """The entry's key, or else the default one: the processor's for its
        options, the remixer's or the sink's name."""
        if entry is not None and entry.key is not None:
            return entry.key
        if kind is PROCESSOR:
            return profile.cls.output_key(profile.options)
        return profile.name

    def _resolve_all(
        self,
        kind: Kind,
        workflow: Workflow,
        section: str,
        refs: Sequence[str | ProcessEntry | RemixEntry | DeliveryEntry],
    ) -> list[Use]:
        """A workflow section's uses."""
        return [
            self._resolve(kind, ref, f"workflows.{workflow.name}.{section}.{index}")
            for index, ref in enumerate(refs)
        ]

    def _resolve(
        self,
        kind: Kind,
        ref: str | ProcessEntry | RemixEntry | DeliveryEntry,
        location: str,
    ) -> Use:
        """A catalog entry by id, a type with its section's options, or an
        entry of the workflow's own."""
        if isinstance(ref, str):
            if (use := self._ids[kind].get(ref)) is not None:
                return dataclasses.replace(use, location=location)
            if ref not in self._classes[kind]:
                raise ConfigError(
                    f"{location}: no {kind.label} has the id or type '{ref}'"
                )
            profile = self._type_profile(kind, ref, location)
            return Use(profile, self._key(kind, None, profile), location)
        profile = self._profile(kind, ref.type_name, ref.options, location)
        return Use(profile, self._key(kind, ref, profile), location)

    # --- Runs --------------------------------------------------------------

    def _add_process(self, run: Run) -> None:
        """A process run. Its key is the annotation's identity: in a workflow
        one run writes it; on shared sources, runs of different processors
        cannot, and runs with different options get a warning (the first to
        process an item writes it)."""
        key, workflow = run.key, run.workflow
        if not KEY_PATTERN.fullmatch(key):
            raise ConfigError(f"{run.location}: invalid key '{key}'")
        if (workflow.name, key) in self.process:
            raise ConfigError(
                f"{run.location}: key '{key}' is written by another entry"
                f" of workflow '{workflow.name}'"
            )
        for other in self.process.values():
            if (
                other.key != key
                or other.profile is run.profile
                or not share_sources(other.workflow, workflow)
            ):
                continue
            if other.profile.name != run.profile.name:
                raise ConfigError(
                    f"{run.location}: key '{key}' is written by"
                    f" {other.profile.name} too ({other.location}) on the same"
                    " sources; give one a `key`"
                )
            if other.profile.options != run.profile.options:
                LOGGER.warning(
                    f"{run.location}: key '{key}' is written with other options"
                    f" too ({other.location}) on the same sources; the first"
                    " run to process an item writes it"
                )
        self.process[workflow.name, key] = run

    def _add_remix(self, run: Run) -> None:
        """A remix run. Its key belongs to one workflow: artifacts are not
        per source, so another run would overwrite them."""
        if not NAME_PATTERN.fullmatch(run.key):
            raise ConfigError(f"{run.location}: invalid remix key '{run.key}'")
        if (other := self.remix.get(run.key)) is not None:
            raise ConfigError(
                f"{run.location}: remix key '{run.key}' is used by"
                f" {other.location} too (workflow '{other.workflow.name}'); a"
                " remix key belongs to one workflow (give one a `key`, or mark"
                " the catalog entry with `skip_default: true`)"
            )
        self.remix[run.key] = run

    def _add_delivery(self, run: Run) -> None:
        """A delivery run, under its workflow's ledger key."""
        if not NAME_PATTERN.fullmatch(run.key):
            raise ConfigError(f"{run.location}: invalid delivery key '{run.key}'")
        ledger_key = run.workflow.ledger_key(run.key)
        if ledger_key in self.deliveries:
            raise ConfigError(
                f"{run.location}: delivery key '{run.key}' is used by another"
                f" entry of workflow '{run.workflow.name}'; give one a `key`"
            )
        self.deliveries[ledger_key] = run

    # --- Checks ------------------------------------------------------------

    def _check_requirements(self) -> None:
        """Every annotation a run reads is written by a process run on its
        workflow's sources, in any workflow."""
        for run in [*self.process.values(), *self.deliveries.values()]:
            required = run.profile.cls.required_key(run.profile.options)
            if required is None:
                continue
            if not any(
                writer.key == required and share_sources(writer.workflow, run.workflow)
                for writer in self.process.values()
            ):
                raise ConfigError(
                    f"{run.location}: {run.profile.name} reads '{required}', and"
                    " no process run writes it on the sources of workflow"
                    f" '{run.workflow.name}'"
                )

    def _check_llms(self) -> None:
        """Every LLM a profile names exists."""
        for profile in list(self._profiles):
            if isinstance(profile.options, UsesLLMOptions):
                self.llm_profile(profile.options.llm, profile.location)


def check_section(
    location: str, model: type[pydantic.BaseModel], section: Mapping[str, Any]
) -> None:
    """Reject options `model` does not declare, or values it does not take.
    Rules across options (model validators) are checked in each use."""
    errors = []
    for option, value in section.items():
        if (field := model.model_fields.get(option)) is None:
            errors.append(f"{location}.{option}: no such option")
            continue
        annotation = (
            Annotated[field.annotation, *field.metadata]
            if field.metadata
            else field.annotation
        )
        try:
            pydantic.TypeAdapter(annotation).validate_python(value)
        except pydantic.ValidationError as e:
            errors.extend(f"{location}.{option}: {d['msg']}" for d in e.errors())
    if errors:
        raise ConfigError("invalid options:\n" + "\n".join(errors))


def ids_of(uses: list[tuple[Entry, Use]]) -> dict[str, Use]:
    """The uses of the catalog entries with an id, by id."""
    return {entry.id: use for entry, use in uses if entry.id is not None}


def in_default(uses: list[tuple[Entry, Use]]) -> list[Use]:
    """The uses of the catalog entries the `default` workflow runs."""
    return [
        use
        for entry, use in uses
        if isinstance(entry, ProcessEntry | RemixEntry) and not entry.skip_default
    ]


def share_sources(a: Workflow, b: Workflow) -> bool:
    """Whether runs of the two workflows can meet on an item."""
    return a.name == b.name or bool(set(a.sources) & set(b.sources))
