import dataclasses
import logging
import time
from abc import abstractmethod
from typing import Any, Protocol, runtime_checkable

from .db import Database, ProcessingStatus
from .models import ProcessingScope, SourceItem

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


@runtime_checkable
class Processor(Protocol):
    """Annotates items. Its registered name keys its annotations and processing
    state: entry points register each object under its own `name`."""

    def enrich(
        self, db: Database, *, scope: ProcessingScope | None = None, force: bool = False
    ) -> RunSummary: ...


class UnavailableProcessor:
    """Stands in for a processor that cannot run, such as one whose LLM is
    not loaded: `enrich` logs why and leaves every item pending."""

    def __init__(self, name: str, reason: str) -> None:
        self.name = name
        self.reason = reason

    def enrich(
        self, db: Database, *, scope: ProcessingScope | None = None, force: bool = False
    ) -> RunSummary:
        LOGGER.error(f"{self.name}: {self.reason}; nothing processed")
        return RunSummary()


class BaseProcessor:
    """A Processor that produces annotations for each eligible item.

    Changing `version` makes items it finished eligible again. `requires`
    names the processor whose output this one reads: only items it finished
    on their current content are picked up.
    """

    name: str
    version: str | None = None
    requires: str | None = None

    def __init__(self, *, max_retries: int = 3) -> None:
        self.max_retries = max_retries

    def enrich(
        self, db: Database, *, scope: ProcessingScope | None = None, force: bool = False
    ) -> RunSummary:
        items = db.get_unprocessed_items(
            self.name,
            version=self.version,
            max_retries=self.max_retries,
            force=force,
            scope=scope,
            requires=self.requires,
        )
        total = len(items)
        LOGGER.info(
            f"{self.name}: {total} item(s) to process"
            f" (version={self.version}, requires={self.requires}, force={force})"
        )

        summary = RunSummary()
        run_started = time.monotonic()
        for position, item in enumerate(items, start=1):
            LOGGER.info(
                f"{self.name}: [{position}/{total}] '{item.title}' ({item.uri})"
            )
            item_started = time.monotonic()
            status, annotations, error = self._process(db, item)
            LOGGER.debug(
                f"{self.name}: '{item.uri}' {status.value}"
                f" in {time.monotonic() - item_started:.2f}s"
                f" (keys: {', '.join(annotations or {}) or '-'})"
            )
            db.record_result(
                item,
                self.name,
                status,
                annotations=annotations,
                error=error,
                version=self.version,
                reset_attempts=force,
            )
            match status:
                case ProcessingStatus.DONE:
                    summary.done += 1
                case ProcessingStatus.IGNORED:
                    summary.ignored += 1
                case ProcessingStatus.ERROR:
                    summary.failed += 1

        LOGGER.info(
            f"{self.name}: finished in {time.monotonic() - run_started:.1f}s:"
            f" {summary.done} done, {summary.ignored} ignored, {summary.failed} failed"
        )
        return summary

    def _process(
        self, db: Database, item: SourceItem
    ) -> tuple[ProcessingStatus, dict[str, Any] | None, str | None]:
        """Run `process_item` and translate its outcome into a result."""
        try:
            return ProcessingStatus.DONE, self.process_item(db, item), None
        except SkipItem as e:
            LOGGER.info(f"{self.name} ignored '{item.uri}': {e}")
            return ProcessingStatus.IGNORED, None, None
        except PartialFailure as e:
            LOGGER.warning(f"{self.name} partial failure on '{item.uri}': {e.errors}")
            error = "; ".join(f"{k}: {v}" for k, v in e.errors.items())
            return ProcessingStatus.ERROR, e.results, error
        except Exception as e:
            LOGGER.exception(f"{self.name} failed on '{item.uri}'")
            return ProcessingStatus.ERROR, None, str(e)

    @staticmethod
    def require_annotation(
        db: Database, item: SourceItem, processor: str, key: str
    ) -> Any:
        """Return an upstream processor's annotation, or raise if it is missing."""
        annotations = db.get_annotations(item, processor=processor, key=key)
        value = annotations.get(processor, {}).get(key)
        if not value:
            raise MissingAnnotationError(f"{processor}.{key} annotation is missing")
        return value

    @abstractmethod
    def process_item(self, db: Database, item: SourceItem) -> dict[str, Any]:
        """Return annotation key -> value on full success.

        Raise `SkipItem` if the item doesn't apply, `PartialFailure` if only
        some keys were computed. Any other exception marks the item `error`
        with no annotations saved.
        """
