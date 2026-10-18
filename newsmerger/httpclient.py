import logging

import requests
from foundation import cache

LOGGER = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:142.0) Gecko/20100101 Firefox/142.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ca,en-US;q=0.7,en;q=0.3",
    # Only what requests decodes without extra packages: br/zstd came back raw.
    "Accept-Encoding": "gzip, deflate",
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

    def get(self, url: str) -> bytes:
        return self.fetch("GET", url)

    def fetch(self, method: str, url: str, *args, **kwargs) -> bytes:
        is_cacheable = method.upper() == "GET"

        if is_cacheable:
            try:
                content = self.cache.get(url)
                LOGGER.debug(f"{url} found in cache ({len(content)} bytes)")
                return content
            except cache.CacheMissError:
                pass

        resp = self.session.request(method, url, *args, **kwargs)
        content = resp.content

        LOGGER.debug(f"{url} fetched {len(content)} bytes")
        # Error pages must not be served from cache for the whole TTL.
        if is_cacheable and resp.ok:
            self.cache.set(url, content)
            LOGGER.debug(f"{url} saved {len(content)} bytes")

        return content
