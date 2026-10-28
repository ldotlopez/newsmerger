"""Sinks act on the outside world: they deliver items or artifacts and record
every delivery in the ledger, which is never regenerated (decision 0007)."""

import dataclasses
import logging
import time
from abc import abstractmethod
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol, runtime_checkable

import pydantic
from foundation.jsonlib import JsonCompatible

from .db import Database, DeliveryStatus, backoff_seconds
from .models import Artifact, Delivery, ProcessingScope, SourceItem
from .plugins import PluginOptions, Services
from .processors import RunSummary

LOGGER = logging.getLogger(__name__)

type ArtifactNames = tuple[tuple[str, str], ...]  # (remixer, name) pairs


class SelectionRequiredError(ValueError):
    """A forced delivery names no subject explicitly."""


class DeliveryOptions(PluginOptions):
    """Options every sink takes."""

    # Minutes between the entry's deliveries, oldest subject first; 0: no
    # pacing.
    interval: pydantic.NonNegativeInt = 0
    # Deliveries per run at most, against flooding (a new key starts with an
    # empty ledger).
    max_per_run: pydantic.PositiveInt = 5
    max_retries: int = 3
    lookback: int = 24  # hours: the candidates without --since or --item


class ArtifactDeliveryOptions(DeliveryOptions):
    # Remixers whose artifacts are sent.
    artifacts: list[str] = pydantic.Field(default_factory=list)


@runtime_checkable
class Sink(Protocol):
    """Delivers subjects to the outside world under a ledger key: the rows of
    that key are the run's record."""

    def deliver(
        self,
        db: Database,
        *,
        key: str,
        scope: ProcessingScope | None = None,
        artifacts: ArtifactNames = (),
        requeue: bool = False,
        force: bool = False,
    ) -> RunSummary: ...


@runtime_checkable
class SinkType(Protocol):
    """A Sink class, as plugins register it: each configured use builds one
    with its options, validated at startup with `options_model`."""

    options_model: type[pydantic.BaseModel]

    def __call__(self, options: Any, services: Services) -> Sink: ...

    def required_key(self, options: Any) -> str | None:
        """The annotation key a run with `options` delivers, if any."""
        ...


class BaseSink[S: (SourceItem, Artifact), O: DeliveryOptions]:
    """The delivery cycle shared by item and artifact sinks, over the rows of
    one ledger key:

    1. queue the candidates: subjects in scope without a row;
    2. `select` what could go now from the pending rows (queued, or failed
       with attempts left), then `pace` it: one per `interval`, at most
       `max_per_run`;
    3. mark each selected row `sending`, `send` it, then mark it `done`
       with the external reference, or `error`.

    Rows left `sending` by an interrupted run are never retried.
    `options_model` declares its options.
    """

    name: str
    selection_hint: str  # what a forced delivery must name
    options_model: type[O]

    def __init__(self, options: O, services: Services) -> None:
        self.options = options

    @classmethod
    def required_key(cls, options: Any) -> str | None:
        return None

    def deliver(
        self,
        db: Database,
        *,
        key: str,
        scope: ProcessingScope | None = None,
        artifacts: ArtifactNames = (),
        requeue: bool = False,
        force: bool = False,
    ) -> RunSummary:
        """Queue, select and send. `requeue` gives the failed rows in scope
        fresh attempts first; `force` sends the explicitly selected subjects
        now, whatever their state, with no backoff and no pacing."""
        scope = scope or ProcessingScope()
        now = datetime.now(UTC)
        if force:
            if not self.is_explicit(scope, artifacts):
                raise SelectionRequiredError(f"{key}: {self.selection_hint}")
            self.queue_selected(db, key, scope, artifacts)
            rows = self.rows(db, key, scope, artifacts)
            return self._send_all(db, key, rows)

        if requeue:
            errors = self.rows(db, key, scope, artifacts, [DeliveryStatus.ERROR])
            for delivery, _ in errors:
                delivery.status = DeliveryStatus.QUEUED
                delivery.attempts = 0
                db.save_delivery(delivery)
        self.queue(db, key, scope, artifacts, now)

        rows = self.rows(
            db,
            key,
            ProcessingScope(),
            (),
            [DeliveryStatus.QUEUED, DeliveryStatus.ERROR, DeliveryStatus.SENDING],
        )
        if interrupted := sum(row.status == DeliveryStatus.SENDING for row, _ in rows):
            LOGGER.warning(
                f"{key}: {interrupted} interrupted delivery(ies) stay"
                " `sending`; settle them with `deliveries resolve`"
            )
        pending = [
            (delivery, subject)
            for delivery, subject in rows
            if delivery.status == DeliveryStatus.QUEUED
            or (
                delivery.status == DeliveryStatus.ERROR
                and delivery.attempts < self.options.max_retries
            )
        ]
        selected = self.pace(db, key, self.select(pending, now), now)
        return self._send_all(db, key, selected)

    def is_due(self, delivery: Delivery, now: datetime) -> bool:
        """Queued rows are due; failed ones once their backoff has passed."""
        if delivery.status != DeliveryStatus.ERROR or delivery.updated_at is None:
            return True
        elapsed = (now - delivery.updated_at).total_seconds()
        return elapsed >= backoff_seconds(delivery.attempts)

    def select(
        self, pending: list[tuple[Delivery, S]], now: datetime
    ) -> list[tuple[Delivery, S]]:
        """What could be delivered now: every due row."""
        return [
            (delivery, subject)
            for delivery, subject in pending
            if self.is_due(delivery, now)
        ]

    def pace(
        self,
        db: Database,
        key: str,
        selected: list[tuple[Delivery, S]],
        now: datetime,
    ) -> list[tuple[Delivery, S]]:
        """With an `interval`, the first selected row once the key's last
        delivery is that old; then at most `max_per_run` rows."""
        interval = self.options.interval
        if interval:
            last = db.last_delivered_at(key)
            if last is not None and now - last < timedelta(minutes=interval):
                return []
            selected = selected[:1]
        return selected[: self.options.max_per_run]

    def _send_all(
        self, db: Database, key: str, rows: list[tuple[Delivery, S]]
    ) -> RunSummary:
        LOGGER.info(f"{key}: {len(rows)} to deliver")
        started = time.monotonic()
        summary = RunSummary()
        for delivery, subject in rows:
            delivery.status = DeliveryStatus.SENDING
            db.save_delivery(delivery)
            try:
                external_ref = self.send(db, subject)
            except Exception as e:
                LOGGER.exception(f"{key}: could not deliver {self.label(subject)}")
                delivery.status = DeliveryStatus.ERROR
                delivery.attempts += 1
                delivery.last_error = str(e)
                summary.failed += 1
            else:
                LOGGER.info(f"{key}: delivered {self.label(subject)}")
                delivery.status = DeliveryStatus.DONE
                delivery.attempts = 0
                delivery.last_error = None
                delivery.external_ref = external_ref
                delivery.content_sha256 = subject.content_sha256
                summary.done += 1
            db.save_delivery(delivery)
        LOGGER.info(
            f"{key}: finished in {time.monotonic() - started:.1f}s:"
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
        key: str,
        scope: ProcessingScope,
        artifacts: ArtifactNames,
        now: datetime,
    ) -> None:
        """Queue the candidates in scope."""

    @abstractmethod
    def queue_selected(
        self,
        db: Database,
        key: str,
        scope: ProcessingScope,
        artifacts: ArtifactNames,
    ) -> None:
        """Give every explicitly selected subject a row."""

    @abstractmethod
    def rows(
        self,
        db: Database,
        key: str,
        scope: ProcessingScope,
        artifacts: ArtifactNames,
        statuses: list[DeliveryStatus] | None = None,
    ) -> list[tuple[Delivery, S]]:
        """The key's rows in scope, with their subjects, in delivery order."""

    @abstractmethod
    def label(self, subject: S) -> str:
        """How logs name a subject."""

    @abstractmethod
    def send(self, db: Database, subject: S) -> JsonCompatible:
        """Deliver one subject; return its external reference. Raise on
        failure; the error is logged with its traceback, so it must not
        chain an exception that holds a secret (raise it `from None`)."""


class BaseItemSink[O: DeliveryOptions](BaseSink[SourceItem, O]):
    """Delivers items, oldest first. Without `since` or item ids in scope,
    the candidates are the items of the last `lookback` hours; with
    `required_key`, only those whose run of that annotation key finished. Each
    source is a strict FIFO queue: a row that is not due yet holds back the
    ones after it."""

    requires: str | None = None
    selection_hint = "a forced delivery needs --item"

    def is_explicit(self, scope: ProcessingScope, artifacts: ArtifactNames) -> bool:
        return bool(scope.item_ids)

    @classmethod
    def required_key(cls, options: Any) -> str | None:
        return cls.requires

    def queue(
        self,
        db: Database,
        key: str,
        scope: ProcessingScope,
        artifacts: ArtifactNames,
        now: datetime,
    ) -> None:
        if scope.since is None and scope.item_ids is None:
            since = now - timedelta(hours=self.options.lookback)
            scope = dataclasses.replace(scope, since=since)
        db.queue_item_deliveries(key, scope, requires=self.required_key(self.options))

    def queue_selected(
        self,
        db: Database,
        key: str,
        scope: ProcessingScope,
        artifacts: ArtifactNames,
    ) -> None:
        db.queue_item_deliveries(key, scope)

    def rows(
        self,
        db: Database,
        key: str,
        scope: ProcessingScope,
        artifacts: ArtifactNames,
        statuses: list[DeliveryStatus] | None = None,
    ) -> list[tuple[Delivery, SourceItem]]:
        return db.get_item_deliveries(key, scope, statuses=statuses)

    def select(
        self, pending: list[tuple[Delivery, SourceItem]], now: datetime
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


class BaseArtifactSink[O: ArtifactDeliveryOptions](BaseSink[Artifact, O]):
    """Delivers the artifacts of the remixers its `artifacts` option names.
    Without `since` or `--artifact`, the candidates are those created in the
    last `lookback` hours."""

    selection_hint = "a forced delivery needs --artifact"

    def is_explicit(self, scope: ProcessingScope, artifacts: ArtifactNames) -> bool:
        return bool(artifacts)

    def queue(
        self,
        db: Database,
        key: str,
        scope: ProcessingScope,
        artifacts: ArtifactNames,
        now: datetime,
    ) -> None:
        remixers = self.options.artifacts
        if artifacts:
            db.queue_artifact_deliveries(key, remixers, names=artifacts)
        else:
            since = scope.since or now - timedelta(hours=self.options.lookback)
            db.queue_artifact_deliveries(key, remixers, since=since)

    def queue_selected(
        self,
        db: Database,
        key: str,
        scope: ProcessingScope,
        artifacts: ArtifactNames,
    ) -> None:
        db.queue_artifact_deliveries(key, self.options.artifacts, names=artifacts)

    def rows(
        self,
        db: Database,
        key: str,
        scope: ProcessingScope,
        artifacts: ArtifactNames,
        statuses: list[DeliveryStatus] | None = None,
    ) -> list[tuple[Delivery, Artifact]]:
        return db.get_artifact_deliveries(
            key, statuses=statuses, names=artifacts or None
        )

    def label(self, subject: Artifact) -> str:
        return f"artifact {subject.remixer}/{subject.name}"
