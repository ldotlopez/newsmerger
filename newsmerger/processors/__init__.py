import dataclasses
import logging
from abc import abstractmethod
from typing import Any

from ..db import Database, ProcessingStatus
from ..models import ProcessingScope, SourceItem

LOGGER = logging.getLogger(__name__)


class SkipItem(Exception):
    """Raise from `process_item` when the item doesn't apply to this processor
    (e.g. wrong language). Recorded as `ignored`: permanent for the item's
    current content, revisited only if it changes or the run is forced."""


class MissingAnnotationError(LookupError):
    """An annotation a processor needs from an upstream one is missing."""


class PartialFailure(Exception):
    """Raise from `process_item` when only some annotation keys were computed.

    `results` is saved anyway and the item is marked `error`, so a retry may
    recompute keys that already succeeded.
    """

    def __init__(self, results: dict[str, Any], errors: dict[str, str]) -> None:
        self.results = results
        self.errors = errors
        super().__init__(f"{len(errors)} key(s) failed: {list(errors)}")


@dataclasses.dataclass(slots=True)
class RunSummary:
    done: int = 0
    ignored: int = 0
    failed: int = 0


class BaseProcessor:
    """Produces annotations for each eligible item.

    NAME is the processor's module name. Changing VERSION makes items it
    finished eligible again. REQUIRES names the processor whose output this
    one reads: only items it finished on their current content are picked up.
    """

    NAME: str
    VERSION: str | None = None
    REQUIRES: str | None = None
    MAX_RETRIES = 3

    def __init__(self, db: Database, *, max_retries: int | None = None) -> None:
        self.db = db
        if max_retries is not None:
            self.MAX_RETRIES = max_retries

    def run(
        self, *, scope: ProcessingScope | None = None, force: bool = False
    ) -> RunSummary:
        items = self.db.get_unprocessed_items(
            self.NAME,
            version=self.VERSION,
            max_retries=self.MAX_RETRIES,
            force=force,
            scope=scope,
            requires=self.REQUIRES,
        )
        LOGGER.info(f"{self.NAME}: {len(items)} item(s) to process")

        summary = RunSummary()
        for item in items:
            status, annotations, error = self._process(item)
            self.db.record_result(
                item,
                self.NAME,
                status,
                annotations=annotations,
                error=error,
                version=self.VERSION,
                reset_attempts=force,
            )
            match status:
                case ProcessingStatus.DONE:
                    summary.done += 1
                case ProcessingStatus.IGNORED:
                    summary.ignored += 1
                case ProcessingStatus.ERROR:
                    summary.failed += 1
        return summary

    def _process(
        self, item: SourceItem
    ) -> tuple[ProcessingStatus, dict[str, Any] | None, str | None]:
        """Run `process_item` and translate its outcome into a result."""
        try:
            return ProcessingStatus.DONE, self.process_item(item), None
        except SkipItem as e:
            LOGGER.info(f"{self.NAME} ignored '{item.uri}': {e}")
            return ProcessingStatus.IGNORED, None, None
        except PartialFailure as e:
            LOGGER.warning(f"{self.NAME} partial failure on '{item.uri}': {e.errors}")
            error = "; ".join(f"{k}: {v}" for k, v in e.errors.items())
            return ProcessingStatus.ERROR, e.results, error
        except Exception as e:
            LOGGER.exception(f"{self.NAME} failed on '{item.uri}'")
            return ProcessingStatus.ERROR, None, str(e)

    def require_annotation(self, item: SourceItem, processor: str, key: str) -> Any:
        """Return an upstream processor's annotation, or raise if it is missing."""
        annotations = self.db.get_annotations(item, processor=processor, key=key)
        value = annotations.get(processor, {}).get(key)
        if not value:
            raise MissingAnnotationError(f"{processor}.{key} annotation is missing")
        return value

    @abstractmethod
    def process_item(self, item: SourceItem) -> dict[str, Any]:
        """Return annotation key -> value on full success.

        Raise `SkipItem` if the item doesn't apply, `PartialFailure` if only
        some keys were computed. Any other exception marks the item `error`
        with no annotations saved.
        """
