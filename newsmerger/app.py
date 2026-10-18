"""Application core: wires config, HTTP cache, database, providers and
processors, and exposes the operations every front end (CLI, scripts) uses.

Reads go straight through `App.db`; this layer only owns the wiring and the
multi-step operations, so it does not re-wrap Database methods.
"""

from __future__ import annotations

import importlib
import logging
import os
import pickle
from pathlib import Path
from types import TracebackType
from typing import Self

from foundation.cache import UserCache

from .config import Config, PipelineConfig
from .consts import PACKAGE_NAME
from .db import Database, ProcessingScope
from .httpclient import HTTPClient
from .models import SourceData, SourceItem
from .processors import BaseProcessor
from .providers import BaseProvider, IndexSiteProvider

LOGGER = logging.getLogger(__name__)

_USE_PICKLE_DATA = os.environ.get("NEWSMERGER_PICKLE_CACHE", "0").lower() not in (
    "0",
    "false",
    "",
)


class UnsupportedProviderError(ValueError):
    """The provider cannot perform the requested operation."""


class PipelineError(Exception):
    """A pipeline step finished without producing output for the item."""


def provider_factory(source: SourceData, *args, **kwargs) -> BaseProvider:
    """Instantiate the Provider of the module named by `source.provider`."""
    try:
        m = importlib.import_module(f"newsmerger.providers.{source.provider}")
    except ModuleNotFoundError:
        LOGGER.error(f"provider {source.provider} not found")
        raise

    return m.Provider(source, *args, **kwargs)


def processor_factory(name: str, db: Database, **params) -> BaseProcessor:
    try:
        m = importlib.import_module(f"newsmerger.processors.{name}")
    except ModuleNotFoundError:
        LOGGER.error(f"processor {name} not found")
        raise

    return m.Processor(db, **params)


class App:
    def __init__(self, config: Config, *, create_schema: bool = True) -> None:
        self.config = config
        self.db = Database(
            self.config.db.uri, self.config.db.content_dir, create_schema=create_schema
        )
        self.cache = UserCache(
            app=PACKAGE_NAME,
            expiration_time=self.config.cache.expiration,
            base_dir=self.config.cache.base_dir,
        )
        LOGGER.info(
            "using cache ("
            + f"base_dir='{self.config.cache.base_dir}', "
            + f"expiration_time={config.cache.expiration}"
            + ")"
        )
        self.fetcher = HTTPClient(cache=self.cache)

    @classmethod
    def from_config_file(
        cls, config_path: Path | None, *, create_schema: bool = True
    ) -> Self:
        """Build an App from a config file, or from defaults when None."""
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
        self.cache.prune()
        self.cache.close()
        self.db.close()

    def import_source(self, source: SourceData) -> list[SourceItem]:
        """Fetch every item of a source and store it."""
        provider = provider_factory(source, fetcher=self.fetcher)
        pickle_path = Path(f"{source.name}.pkl")
        items: list[SourceItem] | None = None

        if _USE_PICKLE_DATA and pickle_path.exists():
            with pickle_path.open("rb") as fh:
                items = pickle.load(fh)

        if items is None:
            items = [
                SourceItem.from_data(source, item_data)
                for item_data in provider.retrieve_items()
            ]

        if _USE_PICKLE_DATA:
            with pickle_path.open("wb") as fh:
                pickle.dump(items, fh)

        self.db.upsert_source_items(items)

        return items

    def import_url(self, source: SourceData) -> SourceItem:
        """Fetch one item URL with the source's provider and store it."""
        provider = provider_factory(source.model_copy(deep=True), fetcher=self.fetcher)
        if not isinstance(provider, IndexSiteProvider):
            raise UnsupportedProviderError(
                f"provider '{source.provider}' does not support URL imports"
            )

        item_data = provider.retrieve_item(str(source.url))
        item = SourceItem.from_data(source, item_data)
        self.db.upsert_source_items([item])
        return item

    def run_processor(
        self,
        name: str,
        *,
        scope: ProcessingScope | None = None,
        force: bool = False,
        params: dict | None = None,
    ) -> None:
        """Run a processor with its configured params, overridden by `params`."""
        configured = next((p for p in self.config.processors if p.name == name), None)
        if configured is None:
            LOGGER.warning(
                f"Processor '{name}' not found in config; using default parameters"
            )
        merged = configured.params.model_dump() if configured else {}
        merged.update(params or {})

        processor = processor_factory(name, self.db, **merged)
        processor.run(scope=scope, force=force)

    def run_pipeline(
        self,
        item: SourceItem,
        pipeline: PipelineConfig,
        *,
        force: bool = False,
    ) -> None:
        """Run each pipeline step on one item, stopping at a step with no output."""
        scope = ProcessingScope(uids=(item.uid,))
        for step in pipeline.steps:
            self.run_processor(
                step.processor,
                scope=scope,
                force=force,
                params=step.params.model_dump(),
            )
            if not self.db.get_annotations(item, processor=step.processor):
                raise PipelineError(
                    f"processor '{step.processor}' did not produce an output"
                )
