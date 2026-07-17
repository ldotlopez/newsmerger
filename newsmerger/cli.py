from __future__ import annotations

import importlib
import logging
import os
import pickle
from datetime import timezone
from pathlib import Path

import requests
import rich
import rich_click as click
from foundation.cache import Cache, StatValidator
from foundation.logging import setup as setup_logging
from foundation.storage import DiskStorage

from newsmerger.config import Config
from newsmerger.consts import PACKAGE_NAME
from newsmerger.db import Database, ProcessingScope
from newsmerger.models import SourceData, SourceItem
from newsmerger.processors import BaseProcessor
from newsmerger.providers import BaseProvider

from .httpclient import HTTPClient

LOGGER = logging.getLogger(PACKAGE_NAME)

_USE_PICKLE_DATA = os.environ.get("NEWSMERGER_PICKLE_CACHE", "0").lower() not in (
    "0",
    "false",
    "",
)


class NetworkError(Exception):
    pass


class ServerError(NetworkError):
    def __init__(self, url: str, response: requests.Response):
        self.url = url
        self.response = response


def provider_factory(source: SourceData, *args, **kwargs) -> BaseProvider:
    """Instantiate a Provider.

    Accepts either a config-like object with a `.provider` and `.url` attributes
    (e.g., SourceConfig) or a provider module name string. If a config object is
    provided and `url` is not in kwargs, the url will be filled from it.
    """
    try:
        m = importlib.import_module(f"newsmerger.providers.{source.provider}")
    except ModuleNotFoundError:
        LOGGER.error(f"provider {source.provider} not found")
        raise

    return getattr(m, "Provider")(source, *args, **kwargs)


def processor_factory(name: str, db: Database, **params) -> BaseProcessor:
    try:
        m = importlib.import_module(f"newsmerger.processors.{name}")
    except ModuleNotFoundError:
        LOGGER.error(f"processor {name} not found")
        raise

    return getattr(m, "Processor")(db, **params)


class App:
    def __init__(self, config: Config):
        self.config = config
        self.db = Database(self.config.db.uri)
        self.cache = Cache(
            storage=DiskStorage(base_dir=self.config.cache.base_dir),
            validator=StatValidator(expiration_time=self.config.cache.expiration),
        )
        LOGGER.info(
            "using cache ("
            + f"base_dir='{self.cache.storage}', "
            + f"stat_expiration_time={config.cache.expiration}"
            + ")"
        )
        self.fetcher = HTTPClient(cache=self.cache)

    @classmethod
    def from_click_context(cls, ctx: click.Context) -> App:
        config_path = ctx.obj["config_path"]
        return cls(config=Config.from_file(config_path) if config_path else Config())

    def import_source(self, provider: BaseProvider) -> list[SourceItem]:
        """Import items from a runtime provider instance and return raw entry data."""
        pickle_path = f"{provider.source.name}.pkl"
        items: list[SourceItem] | None = None

        if _USE_PICKLE_DATA and os.path.exists(pickle_path):
            with open(pickle_path, "rb") as fh:
                items = pickle.load(fh)

        if items is None:
            items = [
                SourceItem.from_data(provider.source, item_data)
                for item_data in provider.retrieve_items()
            ]

        if _USE_PICKLE_DATA:
            with open(pickle_path, "wb") as fh:
                pickle.dump(items, fh)

        self.db.upsert_source_items(items)

        return items


@click.group()
@click.option("-c", "--config", "config_path", type=Path, default=None)
@click.pass_context
def cli(ctx, config_path: Path | None):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    setup_logging(PACKAGE_NAME)
    LOGGER.setLevel(logging.DEBUG)

    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config_path


@cli.command("import")
@click.pass_context
def import_cmd(ctx):
    app = App.from_click_context(ctx)

    rich.print(
        f"Importing {len(app.config.sources)} sources from {ctx.obj['config_path']}"
    )
    for source_config in app.config.sources:
        provider = provider_factory(source_config, fetcher=app.fetcher)
        items = app.import_source(provider)
        rich.print(f"Imported {len(items)} items from '{source_config.name}'")


@cli.command("process")
@click.argument("processor_name")
@click.option("--source", default=None, help="Limit to a source name or uid")
@click.option("--since", type=click.DateTime(), default=None)
@click.option("--until", type=click.DateTime(), default=None)
@click.option("--limit", type=int, default=None)
@click.option(
    "--force",
    "--reprocess",
    "force",
    is_flag=True,
    default=False,
    help="Ignore stored processing state (including ignored items) and reprocess everything in scope",
)
@click.pass_context
def process_cmd(ctx, processor_name, source, since, until, limit, force):
    app = App.from_click_context(ctx)

    config_entry = next(
        (p for p in app.config.processors if p.name == processor_name), None
    )
    params = config_entry.params if config_entry else {}

    processor = processor_factory(processor_name, app.db, **params)

    scope = ProcessingScope(
        source=source,
        since=since.replace(tzinfo=timezone.utc) if since else None,
        until=until.replace(tzinfo=timezone.utc) if until else None,
        limit=limit,
    )
    processor.run(scope=scope, force=force)
