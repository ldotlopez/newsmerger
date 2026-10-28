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
        # Two runs of one processor, each with its own key and state.
        for item in self.items:
            for key in ("tags_embedding", "markdown_embedding"):
                self.db.record_result(
                    item, "embed", key, ProcessingStatus.DONE, value=[0.5]
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
        for args in (
            ("items", "--limit", "1"),
            ("annotations", "--limit", "1"),
            ("artifacts",),
            ("deliveries", "--limit", "1"),
        ):
            with self.subTest(command=args[0]):
                result = self.run_cli("delete", *args)

                self.assertEqual(result.exit_code, 2)
                self.assertIn("name a filter or an id", result.output)
        self.assertEqual(len(self.db.get_items()), 2)

    def test_annotations_are_deleted_per_processor(self) -> None:
        args = ("annotations", "--processor", "embed", "--item", "1")
        listed = self.run_cli("inspect", *args)
        self.assertIn("embed.markdown_embedding", listed.output)

        result = self.run_cli("delete", *args)

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Deleted 2 annotation(s)", result.stdout)
        self.assertEqual([a.item_id for a in self.db.find_annotations()], [2, 2])
        for key in ("tags_embedding", "markdown_embedding"):
            pending = self.db.get_unprocessed_items(key, version=None, max_retries=3)
            self.assertEqual([item.uid for item in pending], ["i1"])

    def test_annotations_are_deleted_by_key_without_a_processor(self) -> None:
        args = ("annotations", "--key", "tags_embedding")
        listed = self.run_cli("inspect", *args)
        self.assertEqual(listed.output.count("embed.tags_embedding"), 2)

        result = self.run_cli("delete", *args)

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Deleted 2 annotation(s)", result.stdout)
        self.assertEqual(
            {a.key for a in self.db.find_annotations()}, {"markdown_embedding"}
        )
        for key, uids in (("tags_embedding", ["i1", "i2"]), ("markdown_embedding", [])):
            pending = self.db.get_unprocessed_items(key, version=None, max_retries=3)
            self.assertEqual([item.uid for item in pending], uids)

    def test_annotations_are_deleted_by_id_and_limit(self) -> None:
        by_id = self.run_cli("delete", "annotations", "--annotation", "1")
        missing = self.run_cli("delete", "annotations", "--annotation", "1")
        limited = self.run_cli(
            "delete", "annotations", "--processor", "embed", "--limit", "1"
        )

        self.assertIn("Deleted 1 annotation(s)", by_id.stdout)
        self.assertEqual(missing.exit_code, 1)
        self.assertIn("no annotation 1 in the selection", missing.output)
        self.assertIn("Deleted 1 annotation(s)", limited.stdout)
        self.assertEqual(len(self.db.find_annotations()), 2)

    def test_deliveries_are_deleted_with_the_inspect_selection(self) -> None:
        for item in self.items:
            self.deliver(item)
        self.db.queue_item_deliveries("other", ProcessingScope())
        args = ("deliveries", "--sink", "telegram", "--item", "1")
        listed = self.run_cli("inspect", *args)
        self.assertIn("item 1", listed.output)
        self.assertNotIn("item 2", listed.output)

        result = self.run_cli("delete", *args)

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Deleted 1 delivery(ies)", result.stdout)
        self.assertEqual(
            sorted((d.sink, d.item_id) for d in self.db.find_deliveries()),
            [("other", 1), ("other", 2), ("telegram", 2)],
        )
        self.assertEqual(len(self.db.get_items()), 2)

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
