"""Application: the single entry point for front ends (CLI, scripts) and
external tools. It owns the wiring (config, HTTP cache, database, plugins),
runs the three phases (import, enrich, remix) and answers queries.
"""

from __future__ import annotations

import os
import pickle
from collections.abc import Iterable
from pathlib import Path
from types import TracebackType
from typing import Any, Self

from foundation.cache import UserCache
from foundation.plugin import ClassLoader

from .config import Config
from .consts import PACKAGE_NAME
from .db import Database
from .httpclient import HTTPClient
from .models import Artifact, ItemKey, ProcessingScope, SourceData, SourceItem
from .processors import BaseProcessor, RunSummary
from .providers import BaseProvider, IndexSiteProvider
from .remixers import BaseRemixer

PROVIDERS = ClassLoader("newsmerger.providers", "Provider")
PROCESSORS = ClassLoader("newsmerger.processors", "Processor")
REMIXERS = ClassLoader("newsmerger.remixers", "Remixer")

_USE_PICKLE_DATA = os.environ.get("NEWSMERGER_PICKLE_CACHE", "0").lower() not in (
    "0",
    "false",
    "",
)


class UnsupportedProviderError(ValueError):
    """The provider cannot perform the requested operation."""


class Application:
    def __init__(self, config: Config, *, create_schema: bool = True) -> None:
        self.config = config
        self._db = Database(
            config.db.uri, config.db.content_dir, create_schema=create_schema
        )
        self._cache = UserCache(
            app=PACKAGE_NAME,
            expiration_time=config.cache.expiration,
            base_dir=config.cache.base_dir,
        )
        self._fetcher = HTTPClient(cache=self._cache)

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
        """Drop expired cache entries, then release the cache and database."""
        # UserCache never prunes on its own; once per run keeps it bounded.
        self._cache.prune()
        self._cache.close()
        self._db.close()

    @property
    def sources(self) -> list[SourceData]:
        return self.config.sources

    # --- Import ------------------------------------------------------------

    def _provider(self, source: SourceData) -> BaseProvider:
        return PROVIDERS.instantiate(source.provider, source, fetcher=self._fetcher)

    def import_source(self, source_id: str) -> list[SourceItem]:
        """Fetch every item of a configured source and store it."""
        source = self.config.get_source(source_id)
        pickle_path = Path(f"{source.id}.pkl")

        if _USE_PICKLE_DATA and pickle_path.exists():
            with pickle_path.open("rb") as fh:
                items = pickle.load(fh)
        else:
            items = [
                SourceItem.from_data(source, item_data)
                for item_data in self._provider(source).retrieve_items()
            ]
            if _USE_PICKLE_DATA:
                with pickle_path.open("wb") as fh:
                    pickle.dump(items, fh)

        self._db.upsert_source_items(items)
        return items

    def import_url(self, source_id: str, url: str) -> SourceItem:
        """Fetch one item URL into a configured source, with its provider."""
        source = self.config.get_source(source_id)
        provider = self._provider(source)
        if not isinstance(provider, IndexSiteProvider):
            raise UnsupportedProviderError(
                f"provider '{source.provider}' does not support URL imports"
            )

        item = SourceItem.from_data(source, provider.retrieve_item(url))
        self._db.upsert_source_items([item])
        return item

    # --- Enrich ------------------------------------------------------------

    def run_processor(
        self, name: str, *, scope: ProcessingScope | None = None, force: bool = False
    ) -> RunSummary:
        """Run one configured processor. `force` also resets attempts."""
        params: dict[str, Any] = self.config.get_processor(name).params
        processor: BaseProcessor = PROCESSORS.instantiate(name, self._db, **params)
        return processor.run(scope=scope, force=force)

    def enrich(
        self, *, scope: ProcessingScope | None = None, force: bool = False
    ) -> dict[str, RunSummary]:
        """Run every configured processor, in configuration order."""
        return {
            plugin.name: self.run_processor(plugin.name, scope=scope, force=force)
            for plugin in self.config.processors
        }

    # --- Remix -------------------------------------------------------------

    def run_remixer(
        self, name: str, *, scope: ProcessingScope | None = None
    ) -> list[str]:
        """Run one configured remixer; return the names of the artifacts saved."""
        params: dict[str, Any] = self.config.get_remixer(name).params
        remixer: BaseRemixer = REMIXERS.instantiate(name, self._db, **params)
        return remixer.run(scope=scope)

    def remix(self, *, scope: ProcessingScope | None = None) -> dict[str, list[str]]:
        """Run every configured remixer, in configuration order."""
        return {
            plugin.name: self.run_remixer(plugin.name, scope=scope)
            for plugin in self.config.remixers
        }

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

    def get_annotation_values(
        self, items: Iterable[SourceItem], *, processor: str, key: str
    ) -> dict[ItemKey, Any]:
        """One annotation's value per item; items without it are absent."""
        return self._db.get_annotation_values(items, processor=processor, key=key)

    def get_artifact(self, remixer: str, name: str) -> Artifact | None:
        """The artifact with its content, or None if it does not exist."""
        return self._db.get_artifact(remixer, name)

    def list_artifacts(self, remixer: str | None = None) -> list[Artifact]:
        """Artifacts' metadata, by remixer and name; `content` is None."""
        return self._db.list_artifacts(remixer)

    def delete_annotations(
        self, *, processor: str | None = None, item: SourceItem | None = None
    ) -> int:
        """Delete annotations by processor, by item, or both, with their
        processing state: the items become pending again with fresh attempts.

        Returns the number of annotations deleted.
        """
        return self._db.delete_annotations(processor=processor, item=item)
