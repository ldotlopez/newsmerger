"""Application: the single entry point for front ends (CLI, scripts) and
external tools. It owns the wiring (config, HTTP cache, database, plugins),
runs the four phases (import, process, remix, deliver) and answers queries.
"""

from __future__ import annotations

import dataclasses
import fcntl
import logging
from collections.abc import Iterable
from pathlib import Path
from types import TracebackType
from typing import IO, Any, Self

from foundation.cache import UserCache
from sqlalchemy import make_url

from .catalog import Catalog, Profile
from .config import DEFAULT_WORKFLOW, Config, ConfigError, Workflow
from .consts import PACKAGE_NAME
from .db import Database, DeliveryStatus
from .httpclient import HTTPClient
from .llms import LLM
from .models import (
    Annotation,
    Artifact,
    Delivery,
    ItemKey,
    LazySourceItemData,
    ProcessingScope,
    SourceData,
    SourceItem,
)
from .plugins import ClassRegister, Services
from .processors import RunSummary
from .sinks import ArtifactNames

PLUGINS_NAMESPACE = "newstool.plugins"
PLUGIN_ENTRY_POINT = "__newstool_plugin__"

LOGGER = logging.getLogger(__name__)


class LockedError(RuntimeError):
    """Another newstool command holds the write lock."""


class Application:
    def __init__(self, config: Config, *, create_schema: bool = True) -> None:
        self.config = config
        register = ClassRegister(PLUGINS_NAMESPACE, PLUGIN_ENTRY_POINT)
        register.register_found()
        self._catalog = Catalog(config, register)
        self._workflows = {
            workflow.name: workflow for workflow in config.all_workflows()
        }
        self._services = Services(llm_factory=self._llm)
        # Each profile's object, built when a run first needs it.
        self._objects: dict[Profile, Any] = {}

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

    def _object(self, profile: Profile) -> Any:
        """The profile's object, built on first use."""
        if profile not in self._objects:
            self._objects[profile] = profile.cls(profile.options, self._services)
        return self._objects[profile]

    def _llm(self, name: str | None) -> LLM:
        """The LLM `name` refers to (see `Services`)."""
        return self._object(self._catalog.llm_profile(name))

    @property
    def workflows(self) -> list[str]:
        """Workflow names, `default` first."""
        return list(self._workflows)

    def workflow(self, name: str = DEFAULT_WORKFLOW) -> Workflow:
        return lookup(self._workflows, name, "workflow")

    def sources(self, workflow: str = DEFAULT_WORKFLOW) -> list[SourceData]:
        """The workflow's sources, in configuration order."""
        ids = set(self.workflow(workflow).sources)
        return [source for source in self.config.sources if source.id in ids]

    def process_keys(
        self, processor: str | None = None, *, workflow: str = DEFAULT_WORKFLOW
    ) -> list[str]:
        """The keys of the workflow's process runs, in order; with
        `processor`, only its runs."""
        self.workflow(workflow)
        if processor is not None and processor not in self._catalog.processor_names:
            raise ConfigError(f"processor '{processor}' does not exist")
        return [
            key
            for (name, key), run in self._catalog.process.items()
            if name == workflow and processor in (None, run.profile.name)
        ]

    def remix_keys(self, workflow: str = DEFAULT_WORKFLOW) -> list[str]:
        """The keys of the workflow's remix runs, in order."""
        self.workflow(workflow)
        return [
            key
            for key, run in self._catalog.remix.items()
            if run.workflow.name == workflow
        ]

    def delivery_keys(self, workflow: str = DEFAULT_WORKFLOW) -> list[str]:
        """The keys of the workflow's delivery runs, in order."""
        self.workflow(workflow)
        return [
            run.key
            for run in self._catalog.deliveries.values()
            if run.workflow.name == workflow
        ]

    # --- Import ------------------------------------------------------------

    def import_source(self, source_id: str) -> list[SourceItem]:
        """Fetch every item of a configured source and store it, except lazy
        items already stored."""
        source = self.config.get_source(source_id)
        provider = self._object(self._catalog.sources[source.id])
        stored_uids = self._db.get_item_uids(source.id)
        items = []
        for item_data in provider.retrieve_items(source, self._fetcher):
            if isinstance(item_data, LazySourceItemData):
                if item_data.uid in stored_uids:
                    continue
                item_data = item_data.load()
            item = SourceItem.from_data(source, item_data)
            LOGGER.info(f"{source.id}: {item.uri}")
            items.append(item)

        self._db.upsert_source_items(items)
        return items

    # --- Process -----------------------------------------------------------

    def run_process(
        self,
        key: str,
        *,
        workflow: str = DEFAULT_WORKFLOW,
        scope: ProcessingScope | None = None,
        force: bool = False,
    ) -> RunSummary:
        """Run the workflow's process run that writes `key` on its
        sources. `force` also resets attempts."""
        if (run := self._catalog.process.get((workflow, key))) is None:
            raise ConfigError(
                f"no process run of workflow '{workflow}' writes the key '{key}'"
            )
        return self._object(run.profile).process(
            self._db,
            key=key,
            scope=workflow_scope(run.workflow, scope),
            force=force,
        )

    # --- Remix -------------------------------------------------------------

    def run_remix(self, key: str, *, scope: ProcessingScope | None = None) -> list[str]:
        """Run the remix run `key` on its workflow's sources; return the
        names of the artifacts saved under `key`."""
        if (run := self._catalog.remix.get(key)) is None:
            raise ConfigError(f"no workflow has a remix run '{key}'")
        return self._object(run.profile).remix(
            self._db,
            key=key,
            scope=workflow_scope(run.workflow, scope),
        )

    # --- Deliver -----------------------------------------------------------

    def run_delivery(
        self,
        key: str,
        *,
        workflow: str = DEFAULT_WORKFLOW,
        scope: ProcessingScope | None = None,
        artifacts: ArtifactNames = (),
        requeue: bool = False,
        force: bool = False,
    ) -> RunSummary:
        """Run the workflow's delivery run `key` on its sources. `force`
        sends the selected subjects now and needs an explicit selection."""
        ledger_key = self.workflow(workflow).ledger_key(key)
        if (run := self._catalog.deliveries.get(ledger_key)) is None:
            raise ConfigError(f"workflow '{workflow}' has no delivery '{key}'")
        return self._object(run.profile).deliver(
            self._db,
            key=ledger_key,
            scope=workflow_scope(run.workflow, scope),
            artifacts=artifacts,
            requeue=requeue,
            force=force,
        )

    # --- Queries -----------------------------------------------------------

    def get_items(
        self, scope: ProcessingScope | None = None, *, sort: str = "published"
    ) -> list[SourceItem]:
        """Items in scope by a `db.ITEM_SORTS` key, ascending, without their
        content."""
        return self._db.get_items(scope, sort=sort)

    def get_content(self, item: SourceItem) -> bytes:
        return self._db.get_content(item)

    def get_stored_content(self, sha256: str) -> bytes:
        return self._db.get_stored_content(sha256)

    def get_annotations(
        self, item: SourceItem, *, key: str | None = None
    ) -> dict[str, Any]:
        """An item's annotations as `{key: value}`; `{}` if none."""
        return self._db.get_annotations(item, key=key)

    def get_annotation_keys(
        self, item_ids: Iterable[int]
    ) -> dict[int, list[tuple[int, str, str]]]:
        """The `(id, processor, key)` of each item's annotations, by item id."""
        return self._db.get_annotation_keys(item_ids)

    def find_annotations(
        self,
        scope: ProcessingScope | None = None,
        *,
        processor: str | None = None,
        key: str | None = None,
        annotation_ids: Iterable[int] | None = None,
        sort: str = "item",
    ) -> list[Annotation]:
        """Annotations of the items in scope, with their values, by a
        `db.ANNOTATION_SORTS` key; filters combine and `limit` counts
        annotations."""
        return self._db.find_annotations(
            scope,
            processor=processor,
            key=key,
            annotation_ids=annotation_ids,
            sort=sort,
        )

    def get_annotation_values(
        self, items: Iterable[SourceItem], *, key: str
    ) -> dict[ItemKey, Any]:
        """One annotation's value per item; items without it are absent."""
        return self._db.get_annotation_values(items, key=key)

    def get_artifact(self, remixer: str, name: str) -> Artifact | None:
        """The artifact with its content, or None if it does not exist."""
        return self._db.get_artifact(remixer, name)

    def list_artifacts(
        self,
        remixer: str | None = None,
        *,
        names: Iterable[tuple[str, str]] | None = None,
        limit: int | None = None,
        sort: str = "id",
    ) -> list[Artifact]:
        """Artifacts' metadata by a `db.ARTIFACT_SORTS` key; `content` is
        None. `names` keeps only these `(remixer, name)` pairs."""
        return self._db.list_artifacts(remixer, names=names, limit=limit, sort=sort)

    def find_deliveries(
        self,
        scope: ProcessingScope | None = None,
        *,
        sink: str | None = None,
        status: DeliveryStatus | None = None,
        artifact_names: ArtifactNames | None = None,
        sort: str = "id",
    ) -> list[Delivery]:
        """Ledger rows by a `db.DELIVERY_SORTS` key; item filters keep item
        rows, `artifact_names` artifact rows, and `limit` counts rows."""
        return self._db.find_deliveries(
            scope,
            sink=sink,
            status=status,
            artifact_names=artifact_names,
            sort=sort,
        )

    def delete_annotations(self, annotation_ids: Iterable[int]) -> int:
        """Delete these annotations with the processing state of their
        (item, key): the items become pending again with fresh attempts.

        Returns the number of annotations deleted.
        """
        return self._db.delete_annotations(annotation_ids)

    def delete_deliveries(self, delivery_ids: Iterable[int]) -> int:
        """Delete these ledger rows; return how many. Their subjects are
        queued again if their delivery's lookback still covers them."""
        return self._db.delete_deliveries(delivery_ids)

    def delete_items(self, item_ids: Iterable[int]) -> int:
        """Delete items with their state, annotations and deliveries; return
        how many. One still in its source's index comes back on the next
        import, with a new id."""
        return self._db.delete_items(item_ids)

    def delete_artifacts(self, names: Iterable[tuple[str, str]]) -> int:
        """Delete the `(remixer, name)` artifacts with their deliveries;
        return how many. A remixer that runs again rebuilds them."""
        return self._db.delete_artifacts(names)


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
            f"another newstool command is using the database ({lock_path})"
        ) from None
    return lock_file


def workflow_scope(
    workflow: Workflow, scope: ProcessingScope | None
) -> ProcessingScope:
    """`scope` restricted to the workflow's sources."""
    return dataclasses.replace(
        scope or ProcessingScope(), sources=tuple(workflow.sources)
    )


def lookup[T](objects: dict[str, T], name: str, kind: str) -> T:
    try:
        return objects[name]
    except KeyError:
        raise ConfigError(f"{kind} '{name}' is not configured") from None
