from __future__ import annotations

import json
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock

from newsmerger.db import Database, ProcessingStatus
from newsmerger.models import ProcessingScope, SourceData, SourceItem
from newsmerger.remixers import (
    grouping_avglink,
    grouping_embeddings,
    grouping_singlelink,
    rssfeed,
)

SOURCE = SourceData(id="s", name="S", url="https://s.test/", provider="plaza")


class RemixerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="newsmerger-test-"))
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


class RSSFeedTests(RemixerTestCase):
    def feed(self, **params) -> ET.Element:
        (artifact,) = rssfeed.Remixer(self.db, **params).produce(ProcessingScope())
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
        self.db.record_result(
            item, "tagger", ProcessingStatus.DONE, annotations={"tags": tags}
        )

    def groups(self, module, **params) -> list[list[str]]:
        remixer = module.Remixer(self.db, tau_hours=None, days=10_000, **params)
        return self.groups_of(remixer)

    def groups_of(self, remixer) -> list[list[str]]:
        ((_, content, _),) = remixer.produce(ProcessingScope())
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

        for module in (grouping_singlelink, grouping_avglink):
            self.assertEqual(
                self.groups(module), [["d1", "d2"], ["d3"]], module.__name__
            )

    def test_avglink_does_not_chain_through_a_bridge_item(self) -> None:
        d1, d2, d3 = self.add_items(1, 2, 3)
        self.tag(d1, ["a", "b"])
        self.tag(d2, ["b", "c"])  # bridges d1 and d3
        self.tag(d3, ["c", "d"])

        self.assertEqual(self.groups(grouping_singlelink), [["d1", "d2", "d3"]])
        self.assertEqual(len(self.groups(grouping_avglink)), 2)

    def test_nothing_to_group_produces_no_artifact(self) -> None:
        self.add_items(1)
        remixer = grouping_singlelink.Remixer(self.db)

        self.assertEqual(list(remixer.produce(ProcessingScope())), [])


class EmbeddingGroupingTests(RemixerTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.d1, self.d2, self.d3 = self.add_items(1, 2, 3)
        # No tag overlap at all: only the embeddings can relate them.
        for item, tags in (
            (self.d1, ["BCE"]),
            (self.d2, ["Banco Central Europeo"]),
            (self.d3, ["pleno"]),
        ):
            self.db.record_result(
                item, "tagger", ProcessingStatus.DONE, annotations={"tags": tags}
            )

    def remixer(self, embedding_weight: float) -> grouping_embeddings.Remixer:
        remixer = grouping_embeddings.Remixer(
            self.db,
            model="embedder",
            embedding_weight=embedding_weight,
            tau_hours=None,
            days=10_000,
        )
        remixer.client = Mock()
        remixer.client.embed.return_value = Mock(
            embeddings=[[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]]
        )
        return remixer

    def groups_of(self, remixer) -> tuple[list[list[str]], dict]:
        ((_, content, _),) = remixer.produce(ProcessingScope())
        payload = json.loads(content)
        groups = [
            sorted(member["uid"] for member in group["members"])
            for group in payload["groups"]
        ]
        return groups, payload["params"]

    def test_embeddings_group_variants_without_shared_tags(self) -> None:
        remixer = self.remixer(embedding_weight=0.5)

        groups, params = self.groups_of(remixer)

        self.assertEqual(groups, [["d1", "d2"], ["d3"]])
        remixer.client.embed.assert_called_once_with(
            model="embedder", input=["BCE", "Banco Central Europeo", "pleno"]
        )
        self.assertEqual(params["model"], "embedder")
        self.assertEqual(params["embedding_weight"], 0.5)

    def test_zero_weight_is_plain_tag_overlap(self) -> None:
        groups, _ = self.groups_of(self.remixer(embedding_weight=0.0))

        self.assertEqual(groups, [["d1"], ["d2"], ["d3"]])


if __name__ == "__main__":
    unittest.main()
