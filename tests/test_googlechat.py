import shutil
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pydantic
import requests

from newsmerger.db import Database, DeliveryStatus, ProcessingStatus
from newsmerger.models import SourceData, SourceItem
from newsmerger.plugins import Services, googlechat, merge_options
from newsmerger.plugins.googlechat import (
    WEBHOOK_KEY,
    GoogleChatSink,
    WebhookOptions,
)
from newsmerger.sinks import SinkType

SOURCE = SourceData(id="a", name="A", url="https://a.test/", provider="plaza")


def webhook_options(section: dict[str, Any], overrides: dict[str, Any]) -> Any:
    """A use's options over its plugin section, as the core merges them."""
    return WebhookOptions.model_validate(merge_options(section, overrides))


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
        section = {"channel": "AAAA", "token": "t"}
        self.assertEqual(webhook_options(section, {}).channel, "AAAA")
        self.assertEqual(webhook_options(section, {"channel": "BBBB"}).channel, "BBBB")
        with self.assertRaises(pydantic.ValidationError):
            webhook_options({}, {})

    def test_entry_point_registers_the_sink_class(self) -> None:
        ((name, protocol, cls),) = googlechat.__newsmerger_plugin__()
        self.assertEqual(
            (name, protocol, cls), ("googlechat", SinkType, GoogleChatSink)
        )


@patch("newsmerger.plugins.googlechat.requests.post")
class GoogleChatSinkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="newsmerger-test-"))
        self.db = Database(
            f"sqlite:///{self.tmp_dir}/data.db", self.tmp_dir / "content"
        )
        self.add_summarized("h1")
        self.section = {"channel": "AAAA", "token": "secret"}

    def add_summarized(self, uid: str, key: str = "summary", **data: Any) -> None:
        item = SourceItem(
            source=SOURCE,
            uid=uid,
            title="A <b> & c",
            uri="https://a.test/1?a=1&b=2",
            content=b"<p>1</p>",
            mimetype="text/html",
            data=data,
            published_at=datetime.now(UTC),
        )
        self.db.upsert_source_items([item])
        self.db.record_result(
            item, "summarize", key, ProcessingStatus.DONE, value=f"S {key}"
        )

    def deliver(self, **options: Any) -> None:
        sink = GoogleChatSink(webhook_options(self.section, options), Services())
        sink.deliver(self.db, key="googlechat")

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
                "text": "*A &lt;b&gt; &amp; c*\n\nS summary\n\n"
                "<https://a.test/1?a=1&b=2|original article>"
            },
        )
        ((row, _),) = self.db.get_item_deliveries("googlechat")
        self.assertEqual(row.status, DeliveryStatus.DONE)
        self.assertEqual(row.external_ref, {"message": "spaces/AAAA/messages/m1"})

    def test_summary_option_picks_the_annotation(self, post: Mock) -> None:
        post.return_value = Mock(ok=True)
        post.return_value.json.return_value = {"name": "spaces/AAAA/messages/m1"}
        self.add_summarized("h2", key="summary/ca")

        self.deliver(summary="summary/ca")

        post.assert_called_once()
        self.assertIn("\n\nS summary/ca\n\n", post.call_args.kwargs["json"]["text"])

    def test_image_card_and_link_text(self, post: Mock) -> None:
        post.return_value = Mock(ok=True)
        post.return_value.json.return_value = {"name": "spaces/AAAA/messages/m1"}
        self.add_summarized("h2", image="https://a.test/image.jpg")

        self.deliver(item_url_text="Leer <más>")

        messages = [call.kwargs["json"] for call in post.call_args_list]
        self.assertEqual([("cardsV2" in m) for m in messages], [False, True])
        self.assertTrue(messages[1]["text"].endswith("|Leer &lt;más&gt;>"))
        ((widget,),) = (
            section["widgets"]
            for section in messages[1]["cardsV2"][0]["card"]["sections"]
        )
        self.assertEqual(widget["image"]["imageUrl"], "https://a.test/image.jpg")

    def test_item_image_off_sends_text_only(self, post: Mock) -> None:
        post.return_value = Mock(ok=True)
        post.return_value.json.return_value = {"name": "spaces/AAAA/messages/m1"}
        self.add_summarized("h2", image="https://a.test/image.jpg")

        self.deliver(item_image=False)

        self.assertFalse(
            any("cardsV2" in call.kwargs["json"] for call in post.call_args_list)
        )

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
