"""The digest remixer with a stub LLM: no server needed."""

import shutil
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock

from newsmerger.db import Database, ProcessingStatus
from newsmerger.models import ProcessingScope, SourceData, SourceItem
from newsmerger.plugins import Services, digest
from newsmerger.remixers import Remixer, UnavailableRemixer

SOURCE = SourceData(id="s", name="S", url="https://s.test/", provider="plaza")
OTHER_SOURCE = SourceData(id="o", name="O", url="https://o.test/", provider="plaza")


class DigestRemixerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="newsmerger-test-"))
        self.db = Database(
            f"sqlite:///{self.tmp_dir}/data.db", self.tmp_dir / "content"
        )

    def tearDown(self) -> None:
        self.db.close()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def add_item(self, source: SourceData, day: int, markdown: str | None) -> None:
        item = SourceItem(
            source=source,
            uid=f"d{day}",
            title=f"Day {day}",
            uri=f"https://{source.id}.test/{day}",
            content=b"<p></p>",
            mimetype="text/html",
            published_at=datetime(2026, 10, day, tzinfo=UTC),
        )
        self.db.upsert_source_items([item])
        if markdown is not None:
            self.db.record_result(
                item,
                "markdownify",
                ProcessingStatus.DONE,
                annotations={"markdown": markdown},
            )

    def digest(
        self, scope: ProcessingScope, response: str = "Week.", **options
    ) -> tuple[Mock, list[tuple[str, str, str]]]:
        llm = Mock()
        llm.prompt.return_value = response
        remixer = digest.DigestRemixer(llm, digest.Options(**options))
        return llm, list(remixer.produce(self.db, scope))

    def test_digests_newest_items_with_markdown_oldest_first(self) -> None:
        self.add_item(SOURCE, 1, "Body 1")
        self.add_item(SOURCE, 2, "Body 2 is long")
        self.add_item(SOURCE, 3, None)
        self.add_item(SOURCE, 4, "Body 4")

        llm, artifacts = self.digest(
            ProcessingScope(
                since=datetime(2026, 10, 1, tzinfo=UTC),
                until=datetime(2026, 10, 8, tzinfo=UTC),
            ),
            response="```markdown\nWeek.\n```",
            model="writer",
            max_items=2,
            max_article_chars=6,
        )

        self.assertEqual(
            artifacts,
            [
                (
                    "s/2026-10-01_2026-10-08",
                    "# S: 2026-10-01 – 2026-10-08\n\nWeek.\n",
                    "text/markdown",
                )
            ],
        )
        (prompt,), kwargs = llm.prompt.call_args
        self.assertEqual(kwargs, {"model": "writer", "context_length": 32768})
        self.assertTrue(
            prompt.endswith(
                "### 1. Day 2\nDate: 2026-10-02\nLink: https://s.test/2\n\nBody 2"
                "\n\n### 2. Day 4\nDate: 2026-10-04\nLink: https://s.test/4\n\nBody 4"
            )
        )

    def test_one_digest_per_source_unless_scoped_to_one(self) -> None:
        self.add_item(SOURCE, 1, "Body")
        self.add_item(OTHER_SOURCE, 2, "Body")
        since = datetime(2026, 10, 1, tzinfo=UTC)

        _, artifacts = self.digest(ProcessingScope(since=since))
        self.assertEqual(
            sorted(name.split("/")[0] for name, _, _ in artifacts), ["o", "s"]
        )

        _, artifacts = self.digest(ProcessingScope(source="o", since=since))
        ((name, _, _),) = artifacts
        self.assertTrue(name.startswith("o/2026-10-01_"))

    def test_nothing_in_scope_produces_nothing(self) -> None:
        self.add_item(SOURCE, 1, "Body")

        llm, artifacts = self.digest(ProcessingScope(), days=7)

        self.assertEqual(artifacts, [])
        llm.prompt.assert_not_called()

    def test_empty_response_is_an_error(self) -> None:
        self.add_item(SOURCE, 1, "Body")

        with self.assertRaises(ValueError):
            self.digest(
                ProcessingScope(since=datetime(2026, 10, 1, tzinfo=UTC)), response=" "
            )


class DigestPluginTests(unittest.TestCase):
    def test_uses_the_requested_llm(self) -> None:
        llm = Mock()

        ((name, protocol, remixer),) = digest.__newsmerger_plugin__(
            Services({"ollama": llm}), model="writer"
        )

        self.assertEqual((name, protocol), ("digest", Remixer))
        self.assertIs(remixer.llm, llm)
        self.assertEqual(remixer.model, "writer")

    def test_without_its_llm_it_logs_and_produces_nothing(self) -> None:
        ((name, _, remixer),) = digest.__newsmerger_plugin__(Services())

        self.assertEqual(name, "digest")
        self.assertIsInstance(remixer, UnavailableRemixer)
        with self.assertLogs("newsmerger.remixers", "ERROR") as logs:
            self.assertEqual(remixer.remix(Mock()), [])
        self.assertIn(
            "digest: no llm is loaded (llm plugins must be listed before the plugins that use them); nothing produced",
            logs.output[0],
        )


if __name__ == "__main__":
    unittest.main()
