from __future__ import annotations

import hashlib
import importlib
import logging
from pathlib import Path

import requests
import rich_click as click
from foundation.cache import Cache, MissingKeyError, StatValidator
from foundation.logging import setup as setup_logging
from foundation.storage import DiskStorage

from newsmerger.config import Config
from newsmerger.consts import PACKAGE_NAME
from newsmerger.models import SourceEntryData
from newsmerger.providers import BaseProvider

LOGGER = logging.getLogger(PACKAGE_NAME)


class NetworkError(Exception):
    pass


class ServerError(NetworkError):
    def __init__(self, url: str, response: requests.Response):
        self.url = url
        self.response = response


def ProviderFactory(name: str) -> BaseProvider:
    try:
        m = importlib.import_module(f"newsmerger.providers.{name}")
    except ModuleNotFoundError:
        LOGGER.error(f"provider {name} not found")
        raise

    return getattr(m, "Provider")()


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
        self.storage = DiskStorage(base_dir=self.config.cache.base_dir)
        self.cache = Cache(
            storage=self.storage,
            validator=StatValidator(expiration_time=self.config.cache.expiration),
        )

        LOGGER.info(
            "using cache ("
            + f"base_dir='{self.storage.base_dir}', "
            + f"stat_expiration_time={self.config.cache.expiration}"
            + ")"
        )

    @classmethod
    def from_click_context(cls, ctx: click.Context) -> App:
        config_path = ctx.obj["config_path"]
        return cls(config=Config.from_file(config_path) if config_path else Config())

    def fetch(self, url: str) -> bytes:
        def _build_url_key(url: str) -> str:
            h = hashlib.sha256()
            h.update(url.encode("utf-8"))
            return h.hexdigest()

        key = _build_url_key(url)

        try:
            content = self.cache.get(key)
            LOGGER.debug(f"{url} found in cache")
            return content

        except MissingKeyError:
            LOGGER.debug(f"{url} not found in cache")

        with requests.Session() as s:
            resp = s.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "ca,en-US;q=0.7,en;q=0.3",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-User": "?1",
                    "Priority": "u=0, i",
                    "Pragma": "no-cache",
                    "Cache-Control": "no-cache",
                },
            )
            if resp.status_code != 200:
                LOGGER.error(f"{url} returned {resp.status_code}")
                raise ServerError(url, response=resp)

            self.cache.set(key, resp.content)
            LOGGER.debug(f"{url} saved {len(resp.content)} bytes")

            return resp.content

    def store_many(self, entries: list[SourceEntryData]) -> None: ...

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

    for source in app.config.sources:
        content = app.fetch(str(source.url))
        provider = ProviderFactory(source.provider)

        entries = []
        for uri in provider.parse_index(content):
            content = app.fetch(str(uri))
            try:
                entry = provider.parse_item(content)
            except ValueError as e:
                LOGGER.error(f"error '{e}' while parsing '{uri}'")
                continue

            if not entry.uri:
                entry.uri = uri
            if not entry.content:
                entry.content = entry.title

            entries.append(entry)

        app.store(entries)

        # items = provider.parse_listing(content)

        # source_model = Source(provider=source.provider, url=source.url)
        # entries = [SourceEntry.from_data(source_model, entry) for entry in items]


# @click.command()
# @click.option("-c", "--config", "config_path", type=Path, default=None)
# def main(config_path: Path | None):
#     setup_logging()
#     app = App(config=Config.from_file(config_path) if config_path else Config())
#     print("Hello from news-aggregator!")
