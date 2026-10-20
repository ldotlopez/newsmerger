import json
import shutil
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import requests

from newsmerger.db import Database, ProcessingStatus
from newsmerger.models import Artifact, ProcessingScope, SourceData, SourceItem
from newsmerger.plugins.telegram import (
    MAX_CAPTION_LENGTH,
    Options,
    TelegramRemixer,
    build_caption,
)

SOURCE_A = SourceData(id="a", name="A", url="https://a.test/", provider="plaza")
SOURCE_B = SourceData(id="b", name="B", url="https://b.test/", provider="plaza")


def ok_response(message_id: int = 42) -> Mock:
    response = Mock()
    response.json.return_value = {"ok": True, "result": {"message_id": message_id}}
    return response


@patch("newsmerger.plugins.telegram.requests.post")
class TelegramRemixerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="newsmerger-test-"))
        self.db = Database(
            f"sqlite:///{self.tmp_dir}/data.db", self.tmp_dir / "content"
        )

    def tearDown(self) -> None:
        self.db.close()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def add_summarized(self, source: SourceData, *days: int, **data: Any) -> None:
        items = [
            SourceItem(
                source=source,
                uid=f"d{day}",
                title=f"Day <{day}>",
                uri=f"https://{source.id}.test/{day}?a=1&b=2",
                content=b"<p></p>",
                mimetype="text/html",
                data=data,
                published_at=datetime(2026, 10, day, tzinfo=UTC),
            )
            for day in days
        ]
        self.db.upsert_source_items(items)
        for item in items:
            self.db.record_result(
                item,
                "summarize",
                ProcessingStatus.DONE,
                annotations={"summary": f"Summary {item.uid}"},
            )

    def save_state(self, **state: Any) -> None:
        state = {"watermark": "2026-10-02T00:00:00+00:00"} | state
        state = {"queue": [], "posted": [], "last_post": {}} | state
        self.db.save_artifact(
            Artifact("telegram", "state", json.dumps(state), "application/json")
        )

    def run_remixer(self, scope: ProcessingScope | None = None) -> dict[str, Any]:
        cfg = Options(bot_token="token", chat_id="chat", interval=30)
        TelegramRemixer(cfg).remix(self.db, scope=scope)
        return json.loads(self.db.get_artifact("telegram", "state").content)

    def test_first_run_ignores_existing_items(self, post: Mock) -> None:
        self.add_summarized(SOURCE_A, 1, 2)

        state = self.run_remixer()

        post.assert_not_called()
        self.assertEqual(state["queue"], [])

    def test_posts_oldest_new_item_once_per_source(self, post: Mock) -> None:
        post.return_value = ok_response()
        self.add_summarized(SOURCE_A, 1, 3, 4)
        self.add_summarized(SOURCE_B, 5)
        self.save_state()

        state = self.run_remixer()

        self.assertEqual(state["posted"], [["a", "d3", 42], ["b", "d5", 42]])
        self.assertEqual(state["queue"], [["a", "d4"]])
        self.assertEqual(set(state["last_post"]), {"a", "b"})

    def test_waits_for_the_interval(self, post: Mock) -> None:
        post.return_value = ok_response()
        self.add_summarized(SOURCE_A, 3)
        recent = datetime.now(UTC) - timedelta(minutes=10)
        old = datetime.now(UTC) - timedelta(minutes=31)
        self.save_state(last_post={"a": recent.isoformat()})

        self.assertEqual(self.run_remixer()["queue"], [["a", "d3"]])
        post.assert_not_called()

        self.save_state(queue=[["a", "d3"]], last_post={"a": old.isoformat()})
        self.assertEqual(self.run_remixer()["posted"], [["a", "d3", 42]])

    def test_explicit_scope_queues_old_items_but_never_posted_ones(
        self, post: Mock
    ) -> None:
        self.add_summarized(SOURCE_A, 1, 2)
        self.save_state(
            posted=[["a", "d1", 7]], last_post={"a": "9999-01-01T00:00:00+00:00"}
        )

        since = self.run_remixer(
            ProcessingScope(since=datetime(2026, 10, 1, tzinfo=UTC))
        )
        self.assertEqual(since["queue"], [["a", "d2"]])

        self.save_state(
            posted=[["a", "d1", 7]], last_post={"a": "9999-01-01T00:00:00+00:00"}
        )
        uids = self.run_remixer(ProcessingScope(source="a", uids=("d1", "d2")))
        self.assertEqual(uids["queue"], [["a", "d2"]])
        post.assert_not_called()

    def test_failed_post_stays_queued_without_leaking_the_token(
        self, post: Mock
    ) -> None:
        post.side_effect = requests.ConnectionError("url: /bottoken/sendMessage")
        self.add_summarized(SOURCE_A, 3)
        self.save_state()

        with self.assertLogs("newsmerger.plugins.telegram", "WARNING") as logs:
            state = self.run_remixer()

        self.assertEqual(state["queue"], [["a", "d3"]])
        self.assertEqual(state["posted"], [])
        self.assertNotIn("token", logs.output[0])

    def test_sends_photo_with_escaped_caption(self, post: Mock) -> None:
        post.return_value = ok_response()
        self.add_summarized(SOURCE_A, 3, image="https://a.test/image.jpg")
        self.save_state()

        self.run_remixer()

        (request_url,) = post.call_args.args
        payload = post.call_args.kwargs["json"]
        self.assertTrue(request_url.endswith("/sendPhoto"))
        self.assertEqual(payload["photo"], "https://a.test/image.jpg")
        self.assertIn("Day &lt;3&gt;", payload["caption"])
        self.assertIn('href="https://a.test/3?a=1&amp;b=2"', payload["caption"])

    def test_sends_text_without_image(self, post: Mock) -> None:
        post.return_value = ok_response()
        self.add_summarized(SOURCE_A, 3)
        self.save_state()

        self.run_remixer()

        (request_url,) = post.call_args.args
        self.assertTrue(request_url.endswith("/sendMessage"))
        self.assertIn("Summary d3", post.call_args.kwargs["json"]["text"])


class BuildCaptionTests(unittest.TestCase):
    def test_caption_is_bounded_and_keeps_link(self) -> None:
        caption = build_caption("Title", "A" * 2000, "https://example.test/article")

        self.assertLessEqual(len(caption), MAX_CAPTION_LENGTH)
        self.assertIn("Original article", caption)
        self.assertIn("https://example.test/article", caption)


if __name__ == "__main__":
    unittest.main()
