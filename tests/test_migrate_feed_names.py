import shutil
import tempfile
import unittest
from pathlib import Path

import click

from newstool.db import Database
from newstool.models import Artifact
from scripts.migrate_feed_names import migrate


class MigrateFeedNamesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="newstool-test-"))
        self.db_path = self.tmp_dir / "data.db"
        self.db = Database(f"sqlite:///{self.db_path}", self.tmp_dir / "content")

    def tearDown(self) -> None:
        self.db.close()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def save(self, remixer: str) -> Artifact:
        self.db.save_artifact(Artifact(remixer, "feed", "<rss/>", "text/xml"))
        return self.db.get_artifact(remixer, "feed")

    def test_renames_keeping_the_id_and_runs_once(self) -> None:
        old = self.save("rssfeed")

        self.assertEqual(migrate(self.db_path), 1)
        self.assertEqual(migrate(self.db_path), 0)

        self.assertIsNone(self.db.get_artifact("rssfeed", "feed"))
        self.assertEqual(self.db.get_artifact("feedgenerator", "feed").id, old.id)

    def test_a_clash_with_new_artifacts_changes_nothing(self) -> None:
        self.save("rssfeed")
        self.save("feedgenerator")

        with self.assertRaises(click.ClickException):
            migrate(self.db_path)
        self.assertIsNotNone(self.db.get_artifact("rssfeed", "feed"))
