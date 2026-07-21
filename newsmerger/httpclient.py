import hashlib
import logging

import requests
from foundation import cache

LOGGER = logging.getLogger(__name__)

DEFAULT_HEADERS = {
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
}


class HTTPClient:
    def __init__(self, cache: cache.Cache, headers: dict[str, str] = DEFAULT_HEADERS):
        self.cache = cache
        self.session = requests.Session()
        self.session.headers.update(headers)

    @staticmethod
    def _build_url_key(url: str) -> str:
        h = hashlib.sha256()
        h.update(url.encode("utf-8"))
        return h.hexdigest()

    def get(self, url: str) -> bytes:
        return self.fetch("GET", url)

    def fetch(self, method: str, url: str, *args, **kwargs) -> bytes:
        is_cacheable = method.upper() == "GET"

        if is_cacheable:
            key = self._build_url_key(url)
            try:
                content = self.cache.get(key)
                LOGGER.debug(f"{url} found in cache ({len(content)} bytes)")
                return content
            except cache.CacheMissError:
                pass
        else:
            key = None

        resp = self.session.request(method, url, *args, **kwargs)
        content = resp.content

        LOGGER.debug(f"{url} fetched {len(content)} bytes")
        if is_cacheable:
            self.cache.set(key, content)  # ty:ignore[invalid-argument-type]
            LOGGER.debug(f"{url} saved {len(resp.content)} bytes")

        return content


class NetworkError(Exception):
    pass


class ServerError(NetworkError):
    def __init__(self, url: str, response: requests.Response):
        self.url = url
        self.response = response
