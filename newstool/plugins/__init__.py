"""Plugin bundles. Every module is a bundle: it exposes
`__newstool_plugin__()`, which returns the classes it provides as
`(type name, type Protocol, class)` triples. The core builds one object of
a class per configured use, with that use's options (decision 0010).
"""

import dataclasses
from collections.abc import Callable, Mapping
from typing import Any

import pydantic
from foundation.plugin import BaseRegister, PluginError, ProtocolConformanceError

from ..llms import LLM, LLMUnavailableError

# What an entry point returns: (type name, type Protocol, class) per class.
type PluginTypes = list[tuple[str, type, type]]


class PluginOptions(pydantic.BaseModel):
    """Base for a plugin's options: unknown keys are errors."""

    model_config = pydantic.ConfigDict(extra="forbid")


class NoOptions(PluginOptions):
    """The options of an object that takes none."""


class UsesLLMOptions(PluginOptions):
    """Options of an object that uses an LLM: `llm` names an `llms` entry by
    id, or an LLM type; None is the first `llms` entry."""

    llm: str | None = None


def merge_options(
    defaults: Mapping[str, Any], overrides: Mapping[str, Any]
) -> dict[str, Any]:
    """`overrides` over `defaults`, merged key by key in nested mappings; any
    other value, lists included, replaces the default whole."""
    merged = dict(defaults)
    for name, value in overrides.items():
        default = merged.get(name)
        if isinstance(default, Mapping) and isinstance(value, Mapping):
            merged[name] = merge_options(default, value)
        else:
            merged[name] = value
    return merged


@dataclasses.dataclass(slots=True)
class Services:
    """What the core shares with plugin objects. `llm_factory` returns the
    LLM a name refers to (see `UsesLLMOptions`), built on first use."""

    llm_factory: Callable[[str | None], LLM] | None = None

    def llm(self, name: str | None = None) -> LLM:
        """The LLM `name` refers to. Raise `LLMUnavailableError` if there is
        none."""
        if self.llm_factory is None:
            raise LLMUnavailableError("no llm is configured (`llms`)")
        return self.llm_factory(name)


class ClassRegister(BaseRegister):
    """A register of plugin classes: every entry point returns
    `PluginTypes`, and classes are looked up by their type Protocol."""

    def register_found(self) -> None:
        """Register every module of the namespace. A module that fails to
        load fails the whole register."""
        for name in self.discover():
            self.register(name)

    def classes(self, protocol: type) -> dict[str, type]:
        """The classes registered under `protocol`, by type name, in module
        order. Names are unique per protocol, and every class must conform
        to it."""
        classes: dict[str, type] = {}
        owners: dict[str, str] = {}
        for module in self._registry:
            for name, declared, cls in self.get(module):
                if declared is not protocol:
                    continue
                if not isinstance(cls, type):
                    raise PluginError(
                        f"plugin '{module}' registered {protocol.__name__} '{name}'"
                        " as an instance, not a class"
                    )
                if not isinstance(cls, protocol):
                    raise ProtocolConformanceError(
                        f"plugin '{module}': {cls.__qualname__} does not"
                        f" conform to {protocol.__name__}"
                    )
                if name in owners:
                    raise PluginError(
                        f"{protocol.__name__} '{name}' is registered by both"
                        f" plugin '{owners[name]}' and plugin '{module}'"
                    )
                classes[name] = cls
                owners[name] = module
        return classes
