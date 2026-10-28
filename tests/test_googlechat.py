import shutil
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pydantic
import requests

from newstool.db import Database, DeliveryStatus, ProcessingStatus
from newstool.models import SourceData, SourceItem
from newstool.plugins import Services, googlechat, merge_options
from newstool.plugins.googlechat import (
    WEBHOOK_KEY,
    GoogleChatSink,
    WebhookOptions,
    chat_image_url,
)
from newstool.sinks import SinkType

SOURCE = SourceData(id="a", name="A", url="https://a.test/", provider="plaza")
BLOGGER_IMAGE = (
    "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvX/s72-c/A%20b.png"
)


def card_widgets(message: dict[str, Any]) -> list[dict[str, Any]]:
    ((section,),) = (card["card"]["sections"] for card in message["cardsV2"])
    return section["widgets"]


class ChatImageUrlTests(unittest.TestCase):
    def test_keeps_other_hosts(self) -> None:
        self.assertEqual(
            chat_image_url("https://a.test/s72-c/image.jpg"),
            "https://a.test/s72-c/image.jpg",
        )

    def test_proxies_blogger_at_full_size(self) -> None:
        for size in ("s72-c", "s300", "w1200", "s1600"):
            with self.subTest(size):
                self.assertEqual(
                    chat_image_url(BLOGGER_IMAGE.replace("s72-c", size)),
                    "https://wsrv.nl/?url=https%3A%2F%2Fblogger.googleusercontent.com"
                    "%2Fimg%2Fb%2FR29vZ2xl%2FAVvX%2Fs1600%2FA%2520b.png",
                )


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
        ((name, protocol, cls),) = googlechat.__newstool_plugin__()
        self.assertEqual(
            (name, protocol, cls), ("googlechat", SinkType, GoogleChatSink)
        )


@patch("newstool.plugins.googlechat.requests.post")
class GoogleChatSinkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="newstool-test-"))
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
            card_widgets(post.call_args.kwargs["json"]),
            [
                {
                    "textParagraph": {
                        "text": "<b>A &lt;b&gt; &amp; c</b><br><br>S summary"
                    }
                },
                {
                    "buttonList": {
                        "buttons": [
                            {
                                "text": "original article",
                                "onClick": {
                                    "openLink": {"url": "https://a.test/1?a=1&b=2"}
                                },
                            }
                        ]
                    }
                },
            ],
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
        (paragraph, _) = card_widgets(post.call_args.kwargs["json"])
        self.assertTrue(paragraph["textParagraph"]["text"].endswith("S summary/ca"))

    def test_image_and_link_text(self, post: Mock) -> None:
        post.return_value = Mock(ok=True)
        post.return_value.json.return_value = {"name": "spaces/AAAA/messages/m1"}
        self.add_summarized("h2", image="https://a.test/image.jpg")
        self.add_summarized("h3", image=BLOGGER_IMAGE)

        self.deliver(item_url_text="Leer <más>")

        messages = [card_widgets(call.kwargs["json"]) for call in post.call_args_list]
        self.assertEqual([len(widgets) for widgets in messages], [2, 3, 3])
        self.assertEqual(
            messages[1][1]["image"],
            {"imageUrl": "https://a.test/image.jpg", "altText": "A <b> & c"},
        )
        self.assertEqual(
            messages[2][1]["image"]["imageUrl"], chat_image_url(BLOGGER_IMAGE)
        )
        (button,) = messages[1][2]["buttonList"]["buttons"]
        self.assertEqual(button["text"], "Leer <más>")

    def test_item_image_off_sends_text_only(self, post: Mock) -> None:
        post.return_value = Mock(ok=True)
        post.return_value.json.return_value = {"name": "spaces/AAAA/messages/m1"}
        self.add_summarized("h2", image="https://a.test/image.jpg")

        self.deliver(item_image=False)

        self.assertFalse(
            any(
                "image" in widget
                for call in post.call_args_list
                for widget in card_widgets(call.kwargs["json"])
            )
        )

    def test_failed_post_stays_failed_without_leaking_the_token(
        self, post: Mock
    ) -> None:
        post.side_effect = requests.ConnectionError("url: ...&token=secret")

        with self.assertLogs("newstool.sinks", "ERROR") as logs:
            self.deliver()

        ((row, _),) = self.db.get_item_deliveries("googlechat")
        self.assertEqual(
            (row.status, row.last_error), (DeliveryStatus.ERROR, "ConnectionError")
        )
        self.assertNotIn("secret", "\n".join(logs.output))

    def test_api_error_is_recorded(self, post: Mock) -> None:
        post.return_value = Mock(ok=False)
        post.return_value.json.return_value = {"error": {"message": "bad space"}}

        with self.assertLogs("newstool.sinks", "ERROR"):
            self.deliver()

        ((row, _),) = self.db.get_item_deliveries("googlechat")
        self.assertEqual(row.last_error, "bad space")


if __name__ == "__main__":
    unittest.main()
