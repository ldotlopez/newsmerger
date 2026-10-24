"""Sinks act on the outside world: they deliver items or artifacts and record
every delivery in the ledger, which is never regenerated (decision 0007)."""

import dataclasses
import logging
import time
from abc import abstractmethod
from datetime import UTC, datetime, timedelta
from typing import Protocol, runtime_checkable

from foundation.jsonlib import JsonCompatible

from .db import Database, DeliveryStatus, backoff_seconds
from .models import Artifact, Delivery, ProcessingScope, SourceItem
from .processors import RunSummary

LOGGER = logging.getLogger(__name__)

type ArtifactNames = tuple[tuple[str, str], ...]  # (remixer, name) pairs


class SelectionRequiredError(ValueError):
    """A forced delivery names no subject explicitly."""


@runtime_checkable
class Sink(Protocol):
    """Delivers subjects to the outside world. Its registered name keys its
    ledger rows: entry points register each object under its own `name`."""

    def deliver(
        self,
        db: Database,
        *,
        scope: ProcessingScope | None = None,
        artifacts: ArtifactNames = (),
        requeue: bool = False,
        force: bool = False,
    ) -> RunSummary: ...


class UnavailableSink:
    """Stands in for a sink that cannot run: `deliver` logs why and sends
    nothing."""

    def __init__(self, name: str, reason: str) -> None:
        self.name = name
        self.reason = reason

    def deliver(
        self,
        db: Database,
        *,
        scope: ProcessingScope | None = None,
        artifacts: ArtifactNames = (),
        requeue: bool = False,
        force: bool = False,
    ) -> RunSummary:
        LOGGER.error(f"{self.name}: {self.reason}; nothing delivered")
        return RunSummary()


class BaseSink[S: (SourceItem, Artifact)]:
    """The delivery cycle shared by item and artifact sinks:

    1. queue the candidates: subjects in scope without a row;
    2. `select` what to deliver now from the pending rows (queued, or
       failed with attempts left), which is where rate limits live;
    3. mark each selected row `sending`, `send` it, then mark it `done`
       with the external reference, or `error`.

    Rows left `sending` by an interrupted run are never retried.
    """

    name: str
    selection_hint: str  # what a forced delivery must name

    def __init__(self, *, max_retries: int = 3, lookback: int = 24) -> None:
        self.max_retries = max_retries
        self.lookback = timedelta(hours=lookback)

    def deliver(
        self,
        db: Database,
        *,
        scope: ProcessingScope | None = None,
        artifacts: ArtifactNames = (),
        requeue: bool = False,
        force: bool = False,
    ) -> RunSummary:
        """Queue, select and send. `requeue` gives the failed rows in scope
        fresh attempts first; `force` sends the explicitly selected subjects
        now, whatever their state, with no backoff and no rate limit."""
        scope = scope or ProcessingScope()
        now = datetime.now(UTC)
        if force:
            if not self.is_explicit(scope, artifacts):
                raise SelectionRequiredError(f"{self.name}: {self.selection_hint}")
            self.queue_selected(db, scope, artifacts)
            return self._send_all(db, self.rows(db, scope, artifacts))

        if requeue:
            for delivery, _ in self.rows(db, scope, artifacts, [DeliveryStatus.ERROR]):
                delivery.status = DeliveryStatus.QUEUED
                delivery.attempts = 0
                db.save_delivery(delivery)
        self.queue(db, scope, artifacts, now)

        rows = self.rows(
            db,
            ProcessingScope(),
            (),
            [DeliveryStatus.QUEUED, DeliveryStatus.ERROR, DeliveryStatus.SENDING],
        )
        if interrupted := sum(row.status == DeliveryStatus.SENDING for row, _ in rows):
            LOGGER.warning(
                f"{self.name}: {interrupted} interrupted delivery(ies) stay"
                " `sending`; settle them with `deliveries resolve`"
            )
        pending = [
            (delivery, subject)
            for delivery, subject in rows
            if delivery.status == DeliveryStatus.QUEUED
            or (
                delivery.status == DeliveryStatus.ERROR
                and delivery.attempts < self.max_retries
            )
        ]
        return self._send_all(db, self.select(db, pending, now))

    def is_due(self, delivery: Delivery, now: datetime) -> bool:
        """Queued rows are due; failed ones once their backoff has passed."""
        if delivery.status != DeliveryStatus.ERROR or delivery.updated_at is None:
            return True
        elapsed = (now - delivery.updated_at).total_seconds()
        return elapsed >= backoff_seconds(delivery.attempts)

    def select(
        self, db: Database, pending: list[tuple[Delivery, S]], now: datetime
    ) -> list[tuple[Delivery, S]]:
        """What to deliver now: every due row unless a sink limits it."""
        return [
            (delivery, subject)
            for delivery, subject in pending
            if self.is_due(delivery, now)
        ]

    def _send_all(self, db: Database, rows: list[tuple[Delivery, S]]) -> RunSummary:
        LOGGER.info(f"{self.name}: {len(rows)} to deliver")
        started = time.monotonic()
        summary = RunSummary()
        for delivery, subject in rows:
            delivery.status = DeliveryStatus.SENDING
            db.save_delivery(delivery)
            try:
                external_ref = self.send(db, subject)
            except Exception as e:
                LOGGER.exception(
                    f"{self.name}: could not deliver {self.label(subject)}"
                )
                delivery.status = DeliveryStatus.ERROR
                delivery.attempts += 1
                delivery.last_error = str(e)
                summary.failed += 1
            else:
                LOGGER.info(f"{self.name}: delivered {self.label(subject)}")
                delivery.status = DeliveryStatus.DONE
                delivery.attempts = 0
                delivery.last_error = None
                delivery.external_ref = external_ref
                delivery.content_sha256 = subject.content_sha256
                summary.done += 1
            db.save_delivery(delivery)
        LOGGER.info(
            f"{self.name}: finished in {time.monotonic() - started:.1f}s:"
            f" {summary.done} delivered, {summary.failed} failed"
        )
        return summary

    @abstractmethod
    def is_explicit(self, scope: ProcessingScope, artifacts: ArtifactNames) -> bool:
        """Whether the selection names subjects, as a forced send needs."""

    @abstractmethod
    def queue(
        self,
        db: Database,
        scope: ProcessingScope,
        artifacts: ArtifactNames,
        now: datetime,
    ) -> None:
        """Queue the candidates in scope."""

    @abstractmethod
    def queue_selected(
        self, db: Database, scope: ProcessingScope, artifacts: ArtifactNames
    ) -> None:
        """Give every explicitly selected subject a row."""

    @abstractmethod
    def rows(
        self,
        db: Database,
        scope: ProcessingScope,
        artifacts: ArtifactNames,
        statuses: list[DeliveryStatus] | None = None,
    ) -> list[tuple[Delivery, S]]:
        """This sink's rows in scope, with their subjects, in delivery order."""

    @abstractmethod
    def label(self, subject: S) -> str:
        """How logs name a subject."""

    @abstractmethod
    def send(self, db: Database, subject: S) -> JsonCompatible:
        """Deliver one subject; return its external reference. Raise on
        failure; the error is logged with its traceback, so it must not
        chain an exception that holds a secret (raise it `from None`)."""


class BaseItemSink(BaseSink[SourceItem]):
    """Delivers items. Without `since` or item ids in scope, the candidates
    are the items of the last `lookback` hours; with `requires`, only those
    that processor finished. Each source is a strict FIFO queue: a row that
    is not due yet holds back the ones after it."""

    requires: str | None = None
    selection_hint = "a forced delivery needs --item"

    def is_explicit(self, scope: ProcessingScope, artifacts: ArtifactNames) -> bool:
        return bool(scope.item_ids)

    def queue(
        self,
        db: Database,
        scope: ProcessingScope,
        artifacts: ArtifactNames,
        now: datetime,
    ) -> None:
        if scope.since is None and scope.item_ids is None:
            scope = dataclasses.replace(scope, since=now - self.lookback)
        db.queue_item_deliveries(self.name, scope, requires=self.requires)

    def queue_selected(
        self, db: Database, scope: ProcessingScope, artifacts: ArtifactNames
    ) -> None:
        db.queue_item_deliveries(self.name, scope)

    def rows(
        self,
        db: Database,
        scope: ProcessingScope,
        artifacts: ArtifactNames,
        statuses: list[DeliveryStatus] | None = None,
    ) -> list[tuple[Delivery, SourceItem]]:
        return db.get_item_deliveries(self.name, scope, statuses=statuses)

    def select(
        self, db: Database, pending: list[tuple[Delivery, SourceItem]], now: datetime
    ) -> list[tuple[Delivery, SourceItem]]:
        selected = []
        blocked: set[str] = set()
        for delivery, item in pending:
            if item.source.id in blocked:
                continue
            if self.is_due(delivery, now):
                selected.append((delivery, item))
            else:
                blocked.add(item.source.id)
        return selected

    def label(self, subject: SourceItem) -> str:
        return f"item {subject.id} ({subject.uri})"


class BaseArtifactSink(BaseSink[Artifact]):
    """Delivers the artifacts of the remixers it is given. Without `since`
    or `--artifact`, the candidates are those created in the last
    `lookback` hours."""

    selection_hint = "a forced delivery needs --artifact"

    def __init__(
        self, remixers: list[str], *, max_retries: int = 3, lookback: int = 24
    ) -> None:
        super().__init__(max_retries=max_retries, lookback=lookback)
        self.remixers = remixers

    def is_explicit(self, scope: ProcessingScope, artifacts: ArtifactNames) -> bool:
        return bool(artifacts)

    def queue(
        self,
        db: Database,
        scope: ProcessingScope,
        artifacts: ArtifactNames,
        now: datetime,
    ) -> None:
        if artifacts:
            db.queue_artifact_deliveries(self.name, self.remixers, names=artifacts)
        else:
            since = scope.since or now - self.lookback
            db.queue_artifact_deliveries(self.name, self.remixers, since=since)

    def queue_selected(
        self, db: Database, scope: ProcessingScope, artifacts: ArtifactNames
    ) -> None:
        db.queue_artifact_deliveries(self.name, self.remixers, names=artifacts)

    def rows(
        self,
        db: Database,
        scope: ProcessingScope,
        artifacts: ArtifactNames,
        statuses: list[DeliveryStatus] | None = None,
    ) -> list[tuple[Delivery, Artifact]]:
        return db.get_artifact_deliveries(
            self.name, statuses=statuses, names=artifacts or None
        )

    def label(self, subject: Artifact) -> str:
        return f"artifact {subject.remixer}/{subject.name}"
