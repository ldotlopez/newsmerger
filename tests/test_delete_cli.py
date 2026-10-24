"""The delete commands end to end, on a temp database through the CLI."""

import shutil
import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner

from newsmerger.cli import cli
from newsmerger.db import Database, DeliveryStatus, ProcessingStatus
from newsmerger.models import Artifact, ProcessingScope, SourceData, SourceItem

SOURCE = SourceData(id="a", name="A", url="https://a.test/", provider="plaza")


class DeleteCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="newsmerger-test-"))
        self.config = self.tmp_dir / "config.yaml"
        self.config.write_text(
            f"db:\n  uri: sqlite:///{self.tmp_dir}/data.db\n"
            f"  content_dir: {self.tmp_dir}/content\n"
            f"cache:\n  base_dir: {self.tmp_dir}/cache\n"
        )
        self.db = Database(
            f"sqlite:///{self.tmp_dir}/data.db", self.tmp_dir / "content"
        )
        self.items = [
            SourceItem(
                source=SOURCE,
                uid=uid,
                title=uid,
                uri=f"https://a.test/{uid}",
                content=uid.encode(),
                mimetype="text/html",
            )
            for uid in ("i1", "i2")
        ]
        self.db.upsert_source_items(self.items)
        for item in self.items:
            self.db.record_result(
                item,
                "tagger",
                ProcessingStatus.DONE,
                annotations={"tags": ["t"], "tags_text": "t"},
            )

    def tearDown(self) -> None:
        self.db.close()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def run_cli(self, *args: str):
        return CliRunner().invoke(cli, ["-c", str(self.config), *args])

    def deliver(self, item: SourceItem) -> None:
        self.db.queue_item_deliveries("telegram", ProcessingScope(item_ids=(item.id,)))

    def test_items_with_deliveries_are_skipped_unless_forced(self) -> None:
        self.deliver(self.items[0])

        result = self.run_cli("delete", "items", "--source", "a")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Skipped item 1: it has deliveries", result.stderr)
        self.assertIn("Deleted 1 item(s)", result.stdout)
        self.assertEqual([item.uid for item in self.db.get_items()], ["i1"])

        forced = self.run_cli("delete", "items", "--item", "1", "--force")
        self.assertIn("Deleted 1 item(s)", forced.stdout)
        self.assertEqual(self.db.get_items(), [])
        self.assertEqual(self.db.find_deliveries(), [])

    def test_a_selection_without_filters_is_refused(self) -> None:
        for args in (("items", "--limit", "1"), ("annotations",), ("artifacts",)):
            with self.subTest(command=args[0]):
                result = self.run_cli("delete", *args)

                self.assertEqual(result.exit_code, 2)
                self.assertIn("name a filter or an id", result.output)
        self.assertEqual(len(self.db.get_items()), 2)

    def test_annotations_are_deleted_per_processor(self) -> None:
        args = ("annotations", "--processor", "tagger", "--item", "1")
        listed = self.run_cli("inspect", *args)
        self.assertIn("tagger.tags_text", listed.output)

        result = self.run_cli("delete", *args)

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Deleted 2 annotation(s)", result.stdout)
        self.assertEqual([a.item_id for a in self.db.find_annotations()], [2, 2])
        pending = self.db.get_unprocessed_items("tagger", version=None, max_retries=3)
        self.assertEqual([item.uid for item in pending], ["i1"])

    def test_single_annotation_keys_cannot_be_deleted(self) -> None:
        for option, value in (("--key", "tags"), ("--annotation", "1")):
            with self.subTest(option=option):
                result = self.run_cli("delete", "annotations", option, value)

                self.assertEqual(result.exit_code, 2)
                self.assertIn("No such option", result.output)
                self.assertIn(option, result.output)
        self.assertEqual(len(self.db.find_annotations()), 4)

    def test_annotations_refuse_a_limit(self) -> None:
        result = self.run_cli(
            "delete", "annotations", "--processor", "tagger", "--limit", "1"
        )

        self.assertEqual(result.exit_code, 2)
        self.assertIn("deleted per processor", result.output)
        self.assertEqual(len(self.db.find_annotations()), 4)

    def test_artifacts_with_deliveries_are_skipped_unless_forced(self) -> None:
        for name in ("a/1", "a/2"):
            self.db.save_artifact(Artifact("digest", name, name, "text/markdown"))
        self.db.queue_artifact_deliveries(
            "telegram_artifacts", ["digest"], names=[("digest", "a/1")]
        )

        result = self.run_cli("delete", "artifacts", "--remixer", "digest")
        missing = self.run_cli("delete", "artifacts", "--artifact", "digest/a/9")

        self.assertIn("Skipped artifact digest/a/1", result.stderr)
        self.assertIn("Deleted 1 artifact(s)", result.stdout)
        self.assertEqual([a.name for a in self.db.list_artifacts()], ["a/1"])
        self.assertEqual(missing.exit_code, 1)
        self.assertIn("no artifact digest/a/9 in the selection", missing.output)
        (row,) = self.db.find_deliveries()
        self.assertEqual(row.status, DeliveryStatus.QUEUED)


if __name__ == "__main__":
    unittest.main()
