import unittest
from unittest.mock import Mock

from foundation import cache

from newsmerger.httpclient import HTTPClient


class TestHTTPClient(unittest.TestCase):
    def setUp(self) -> None:
        self.cache = Mock()
        self.cache.get.side_effect = cache.CacheMissError("miss")
        self.client = HTTPClient(cache=self.cache)
        self.client.session = Mock()
        self.client.session.request.return_value = Mock(ok=True, content=b"body")

    def test_cache_miss_fetches_and_stores(self) -> None:
        self.assertEqual(self.client.get("https://example.test/"), b"body")
        self.cache.set.assert_called_once_with("https://example.test/", b"body")

    def test_use_cache_false_skips_the_cache(self) -> None:
        self.cache.get.side_effect = None
        self.cache.get.return_value = b"stale"

        self.assertEqual(
            self.client.get("https://example.test/", use_cache=False), b"body"
        )
        self.cache.get.assert_not_called()
        self.cache.set.assert_not_called()
