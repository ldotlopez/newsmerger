import shutil
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import Mock

import pydantic

from newstool.db import Database, DBDelivery, DeliveryStatus, ProcessingStatus
from newstool.errors import PluginFailure
from newstool.models import Artifact, ProcessingScope, SourceData, SourceItem
from newstool.plugins import Services
from newstool.processors import RunSummary
from newstool.sinks import (
    ArtifactDeliveryOptions,
    BaseArtifactSink,
    BaseItemSink,
    DeliveryOptions,
    SelectionRequiredError,
)

SOURCE_A = SourceData(id="a", name="A", url="https://a.test/", provider="plaza")
SOURCE_B = SourceData(id="b", name="B", url="https://b.test/", provider="plaza")


class RecordingItemSink(BaseItemSink[DeliveryOptions]):
    name = "recorder"
    requires = "summary"
    options_model = DeliveryOptions

    def __init__(self, failing: set[str] | None = None, **options) -> None:
        super().__init__(DeliveryOptions.model_validate(options), Services())
        self.failing = failing or set()
        self.sent: list[str] = []

    def run(self, db: Database, **kwargs) -> RunSummary:
        return self.deliver(db, key="recorder", **kwargs)

    def send(self, db: Database, subject: SourceItem) -> dict:
        if subject.uid in self.failing:
            raise RuntimeError(f"{subject.uid} rejected")
        self.sent.append(subject.uid)
        return {"message_id": len(self.sent)}


class RecordingArtifactSink(BaseArtifactSink[ArtifactDeliveryOptions]):
    name = "artifact_recorder"
    options_model = ArtifactDeliveryOptions

    def __init__(self, **options) -> None:
        options = {"artifacts": ["digest"], **options}
        super().__init__(ArtifactDeliveryOptions.model_validate(options), Services())
        self.sent: list[str] = []

    def run(self, db: Database, **kwargs) -> RunSummary:
        return self.deliver(db, key="artifacts", **kwargs)

    def send(self, db: Database, subject: Artifact) -> dict:
        self.sent.append(subject.name)
        return {"message_id": len(self.sent)}


class SinkTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="newstool-test-"))
        self.db = Database(
            f"sqlite:///{self.tmp_dir}/data.db", self.tmp_dir / "content"
        )
        self.now = datetime.now(UTC)

    def tearDown(self) -> None:
        self.db.close()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def add(
        self, source: SourceData, uid: str, hours_ago: float, summarized: bool = True
    ) -> SourceItem:
        item = SourceItem(
            source=source,
            uid=uid,
            title=uid,
            uri=f"https://{source.id}.test/{uid}",
            content=uid.encode(),
            mimetype="text/html",
            published_at=self.now - timedelta(hours=hours_ago),
        )
        self.db.upsert_source_items([item])
        if summarized:
            self.db.record_result(
                item, "summarize", "summary", ProcessingStatus.DONE, value="S"
            )
        return item

    def statuses(self, sink: str = "recorder") -> dict[str, str]:
        return {item.uid: row.status for row, item in self.db.get_item_deliveries(sink)}


class ItemSinkTests(SinkTestCase):
    def test_delivers_summarized_items_of_the_lookback_window_once(self) -> None:
        old = self.add(SOURCE_A, "old", hours_ago=30)
        self.add(SOURCE_A, "new", hours_ago=2)
        self.add(SOURCE_A, "bare", hours_ago=1, summarized=False)
        sink = RecordingItemSink()

        summary = sink.run(self.db)
        sink.run(self.db)

        self.assertEqual((summary.done, summary.failed), (1, 0))
        self.assertEqual(sink.sent, ["new"])
        ((row, item),) = self.db.get_item_deliveries("recorder")
        self.assertEqual(row.status, DeliveryStatus.DONE)
        self.assertEqual(row.external_ref, {"message_id": 1})
        self.assertEqual(row.content_sha256, item.content_sha256)

        sink.run(self.db, scope=ProcessingScope(item_ids=(old.id,)))
        self.assertEqual(sink.sent, ["new", "old"])

    def test_interval_paces_the_whole_entry_oldest_first(self) -> None:
        self.add(SOURCE_B, "b1", hours_ago=3)
        self.add(SOURCE_A, "a1", hours_ago=2)
        sink = RecordingItemSink(interval="30m")

        sink.run(self.db)
        sink.run(self.db)  # the first delivery is not 30 minutes old yet

        self.assertEqual(sink.sent, ["b1"])
        ((row, _),) = self.db.get_item_deliveries("recorder", statuses=["done"])
        row.updated_at = self.now - timedelta(minutes=31)
        with self.db.session_scope() as sess:  # save_delivery would stamp it now
            sess.get_one(DBDelivery, row.id).updated_at = row.updated_at
        sink.run(self.db)
        self.assertEqual(sink.sent, ["b1", "a1"])

    def test_max_per_run_caps_every_run(self) -> None:
        for number in range(3):
            self.add(SOURCE_A, f"a{number}", hours_ago=3 - number)
        sink = RecordingItemSink(max_per_run=2)

        sink.run(self.db)
        self.assertEqual(sink.sent, ["a0", "a1"])
        sink.run(self.db)
        self.assertEqual(sink.sent, ["a0", "a1", "a2"])

    def test_options_are_validated(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            RecordingItemSink(max_per_run=0)
        with self.assertRaises(pydantic.ValidationError):
            RecordingItemSink(chat_id="x")

    def test_a_failure_holds_back_its_source_until_it_is_due(self) -> None:
        self.add(SOURCE_A, "a1", hours_ago=3)
        self.add(SOURCE_A, "a2", hours_ago=2)
        self.add(SOURCE_B, "b1", hours_ago=1)
        sink = RecordingItemSink(failing={"a1"})

        with self.assertLogs("newstool.sinks", "ERROR"):
            summary = sink.run(self.db)
        sink.run(self.db)  # a1 is in its backoff: nothing of source a moves

        self.assertEqual((summary.done, summary.failed), (2, 1))
        self.assertEqual(sink.sent, ["a2", "b1"])
        self.assertEqual(self.statuses()["a1"], DeliveryStatus.ERROR)

    def test_an_expected_failure_is_logged_without_traceback(self) -> None:
        self.add(SOURCE_A, "a1", hours_ago=1)
        sink = RecordingItemSink(failing={"a1"})
        sink.send = Mock(side_effect=PluginFailure("a1 rejected"))

        with self.assertLogs("newstool.sinks", "ERROR") as logs:
            sink.run(self.db)

        self.assertTrue(logs.records[0].getMessage().endswith(": a1 rejected"))
        self.assertIsNone(logs.records[0].exc_info)
        ((row, _),) = self.db.get_item_deliveries("recorder")
        self.assertEqual(row.last_error, "a1 rejected")

    def test_exhausted_rows_stay_failed_and_the_queue_moves_on(self) -> None:
        self.add(SOURCE_A, "a1", hours_ago=3)
        self.add(SOURCE_A, "a2", hours_ago=2)
        sink = RecordingItemSink(failing={"a1", "a2"}, max_retries=1)

        with self.assertLogs("newstool.sinks", "ERROR"):
            sink.run(self.db)
        sink.failing = set()
        sink.run(self.db)

        self.assertEqual(sink.sent, [])
        self.assertEqual(
            self.statuses(), {"a1": DeliveryStatus.ERROR, "a2": DeliveryStatus.ERROR}
        )

    def test_requeue_gives_failed_rows_fresh_attempts(self) -> None:
        self.add(SOURCE_A, "a1", hours_ago=3)
        sink = RecordingItemSink(failing={"a1"}, max_retries=1)
        with self.assertLogs("newstool.sinks", "ERROR"):
            sink.run(self.db)
        sink.failing = set()

        sink.run(self.db, requeue=True)

        self.assertEqual(sink.sent, ["a1"])
        self.assertEqual(self.statuses(), {"a1": DeliveryStatus.DONE})

    def test_interrupted_rows_are_never_retried(self) -> None:
        self.add(SOURCE_A, "a1", hours_ago=3)
        self.db.queue_item_deliveries("recorder", ProcessingScope())
        ((row, _),) = self.db.get_item_deliveries("recorder")
        row.status = DeliveryStatus.SENDING
        self.db.save_delivery(row)
        sink = RecordingItemSink()

        with self.assertLogs("newstool.sinks", "WARNING") as logs:
            sink.run(self.db)

        self.assertEqual(sink.sent, [])
        self.assertIn("delete deliveries --status sending", logs.output[0])

    def test_force_resends_the_selected_items_whatever_their_state(self) -> None:
        item = self.add(SOURCE_A, "a1", hours_ago=3)
        sink = RecordingItemSink()
        sink.run(self.db)

        with self.assertRaises(SelectionRequiredError):
            sink.run(self.db, force=True)
        sink.run(self.db, scope=ProcessingScope(item_ids=(item.id,)), force=True)

        self.assertEqual(sink.sent, ["a1", "a1"])
        ((row, _),) = self.db.get_item_deliveries("recorder")
        self.assertEqual(row.external_ref, {"message_id": 2})


class ArtifactSinkTests(SinkTestCase):
    def test_delivers_new_artifacts_of_its_remixers_once(self) -> None:
        self.db.save_artifact(Artifact("digest", "a/1", "# A", "text/markdown"))
        self.db.save_artifact(Artifact("feedgenerator", "feed", "<rss/>", "text/xml"))
        sink = RecordingArtifactSink()

        sink.run(self.db)
        self.db.save_artifact(Artifact("digest", "a/1", "# A again", "text/markdown"))
        sink.run(self.db)

        self.assertEqual(sink.sent, ["a/1"])

    def test_force_needs_and_sends_the_named_artifacts(self) -> None:
        self.db.save_artifact(Artifact("digest", "a/1", "# A", "text/markdown"))
        sink = RecordingArtifactSink(lookback=0)

        with self.assertRaises(SelectionRequiredError):
            sink.run(self.db, force=True)
        sink.run(self.db, artifacts=(("digest", "a/1"),), force=True)

        self.assertEqual(sink.sent, ["a/1"])


if __name__ == "__main__":
    unittest.main()
