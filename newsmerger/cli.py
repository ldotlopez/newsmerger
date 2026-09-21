from __future__ import annotations

import importlib
import logging
import os
import pickle
from datetime import UTC
from pathlib import Path

import rich
import rich_click as click
from foundation.cache import Cache, TTLValidator
from foundation.loglib import setup_logger
from foundation.storage import DiskStorage

from newsmerger.config import Config, PipelineConfig
from newsmerger.consts import PACKAGE_NAME
from newsmerger.db import Database, ProcessingScope
from newsmerger.models import SourceData, SourceItem
from newsmerger.processors import BaseProcessor
from newsmerger.providers import BaseProvider, IndexSiteProvider

from .httpclient import HTTPClient

LOGGER = logging.getLogger(PACKAGE_NAME)

_USE_PICKLE_DATA = os.environ.get("NEWSMERGER_PICKLE_CACHE", "0").lower() not in (
    "0",
    "false",
    "",
)


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

    return m.Provider(source, *args, **kwargs)


def processor_factory(name: str, db: Database, **params) -> BaseProcessor:
    try:
        m = importlib.import_module(f"newsmerger.processors.{name}")
    except ModuleNotFoundError:
        LOGGER.error(f"processor {name} not found")
        raise

    return m.Processor(db, **params)


class App:
    def __init__(self, config: Config):
        self.config = config
        self.db = Database(self.config.db.uri)
        self.cache = Cache(
            storage=DiskStorage(base_dir=self.config.cache.base_dir),
            validator=TTLValidator(expiration_time=self.config.cache.expiration),
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

    def import_url(self, source: SourceData) -> SourceItem:
        """Import one item URL with its configured provider."""
        provider = provider_factory(source.model_copy(deep=True), fetcher=self.fetcher)
        if not isinstance(provider, IndexSiteProvider):
            raise click.ClickException(
                f"provider '{source.provider}' does not support URL imports"
            )

        item_data = provider.retrieve_item(str(source.url))
        item = SourceItem.from_data(source, item_data)
        self.db.upsert_source_items([item])
        return item

    def run_pipeline(
        self,
        item: SourceItem,
        pipeline: PipelineConfig,
        *,
        force: bool = False,
    ) -> None:
        scope = ProcessingScope(uids=(item.uid,))
        configured_processors = {
            processor.name: processor.params.model_dump()
            for processor in self.config.processors
        }
        for step in pipeline.steps:
            processor_name = step.processor
            params = configured_processors.get(processor_name, {}).copy()
            params.update(step.params.model_dump())
            processor = processor_factory(processor_name, self.db, **params)
            processor.run(scope=scope, force=force)
            if not self.db.get_annotations(item, processor=processor_name):
                raise click.ClickException(
                    f"processor '{processor_name}' did not produce an output"
                )


@click.group()
@click.option("-c", "--config", "config_path", type=Path, default=None)
@click.pass_context
def cli(ctx, config_path: Path | None):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    setup_logger(PACKAGE_NAME)
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


@cli.command("import-url")
@click.option("-p", "--provider", required=True, help="Provider module name")
@click.argument("url")
@click.pass_context
def import_url_cmd(ctx, provider: str, url: str) -> None:
    app = App.from_click_context(ctx)

    try:
        source = SourceData(
            name=f"{provider}:{url}",
            provider=provider,
            url=url,
        )
        item = app.import_url(source)
    except ModuleNotFoundError as exc:
        raise click.ClickException(f"provider '{provider}' not found") from exc
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    rich.print(f"Imported item '{item.title}' from '{item.uri}'")


@cli.command("pipeline-url")
@click.argument("pipeline_name")
@click.option("-p", "--provider", required=True, help="Provider module name")
@click.option("--force", is_flag=True, help="Re-run already completed processors")
@click.argument("url")
@click.pass_context
def pipeline_url_cmd(
    ctx: click.Context,
    pipeline_name: str,
    provider: str,
    force: bool,
    url: str,
) -> None:
    app = App.from_click_context(ctx)

    try:
        source = SourceData(name=f"{provider}:{url}", provider=provider, url=url)
        item = app.import_url(source)
        pipeline = app.config.get_pipeline(pipeline_name)
        app.run_pipeline(item, pipeline, force=force)
    except (ModuleNotFoundError, ValueError, click.ClickException) as exc:
        if isinstance(exc, click.ClickException):
            raise
        raise click.ClickException(str(exc)) from exc

    rich.print(
        f"Processed '{item.title}' with pipeline '{pipeline.name}' "
        f"({', '.join(step.processor for step in pipeline.steps)})"
    )


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
    if not config_entry:
        LOGGER.warning(
            f"Processor '{processor_name}' not found in config; using default parameters"
        )

    params = config_entry.params.model_dump() if config_entry else {}

    processor = processor_factory(processor_name, app.db, **params)

    scope = ProcessingScope(
        source=source,
        since=since.replace(tzinfo=UTC) if since else None,
        until=until.replace(tzinfo=UTC) if until else None,
        limit=limit,
    )
    processor.run(scope=scope, force=force)
