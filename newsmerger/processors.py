import dataclasses
import inspect
import logging
import time
from abc import abstractmethod
from collections.abc import Callable
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


@dataclasses.dataclass(slots=True)
class RunSummary:
    done: int = 0
    ignored: int = 0
    failed: int = 0


@runtime_checkable
class Processor(Protocol):
    """Annotates items. Each `process:` entry runs it with its options, which
    an implementation declares one by one (never `**kwargs`). Every run
    writes one annotation key, which also keys its processing state."""

    def output_key(self, **options: Any) -> str:
        """The key a run with `options` writes unless the entry names one.
        Raise `TypeError` for options the processor does not take."""
        ...

    def process(
        self,
        db: Database,
        *,
        key: str,
        scope: ProcessingScope | None = None,
        force: bool = False,
        **options: Any,
    ) -> RunSummary: ...


class UnavailableProcessor:
    """Stands in for a processor that cannot run, such as one whose LLM is
    not loaded: `process` logs why and leaves every item pending.
    `output_key` is the real processor's, so its entries are still checked."""

    def __init__(self, name: str, reason: str, output_key: Callable[..., str]) -> None:
        self.name = name
        self.reason = reason
        self._output_key = output_key

    def output_key(self, **options: Any) -> str:
        return self._output_key(**options)

    def process(
        self,
        db: Database,
        *,
        key: str,
        scope: ProcessingScope | None = None,
        force: bool = False,
        **options: Any,
    ) -> RunSummary:
        LOGGER.error(f"{self.name}: {self.reason}; nothing processed")
        return RunSummary()


class BaseProcessor:
    """A Processor that produces one annotation for each eligible item.

    `key` is the annotation it writes by default. Changing `version` makes
    items it finished eligible again. `requires` names the annotation key
    this one reads: only items whose run of it finished on their current
    content are picked up.
    """

    name: str
    key: str
    version: str | None = None
    requires: str | None = None

    def __init__(self, *, max_retries: int = 3) -> None:
        self.max_retries = max_retries

    @classmethod
    def output_key(cls, **options: Any) -> str:
        inspect.signature(cls.process_item).bind(None, None, None, **options)
        return cls.key

    def required_key(self, **options: Any) -> str | None:
        """The key a run with `options` reads, if any."""
        return self.requires

    def process(
        self,
        db: Database,
        *,
        key: str,
        scope: ProcessingScope | None = None,
        force: bool = False,
        **options: Any,
    ) -> RunSummary:
        requires = self.required_key(**options)
        items = db.get_unprocessed_items(
            key,
            version=self.version,
            max_retries=self.max_retries,
            force=force,
            scope=scope,
            requires=requires,
        )
        total = len(items)
        LOGGER.info(
            f"{key}: {total} item(s) to process with {self.name}"
            f" (version={self.version}, requires={requires}, force={force})"
        )

        summary = RunSummary()
        run_started = time.monotonic()
        for position, item in enumerate(items, start=1):
            LOGGER.info(f"{key}: [{position}/{total}] '{item.title}' ({item.uri})")
            item_started = time.monotonic()
            status, value, error = self._run_item(db, item, options)
            LOGGER.debug(
                f"{key}: '{item.uri}' {status.value}"
                f" in {time.monotonic() - item_started:.2f}s"
            )
            db.record_result(
                item,
                self.name,
                key,
                status,
                value=value,
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
            f"{key}: finished in {time.monotonic() - run_started:.1f}s:"
            f" {summary.done} done, {summary.ignored} ignored, {summary.failed} failed"
        )
        return summary

    def _run_item(
        self, db: Database, item: SourceItem, options: dict[str, Any]
    ) -> tuple[ProcessingStatus, Any, str | None]:
        """Run `process_item` and translate its outcome into a result."""
        try:
            return ProcessingStatus.DONE, self.process_item(db, item, **options), None
        except SkipItem as e:
            LOGGER.info(f"{self.name} ignored '{item.uri}': {e}")
            return ProcessingStatus.IGNORED, None, None
        except Exception as e:
            LOGGER.exception(f"{self.name} failed on '{item.uri}'")
            return ProcessingStatus.ERROR, None, str(e)

    @staticmethod
    def require_annotation(db: Database, item: SourceItem, key: str) -> Any:
        """Return an upstream annotation, or raise if it is missing."""
        value = db.get_annotations(item, key=key).get(key)
        if not value:
            raise MissingAnnotationError(f"{key} annotation is missing")
        return value

    @abstractmethod
    def process_item(self, db: Database, item: SourceItem, **options: Any) -> Any:
        """Return the annotation's value. Implementations declare each option
        they take, with a default.

        Raise `SkipItem` if the item doesn't apply. Any other exception marks
        the item `error`.
        """
