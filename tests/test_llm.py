"""The llm bundle with a stubbed Ollama client: no server needed."""

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from newsmerger.db import Database, ProcessingStatus
from newsmerger.models import SourceData, SourceItem
from newsmerger.plugins import llm
from newsmerger.processors import Processor

SOURCE = SourceData(id="s", name="S", url="https://s.test/", provider="plaza")


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

    def test_api_key_is_not_shown(self) -> None:
        cfg = llm.Options(api_key="secret")

        self.assertNotIn("secret", repr(cfg))


if __name__ == "__main__":
    unittest.main()
