from __future__ import annotations

import logging
import time
from abc import abstractmethod
from collections.abc import Iterator, Mapping
from typing import Any, Protocol, runtime_checkable

import pydantic

from .db import Database
from .models import Artifact, ProcessingScope
from .plugins import NoOptions, PluginOptions, merge_options

LOGGER = logging.getLogger(__name__)


@runtime_checkable
class Remixer[O: pydantic.BaseModel](Protocol):
    """Produces artifacts from many items. Each `remix:` entry runs it with
    its options, validated once, at startup, by `use_options`, and saves its
    artifacts under the entry's key."""

    def use_options(self, overrides: Mapping[str, Any]) -> O:
        """An entry's options over the plugin section's defaults. Raise
        `pydantic.ValidationError` for options the remixer does not take."""
        ...

    def remix(
        self,
        db: Database,
        *,
        key: str,
        options: O,
        scope: ProcessingScope | None = None,
    ) -> list[str]: ...


class UnavailableRemixer:
    """Stands in for a remixer that cannot run, such as one whose LLM is not
    loaded: `remix` logs why and saves nothing. Options are the real
    remixer's, so its entries are still checked."""

    def __init__(
        self,
        name: str,
        reason: str,
        remixer: type[BaseRemixer],
        defaults: PluginOptions,
    ) -> None:
        self.name = name
        self.reason = reason
        self.remixer = remixer
        self.defaults = defaults

    def use_options(self, overrides: Mapping[str, Any]) -> pydantic.BaseModel:
        return merge_options(self.remixer.options_model, self.defaults, overrides)

    def remix(
        self,
        db: Database,
        *,
        key: str,
        options: Any,
        scope: ProcessingScope | None = None,
    ) -> list[str]:
        LOGGER.error(f"{key}: {self.reason}; nothing produced")
        return []


class BaseRemixer:
    """A Remixer whose named artifacts are regenerated on every run.

    Remixers may read items, annotations and other remixers' artifacts
    through `db`. `options_model` declares the per-use options, whose
    defaults come from `defaults`, the plugin section.
    """

    name: str
    options_model: type[pydantic.BaseModel] = NoOptions

    def __init__(self, defaults: PluginOptions | None = None) -> None:
        self.defaults = defaults or NoOptions()

    def use_options(self, overrides: Mapping[str, Any]) -> pydantic.BaseModel:
        return merge_options(self.options_model, self.defaults, overrides)

    def remix(
        self,
        db: Database,
        *,
        key: str,
        options: Any,
        scope: ProcessingScope | None = None,
    ) -> list[str]:
        """Produce and save this entry's artifacts under `key`; return their
        names."""
        LOGGER.info(f"{key}: remixing with {self.name}")
        started = time.monotonic()
        names = []
        for name, content, content_type in self.produce(
            db, scope or ProcessingScope(), options
        ):
            db.save_artifact(Artifact(key, name, content, content_type))
            LOGGER.info(f"{key}: saved artifact '{name}' ({len(content)} chars)")
            names.append(name)
        LOGGER.info(
            f"{key}: finished in {time.monotonic() - started:.1f}s:"
            f" {len(names)} artifact(s)"
        )
        return names

    @abstractmethod
    def produce(
        self, db: Database, scope: ProcessingScope, options: Any
    ) -> Iterator[tuple[str, str, str]]:
        """Yield (name, content, content_type) tuples; `options` is an
        `options_model`."""
