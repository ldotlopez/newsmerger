import logging
import time
from abc import abstractmethod
from collections.abc import Iterator
from typing import Protocol, runtime_checkable

from .db import Database
from .models import Artifact, ProcessingScope

LOGGER = logging.getLogger(__name__)


@runtime_checkable
class Remixer(Protocol):
    """Produces artifacts from many items. Its registered name keys its
    artifacts: entry points register each object under its own `name`."""

    def remix(
        self, db: Database, *, scope: ProcessingScope | None = None
    ) -> list[str]: ...


class UnavailableRemixer:
    """Stands in for a remixer that cannot run, such as one whose LLM is not
    loaded: `remix` logs why and saves nothing."""

    def __init__(self, name: str, reason: str) -> None:
        self.name = name
        self.reason = reason

    def remix(self, db: Database, *, scope: ProcessingScope | None = None) -> list[str]:
        LOGGER.error(f"{self.name}: {self.reason}; nothing produced")
        return []


class BaseRemixer:
    """A Remixer whose named artifacts are regenerated on every run.

    Remixers may read items, annotations and other remixers' artifacts
    through `db`.
    """

    name: str

    def remix(self, db: Database, *, scope: ProcessingScope | None = None) -> list[str]:
        """Produce and save this remixer's artifacts; return their names."""
        LOGGER.info(f"{self.name}: remixing")
        started = time.monotonic()
        names = []
        for name, content, content_type in self.produce(db, scope or ProcessingScope()):
            db.save_artifact(Artifact(self.name, name, content, content_type))
            LOGGER.info(f"{self.name}: saved artifact '{name}' ({len(content)} chars)")
            names.append(name)
        LOGGER.info(
            f"{self.name}: finished in {time.monotonic() - started:.1f}s:"
            f" {len(names)} artifact(s)"
        )
        return names

    @abstractmethod
    def produce(
        self, db: Database, scope: ProcessingScope
    ) -> Iterator[tuple[str, str, str]]:
        """Yield (name, content, content_type) tuples."""
