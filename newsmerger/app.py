"""Application: the single entry point for front ends (CLI, scripts) and
external tools. It owns the wiring (config, HTTP cache, database, plugins),
runs the four phases (import, enrich, remix, deliver) and answers queries.
"""

from __future__ import annotations

import fcntl
import os
import pickle
from collections.abc import Iterable
from pathlib import Path
from types import TracebackType
from typing import IO, Any, Self

import pydantic
from foundation.cache import UserCache
from foundation.plugin import EntryPointError, ProtocolConformanceError, Register
from sqlalchemy import make_url

from .config import Config, ConfigError, plugin_options_error
from .consts import PACKAGE_NAME
from .db import Database, DeliveryStatus
from .httpclient import HTTPClient
from .llms import LLM
from .models import (
    Annotation,
    Artifact,
    Delivery,
    ItemKey,
    ProcessingScope,
    SourceData,
    SourceItem,
)
from .plugins import Services
from .processors import Processor, RunSummary
from .providers import Provider, URLProvider
from .remixers import Remixer
from .sinks import ArtifactNames, Sink

PLUGINS_NAMESPACE = "newsmerger.plugins"
PLUGIN_ENTRY_POINT = "__newsmerger_plugin__"
# register()'s own parameters: options with these names would collide with them.
RESERVED_OPTIONS = ("self", "name")

_USE_PICKLE_DATA = os.environ.get("NEWSMERGER_PICKLE_CACHE", "0").lower() not in (
    "0",
    "false",
    "",
)


class UnsupportedProviderError(ValueError):
    """The provider cannot perform the requested operation."""


class LockedError(RuntimeError):
    """Another newsmerger command holds the write lock."""


class Application:
    def __init__(self, config: Config, *, create_schema: bool = True) -> None:
        self.config = config
        plugins = load_plugins(config.plugins)
        self._providers: dict[str, Provider] = objects_by_name(plugins, Provider)
        self._processors: dict[str, Processor] = objects_by_name(plugins, Processor)
        self._remixers: dict[str, Remixer] = objects_by_name(plugins, Remixer)
        self._sinks: dict[str, Sink] = objects_by_name(plugins, Sink)
        for source in config.sources:
            if source.provider not in self._providers:
                raise ConfigError(
                    f"source '{source.id}': provider '{source.provider}' is not loaded"
                )

        self._db = Database(
            config.db.uri, config.db.content_dir, create_schema=create_schema
        )
        self._cache = UserCache(
            app=PACKAGE_NAME,
            expiration_time=config.cache.expiration,
            base_dir=config.cache.base_dir,
        )
        self._fetcher = HTTPClient(cache=self._cache)
        self._lock_file: IO[str] | None = None

    @classmethod
    def from_config_file(
        cls, config_path: Path | None, *, create_schema: bool = True
    ) -> Self:
        """Build an Application from a config file, or from defaults when None."""
        config = Config.from_file(config_path) if config_path else Config()
        return cls(config, create_schema=create_schema)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        """Drop expired cache entries, then release the cache, the database
        and the write lock."""
        # UserCache never prunes on its own; once per run keeps it bounded.
        self._cache.prune()
        self._cache.close()
        self._db.close()
        if self._lock_file is not None:
            self._lock_file.close()
            self._lock_file = None

    def lock(self) -> None:
        """Take the write lock (see `write_lock`) until `close()`. Every
        command that writes takes it, so writers never overlap."""
        self._lock_file = write_lock(self.config.db.uri)

    @property
    def sources(self) -> list[SourceData]:
        return self.config.sources

    # --- Import ------------------------------------------------------------

    def import_source(self, source_id: str) -> list[SourceItem]:
        """Fetch every item of a configured source and store it."""
        source = self.config.get_source(source_id)
        pickle_path = Path(f"{source.id}.pkl")

        if _USE_PICKLE_DATA and pickle_path.exists():
            with pickle_path.open("rb") as fh:
                items = pickle.load(fh)
        else:
            provider = self._providers[source.provider]
            items = [
                SourceItem.from_data(source, item_data)
                for item_data in provider.retrieve_items(source, self._fetcher)
            ]
            if _USE_PICKLE_DATA:
                with pickle_path.open("wb") as fh:
                    pickle.dump(items, fh)

        self._db.upsert_source_items(items)
        return items

    def import_url(self, source_id: str, url: str) -> SourceItem:
        """Fetch one item URL into a configured source, with its provider."""
        source = self.config.get_source(source_id)
        provider = self._providers[source.provider]
        if not isinstance(provider, URLProvider):
            raise UnsupportedProviderError(
                f"provider '{source.provider}' does not support URL imports"
            )

        item = SourceItem.from_data(source, provider.retrieve_item(url, self._fetcher))
        self._db.upsert_source_items([item])
        return item

    # --- Enrich ------------------------------------------------------------

    def run_processor(
        self, name: str, *, scope: ProcessingScope | None = None, force: bool = False
    ) -> RunSummary:
        """Run one loaded processor. `force` also resets attempts."""
        processor = lookup(self._processors, name, "processor")
        return processor.enrich(self._db, scope=scope, force=force)

    def enrich(
        self, *, scope: ProcessingScope | None = None, force: bool = False
    ) -> dict[str, RunSummary]:
        """Run every loaded processor, in configuration order."""
        return {
            name: self.run_processor(name, scope=scope, force=force)
            for name in self._processors
        }

    # --- Remix -------------------------------------------------------------

    def run_remixer(
        self, name: str, *, scope: ProcessingScope | None = None
    ) -> list[str]:
        """Run one loaded remixer; return the names of the artifacts saved."""
        remixer = lookup(self._remixers, name, "remixer")
        return remixer.remix(self._db, scope=scope)

    def remix(self, *, scope: ProcessingScope | None = None) -> dict[str, list[str]]:
        """Run every loaded remixer, in configuration order."""
        return {name: self.run_remixer(name, scope=scope) for name in self._remixers}

    # --- Deliver -----------------------------------------------------------

    def run_sink(
        self,
        name: str,
        *,
        scope: ProcessingScope | None = None,
        artifacts: ArtifactNames = (),
        requeue: bool = False,
        force: bool = False,
    ) -> RunSummary:
        """Run one loaded sink. `force` sends the selected subjects now and
        needs an explicit selection."""
        sink = lookup(self._sinks, name, "sink")
        return sink.deliver(
            self._db, scope=scope, artifacts=artifacts, requeue=requeue, force=force
        )

    def deliver(
        self,
        *,
        scope: ProcessingScope | None = None,
        artifacts: ArtifactNames = (),
        requeue: bool = False,
    ) -> dict[str, RunSummary]:
        """Run every loaded sink, in configuration order."""
        return {
            name: self.run_sink(name, scope=scope, artifacts=artifacts, requeue=requeue)
            for name in self._sinks
        }

    def resolve_deliveries(
        self,
        sink: str,
        status: DeliveryStatus,
        *,
        scope: ProcessingScope | None = None,
        artifact_names: ArtifactNames | None = None,
    ) -> int:
        """Settle the sink's interrupted (`sending`) rows in the selection as
        `done` (it was delivered) or `queued` (deliver it again); return how
        many. The sink does not need to be loaded."""
        if status not in (DeliveryStatus.DONE, DeliveryStatus.QUEUED):
            raise ValueError(f"cannot resolve a delivery as '{status}'")
        rows = self._db.find_deliveries(
            scope,
            sink=sink,
            status=DeliveryStatus.SENDING,
            artifact_names=artifact_names,
        )
        for delivery in rows:
            delivery.status = status
            delivery.attempts = 0
            self._db.save_delivery(delivery)
        return len(rows)

    # --- Queries -----------------------------------------------------------

    def get_items(self, scope: ProcessingScope | None = None) -> list[SourceItem]:
        """Items in scope, oldest first, without their content."""
        return self._db.get_items(scope)

    def get_content(self, item: SourceItem) -> bytes:
        return self._db.get_content(item)

    def get_annotations(
        self,
        item: SourceItem,
        *,
        processor: str | None = None,
        key: str | None = None,
    ) -> dict[str, dict[str, Any]]:
        """An item's annotations as `{processor: {key: value}}`; `{}` if none."""
        return self._db.get_annotations(item, processor=processor, key=key)

    def get_annotation_keys(
        self, items: Iterable[SourceItem]
    ) -> dict[int, list[tuple[int, str, str]]]:
        """The `(id, processor, key)` of each item's annotations, by item id."""
        return self._db.get_annotation_keys(items)

    def find_annotations(
        self,
        scope: ProcessingScope | None = None,
        *,
        processor: str | None = None,
        key: str | None = None,
        annotation_ids: Iterable[int] | None = None,
    ) -> list[Annotation]:
        """Annotations of the items in scope, with their values; filters
        combine and `limit` counts annotations."""
        return self._db.find_annotations(
            scope, processor=processor, key=key, annotation_ids=annotation_ids
        )

    def get_annotation_values(
        self, items: Iterable[SourceItem], *, processor: str, key: str
    ) -> dict[ItemKey, Any]:
        """One annotation's value per item; items without it are absent."""
        return self._db.get_annotation_values(items, processor=processor, key=key)

    def get_artifact(self, remixer: str, name: str) -> Artifact | None:
        """The artifact with its content, or None if it does not exist."""
        return self._db.get_artifact(remixer, name)

    def list_artifacts(
        self,
        remixer: str | None = None,
        *,
        names: Iterable[tuple[str, str]] | None = None,
        limit: int | None = None,
    ) -> list[Artifact]:
        """Artifacts' metadata, by remixer and name; `content` is None.
        `names` keeps only these `(remixer, name)` pairs."""
        return self._db.list_artifacts(remixer, names=names, limit=limit)

    def find_deliveries(
        self,
        scope: ProcessingScope | None = None,
        *,
        sink: str | None = None,
        status: DeliveryStatus | None = None,
        artifact_names: ArtifactNames | None = None,
    ) -> list[Delivery]:
        """Ledger rows in creation order; item filters keep item rows,
        `artifact_names` artifact rows, and `limit` counts rows."""
        return self._db.find_deliveries(
            scope, sink=sink, status=status, artifact_names=artifact_names
        )

    def delete_annotations(
        self, *, processor: str | None = None, item: SourceItem | None = None
    ) -> int:
        """Delete annotations by processor, by item, or both, with their
        processing state: the items become pending again with fresh attempts.

        Returns the number of annotations deleted.
        """
        return self._db.delete_annotations(processor=processor, item=item)


def write_lock(database_url: str) -> IO[str] | None:
    """Take the exclusive write lock, a file next to the database, held
    until the returned file is closed. Raise `LockedError` at once if another
    process holds it. In-memory databases are private to their process and
    need none (None).
    """
    url = make_url(database_url)
    if url.get_backend_name() != "sqlite" or url.database in (None, "", ":memory:"):
        return None
    lock_path = Path(f"{url.database}.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_file = lock_path.open("a")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock_file.close()
        raise LockedError(
            f"another newsmerger command is using the database ({lock_path})"
        ) from None
    return lock_file


def load_plugins(sections: dict[str, dict[str, Any] | None]) -> Register:
    """Register every plugin with a config section, in configuration order,
    passing it the services provided by the plugins before it and its section
    as keyword arguments."""
    plugins = Register(PLUGINS_NAMESPACE, PLUGIN_ENTRY_POINT)
    services = Services()
    for name, section in sections.items():
        options = section or {}
        for option in RESERVED_OPTIONS:
            if option in options:
                raise ConfigError(
                    f"plugins.{name}: '{option}' is a reserved option name"
                )
        try:
            plugins.register(name, services, **options)
        except EntryPointError as e:
            if isinstance(e.__cause__, pydantic.ValidationError):
                raise plugin_options_error(name, e.__cause__) from e
            raise
        services.llms = objects_by_name(plugins, LLM)
    return plugins


def objects_by_name[T](plugins: Register, protocol: type[T]) -> dict[str, T]:
    """The loaded objects implementing `protocol`, by object name, in
    configuration order. Names must be unique per protocol."""
    objects: dict[str, T] = {}
    owners: dict[str, str] = {}
    for plugin, name, obj in plugins.get_by_protocol(protocol):
        if name in owners:
            raise ConfigError(
                f"{protocol.__name__} '{name}' is provided by both plugin "
                f"'{owners[name]}' and plugin '{plugin}'"
            )
        objects[name] = obj
        owners[name] = plugin
    if failed := plugins.get_conformance_warnings():
        raise ProtocolConformanceError(
            ", ".join(
                f"'{entry.name}' is not a {entry.protocol.__name__}" for entry in failed
            )
        )
    return objects


def lookup[T](objects: dict[str, T], name: str, kind: str) -> T:
    try:
        return objects[name]
    except KeyError:
        raise ConfigError(f"{kind} '{name}' is not loaded") from None
