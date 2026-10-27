"""Application: the single entry point for front ends (CLI, scripts) and
external tools. It owns the wiring (config, HTTP cache, database, plugins),
runs the four phases (import, process, remix, deliver) and answers queries.
"""

from __future__ import annotations

import dataclasses
import fcntl
import logging
import re
from collections.abc import Iterable
from pathlib import Path
from types import TracebackType
from typing import IO, Any, Self

import pydantic
from foundation.cache import UserCache
from foundation.plugin import (
    EntryPointError,
    PluginError,
    PluginNotFoundError,
    ProtocolConformanceError,
    Register,
)
from sqlalchemy import make_url

from .config import (
    DEFAULT_WORKFLOW,
    Config,
    ConfigError,
    Workflow,
    options_error,
)
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
from .providers import Provider
from .remixers import Remixer
from .sinks import ArtifactNames, Sink

PLUGINS_NAMESPACE = "newsmerger.plugins"
PLUGIN_ENTRY_POINT = "__newsmerger_plugin__"
# register()'s own parameters: options with these names would collide with them.
RESERVED_OPTIONS = ("self", "name")
# Annotation keys: lowercase words, optionally in `/`-separated parts.
KEY_PATTERN = re.compile(r"[a-z0-9_]+(/[a-z0-9_]+)*")

LOGGER = logging.getLogger(__name__)


class LockedError(RuntimeError):
    """Another newsmerger command holds the write lock."""


@dataclasses.dataclass(frozen=True, slots=True)
class Run:
    """One configured use of a plugin object: in which workflow, by which
    object, with its options validated at startup."""

    workflow: Workflow
    name: str  # the object's
    options: pydantic.BaseModel | None = None


class Application:
    def __init__(self, config: Config, *, create_schema: bool = True) -> None:
        self.config = config
        plugins = load_plugins(config.plugins, referenced_plugins(config))
        self._providers: dict[str, Provider] = objects_by_name(plugins, Provider)
        self._processors: dict[str, Processor] = objects_by_name(plugins, Processor)
        self._remixers: dict[str, Remixer] = objects_by_name(plugins, Remixer)
        self._sinks: dict[str, Sink] = objects_by_name(plugins, Sink)
        self._source_options = source_options(config.sources, self._providers)
        workflows = config.all_workflows()
        self._workflows = {workflow.name: workflow for workflow in workflows}
        self._process = process_runs(workflows, self._processors)
        self._remix = remix_runs(workflows, self._remixers)
        self._deliveries = delivery_runs(workflows, self._sinks)

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
    def workflows(self) -> list[str]:
        """Workflow names, `default` first."""
        return list(self._workflows)

    def workflow(self, name: str = DEFAULT_WORKFLOW) -> Workflow:
        return lookup(self._workflows, name, "workflow")

    def sources(self, workflow: str = DEFAULT_WORKFLOW) -> list[SourceData]:
        """The workflow's sources, in configuration order."""
        ids = set(self.workflow(workflow).sources)
        return [source for source in self.config.sources if source.id in ids]

    @property
    def processors(self) -> list[str]:
        """Loaded processor names, in configuration order."""
        return list(self._processors)

    def process_keys(
        self, processor: str | None = None, *, workflow: str = DEFAULT_WORKFLOW
    ) -> list[str]:
        """The keys of the workflow's `process:` runs, in order; with
        `processor`, only its runs."""
        self.workflow(workflow)
        if processor is not None:
            lookup(self._processors, processor, "processor")
        return [
            key
            for (name, key), run in self._process.items()
            if name == workflow and processor in (None, run.name)
        ]

    def remix_keys(self, workflow: str = DEFAULT_WORKFLOW) -> list[str]:
        """The keys of the workflow's `remix:` entries, in order."""
        return [entry.name for entry in self.workflow(workflow).remix]

    def delivery_keys(self, workflow: str = DEFAULT_WORKFLOW) -> list[str]:
        """The keys of the workflow's `deliver:` entries, in order."""
        return [entry.name for entry in self.workflow(workflow).deliver]

    # --- Import ------------------------------------------------------------

    def import_source(self, source_id: str) -> list[SourceItem]:
        """Fetch every item of a configured source and store it."""
        source = self.config.get_source(source_id)
        provider = self._providers[source.provider]
        items = []
        for item_data in provider.retrieve_items(
            source, self._fetcher, self._source_options[source.id]
        ):
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
        """Run the workflow's `process:` entry that writes `key` on its
        sources. `force` also resets attempts."""
        if (run := self._process.get((workflow, key))) is None:
            raise ConfigError(
                f"no process entry of workflow '{workflow}' writes the key '{key}'"
            )
        return self._processors[run.name].process(
            self._db,
            key=key,
            options=run.options,
            scope=workflow_scope(run.workflow, scope),
            force=force,
        )

    # --- Remix -------------------------------------------------------------

    def run_remix(self, key: str, *, scope: ProcessingScope | None = None) -> list[str]:
        """Run the `remix:` entry `key` on its workflow's sources; return the
        names of the artifacts saved under `key`."""
        if (run := self._remix.get(key)) is None:
            raise ConfigError(f"no workflow has a remix entry '{key}'")
        return self._remixers[run.name].remix(
            self._db,
            key=key,
            options=run.options,
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
        """Run the workflow's `deliver:` entry `key` on its sources. `force`
        sends the selected subjects now and needs an explicit selection."""
        ledger_key = self.workflow(workflow).ledger_key(key)
        if (run := self._deliveries.get(ledger_key)) is None:
            raise ConfigError(f"workflow '{workflow}' has no delivery '{key}'")
        return self._sinks[run.name].deliver(
            self._db,
            key=ledger_key,
            options=run.options,
            scope=workflow_scope(run.workflow, scope),
            artifacts=artifacts,
            requeue=requeue,
            force=force,
        )

    def resolve_deliveries(
        self,
        sink: str,
        status: DeliveryStatus,
        *,
        scope: ProcessingScope | None = None,
        artifact_names: ArtifactNames | None = None,
    ) -> int:
        """Settle the interrupted (`sending`) rows of the ledger key `sink`
        in the selection as `done` (it was delivered) or `queued` (deliver it
        again); return how many. Its entry does not need to be configured."""
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

    def delete_annotations(
        self, *, processor: str | None = None, item_id: int | None = None
    ) -> int:
        """Delete annotations by processor, by item, or both, with their
        processing state: the items become pending again with fresh attempts.

        Returns the number of annotations deleted.
        """
        return self._db.delete_annotations(processor=processor, item_id=item_id)

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
            f"another newsmerger command is using the database ({lock_path})"
        ) from None
    return lock_file


def workflow_scope(
    workflow: Workflow, scope: ProcessingScope | None
) -> ProcessingScope:
    """`scope` restricted to the workflow's sources."""
    return dataclasses.replace(
        scope or ProcessingScope(), sources=tuple(workflow.sources)
    )


def entry_location(workflow: Workflow, section: str, index: int) -> str:
    """Where a workflow's entry is in the config, for error messages."""
    if workflow.name == DEFAULT_WORKFLOW:
        return f"{section}.{index}"
    return f"workflows.{workflow.name}.{section}.{index}"


def referenced_plugins(config: Config) -> list[tuple[str, type, str]]:
    """The `(name, protocol, config location)` of every object the sources
    and the workflows' entries use, in order."""
    referenced = [
        (source.provider, Provider, f"sources.{source.id}.provider")
        for source in config.sources
    ]
    for workflow in config.all_workflows():
        for index, entry in enumerate(workflow.process):
            location = entry_location(workflow, "process", index)
            referenced.append((entry.processor, Processor, f"{location}.processor"))
        for index, remix in enumerate(workflow.remix):
            location = entry_location(workflow, "remix", index)
            referenced.append((remix.remixer, Remixer, f"{location}.remixer"))
        for index, delivery in enumerate(workflow.deliver):
            location = entry_location(workflow, "deliver", index)
            referenced.append((delivery.sink, Sink, f"{location}.sink"))
    return referenced


def load_plugins(
    sections: dict[str, dict[str, Any] | None],
    referenced: list[tuple[str, type, str]],
) -> Register:
    """Register every plugin with a config section, in configuration order,
    passing it the services provided by the plugins before it and its section
    as keyword arguments. Then, for each `referenced` object no plugin
    provides, register the plugin of the same name with its defaults."""
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
                raise options_error(f"plugins.{name}", e.__cause__) from e
            raise
        services.llms = objects_by_name(plugins, LLM)
    loaded = set(sections)
    for name, protocol, location in referenced:
        provided = {
            object_name for _, object_name, _ in plugins.get_by_protocol(protocol)
        }
        if name in provided or name in loaded:
            continue
        try:
            plugins.register(name, services)
        except PluginNotFoundError:
            raise ConfigError(f"{location}: no plugin provides '{name}'") from None
        loaded.add(name)
    return plugins


def source_options(
    sources: list[SourceData], providers: dict[str, Provider]
) -> dict[str, pydantic.BaseModel]:
    """Each source's provider options, by source id. Reject, at startup
    rather than on import, sources whose provider is not loaded or does not
    take their options."""
    options = {}
    for source in sources:
        if (provider := providers.get(source.provider)) is None:
            raise ConfigError(
                f"source '{source.id}': provider '{source.provider}' is not loaded"
            )
        try:
            options[source.id] = provider.use_options(source.options)
        except pydantic.ValidationError as e:
            raise options_error(f"sources.{source.id}.options", e) from None
    return options


def process_runs(
    workflows: list[Workflow], processors: dict[str, Processor]
) -> dict[tuple[str, str], Run]:
    """Every workflow's `process:` entries by `(workflow, key)`, in order.
    Reject, at startup, entries whose processor is not loaded or does not
    take their options, malformed keys, and keys written twice in a workflow
    or differently by workflows that share a source: annotations are per
    item, so workflows that share a source may write the same key only with
    the same processor and options, the same run."""
    runs: dict[tuple[str, str], Run] = {}
    for workflow in workflows:
        for index, entry in enumerate(workflow.process):
            location = entry_location(workflow, "process", index)
            if (processor := processors.get(entry.processor)) is None:
                raise ConfigError(
                    f"{location}: processor '{entry.processor}' is not loaded"
                )
            try:
                options = processor.use_options(entry.options)
            except pydantic.ValidationError as e:
                raise options_error(f"{location}.options", e) from None
            key = entry.key or processor.output_key(options)
            if not KEY_PATTERN.fullmatch(key):
                raise ConfigError(f"{location}: invalid key '{key}'")
            for (other, other_key), run in runs.items():
                if other_key != key:
                    continue
                if other == workflow.name:
                    raise ConfigError(
                        f"{location}: key '{key}' is written by another entry"
                        f" (workflow '{other}')"
                    )
                same_run = run.name == entry.processor and run.options == options
                if set(workflow.sources) & set(run.workflow.sources) and not same_run:
                    raise ConfigError(
                        f"{location}: key '{key}' is written differently by"
                        f" another entry (workflow '{other}') on the same"
                        " sources; give one a `key`"
                    )
            runs[workflow.name, key] = Run(workflow, entry.processor, options)
    return runs


def remix_runs(
    workflows: list[Workflow], remixers: dict[str, Remixer]
) -> dict[str, Run]:
    """Every workflow's `remix:` entries by key, in order. Reject, at
    startup, entries whose remixer is not loaded or does not take their
    options, and keys used twice, in any workflow: artifacts are shared."""
    runs: dict[str, Run] = {}
    for workflow in workflows:
        for index, entry in enumerate(workflow.remix):
            location = entry_location(workflow, "remix", index)
            if (remixer := remixers.get(entry.remixer)) is None:
                raise ConfigError(
                    f"{location}: remixer '{entry.remixer}' is not loaded"
                )
            try:
                options = remixer.use_options(entry.options)
            except pydantic.ValidationError as e:
                raise options_error(f"{location}.options", e) from None
            if entry.name in runs:
                raise ConfigError(
                    f"{location}: key '{entry.name}' is used by another remix"
                    " entry; give one a `key`"
                )
            runs[entry.name] = Run(workflow, entry.remixer, options)
    return runs


def delivery_runs(workflows: list[Workflow], sinks: dict[str, Sink]) -> dict[str, Run]:
    """Every workflow's `deliver:` entries by ledger key, in order. Reject,
    at startup, entries whose sink is not loaded or does not take their
    options."""
    runs: dict[str, Run] = {}
    for workflow in workflows:
        for index, entry in enumerate(workflow.deliver):
            location = entry_location(workflow, "deliver", index)
            if (sink := sinks.get(entry.sink)) is None:
                raise ConfigError(f"{location}: sink '{entry.sink}' is not loaded")
            try:
                options = sink.use_options(entry.options)
            except pydantic.ValidationError as e:
                raise options_error(f"{location}.options", e) from None
            runs[workflow.ledger_key(entry.name)] = Run(workflow, entry.sink, options)
    return runs


def objects_by_name[T](plugins: Register, protocol: type[T]) -> dict[str, T]:
    """The loaded objects implementing `protocol`, by object name, in
    configuration order. Names must be unique per protocol."""
    objects: dict[str, T] = {}
    owners: dict[str, str] = {}
    for plugin, name, obj in plugins.get_by_protocol(protocol):
        if isinstance(obj, type):
            raise PluginError(
                f"plugin '{plugin}' returned the class of {protocol.__name__} "
                f"'{name}', not an instance"
            )
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
