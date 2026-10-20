"""The llm bundle with a stubbed Ollama client: no server needed."""

import shutil
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock

from newsmerger.db import Database, ProcessingStatus
from newsmerger.models import ProcessingScope, SourceData, SourceItem
from newsmerger.plugins import llm
from newsmerger.processors import Processor
from newsmerger.remixers import Remixer

SOURCE = SourceData(id="s", name="S", url="https://s.test/", provider="plaza")
OTHER_SOURCE = SourceData(id="o", name="O", url="https://o.test/", provider="plaza")


class EmbedProcessorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="newsmerger-test-"))
        self.db = Database(
            f"sqlite:///{self.tmp_dir}/data.db", self.tmp_dir / "content"
        )
        self.db.upsert_source_items(
            [
                SourceItem(
                    source=SOURCE,
                    uid="1",
                    title="T",
                    uri="https://s.test/1",
                    content=b"<p></p>",
                    mimetype="text/html",
                )
            ]
        )
        (self.item,) = self.db.get_items()
        for processor, annotations in (
            ("markdownify", {"markdown": "# T\n\nBody"}),
            ("tagger", {"tags": ["pleno", "BCE"]}),
        ):
            self.db.record_result(
                self.item, processor, ProcessingStatus.DONE, annotations=annotations
            )

    def tearDown(self) -> None:
        self.db.close()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def embed(self, **options) -> tuple[Mock, dict]:
        client = Mock()
        client.embed.side_effect = lambda model, input: Mock(
            embeddings=[[float(i)] for i, _ in enumerate(input)]
        )
        processor = llm.EmbedProcessor(client, llm.EmbedOptions(**options))
        self.assertEqual(processor.enrich(self.db).done, 1)
        return client, self.db.get_annotations(self.item, processor="embed")["embed"]

    def test_embeds_tags_and_markdown_in_one_call(self) -> None:
        client, annotations = self.embed(model="embedder")

        client.embed.assert_called_once_with(
            model="embedder", input=["BCE, pleno", "# T\n\nBody"]
        )
        self.assertEqual(
            annotations,
            {
                "tags_text": "BCE, pleno",
                "tags_embedding": [0.0],
                "markdown_embedding": [1.0],
            },
        )

    def test_embeds_only_the_configured_inputs(self) -> None:
        _, annotations = self.embed(inputs=["markdown"])

        self.assertEqual(annotations, {"markdown_embedding": [0.0]})


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
        self.db.upsert_source_items(
            [
                SourceItem(
                    source=source,
                    uid=f"d{day}",
                    title=f"Day {day}",
                    uri=f"https://{source.id}.test/{day}",
                    content=b"<p></p>",
                    mimetype="text/html",
                    published_at=datetime(2026, 10, day, tzinfo=UTC),
                )
            ]
        )
        if markdown is not None:
            (item,) = self.db.get_items(
                ProcessingScope(source=source.id, uids=(f"d{day}",))
            )
            self.db.record_result(
                item,
                "markdownify",
                ProcessingStatus.DONE,
                annotations={"markdown": markdown},
            )

    def digest(
        self, scope: ProcessingScope, response: str = "Week.", **options
    ) -> tuple[Mock, list[tuple[str, str, str]]]:
        client = Mock()
        client.generate.return_value = Mock(response=response)
        remixer = llm.DigestRemixer(client, llm.DigestOptions(**options))
        return client, list(remixer.produce(self.db, scope))

    def test_digests_newest_items_with_markdown_oldest_first(self) -> None:
        self.add_item(SOURCE, 1, "Body 1")
        self.add_item(SOURCE, 2, "Body 2 is long")
        self.add_item(SOURCE, 3, None)
        self.add_item(SOURCE, 4, "Body 4")

        client, artifacts = self.digest(
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
            [("s", "# S: 2026-10-01 – 2026-10-08\n\nWeek.\n", "text/markdown")],
        )
        kwargs = client.generate.call_args.kwargs
        self.assertEqual(kwargs["model"], "writer")
        self.assertEqual(kwargs["options"], {"num_ctx": 32768})
        self.assertTrue(
            kwargs["prompt"].endswith(
                "### 1. Day 2\nDate: 2026-10-02\nLink: https://s.test/2\n\nBody 2"
                "\n\n### 2. Day 4\nDate: 2026-10-04\nLink: https://s.test/4\n\nBody 4"
            )
        )

    def test_one_digest_per_source_unless_scoped_to_one(self) -> None:
        self.add_item(SOURCE, 1, "Body")
        self.add_item(OTHER_SOURCE, 2, "Body")
        since = datetime(2026, 10, 1, tzinfo=UTC)

        _, artifacts = self.digest(ProcessingScope(since=since))
        self.assertEqual(sorted(name for name, _, _ in artifacts), ["o", "s"])

        _, artifacts = self.digest(ProcessingScope(source="o", since=since))
        self.assertEqual([name for name, _, _ in artifacts], ["o"])

    def test_nothing_in_scope_produces_nothing(self) -> None:
        self.add_item(SOURCE, 1, "Body")

        client, artifacts = self.digest(ProcessingScope(), days=7)

        self.assertEqual(artifacts, [])
        client.generate.assert_not_called()

    def test_empty_response_is_an_error(self) -> None:
        self.add_item(SOURCE, 1, "Body")

        with self.assertRaises(ValueError):
            self.digest(
                ProcessingScope(since=datetime(2026, 10, 1, tzinfo=UTC)), response=" "
            )


class LLMPluginTests(unittest.TestCase):
    def test_no_sections_enable_every_processor_with_defaults(self) -> None:
        objects = llm.__newsmerger_plugin__()

        self.assertEqual(
            [(name, protocol) for name, protocol, _ in objects],
            [("summarize", Processor), ("tagger", Processor), ("embed", Processor)],
        )
        self.assertEqual(objects[0][2].model, llm.DEFAULT_MODEL)
        self.assertEqual(objects[2][2].model, llm.DEFAULT_EMBEDDING_MODEL)

    def test_sections_enable_only_the_listed_processors(self) -> None:
        objects = llm.__newsmerger_plugin__(
            api_key="secret", tagger={"model": "small"}, summarize=None
        )

        self.assertEqual([name for name, _, _ in objects], ["tagger", "summarize"])
        self.assertEqual(objects[0][2].model, "small")

    def test_digest_is_enabled_only_by_its_section(self) -> None:
        objects = llm.__newsmerger_plugin__(digest={"model": "writer"})

        self.assertEqual(
            [(name, protocol) for name, protocol, _ in objects], [("digest", Remixer)]
        )
        self.assertEqual(objects[0][2].model, "writer")

    def test_api_key_is_not_shown(self) -> None:
        cfg = llm.Options(api_key="secret")

        self.assertNotIn("secret", repr(cfg))


if __name__ == "__main__":
    unittest.main()
