from __future__ import annotations

import importlib
import logging
from pathlib import Path

import requests
import rich_click as click
from foundation.cache import Cache, StatValidator
from foundation.logging import setup as setup_logging
from foundation.storage import DiskStorage

from newsmerger.config import Config
from newsmerger.consts import PACKAGE_NAME
from newsmerger.db import Database
from newsmerger.models import Source, SourceEntryData
from newsmerger.providers import BaseProvider

from .httpclient import HTTPClient

LOGGER = logging.getLogger(PACKAGE_NAME)


class NetworkError(Exception):
    pass


class ServerError(NetworkError):
    def __init__(self, url: str, response: requests.Response):
        self.url = url
        self.response = response


def SourceFactory(name: str, *args, **kwargs) -> BaseProvider:
    try:
        m = importlib.import_module(f"newsmerger.providers.{name}")
    except ModuleNotFoundError:
        LOGGER.error(f"provider {name} not found")
        raise

    return getattr(m, "Provider")(*args, **kwargs)


class Fetcher:
    def __init__(self):
        self.sess = requests.Session()

    def get(self, url: str) -> bytes:
        return self.request(url)

    def request(self, url: str, method: str = "GET") -> bytes:
        return self.raw_request(requests.Request(method=method, url=url))

    def raw_request(self, request: requests.Request) -> bytes:
        return self.sess.send(request.prepare()).content


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
            + f"base_dir='{self.cache.storage.base_dir}', "
            + f"stat_expiration_time={config.cache.expiration}"
            + ")"
        )
        self.fetcher = HTTPClient(cache=self.cache)

    @classmethod
    def from_click_context(cls, ctx: click.Context) -> App:
        config_path = ctx.obj["config_path"]
        return cls(config=Config.from_file(config_path) if config_path else Config())

    def import_source(self, source: Source) -> list[SourceEntryData]:
        return list(source.retrieve_items())

    def store_many(self, entries: list[SourceEntryData]) -> None:
        self.db.upsert_many(entries)

    def store(self, entry_data: SourceEntryData) -> None:
        self.store_many([entry_data])


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

    for source_config in app.config.sources:
        app.import_source(
            SourceFactory(
                source_config.provider, url=str(source_config.url), fetcher=app.fetcher
            )
        )
