import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from sqlalchemy import MetaData, create_engine

from newsmerger.db import Base, Database, ProcessingStatus
from newsmerger.models import Artifact, SourceData, SourceItem
from scripts.migrate_autoincrement import migrate

SOURCE = SourceData(id="a", name="A", url="https://a.test/", provider="plaza")


def make_item(uid: str) -> SourceItem:
    return SourceItem(
        source=SOURCE,
        uid=uid,
        title=uid,
        uri=f"https://a.test/{uid}",
        content=uid.encode(),
        mimetype="text/html",
    )


class MigrateAutoincrementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="newsmerger-test-"))
        self.db_path = self.tmp_dir / "data.db"
        self.url = f"sqlite:///{self.db_path}"

        # The schema before decision 0008: the same tables, without AUTOINCREMENT.
        legacy = MetaData()
        for table in Base.metadata.sorted_tables:
            table.to_metadata(legacy).dialect_options["sqlite"]["autoincrement"] = False
        engine = create_engine(self.url)
        legacy.create_all(engine)
        engine.dispose()

        db = Database(self.url, self.tmp_dir / "content", create_schema=False)
        db.upsert_source_items([make_item("i1"), make_item("i2")])
        db.record_result(
            make_item("i1"),
            "summarize",
            ProcessingStatus.DONE,
            annotations={"summary": "S"},
        )
        db.save_artifact(Artifact("rssfeed", "feed", "<rss/>", "application/rss+xml"))
        db.close()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def query(self, sql: str) -> list[tuple]:
        connection = sqlite3.connect(self.db_path)
        try:
            return connection.execute(sql).fetchall()
        finally:
            connection.close()

    def test_tables_get_autoincrement_and_keep_their_rows(self) -> None:
        before = {
            table: self.query(f"SELECT * FROM {table} ORDER BY id")
            for table in ("source_items", "item_annotations", "artifacts")
        }

        migrated = migrate(self.db_path)

        self.assertEqual(
            set(migrated),
            {
                "source_items",
                "processing_state",
                "item_annotations",
                "artifacts",
                "deliveries",
            },
        )
        for (sql,) in self.query(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name IN"
            " ('source_items', 'processing_state', 'item_annotations', 'artifacts')"
        ):
            self.assertIn("AUTOINCREMENT", sql)
        for table, rows in before.items():
            self.assertEqual(self.query(f"SELECT * FROM {table} ORDER BY id"), rows)
        self.assertEqual(self.query("PRAGMA foreign_key_check"), [])
        self.assertIn(
            ("ix_source_items_content_sha256",),
            self.query("SELECT name FROM sqlite_master WHERE type = 'index'"),
        )

    def test_deleted_ids_are_not_reused_and_a_second_run_does_nothing(self) -> None:
        migrate(self.db_path)
        self.assertEqual(migrate(self.db_path), [])

        connection = sqlite3.connect(self.db_path)
        connection.execute("DELETE FROM source_items WHERE uid = 'i2'")
        connection.commit()
        connection.close()
        db = Database(self.url, self.tmp_dir / "content")
        db.upsert_source_items([make_item("i3")])
        db.close()

        self.assertEqual(
            self.query("SELECT uid, id FROM source_items ORDER BY id"),
            [("i1", 1), ("i3", 3)],
        )


if __name__ == "__main__":
    unittest.main()
