from __future__ import annotations

import json
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

from newstool.db import Database, ProcessingStatus
from newstool.models import ProcessingScope, SourceData, SourceItem
from newstool.plugins import Services, feedgenerator, grouping
from newstool.remixers import RemixerType

SOURCE = SourceData(id="s", name="S", url="https://s.test/", provider="plaza")


class RemixerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="newstool-test-"))
        self.db = Database(
            f"sqlite:///{self.tmp_dir}/data.db", self.tmp_dir / "content"
        )

    def tearDown(self) -> None:
        self.db.close()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def add_items(self, *days: int) -> list[SourceItem]:
        self.db.upsert_source_items(
            [
                SourceItem(
                    source=SOURCE,
                    uid=f"d{day}",
                    title=f"Day {day}",
                    uri=f"https://s.test/{day}",
                    content=f"<p>{day}</p>".encode(),
                    mimetype="text/html",
                    published_at=datetime(2026, 10, day, tzinfo=UTC),
                )
                for day in days
            ]
        )
        return self.db.get_items()


class FeedGeneratorTests(RemixerTestCase):
    def feed(self, **params) -> ET.Element:
        remixer = feedgenerator.FeedGeneratorRemixer(
            feedgenerator.Options(**params), Services()
        )
        (artifact,) = remixer.produce(self.db, ProcessingScope())
        name, content, content_type = artifact
        self.assertEqual((name, content_type), ("feed", "application/rss+xml"))
        return ET.fromstring(content)

    def test_newest_items_first_capped_at_max_items(self) -> None:
        self.add_items(1, 2, 3)

        channel = self.feed(max_items=2).find("channel")

        titles = [item.findtext("title") for item in channel.findall("item")]
        self.assertEqual(titles, ["Day 3", "Day 2"])

    def test_channel_has_required_elements_and_unique_guids(self) -> None:
        self.add_items(1)

        channel = self.feed(title="News", link="https://news.test/").find("channel")

        self.assertEqual(channel.findtext("title"), "News")
        self.assertEqual(channel.findtext("link"), "https://news.test/")
        self.assertEqual(channel.findtext("description"), "News")
        self.assertEqual(channel.find("item").findtext("guid"), "s/d1")

    def test_link_is_omitted_when_not_configured(self) -> None:
        self.assertIsNone(self.feed().find("channel").find("link"))


class GroupingTests(RemixerTestCase):
    def tag(self, item: SourceItem, tags: list[str]) -> None:
        self.db.record_result(item, "tagger", "tags", ProcessingStatus.DONE, value=tags)

    def groups(self, remixer_class) -> list[list[str]]:
        cfg = grouping.GroupingOptions(tau=None, lookback="10000d")
        remixer = remixer_class(cfg, Services())
        ((_, content, _),) = remixer.produce(self.db, ProcessingScope())
        return [
            sorted(member["uid"] for member in group["members"])
            for group in json.loads(content)["groups"]
        ]

    def test_groups_by_tag_overlap_and_keeps_singletons(self) -> None:
        d1, d2, d3, _untagged = self.add_items(1, 2, 3, 4)
        self.tag(d1, ["fiestas", "grau"])
        self.tag(d2, ["fiestas", "grau"])
        self.tag(d3, ["pleno"])
        # The fourth item has no tags: it can't be grouped and is left out.

        for remixer_class in (grouping.SingleLinkRemixer, grouping.AverageLinkRemixer):
            self.assertEqual(
                self.groups(remixer_class), [["d1", "d2"], ["d3"]], remixer_class
            )

    def test_avglink_does_not_chain_through_a_bridge_item(self) -> None:
        d1, d2, d3 = self.add_items(1, 2, 3)
        self.tag(d1, ["a", "b"])
        self.tag(d2, ["b", "c"])  # bridges d1 and d3
        self.tag(d3, ["c", "d"])

        self.assertEqual(self.groups(grouping.SingleLinkRemixer), [["d1", "d2", "d3"]])
        self.assertEqual(len(self.groups(grouping.AverageLinkRemixer)), 2)

    def test_nothing_to_group_produces_no_artifact(self) -> None:
        self.add_items(1)
        cfg = grouping.GroupingOptions()
        remixer = grouping.SingleLinkRemixer(cfg, Services())

        self.assertEqual(list(remixer.produce(self.db, ProcessingScope())), [])


class EmbeddingGroupingTests(RemixerTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.d1, self.d2, self.d3, self.d4 = self.add_items(1, 2, 3, 4)
        # No tag overlap at all: only the embeddings can relate them.
        for item, tags, embedding in (
            (self.d1, ["BCE"], [1.0, 0.0]),
            (self.d2, ["Banco Central Europeo"], [0.9, 0.1]),
            (self.d3, ["pleno"], [0.0, 1.0]),
            (self.d4, ["BCE"], None),  # tagged, but not embedded yet
        ):
            self.db.record_result(
                item, "tagger", "tags", ProcessingStatus.DONE, value=tags
            )
            if embedding is not None:
                self.db.record_result(
                    item,
                    "embed",
                    "tags_embedding",
                    ProcessingStatus.DONE,
                    value=embedding,
                )

    def groups_of(self, **options) -> tuple[list[list[str]], dict]:
        cfg = grouping.EmbeddingsOptions(tau=None, lookback="10000d", **options)
        ((_, content, _),) = grouping.EmbeddingsRemixer(cfg, Services()).produce(
            self.db, ProcessingScope()
        )
        payload = json.loads(content)
        groups = [
            sorted(member["uid"] for member in group["members"])
            for group in payload["groups"]
        ]
        return groups, payload["params"]

    def test_embeddings_group_variants_without_shared_tags(self) -> None:
        groups, params = self.groups_of(embedding_weight=0.5)

        # d4 has no embedding: it is left out.
        self.assertEqual(groups, [["d1", "d2"], ["d3"]])
        self.assertEqual(params["algorithm"], "embeddings")
        self.assertEqual(params["embedding"], "tags")
        self.assertEqual(params["embedding_weight"], 0.5)

    def test_zero_weight_is_plain_tag_overlap(self) -> None:
        groups, _ = self.groups_of(embedding_weight=0.0)

        self.assertEqual(groups, [["d1"], ["d2"], ["d3"]])

    def test_reads_the_configured_embedding(self) -> None:
        groups, _ = self.groups_of(embedding="markdown")

        self.assertEqual(groups, [])


class GroupingPluginTests(unittest.TestCase):
    def test_registers_every_remixer_class(self) -> None:
        registered = grouping.__newstool_plugin__()

        names = [name for name, _, _ in registered]
        self.assertEqual(names, ["singlelink", "avglink", "embeddings"])
        for _, protocol, cls in registered:
            self.assertIs(protocol, RemixerType)
            self.assertIsInstance(cls, RemixerType)


if __name__ == "__main__":
    unittest.main()
