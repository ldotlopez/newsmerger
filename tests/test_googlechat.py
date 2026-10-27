import shutil
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pydantic
import requests

from newsmerger.db import Database, DeliveryStatus, ProcessingStatus
from newsmerger.models import SourceData, SourceItem
from newsmerger.plugins import Services, googlechat
from newsmerger.plugins.googlechat import (
    WEBHOOK_KEY,
    GoogleChatSink,
    Options,
    WebhookOptions,
)
from newsmerger.sinks import Sink

SOURCE = SourceData(id="a", name="A", url="https://a.test/", provider="plaza")


class OptionsTests(unittest.TestCase):
    def test_builds_the_url_from_channel_and_token(self) -> None:
        cfg = WebhookOptions(channel="AAAA", token="t0k=")
        self.assertEqual(
            cfg.webhook_url().get_secret_value(),
            "https://chat.googleapis.com/v1/spaces/AAAA/messages"
            f"?key={WEBHOOK_KEY}&token=t0k%3D",
        )

    def test_takes_the_url_as_given(self) -> None:
        cfg = WebhookOptions(url="https://chat.test/hook")
        self.assertEqual(cfg.webhook_url().get_secret_value(), "https://chat.test/hook")

    def test_needs_exactly_one_form(self) -> None:
        for options in (
            {},
            {"channel": "AAAA"},
            {"token": "t"},
            {"url": "https://chat.test/hook", "channel": "AAAA", "token": "t"},
        ):
            with self.subTest(options), self.assertRaises(pydantic.ValidationError):
                WebhookOptions.model_validate(options)

    def test_an_entry_overrides_the_section(self) -> None:
        sink = GoogleChatSink(Options(channel="AAAA", token="t"))
        self.assertEqual(sink.use_options({}).channel, "AAAA")
        self.assertEqual(sink.use_options({"channel": "BBBB"}).channel, "BBBB")
        with self.assertRaises(pydantic.ValidationError):
            GoogleChatSink(Options()).use_options({})

    def test_entry_point_registers_the_sink(self) -> None:
        ((name, protocol, sink),) = googlechat.__newsmerger_plugin__(
            Services(), url="https://chat.test/hook"
        )
        self.assertEqual((name, protocol), ("googlechat", Sink))
        self.assertIsInstance(sink, GoogleChatSink)


@patch("newsmerger.plugins.googlechat.requests.post")
class GoogleChatSinkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="newsmerger-test-"))
        self.db = Database(
            f"sqlite:///{self.tmp_dir}/data.db", self.tmp_dir / "content"
        )
        item = SourceItem(
            source=SOURCE,
            uid="h1",
            title="A <b> & c",
            uri="https://a.test/1?a=1&b=2",
            content=b"<p>1</p>",
            mimetype="text/html",
            published_at=datetime.now(UTC),
        )
        self.db.upsert_source_items([item])
        self.db.record_result(
            item, "summarize", "summary", ProcessingStatus.DONE, value="S"
        )
        sink = GoogleChatSink(Options(channel="AAAA", token="secret"))
        options = sink.use_options({})
        self.deliver = lambda: sink.deliver(self.db, key="googlechat", options=options)

    def tearDown(self) -> None:
        self.db.close()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_posts_the_summarized_item_once(self, post: Mock) -> None:
        post.return_value = Mock(ok=True)
        post.return_value.json.return_value = {"name": "spaces/AAAA/messages/m1"}

        self.deliver()
        self.deliver()

        post.assert_called_once()
        self.assertEqual(
            post.call_args.kwargs["json"],
            {
                "text": "*A &lt;b&gt; &amp; c*\n\nS\n\n"
                "<https://a.test/1?a=1&b=2|Original article>"
            },
        )
        ((row, _),) = self.db.get_item_deliveries("googlechat")
        self.assertEqual(row.status, DeliveryStatus.DONE)
        self.assertEqual(row.external_ref, {"message": "spaces/AAAA/messages/m1"})

    def test_failed_post_stays_failed_without_leaking_the_token(
        self, post: Mock
    ) -> None:
        post.side_effect = requests.ConnectionError("url: ...&token=secret")

        with self.assertLogs("newsmerger.sinks", "ERROR") as logs:
            self.deliver()

        ((row, _),) = self.db.get_item_deliveries("googlechat")
        self.assertEqual(
            (row.status, row.last_error), (DeliveryStatus.ERROR, "ConnectionError")
        )
        self.assertNotIn("secret", "\n".join(logs.output))

    def test_api_error_is_recorded(self, post: Mock) -> None:
        post.return_value = Mock(ok=False)
        post.return_value.json.return_value = {"error": {"message": "bad space"}}

        with self.assertLogs("newsmerger.sinks", "ERROR"):
            self.deliver()

        ((row, _),) = self.db.get_item_deliveries("googlechat")
        self.assertEqual(row.last_error, "bad space")


if __name__ == "__main__":
    unittest.main()
