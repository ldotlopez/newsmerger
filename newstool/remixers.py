from __future__ import annotations

import logging
import time
from abc import abstractmethod
from collections.abc import Iterator
from typing import Any, Protocol, runtime_checkable

import pydantic

from .models import Artifact, ProcessingScope
from .plugins import NoOptions, Services

LOGGER = logging.getLogger(__name__)


@runtime_checkable
class Remixer(Protocol):
    """Produces artifacts from many items, saved under the run's key."""

    def remix(
        self,
        *,
        key: str,
        scope: ProcessingScope | None = None,
    ) -> list[str]: ...


@runtime_checkable
class RemixerType(Protocol):
    """A Remixer class, as plugins register it: each configured use builds
    one with its options, validated at startup with `options_model`."""

    options_model: type[pydantic.BaseModel]

    def __call__(self, options: Any, services: Services) -> Remixer: ...


class BaseRemixer:
    """A Remixer whose named artifacts are regenerated on every run.
    Remixers may read items, annotations and other remixers' artifacts
    through `self.db`. `options_model` declares its options.
    """

    name: str
    options_model: type[pydantic.BaseModel] = NoOptions

    def __init__(self, options: Any, services: Services) -> None:
        self.options = options
        self.db = services.db

    def remix(
        self,
        *,
        key: str,
        scope: ProcessingScope | None = None,
    ) -> list[str]:
        """Produce and save this entry's artifacts under `key`; return their
        names."""
        LOGGER.info(f"{key}: remixing with {self.name}")
        started = time.monotonic()
        names = []
        for name, content, content_type in self.produce(scope or ProcessingScope()):
            self.db.save_artifact(Artifact(key, name, content, content_type))
            LOGGER.info(f"{key}: saved artifact '{name}' ({len(content)} chars)")
            names.append(name)
        LOGGER.info(
            f"{key}: finished in {time.monotonic() - started:.1f}s:"
            f" {len(names)} artifact(s)"
        )
        return names

    @abstractmethod
    def produce(self, scope: ProcessingScope) -> Iterator[tuple[str, str, str]]:
        """Yield (name, content, content_type) tuples."""
