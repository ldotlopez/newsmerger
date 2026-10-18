"""Unit tests for newsmerger.db.

Uses a real (file-based, temp-dir) SQLite database per test via
Database's own directory-creation logic — no mocking of SQLAlchemy itself,
since the behavior under test (unit-of-work diffing, upsert semantics,
timestamp rules) only means something against a real engine/session.

Covers Database.upsert_source_items (diff-aware upsert) and the content
storage behind it.
"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import text

from newsmerger.db import Database, DBSource, DBSourceItem, ProcessingStatus
from newsmerger.models import Artifact, SourceData, SourceItem


def make_source(name: str = "Example", provider: str = "exampleprovider") -> SourceData:
    return SourceData(
        name=name,
        url=f"https://example.test/{name.lower()}",
        provider=provider,
    )


def make_item(
    source: SourceData,
    uid: str = "item-1",
    title: str = "Title",
    uri: str | None = None,
    content: bytes = b"content",
    data: dict | None = None,
    published_at: datetime | None = None,
    modified_at: datetime | None = None,
) -> SourceItem:
    return SourceItem(
        source=source,
        uid=uid,
        title=title,
        uri=uri if uri is not None else f"https://example.test/{uid}",
        content=content,
        mimetype="text/html",
        data=data if data is not None else {},
        published_at=published_at,
        modified_at=modified_at,
    )


class DatabaseTestCase(unittest.TestCase):
    """Base class: spins up a fresh temp-file SQLite DB per test."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.mkdtemp(prefix="newsmerger-test-")
        db_path = Path(self.tmp_dir) / "test.db"
        self.db = Database(f"sqlite:///{db_path}", Path(self.tmp_dir) / "content")

    def tearDown(self) -> None:
        self.db.close()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def get_item(self, uid: str) -> DBSourceItem | None:
        with self.db.session_scope() as sess:
            row = sess.query(DBSourceItem).filter(DBSourceItem.uid == uid).one_or_none()
            if row is not None:
                # Detach values we need before the session closes.
                sess.expunge(row)
            return row

    def content_of(self, row: DBSourceItem) -> bytes:
        return self.db.contents.get(row.content_sha256)

    def count_sources(self) -> int:
        with self.db.session_scope() as sess:
            return sess.query(DBSource).count()

    def count_items(self) -> int:
        with self.db.session_scope() as sess:
            return sess.query(DBSourceItem).count()


# ---------------------------------------------------------------------------
# upsert_source_items -- diff-aware upsert
# ---------------------------------------------------------------------------


class UpsertSourceItemsTests(DatabaseTestCase):
    def test_new_row_uses_provider_supplied_dates(self):
        source = make_source()
        pub = datetime(2026, 1, 1, tzinfo=UTC)
        mod = datetime(2026, 1, 2, tzinfo=UTC)
        item = make_item(source, uid="a1", published_at=pub, modified_at=mod)

        self.db.upsert_source_items([item])

        row = self.get_item("a1")
        self.assertEqual(row.published_at, pub)
        self.assertEqual(row.modified_at, mod)

    def test_new_row_falls_back_to_now_when_provider_gives_no_dates(self):
        source = make_source()
        item = make_item(source, uid="a1", published_at=None, modified_at=None)

        before = datetime.now(UTC)
        self.db.upsert_source_items([item])
        after = datetime.now(UTC)

        row = self.get_item("a1")
        self.assertIsNotNone(row.published_at)
        self.assertIsNotNone(row.modified_at)
        self.assertTrue(before <= row.published_at <= after)
        self.assertTrue(before <= row.modified_at <= after)

    def test_identical_resend_is_a_complete_no_op(self):
        source = make_source()
        mod = datetime(2026, 1, 1, tzinfo=UTC)
        item = make_item(
            source, uid="a1", title="Same", content=b"Same", modified_at=mod
        )
        self.db.upsert_source_items([item])

        # Re-send the exact same item later -- nothing should change,
        # in particular modified_at must NOT be bumped to "now".
        self.db.upsert_source_items([item])

        row = self.get_item("a1")
        self.assertEqual(row.modified_at, mod)
        self.assertEqual(self.count_items(), 1)

    def test_content_change_with_newer_provider_date_updates_modified_at(self):
        source = make_source()
        t1 = datetime(2026, 1, 1, tzinfo=UTC)
        t2 = datetime(2026, 1, 5, tzinfo=UTC)

        original = make_item(source, uid="a1", content=b"v1", modified_at=t1)
        self.db.upsert_source_items([original])

        changed = make_item(source, uid="a1", content=b"v2", modified_at=t2)
        self.db.upsert_source_items([changed])

        row = self.get_item("a1")
        self.assertEqual(self.content_of(row), b"v2")
        self.assertEqual(row.modified_at, t2)

    def test_content_change_with_older_provider_date_trusts_database(self):
        source = make_source()
        t_old = datetime(2026, 1, 1, tzinfo=UTC)
        t_stored = datetime(2026, 1, 10, tzinfo=UTC)

        original = make_item(source, uid="a1", content=b"v1", modified_at=t_stored)
        self.db.upsert_source_items([original])

        # Stale/out-of-order re-scrape: content differs, but its modified_at
        # is OLDER than what's already stored.
        stale = make_item(source, uid="a1", content=b"v2", modified_at=t_old)
        self.db.upsert_source_items([stale])

        row = self.get_item("a1")
        self.assertEqual(self.content_of(row), b"v2")  # content still applied
        self.assertEqual(row.modified_at, t_stored)  # but stored date wins

    def test_content_change_with_equal_provider_date_trusts_database(self):
        source = make_source()
        t_stored = datetime(2026, 1, 10, tzinfo=UTC)

        original = make_item(source, uid="a1", content=b"v1", modified_at=t_stored)
        self.db.upsert_source_items([original])

        same_date = make_item(source, uid="a1", content=b"v2", modified_at=t_stored)
        self.db.upsert_source_items([same_date])

        row = self.get_item("a1")
        self.assertEqual(self.content_of(row), b"v2")
        self.assertEqual(row.modified_at, t_stored)  # equal -> not "newer", DB wins

    def test_content_change_with_no_provider_date_falls_back_to_now(self):
        source = make_source()
        t1 = datetime(2026, 1, 1, tzinfo=UTC)
        original = make_item(source, uid="a1", content=b"v1", modified_at=t1)
        self.db.upsert_source_items([original])

        before = datetime.now(UTC)
        changed = make_item(source, uid="a1", content=b"v2", modified_at=None)
        self.db.upsert_source_items([changed])
        after = datetime.now(UTC)

        row = self.get_item("a1")
        self.assertEqual(self.content_of(row), b"v2")
        self.assertTrue(before <= row.modified_at <= after)

    def test_published_at_is_filled_once_and_never_overwritten(self):
        source = make_source()
        item = make_item(source, uid="a1", content=b"v1", published_at=None)

        before = datetime.now(UTC)
        self.db.upsert_source_items([item])
        after = datetime.now(UTC)

        row = self.get_item("a1")
        first_published_at = row.published_at
        self.assertTrue(before <= first_published_at <= after)

        later_published = datetime(2030, 1, 1, tzinfo=UTC)
        changed = make_item(
            source, uid="a1", content=b"v2", published_at=later_published
        )
        self.db.upsert_source_items([changed])

        row = self.get_item("a1")
        self.assertEqual(self.content_of(row), b"v2")
        # published_at must be untouched by the update, despite a new
        # incoming value being present.
        self.assertEqual(row.published_at, first_published_at)

    def test_mixed_new_and_existing_items_in_one_call(self):
        source = make_source()
        existing = make_item(source, uid="a1", content=b"v1")
        self.db.upsert_source_items([existing])

        new_item = make_item(source, uid="a2", content=b"brand new")
        updated_existing = make_item(source, uid="a1", content=b"v2")
        self.db.upsert_source_items([new_item, updated_existing])

        self.assertEqual(self.count_items(), 2)
        self.assertEqual(self.content_of(self.get_item("a1")), b"v2")
        self.assertEqual(self.content_of(self.get_item("a2")), b"brand new")

    def test_shared_source_is_created_only_once(self):
        source = make_source()
        item_a = make_item(source, uid="a1")
        item_b = make_item(source, uid="a2")

        self.db.upsert_source_items([item_a, item_b])

        self.assertEqual(self.count_sources(), 1)
        self.assertEqual(self.count_items(), 2)

    def test_data_dict_change_alone_counts_as_a_change(self):
        source = make_source()
        t1 = datetime(2026, 1, 1, tzinfo=UTC)
        original = make_item(source, uid="a1", data={"tags": ["a"]}, modified_at=t1)
        self.db.upsert_source_items([original])

        t2 = datetime(2026, 1, 2, tzinfo=UTC)
        changed = make_item(source, uid="a1", data={"tags": ["a", "b"]}, modified_at=t2)
        self.db.upsert_source_items([changed])

        row = self.get_item("a1")
        self.assertEqual(row.data, {"tags": ["a", "b"]})
        self.assertEqual(row.modified_at, t2)


class ContentStorageTests(DatabaseTestCase):
    def test_replaced_content_is_deleted(self):
        source = make_source()
        original = make_item(source, uid="a1", content=b"v1")
        self.db.upsert_source_items([original])

        self.db.upsert_source_items([make_item(source, uid="a1", content=b"v2")])

        self.assertEqual(
            list(self.db.contents.iter()), [self.get_item("a1").content_sha256]
        )

    def test_replaced_content_shared_with_another_item_is_kept(self):
        source = make_source()
        shared = make_item(source, uid="a1", content=b"shared")
        self.db.upsert_source_items(
            [shared, make_item(source, uid="a2", content=b"shared")]
        )

        self.db.upsert_source_items([make_item(source, uid="a1", content=b"v2")])

        self.assertEqual(self.content_of(self.get_item("a2")), b"shared")

    def test_get_content_loads_from_storage(self):
        source = make_source()
        self.db.upsert_source_items([make_item(source, uid="a1", content=b"%PDF")])

        (item,) = self.db.get_source_items()

        self.assertIsNone(item.content)
        self.assertEqual(self.db.get_content(item), b"%PDF")


class ConnectionTests(DatabaseTestCase):
    def test_foreign_keys_are_enforced(self):
        with self.db.session_scope() as sess:
            enabled = sess.execute(text("PRAGMA foreign_keys")).scalar()
        self.assertEqual(enabled, 1)


class ProcessingTests(DatabaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.source = make_source()
        self.db.upsert_source_items([make_item(self.source, uid="a1", content=b"v1")])
        (self.item,) = self.db.get_source_items()

    def unprocessed_uids(self, processor: str, **kwargs) -> list[str]:
        return [i.uid for i in self.db.get_unprocessed_items(processor, **kwargs)]

    def test_done_item_is_eligible_again_after_its_content_changes(self):
        self.db.record_result(self.item, "markdownify", ProcessingStatus.DONE)
        self.assertEqual(self.unprocessed_uids("markdownify"), [])

        self.db.upsert_source_items([make_item(self.source, uid="a1", content=b"v2")])

        self.assertEqual(self.unprocessed_uids("markdownify"), ["a1"])

    def test_requires_waits_for_upstream_done_on_current_content(self):
        self.assertEqual(self.unprocessed_uids("tagger", requires="markdownify"), [])

        self.db.record_result(self.item, "markdownify", ProcessingStatus.DONE)
        self.assertEqual(
            self.unprocessed_uids("tagger", requires="markdownify"), ["a1"]
        )

        self.db.upsert_source_items([make_item(self.source, uid="a1", content=b"v2")])
        self.assertEqual(self.unprocessed_uids("tagger", requires="markdownify"), [])

    def test_requires_skips_items_upstream_ignored_even_with_force(self):
        self.db.record_result(self.item, "markdownify", ProcessingStatus.IGNORED)

        self.assertEqual(
            self.unprocessed_uids("tagger", requires="markdownify", force=True), []
        )

    def test_record_result_saves_annotations_and_state_together(self):
        self.db.record_result(
            self.item,
            "markdownify",
            ProcessingStatus.DONE,
            annotations={"markdown": "# Title"},
        )

        self.assertEqual(
            self.db.get_annotations(self.item),
            {"markdownify": {"markdown": "# Title"}},
        )
        self.assertEqual(self.unprocessed_uids("markdownify"), [])

    def test_get_annotation_values_maps_uids_with_the_annotation(self):
        self.db.upsert_source_items([make_item(self.source, uid="a2", content=b"x")])
        items = self.db.get_source_items()
        self.db.record_result(
            self.item, "tagger", ProcessingStatus.DONE, annotations={"tags": ["a"]}
        )

        values = self.db.get_annotation_values(items, processor="tagger", key="tags")

        self.assertEqual(values, {"a1": ["a"]})


class ArtifactTests(DatabaseTestCase):
    def test_save_replaces_and_get_returns_the_artifact(self):
        self.db.save_artifact(
            Artifact("rssfeed", "feed", "<rss/>", "application/rss+xml")
        )
        self.db.save_artifact(
            Artifact("rssfeed", "feed", "<rss>2</rss>", "application/rss+xml")
        )

        artifact = self.db.get_artifact("rssfeed", "feed")

        self.assertEqual(artifact.content, "<rss>2</rss>")
        self.assertIsNotNone(artifact.updated_at)
        self.assertIsNone(self.db.get_artifact("rssfeed", "missing"))


if __name__ == "__main__":
    unittest.main()
