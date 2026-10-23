"""Unit tests for newsmerger.db.

Uses a real (file-based, temp-dir) SQLite database per test, without mocking
SQLAlchemy: unit-of-work diffing, upsert semantics and timestamp rules only
mean something against a real engine and session.
"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from newsmerger.db import (
    Database,
    DBDelivery,
    DBProcessingState,
    DBSource,
    DBSourceItem,
    DeliveryStatus,
    ProcessingStatus,
)
from newsmerger.models import Artifact, ProcessingScope, SourceData, SourceItem


def make_source(source_id: str = "example", name: str = "Example") -> SourceData:
    return SourceData(
        id=source_id,
        name=name,
        url=f"https://example.test/{source_id}",
        provider="exampleprovider",
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

    def get_item(self, uid: str, source_id: str = "example") -> DBSourceItem | None:
        with self.db.session_scope() as sess:
            row = (
                sess.query(DBSourceItem)
                .filter_by(source_id=source_id, uid=uid)
                .one_or_none()
            )
            if row is not None:
                sess.expunge(row)
            return row

    def content_of(self, row: DBSourceItem) -> bytes:
        return self.db.contents.get(row.content_sha256)

    def stored_contents(self) -> set[str]:
        return set(self.db.contents.iter())

    def count(self, model: type) -> int:
        with self.db.session_scope() as sess:
            return sess.query(model).count()


class UpsertSourceItemsTests(DatabaseTestCase):
    def test_new_row_uses_provider_supplied_dates(self):
        source = make_source()
        pub = datetime(2026, 1, 1, tzinfo=UTC)
        mod = datetime(2026, 1, 2, tzinfo=UTC)

        self.db.upsert_source_items(
            [make_item(source, uid="a1", published_at=pub, modified_at=mod)]
        )

        row = self.get_item("a1")
        self.assertEqual(row.published_at, pub)
        self.assertEqual(row.modified_at, mod)

    def test_new_row_falls_back_to_now_when_provider_gives_no_dates(self):
        before = datetime.now(UTC)
        self.db.upsert_source_items([make_item(make_source(), uid="a1")])
        after = datetime.now(UTC)

        row = self.get_item("a1")
        self.assertTrue(before <= row.published_at <= after)
        self.assertTrue(before <= row.modified_at <= after)

    def test_identical_resend_is_a_complete_no_op(self):
        mod = datetime(2026, 1, 1, tzinfo=UTC)
        item = make_item(make_source(), uid="a1", modified_at=mod)
        self.db.upsert_source_items([item])

        self.db.upsert_source_items([item])

        self.assertEqual(self.get_item("a1").modified_at, mod)
        self.assertEqual(self.count(DBSourceItem), 1)

    def test_content_change_with_newer_provider_date_updates_modified_at(self):
        source = make_source()
        t1 = datetime(2026, 1, 1, tzinfo=UTC)
        t2 = datetime(2026, 1, 5, tzinfo=UTC)
        self.db.upsert_source_items(
            [make_item(source, uid="a1", content=b"v1", modified_at=t1)]
        )

        self.db.upsert_source_items(
            [make_item(source, uid="a1", content=b"v2", modified_at=t2)]
        )

        row = self.get_item("a1")
        self.assertEqual(self.content_of(row), b"v2")
        self.assertEqual(row.modified_at, t2)

    def test_content_change_with_older_or_equal_provider_date_trusts_database(self):
        source = make_source()
        t_stored = datetime(2026, 1, 10, tzinfo=UTC)
        self.db.upsert_source_items(
            [make_item(source, uid="a1", content=b"v1", modified_at=t_stored)]
        )

        for content, modified_at in (
            (b"v2", t_stored - timedelta(days=9)),
            (b"v3", t_stored),
        ):
            self.db.upsert_source_items(
                [make_item(source, uid="a1", content=content, modified_at=modified_at)]
            )
            row = self.get_item("a1")
            self.assertEqual(self.content_of(row), content)
            self.assertEqual(row.modified_at, t_stored)

    def test_content_change_with_no_provider_date_falls_back_to_now(self):
        source = make_source()
        t1 = datetime(2026, 1, 1, tzinfo=UTC)
        self.db.upsert_source_items(
            [make_item(source, uid="a1", content=b"v1", modified_at=t1)]
        )

        before = datetime.now(UTC)
        self.db.upsert_source_items([make_item(source, uid="a1", content=b"v2")])
        after = datetime.now(UTC)

        self.assertTrue(before <= self.get_item("a1").modified_at <= after)

    def test_published_at_is_set_once_and_never_overwritten(self):
        source = make_source()
        self.db.upsert_source_items([make_item(source, uid="a1", content=b"v1")])
        first_published_at = self.get_item("a1").published_at

        self.db.upsert_source_items(
            [
                make_item(
                    source,
                    uid="a1",
                    content=b"v2",
                    published_at=datetime(2030, 1, 1, tzinfo=UTC),
                )
            ]
        )

        self.assertEqual(self.get_item("a1").published_at, first_published_at)

    def test_data_dict_change_alone_counts_as_a_change(self):
        source = make_source()
        t1 = datetime(2026, 1, 1, tzinfo=UTC)
        t2 = datetime(2026, 1, 2, tzinfo=UTC)
        self.db.upsert_source_items(
            [make_item(source, uid="a1", data={"tags": ["a"]}, modified_at=t1)]
        )

        self.db.upsert_source_items(
            [make_item(source, uid="a1", data={"tags": ["a", "b"]}, modified_at=t2)]
        )

        row = self.get_item("a1")
        self.assertEqual(row.data, {"tags": ["a", "b"]})
        self.assertEqual(row.modified_at, t2)


class IdentityTests(DatabaseTestCase):
    def test_same_uid_in_two_sources_is_two_items(self):
        a, b = make_source("a"), make_source("b")

        self.db.upsert_source_items(
            [make_item(a, uid="same"), make_item(b, uid="same")]
        )

        self.assertEqual(self.count(DBSourceItem), 2)
        self.assertEqual(
            sorted(item.key for item in self.db.get_items()),
            [("a", "same"), ("b", "same")],
        )

    def test_uri_is_not_unique(self):
        source = make_source()

        self.db.upsert_source_items(
            [
                make_item(source, uid="a1", uri="https://x/1"),
                make_item(source, uid="a2", uri="https://x/1"),
            ]
        )

        self.assertEqual(self.count(DBSourceItem), 2)

    def test_upsert_sets_ids_that_reimports_keep(self):
        source = make_source()
        first = [make_item(source, uid="a1"), make_item(source, uid="a2")]
        self.db.upsert_source_items(first)
        again = make_item(source, uid="a2", title="Changed")
        self.db.upsert_source_items([again])

        self.assertEqual([item.id for item in first], [1, 2])
        self.assertEqual(again.id, 2)
        self.assertEqual([item.id for item in self.db.get_items()], [1, 2])

    def test_reimport_updates_the_source_row(self):
        self.db.upsert_source_items([make_item(make_source(name="Old"))])
        self.db.upsert_source_items([make_item(make_source(name="New"))])

        self.assertEqual(self.count(DBSource), 1)
        (item,) = self.db.get_items()
        self.assertEqual(item.source.name, "New")


class ContentStorageTests(DatabaseTestCase):
    def test_replaced_content_is_deleted(self):
        source = make_source()
        self.db.upsert_source_items([make_item(source, uid="a1", content=b"v1")])

        self.db.upsert_source_items([make_item(source, uid="a1", content=b"v2")])

        self.assertEqual(self.stored_contents(), {self.get_item("a1").content_sha256})

    def test_replaced_content_shared_with_another_item_is_kept(self):
        source = make_source()
        self.db.upsert_source_items(
            [
                make_item(source, uid="a1", content=b"shared"),
                make_item(source, uid="a2", content=b"shared"),
            ]
        )

        self.db.upsert_source_items([make_item(source, uid="a1", content=b"v2")])

        self.assertEqual(self.content_of(self.get_item("a2")), b"shared")

    def test_get_content_loads_from_storage(self):
        self.db.upsert_source_items(
            [make_item(make_source(), uid="a1", content=b"%PDF")]
        )

        (item,) = self.db.get_items()

        self.assertIsNone(item.content)
        self.assertEqual(self.db.get_content(item), b"%PDF")


class GetItemsTests(DatabaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        source = make_source()
        self.db.upsert_source_items(
            [
                make_item(
                    source,
                    uid=f"d{day}",
                    published_at=datetime(2026, 1, day, tzinfo=UTC),
                )
                for day in (1, 2, 3)
            ]
        )

    def uids(self, **kwargs) -> list[str]:
        return [item.uid for item in self.db.get_items(**kwargs)]

    def test_oldest_first_by_default_and_limit_keeps_the_first(self):
        self.assertEqual(self.uids(), ["d1", "d2", "d3"])
        self.assertEqual(self.uids(scope=ProcessingScope(limit=2)), ["d1", "d2"])

    def test_newest_first_with_limit_keeps_the_newest(self):
        self.assertEqual(
            self.uids(scope=ProcessingScope(limit=2), newest_first=True), ["d3", "d2"]
        )

    def test_scope_filters_by_source_dates_and_ids(self):
        since = datetime(2026, 1, 2, tzinfo=UTC)
        self.assertEqual(self.uids(scope=ProcessingScope(since=since)), ["d2", "d3"])
        self.assertEqual(self.uids(scope=ProcessingScope(until=since)), ["d1"])
        self.assertEqual(self.uids(scope=ProcessingScope(item_ids=(3,))), ["d3"])
        self.assertEqual(self.uids(scope=ProcessingScope(source="other")), [])


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
        (self.item,) = self.db.get_items()

    def unprocessed_uids(self, processor: str, **kwargs) -> list[str]:
        kwargs.setdefault("version", None)
        kwargs.setdefault("max_retries", 3)
        return [i.uid for i in self.db.get_unprocessed_items(processor, **kwargs)]

    def attempts(self, processor: str) -> int:
        with self.db.session_scope() as sess:
            return (
                sess.query(DBProcessingState)
                .filter_by(processor=processor)
                .one()
                .attempts
            )

    def test_done_item_is_eligible_again_after_its_content_changes(self):
        self.db.record_result(self.item, "markdownify", ProcessingStatus.DONE)
        self.assertEqual(self.unprocessed_uids("markdownify"), [])

        self.db.upsert_source_items([make_item(self.source, uid="a1", content=b"v2")])

        self.assertEqual(self.unprocessed_uids("markdownify"), ["a1"])

    def test_version_change_makes_done_items_eligible(self):
        self.db.record_result(
            self.item, "markdownify", ProcessingStatus.DONE, version="1"
        )

        self.assertEqual(self.unprocessed_uids("markdownify", version="1"), [])
        self.assertEqual(self.unprocessed_uids("markdownify", version="2"), ["a1"])

    def test_ignored_item_is_only_revisited_when_forced(self):
        self.db.record_result(self.item, "markdownify", ProcessingStatus.IGNORED)

        self.assertEqual(self.unprocessed_uids("markdownify"), [])
        self.assertEqual(self.unprocessed_uids("markdownify", force=True), ["a1"])

    def test_errors_stop_at_max_retries(self):
        for _ in range(3):
            self.db.record_result(self.item, "markdownify", ProcessingStatus.ERROR)

        self.assertEqual(self.attempts("markdownify"), 3)
        self.assertEqual(self.unprocessed_uids("markdownify"), [])

    def test_forced_run_resets_attempts(self):
        for _ in range(3):
            self.db.record_result(self.item, "markdownify", ProcessingStatus.ERROR)

        self.db.record_result(
            self.item, "markdownify", ProcessingStatus.ERROR, reset_attempts=True
        )

        self.assertEqual(self.attempts("markdownify"), 1)

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


class AnnotationTests(DatabaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.source = make_source()
        self.db.upsert_source_items([make_item(self.source, uid="a1", content=b"v1")])
        (self.item,) = self.db.get_items()

    def annotate(self, item: SourceItem, processor: str, **values) -> None:
        self.db.record_result(
            item, processor, ProcessingStatus.DONE, annotations=values
        )

    def test_annotations_round_trip_through_storage(self):
        self.annotate(self.item, "markdownify", markdown="# Title")

        self.assertEqual(
            self.db.get_annotations(self.item), {"markdownify": {"markdown": "# Title"}}
        )
        self.assertEqual(len(self.stored_contents()), 2)  # item content + value

    def test_replaced_annotation_value_is_released(self):
        self.annotate(self.item, "summarize", summary="first")
        self.annotate(self.item, "summarize", summary="second")

        self.assertEqual(
            self.db.get_annotations(self.item, processor="summarize"),
            {"summarize": {"summary": "second"}},
        )
        self.assertEqual(len(self.stored_contents()), 2)

    def test_get_annotation_values_is_keyed_by_source_and_uid(self):
        other = make_source("other")
        self.db.upsert_source_items([make_item(other, uid="a1", content=b"x")])
        items = self.db.get_items()
        self.annotate(self.item, "tagger", tags=["a"])

        values = self.db.get_annotation_values(items, processor="tagger", key="tags")

        self.assertEqual(values, {("example", "a1"): ["a"]})

    def test_get_annotation_keys_lists_ids_processors_and_keys_by_item(self):
        other = make_item(self.source, uid="a2", content=b"x")
        self.db.upsert_source_items([other])
        self.annotate(self.item, "tagger", tags=["a"], tags_text="a")
        self.annotate(self.item, "markdownify", markdown="# T")

        keys = self.db.get_annotation_keys([self.item, other])

        self.assertEqual(
            keys,
            {
                self.item.id: [
                    (3, "markdownify", "markdown"),
                    (1, "tagger", "tags"),
                    (2, "tagger", "tags_text"),
                ]
            },
        )

    def test_find_annotations_combines_scope_processor_key_ids_and_limit(self):
        other = make_item(self.source, uid="a2", content=b"x")
        self.db.upsert_source_items([other])
        self.annotate(self.item, "tagger", tags=["a"], tags_text="a")
        self.annotate(other, "tagger", tags=["b"])
        self.annotate(other, "markdownify", markdown="# T")

        def found(scope=None, **filters) -> list[tuple[int, str, str]]:
            return [
                (a.item_id, f"{a.processor}.{a.key}", a.value)
                for a in self.db.find_annotations(scope, **filters)
            ]

        self.assertEqual(
            found(ProcessingScope(item_ids=(other.id,))),
            [
                (other.id, "markdownify.markdown", "# T"),
                (other.id, "tagger.tags", ["b"]),
            ],
        )
        self.assertEqual(
            found(processor="tagger", key="tags"),
            [(self.item.id, "tagger.tags", ["a"]), (other.id, "tagger.tags", ["b"])],
        )
        self.assertEqual(
            found(annotation_ids=[2]), [(self.item.id, "tagger.tags_text", "a")]
        )
        self.assertEqual(len(found(ProcessingScope(limit=3))), 3)

    def test_delete_by_item_and_processor_makes_the_item_pending(self):
        self.annotate(self.item, "markdownify", markdown="# Title")
        self.annotate(self.item, "tagger", tags=["a"])

        deleted = self.db.delete_annotations(processor="markdownify", item=self.item)

        self.assertEqual(deleted, 1)
        self.assertEqual(
            self.db.get_annotations(self.item), {"tagger": {"tags": ["a"]}}
        )
        self.assertEqual(
            [
                i.uid
                for i in self.db.get_unprocessed_items(
                    "markdownify", version=None, max_retries=3
                )
            ],
            ["a1"],
        )
        self.assertEqual(self.count(DBProcessingState), 1)
        self.assertEqual(len(self.stored_contents()), 2)  # item content + tags

    def test_delete_by_processor_covers_every_item(self):
        other = make_source("other")
        self.db.upsert_source_items([make_item(other, uid="b1", content=b"x")])
        for item in self.db.get_items():
            self.annotate(item, "tagger", tags=[item.uid])

        self.assertEqual(self.db.delete_annotations(processor="tagger"), 2)
        self.assertEqual(self.count(DBProcessingState), 0)

    def test_delete_needs_a_processor_or_an_item(self):
        with self.assertRaises(ValueError):
            self.db.delete_annotations()


class ArtifactTests(DatabaseTestCase):
    def test_save_replaces_and_get_returns_the_artifact(self):
        self.db.save_artifact(
            Artifact("rssfeed", "feed", "<rss/>", "application/rss+xml")
        )
        first = self.db.get_artifact("rssfeed", "feed")
        self.db.save_artifact(
            Artifact("rssfeed", "feed", "<rss>2</rss>", "application/rss+xml")
        )

        artifact = self.db.get_artifact("rssfeed", "feed")

        self.assertEqual(artifact.content, "<rss>2</rss>")
        self.assertEqual(artifact.created_at, first.created_at)
        self.assertEqual(artifact.id, first.id)
        self.assertGreaterEqual(artifact.updated_at, first.updated_at)
        self.assertEqual(self.stored_contents(), {artifact.content_sha256})

    def test_missing_artifact_is_none(self):
        self.assertIsNone(self.db.get_artifact("rssfeed", "missing"))

    def test_list_artifacts_returns_metadata_without_content(self):
        for remixer, name in (("rssfeed", "feed"), ("grouping_avglink", "current")):
            self.db.save_artifact(Artifact(remixer, name, f"{name}!", "text/plain"))

        listed = self.db.list_artifacts()
        only_rss = self.db.list_artifacts("rssfeed")

        self.assertEqual(
            [(a.remixer, a.name) for a in listed],
            [("grouping_avglink", "current"), ("rssfeed", "feed")],
        )
        self.assertTrue(all(a.content is None for a in listed))
        self.assertEqual([a.name for a in only_rss], ["feed"])

    def test_list_artifacts_by_names_and_limit(self):
        for remixer, name in (("rssfeed", "feed"), ("digest", "a/2026-10-01")):
            self.db.save_artifact(Artifact(remixer, name, f"{name}!", "text/plain"))

        named = self.db.list_artifacts(names=[("digest", "a/2026-10-01")])
        limited = self.db.list_artifacts(limit=1)

        self.assertEqual(
            [(a.remixer, a.name) for a in named], [("digest", "a/2026-10-01")]
        )
        self.assertEqual([a.remixer for a in limited], ["digest"])


class DeliveryTests(DatabaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.source = make_source()
        self.items = [
            make_item(
                self.source,
                uid=f"d{day}",
                content=f"c{day}".encode(),
                published_at=datetime(2026, 10, day, tzinfo=UTC),
            )
            for day in (3, 1, 2)
        ]
        self.db.upsert_source_items(self.items)

    def summarize(self, item: SourceItem) -> None:
        self.db.record_result(
            item, "summarize", ProcessingStatus.DONE, annotations={"summary": "S"}
        )

    def test_queue_items_once_in_fifo_order_and_only_finished_upstream(self):
        self.summarize(self.items[0])
        self.summarize(self.items[2])

        queued = self.db.queue_item_deliveries(
            "telegram", ProcessingScope(), requires="summarize"
        )
        again = self.db.queue_item_deliveries(
            "telegram", ProcessingScope(), requires="summarize"
        )

        self.assertEqual((queued, again), (2, 0))
        rows = self.db.get_item_deliveries("telegram")
        self.assertEqual([item.uid for _, item in rows], ["d2", "d3"])
        self.assertTrue(all(row.status == DeliveryStatus.QUEUED for row, _ in rows))

    def test_scope_and_statuses_filter_rows(self):
        self.db.queue_item_deliveries("telegram", ProcessingScope())
        (first, _), *_ = self.db.get_item_deliveries("telegram")
        first.status = DeliveryStatus.DONE
        self.db.save_delivery(first)

        done = self.db.get_item_deliveries("telegram", statuses=[DeliveryStatus.DONE])
        in_scope = self.db.get_item_deliveries(
            "telegram", ProcessingScope(item_ids=(self.items[0].id,))
        )

        self.assertEqual([item.uid for _, item in done], ["d1"])
        self.assertEqual([item.uid for _, item in in_scope], ["d3"])
        self.assertEqual(self.db.get_item_deliveries("other"), [])

    def test_last_delivery_by_source_counts_done_rows_only(self):
        self.db.queue_item_deliveries("telegram", ProcessingScope())
        rows = self.db.get_item_deliveries("telegram")
        rows[0][0].status = DeliveryStatus.DONE
        self.db.save_delivery(rows[0][0])
        rows[1][0].status = DeliveryStatus.ERROR
        self.db.save_delivery(rows[1][0])

        last = self.db.last_delivery_by_source("telegram")

        self.assertEqual(last, {"example": rows[0][0].updated_at})
        self.assertIsNotNone(last["example"].tzinfo)

    def test_queue_artifacts_of_the_listed_remixers(self):
        for remixer, name in (
            ("digest", "a/1"),
            ("digest", "a/2"),
            ("rssfeed", "feed"),
        ):
            self.db.save_artifact(Artifact(remixer, name, name, "text/markdown"))

        named = self.db.queue_artifact_deliveries(
            "telegram_artifacts", ["digest"], names=[("digest", "a/2")]
        )
        rest = self.db.queue_artifact_deliveries(
            "telegram_artifacts", ["digest"], since=datetime(2026, 1, 1, tzinfo=UTC)
        )

        self.assertEqual((named, rest), (1, 1))
        rows = self.db.get_artifact_deliveries("telegram_artifacts")
        self.assertEqual([artifact.name for _, artifact in rows], ["a/1", "a/2"])
        self.assertEqual(rows[0][0].artifact_name, "digest/a/1")

    def test_find_deliveries_filters_by_subject_sink_and_status(self):
        self.db.queue_item_deliveries("telegram", ProcessingScope())
        self.db.save_artifact(Artifact("digest", "a/1", "x", "text/markdown"))
        self.db.queue_artifact_deliveries("telegram_artifacts", ["digest"])

        def found(scope=None, **filters) -> list[tuple[str, int | None, str | None]]:
            return [
                (row.sink, row.item_id, row.artifact_name)
                for row in self.db.find_deliveries(scope, **filters)
            ]

        self.assertEqual(len(found()), 4)
        self.assertEqual(
            found(ProcessingScope(item_ids=(self.items[1].id,))),
            [("telegram", self.items[1].id, None)],
        )
        self.assertEqual(
            found(artifact_names=[("digest", "a/1")]),
            [("telegram_artifacts", None, "digest/a/1")],
        )
        self.assertEqual(len(found(sink="telegram", status=DeliveryStatus.QUEUED)), 3)
        self.assertEqual(found(status=DeliveryStatus.DONE), [])

    def test_a_row_has_exactly_one_subject(self):
        with self.assertRaises(IntegrityError), self.db.session_scope() as sess:
            sess.add(
                DBDelivery(
                    sink="telegram",
                    status="queued",
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )
            )

    def test_rows_go_with_their_item(self):
        self.db.queue_item_deliveries("telegram", ProcessingScope())

        with self.db.session_scope() as sess:
            sess.query(DBSourceItem).filter_by(uid="d1").delete()

        self.assertEqual(self.count(DBDelivery), 2)


if __name__ == "__main__":
    unittest.main()
