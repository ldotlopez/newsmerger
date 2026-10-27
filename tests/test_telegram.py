import json
import shutil
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pydantic
import requests

from newsmerger.db import Database, DeliveryStatus, ProcessingStatus
from newsmerger.models import Artifact, ProcessingScope, SourceData, SourceItem
from newsmerger.plugins import Services, telegram
from newsmerger.plugins.telegram import (
    MAX_CAPTION_LENGTH,
    Options,
    TelegramArtifactSink,
    TelegramSink,
    build_caption,
)
from newsmerger.sinks import Sink
from scripts.migrate_telegram_state import migrate

SOURCE_A = SourceData(id="a", name="A", url="https://a.test/", provider="plaza")
SOURCE_B = SourceData(id="b", name="B", url="https://b.test/", provider="plaza")


def ok_response(message_id: int = 42) -> Mock:
    response = Mock()
    response.json.return_value = {"ok": True, "result": {"message_id": message_id}}
    return response


class TelegramTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="newsmerger-test-"))
        self.db = Database(
            f"sqlite:///{self.tmp_dir}/data.db", self.tmp_dir / "content"
        )
        self.cfg = Options(bot_token="s3cr3t", chat_id="chat")

    def tearDown(self) -> None:
        self.db.close()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def add_summarized(
        self, source: SourceData, *hours_ago: int, **data: Any
    ) -> list[SourceItem]:
        now = datetime.now(UTC)
        items = [
            SourceItem(
                source=source,
                uid=f"h{hours}",
                title=f"Hour <{hours}>",
                uri=f"https://{source.id}.test/{hours}?a=1&b=2",
                content=f"<p>{hours}</p>".encode(),
                mimetype="text/html",
                data=data,
                published_at=now - timedelta(hours=hours),
            )
            for hours in hours_ago
        ]
        self.db.upsert_source_items(items)
        for item in items:
            self.db.record_result(
                item,
                "summarize",
                "summary",
                ProcessingStatus.DONE,
                value=f"Summary {item.uid}",
            )
        return items

    def delivered(self, sink: str = "telegram") -> dict[str, Any]:
        return {
            item.uid: row.external_ref
            for row, item in self.db.get_item_deliveries(
                sink, statuses=[DeliveryStatus.DONE]
            )
        }


@patch("newsmerger.plugins.telegram.requests.post")
class TelegramSinkTests(TelegramTestCase):
    def deliver(self, key: str = "telegram", **options: Any) -> None:
        sink = TelegramSink(self.cfg)
        sink.deliver(self.db, key=key, options=sink.use_options(options))

    def test_posts_one_item_per_interval_oldest_first_once(self, post: Mock) -> None:
        post.return_value = ok_response()
        self.add_summarized(SOURCE_A, 3, 2, 30)
        self.add_summarized(SOURCE_B, 1)

        self.deliver(interval=30)
        self.deliver(interval=30)
        self.assertEqual(
            self.delivered(), {"h3": {"chat_id": "chat", "message_id": 42}}
        )

        self.deliver()
        self.deliver()
        self.assertEqual(list(self.delivered()), ["h3", "h2", "h1"])
        self.assertEqual(post.call_count, 3)

    def test_each_entry_posts_to_its_own_chat(self, post: Mock) -> None:
        post.return_value = ok_response()
        self.add_summarized(SOURCE_A, 3)

        self.deliver()
        self.deliver("other", chat_id="other-chat")

        self.assertEqual(
            [call.kwargs["json"]["chat_id"] for call in post.call_args_list],
            ["chat", "other-chat"],
        )
        self.assertEqual(
            self.delivered("other"), {"h3": {"chat_id": "other-chat", "message_id": 42}}
        )

    def test_an_entry_needs_a_token_and_a_chat(self, post: Mock) -> None:
        for section, overrides in (
            (Options(bot_token="token"), {}),
            (Options(chat_id="chat"), {}),
            (Options(), {"chat_id": "c"}),
        ):
            with (
                self.subTest(overrides=overrides),
                self.assertRaises(pydantic.ValidationError),
            ):
                TelegramSink(section).use_options(overrides)

    def test_an_entry_overrides_or_replaces_the_section(self, post: Mock) -> None:
        post.return_value = ok_response()
        self.add_summarized(SOURCE_A, 3)
        sink = TelegramSink(Options())  # no section: the entry says it all

        options = sink.use_options({"bot_token": "other", "chat_id": "@channel"})
        sink.deliver(self.db, key="channel", options=options)

        (request_url,) = post.call_args.args
        self.assertEqual(request_url, "https://api.telegram.org/botother/sendMessage")
        self.assertEqual(post.call_args.kwargs["json"]["chat_id"], "@channel")
        self.assertNotIn("other", repr(options))  # the token stays secret

    def test_failed_post_stays_failed_without_leaking_the_token(
        self, post: Mock
    ) -> None:
        post.side_effect = requests.ConnectionError("url: /bots3cr3t/sendMessage")
        self.add_summarized(SOURCE_A, 3)

        with self.assertLogs("newsmerger.sinks", "ERROR") as logs:
            self.deliver()

        ((row, _),) = self.db.get_item_deliveries("telegram")
        self.assertEqual((row.status, row.attempts), (DeliveryStatus.ERROR, 1))
        self.assertEqual(row.last_error, "ConnectionError")
        self.assertNotIn("s3cr3t", "\n".join(logs.output))

    @patch("newsmerger.plugins.telegram.requests.get")
    def test_uploads_photo_with_escaped_caption(self, get: Mock, post: Mock) -> None:
        get.return_value.content = b"JPEG"
        get.return_value.headers = {"Content-Type": "image/jpeg"}
        post.return_value = ok_response()
        self.add_summarized(SOURCE_A, 3, image="https://a.test/image.jpg")

        self.deliver()

        get.assert_called_once_with("https://a.test/image.jpg", timeout=30)
        (request_url,) = post.call_args.args
        payload = post.call_args.kwargs["data"]
        self.assertTrue(request_url.endswith("/sendPhoto"))
        self.assertEqual(
            post.call_args.kwargs["files"],
            {"photo": ("image.jpg", b"JPEG", "image/jpeg")},
        )
        self.assertIn("Hour &lt;3&gt;", payload["caption"])
        self.assertIn('href="https://a.test/3?a=1&amp;b=2"', payload["caption"])

    @patch("newsmerger.plugins.telegram.requests.get")
    def test_image_download_failure_is_a_failed_delivery(
        self, get: Mock, post: Mock
    ) -> None:
        get.return_value.raise_for_status.side_effect = requests.HTTPError("404")
        self.add_summarized(SOURCE_A, 3, image="https://a.test/image.jpg")

        self.deliver()

        post.assert_not_called()
        ((row, _),) = self.db.get_item_deliveries("telegram")
        self.assertEqual(row.status, DeliveryStatus.ERROR)

    def test_item_image_off_sends_text(self, post: Mock) -> None:
        post.return_value = ok_response()
        self.add_summarized(SOURCE_A, 3, image="https://a.test/image.jpg")

        self.deliver(item_image=False)

        (request_url,) = post.call_args.args
        self.assertTrue(request_url.endswith("/sendMessage"))
        self.assertNotIn("photo", post.call_args.kwargs["json"])

    def test_sends_text_without_image(self, post: Mock) -> None:
        post.return_value = ok_response()
        self.add_summarized(SOURCE_A, 3)

        self.deliver()

        (request_url,) = post.call_args.args
        self.assertTrue(request_url.endswith("/sendMessage"))
        self.assertIn("Summary h3", post.call_args.kwargs["json"]["text"])
        self.assertIn(">original article</a>", post.call_args.kwargs["json"]["text"])
        self.assertEqual(
            post.call_args.kwargs["json"]["link_preview_options"], {"is_disabled": True}
        )

    def test_link_text_and_preview_are_configurable(self, post: Mock) -> None:
        post.return_value = ok_response()
        self.add_summarized(SOURCE_A, 3)

        self.deliver(item_url_preview=True, item_url_text="Leer <más>")

        payload = post.call_args.kwargs["json"]
        self.assertIn(">Leer &lt;más&gt;</a>", payload["text"])
        self.assertEqual(payload["link_preview_options"], {"is_disabled": False})


@patch("newsmerger.plugins.telegram.requests.post")
class TelegramArtifactSinkTests(TelegramTestCase):
    def test_sends_new_artifacts_of_the_listed_remixers_as_documents(
        self, post: Mock
    ) -> None:
        post.return_value = ok_response(7)
        self.db.save_artifact(
            Artifact("digest", "a/2026-10-01_2026-10-08", "# Week", "text/markdown")
        )
        self.db.save_artifact(Artifact("feedgenerator", "feed", "<rss/>", "text/xml"))
        sink = TelegramArtifactSink(self.cfg)
        options = sink.use_options({"artifacts": ["digest"]})

        sink.deliver(self.db, key="telegram_artifacts", options=options)
        sink.deliver(self.db, key="telegram_artifacts", options=options)

        post.assert_called_once()
        (request_url,) = post.call_args.args
        self.assertTrue(request_url.endswith("/sendDocument"))
        self.assertEqual(
            post.call_args.kwargs["data"],
            {"chat_id": "chat", "caption": "digest/a/2026-10-01_2026-10-08"},
        )
        self.assertEqual(
            post.call_args.kwargs["files"]["document"],
            ("digest-a_2026-10-01_2026-10-08.md", b"# Week", "text/markdown"),
        )
        ((row, _),) = self.db.get_artifact_deliveries("telegram_artifacts")
        self.assertEqual(row.external_ref, {"chat_id": "chat", "message_id": 7})


class PluginTests(unittest.TestCase):
    def test_provides_both_sinks_even_without_a_section(self) -> None:
        objects = telegram.__newsmerger_plugin__(Services())

        self.assertEqual(
            [(name, protocol) for name, protocol, _ in objects],
            [("telegram", Sink), ("telegram_artifacts", Sink)],
        )


class MigrateTelegramStateTests(TelegramTestCase):
    def test_posted_items_become_done_and_queued_ones_queued(self) -> None:
        a3, _, _ = self.add_summarized(SOURCE_A, 3, 2, 1)
        state = {
            "watermark": "2026-10-02T00:00:00+00:00",
            "queue": [["a", "h2"]],
            "posted": [["a", "h3", 11], ["a", "gone", 12]],
            "last_post": {"a": "2026-10-02T00:00:00+00:00"},
        }
        self.db.save_artifact(
            Artifact("telegram", "state", json.dumps(state), "application/json")
        )

        with self.assertLogs("newsmerger", "WARNING") as logs:
            self.assertEqual(migrate(self.db), (1, 1))
            self.assertEqual(migrate(self.db), (0, 1))

        self.assertIn("a/gone is no longer stored", logs.output[0])
        rows = {
            item.uid: (row.status, row.external_ref)
            for row, item in self.db.get_item_deliveries("telegram")
        }
        self.assertEqual(
            rows,
            {
                "h3": (DeliveryStatus.DONE, {"message_id": 11}),
                "h2": (DeliveryStatus.QUEUED, None),
            },
        )
        ((row, _),) = self.db.get_item_deliveries(
            "telegram", ProcessingScope(item_ids=(a3.id,))
        )
        self.assertEqual(row.content_sha256, a3.content_sha256)


class BuildCaptionTests(unittest.TestCase):
    def test_caption_is_bounded_and_keeps_link(self) -> None:
        caption = build_caption("Title", "A" * 2000, "https://example.test/article")

        self.assertLessEqual(len(caption), MAX_CAPTION_LENGTH)
        self.assertIn("original article", caption)
        self.assertIn("https://example.test/article", caption)


if __name__ == "__main__":
    unittest.main()
