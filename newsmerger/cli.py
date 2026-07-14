from __future__ import annotations

import importlib
import logging
import pickle
from pathlib import Path

import requests
import rich_click as click
from foundation.cache import Cache, StatValidator
from foundation.logging import setup as setup_logging
from foundation.storage import DiskStorage

from newsmerger.config import Config
from newsmerger.consts import PACKAGE_NAME
from newsmerger.db import Database
from newsmerger.models import SourceData, SourceItem
from newsmerger.providers import BaseProvider

from .httpclient import HTTPClient

LOGGER = logging.getLogger(PACKAGE_NAME)


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

        # items = []
        # for item_data in provider.retrieve_items():
        #     items.append(SourceItem(source=provider.source, **item_data.model_dump()))
        # with open(f"{provider.source.name}.pkl", "wb") as fh:
        #     items = pickle.dump(items, fh)

        with open(f"{provider.source.name}.pkl", "rb") as fh:
            items = pickle.load(fh)

        self.db.save_source_items(items)

        return items

    # def store_many(self, entries: list[SourceItemData]) -> None:
    #     # legacy helper kept for compatibility; prefer store_entries_for_source
    #     for entry in entries:
    #         # Without source context, we cannot store entries directly
    #         raise RuntimeError(
    #             "store_many requires a source context; use store_entries_for_source"
    #         )

    # def store(self, entry_data: SourceItemData) -> None:
    #     self.store_many([entry_data])


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
        provider = provider_factory(source_config, fetcher=app.fetcher)
        _ = app.import_source(provider)  # noqa: F841
