"""Plugin bundles. Each module is loaded only when `plugins:` in the config
has a section with its name, and exposes
`__newsmerger_plugin__(services, **options)`, which validates that section
and returns the objects the bundle provides.
"""

import dataclasses
from collections.abc import Mapping
from typing import Any

import pydantic

from ..llms import LLM, LLMUnavailableError

# What an entry point returns: (object name, Protocol, object) per object.
type PluginObjects = list[tuple[str, type, Any]]


class PluginOptions(pydantic.BaseModel):
    """Base for a plugin's options: unknown keys are errors."""

    model_config = pydantic.ConfigDict(extra="forbid")


class NoOptions(PluginOptions):
    """The per-use options of an object that takes none."""


def merge_options[M: pydantic.BaseModel](
    model: type[M], defaults: pydantic.BaseModel, overrides: Mapping[str, Any]
) -> M:
    """One use's options: `overrides` over the values `defaults` (a plugin
    section) sets for `model`'s fields, validated as `model`. A section holds
    defaults; each use overrides only what its verb declares."""
    inherited = defaults.model_dump(include=set(model.model_fields), exclude_unset=True)
    return model.model_validate({**inherited, **overrides})


@dataclasses.dataclass(slots=True)
class Services:
    """What the core shares with entry points: the LLMs provided by the
    plugins loaded before, by name, in configuration order."""

    llms: dict[str, LLM] = dataclasses.field(default_factory=dict)

    def llm(self, name: str | None = None) -> LLM:
        """The LLM named `name`, or the default one (the first loaded) for
        None. Raise `LLMUnavailableError` if it is not loaded."""
        hint = "llm plugins must be listed before the plugins that use them"
        if not self.llms:
            raise LLMUnavailableError(f"no llm is loaded ({hint})")
        if name is None:
            return next(iter(self.llms.values()))
        try:
            return self.llms[name]
        except KeyError:
            raise LLMUnavailableError(f"llm '{name}' is not loaded ({hint})") from None
