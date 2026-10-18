import logging
from abc import abstractmethod
from collections.abc import Iterator
from typing import Any

from ..db import Database, ProcessingScope, ProcessingStatus
from ..models import Artifact, SourceItem

LOGGER = logging.getLogger(__name__)


class SkipItem(Exception):
    """Raise from `ItemProcessor.process_item` to mark an item as
    deliberately not applicable (e.g. wrong language) rather than a
    processing failure. Recorded as `ignored` — a permanent skip that only
    `--force` will revisit."""


class MissingAnnotationError(LookupError):
    """An annotation a processor needs from an upstream one is missing."""


class PartialFailure(Exception):
    """Raise from `ItemProcessor.process_item` when some annotation keys
    were computed successfully and others weren't. `results` is saved as
    annotations regardless of the failure; the item is still marked
    `error` overall, so it's retried (subject to backoff) — a retry may
    recompute already-succeeded keys, which is accepted as the simple
    tradeoff here."""

    def __init__(self, results: dict[str, Any], errors: dict[str, str]):
        self.results = results
        self.errors = errors
        super().__init__(f"{len(errors)} key(s) failed: {list(errors)}")


class BaseProcessor:
    NAME: str
    MAX_RETRIES = 3
    VERSION: str | None = None

    def __init__(
        self,
        db: Database,
        *,
        max_retries: int | None = None,
        version: str | None = None,
        **params: Any,
    ) -> None:
        self.db = db
        if max_retries is not None:
            self.MAX_RETRIES = max_retries
        if version is not None:
            self.VERSION = version

    @abstractmethod
    def run(
        self, *, scope: ProcessingScope | None = None, force: bool = False
    ) -> None: ...


class ItemProcessor(BaseProcessor):
    """Runs over individual items that don't yet have output from this
    processor (or are eligible for a retry / reprocess — see
    `Database.get_unprocessed_items`).

    REQUIRES names the processor whose output this one reads: only items it
    finished on their current content are picked up.
    """

    REQUIRES: str | None = None

    def run(self, *, scope: ProcessingScope | None = None, force: bool = False) -> None:
        items = self.db.get_unprocessed_items(
            self.NAME,
            version=self.VERSION,
            max_retries=self.MAX_RETRIES,
            force=force,
            scope=scope,
            requires=self.REQUIRES,
        )
        LOGGER.info(f"{self.NAME}: {len(items)} item(s) to process")

        for item in items:
            try:
                result = self.process_item(item)
            except SkipItem as e:
                self.db.record_result(
                    item, self.NAME, ProcessingStatus.IGNORED, version=self.VERSION
                )
                LOGGER.info(f"{self.NAME} ignored '{item.uri}': {e}")
                continue
            except PartialFailure as e:
                self.db.record_result(
                    item,
                    self.NAME,
                    ProcessingStatus.ERROR,
                    annotations=e.results,
                    error="; ".join(f"{k}: {v}" for k, v in e.errors.items()),
                    version=self.VERSION,
                )
                LOGGER.warning(
                    f"{self.NAME} partial failure on '{item.uri}': {e.errors}"
                )
                continue
            except Exception as e:
                self.db.record_result(
                    item,
                    self.NAME,
                    ProcessingStatus.ERROR,
                    error=str(e),
                    version=self.VERSION,
                )
                LOGGER.exception(f"{self.NAME} failed on '{item.uri}'")
                continue

            self.db.record_result(
                item,
                self.NAME,
                ProcessingStatus.DONE,
                annotations=result,
                version=self.VERSION,
            )

    def require_annotation(self, item: SourceItem, processor: str, key: str) -> Any:
        """Return an upstream processor's annotation, or raise if it is missing."""
        annotations = self.db.get_annotations(item, processor=processor, key=key)
        value = annotations.get(processor, {}).get(key)
        if not value:
            raise MissingAnnotationError(f"{processor}.{key} annotation is missing")
        return value

    @abstractmethod
    def process_item(self, item: SourceItem) -> dict[str, Any]:
        """Return a dict of annotation key -> value on full success.

        Raise `SkipItem` if this item doesn't apply. Raise `PartialFailure`
        if only some keys were computed. Any other exception marks the
        whole item as `error` with no annotations saved.
        """
        ...


class ArtifactProcessor(BaseProcessor):
    """Produces one or more named artifacts derived from many items, rather
    than per-item output. Not tracked via DBProcessingState — an artifact
    isn't "done" or "error" per item, it's regenerated wholesale on each
    run. `force` is accepted for interface symmetry with ItemProcessor but
    unused here; subclasses may use it to short-circuit regeneration."""

    def run(self, *, scope: ProcessingScope | None = None, force: bool = False) -> None:
        for name, content, content_type in self.produce(scope or ProcessingScope()):
            self.db.save_artifact(Artifact(self.NAME, name, content, content_type))
            LOGGER.info(f"{self.NAME}: saved artifact '{name}' ({len(content)} bytes)")

    @abstractmethod
    def produce(self, scope: ProcessingScope) -> Iterator[tuple[str, str, str]]:
        """Yield (name, content, content_type) tuples."""
        ...
