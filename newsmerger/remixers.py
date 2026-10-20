import logging
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


class BaseRemixer:
    """A Remixer whose named artifacts are regenerated on every run.

    Remixers may read items, annotations and other remixers' artifacts
    through `db`.
    """

    name: str

    def remix(self, db: Database, *, scope: ProcessingScope | None = None) -> list[str]:
        """Produce and save this remixer's artifacts; return their names."""
        names = []
        for name, content, content_type in self.produce(db, scope or ProcessingScope()):
            db.save_artifact(Artifact(self.name, name, content, content_type))
            LOGGER.info(f"{self.name}: saved artifact '{name}' ({len(content)} chars)")
            names.append(name)
        return names

    @abstractmethod
    def produce(
        self, db: Database, scope: ProcessingScope
    ) -> Iterator[tuple[str, str, str]]:
        """Yield (name, content, content_type) tuples."""
