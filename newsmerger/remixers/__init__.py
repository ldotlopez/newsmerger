import logging
from abc import abstractmethod
from collections.abc import Iterator

from ..db import Database
from ..models import Artifact, ProcessingScope

LOGGER = logging.getLogger(__name__)


class BaseRemixer:
    """Produces named artifacts from many items, regenerated on every run.

    NAME is the remixer's module name. Remixers may read items, annotations
    and other remixers' artifacts through `db`.
    """

    NAME: str

    def __init__(self, db: Database) -> None:
        self.db = db

    def run(self, *, scope: ProcessingScope | None = None) -> list[str]:
        """Produce and save this remixer's artifacts; return their names."""
        names = []
        for name, content, content_type in self.produce(scope or ProcessingScope()):
            self.db.save_artifact(Artifact(self.NAME, name, content, content_type))
            LOGGER.info(f"{self.NAME}: saved artifact '{name}' ({len(content)} chars)")
            names.append(name)
        return names

    @abstractmethod
    def produce(self, scope: ProcessingScope) -> Iterator[tuple[str, str, str]]:
        """Yield (name, content, content_type) tuples."""
