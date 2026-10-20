"""The LLM plugins: the ollama backend with a stubbed client, and its
consumers with a stub LLM. No server needed."""

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from newsmerger.db import Database, ProcessingStatus
from newsmerger.llms import LLM, LLMUnavailableError
from newsmerger.models import SourceData, SourceItem
from newsmerger.plugins import Services, embed, ollama, summarize, tagger
from newsmerger.processors import Processor, UnavailableProcessor

SOURCE = SourceData(id="s", name="S", url="https://s.test/", provider="plaza")


class StubLLM:
    def __init__(self, response: str = "") -> None:
        self.response = response
        self.calls: list[tuple[str, object, dict]] = []

    def prompt(
        self, prompt: str, *, model: str | None = None, json_mode: bool = False
    ) -> str:
        self.calls.append(("prompt", prompt, {"model": model, "json_mode": json_mode}))
        return self.response

    def embed(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        self.calls.append(("embed", texts, {"model": model}))
        return [[float(i)] for i, _ in enumerate(texts)]


class ServicesTests(unittest.TestCase):
    def test_none_is_the_first_loaded_llm(self) -> None:
        first, second = StubLLM(), StubLLM()
        services = Services({"a": first, "b": second})

        self.assertIs(services.llm(), first)
        self.assertIs(services.llm("b"), second)

    def test_unavailable_llms_raise(self) -> None:
        with self.assertRaisesRegex(LLMUnavailableError, "no llm is loaded"):
            Services().llm()
        with self.assertRaisesRegex(LLMUnavailableError, "llm 'b' is not loaded"):
            Services({"a": StubLLM()}).llm("b")


class ProcessorTestCase(unittest.TestCase):
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
                    data={"tags": ["bce"]},
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

    def annotations(self, processor: Processor, name: str) -> dict:
        self.assertEqual(processor.enrich(self.db, force=True).done, 1)
        return self.db.get_annotations(self.item, processor=name)[name]


class SummarizeTests(ProcessorTestCase):
    def test_summarizes_with_the_backend_model_unless_overridden(self) -> None:
        llm = StubLLM(" A summary. ")
        processor = summarize.SummarizeProcessor(llm, summarize.Options())

        self.assertEqual(
            self.annotations(processor, "summarize"), {"summary": "A summary."}
        )
        self.assertEqual(llm.calls[0][2], {"model": None, "json_mode": False})

        processor.model = "small"
        self.annotations(processor, "summarize")
        self.assertEqual(llm.calls[1][2]["model"], "small")


class TaggerTests(ProcessorTestCase):
    def test_merges_json_tags_with_the_item_tags(self) -> None:
        llm = StubLLM('```json\n{"items": ["BCE", "Pleno"]}\n```')
        processor = tagger.TaggerProcessor(llm, tagger.Options(model="small"))

        self.assertEqual(
            self.annotations(processor, "tagger"), {"tags": ["BCE", "Pleno"]}
        )
        self.assertEqual(llm.calls[0][2], {"model": "small", "json_mode": True})


class EmbedTests(ProcessorTestCase):
    def test_embeds_tags_and_markdown_in_one_call(self) -> None:
        llm = StubLLM()
        processor = embed.EmbedProcessor(llm, embed.Options(model="embedder"))

        self.assertEqual(
            self.annotations(processor, "embed"),
            {
                "tags_text": "BCE, pleno",
                "tags_embedding": [0.0],
                "markdown_embedding": [1.0],
            },
        )
        self.assertEqual(
            llm.calls, [("embed", ["BCE, pleno", "# T\n\nBody"], {"model": "embedder"})]
        )

    def test_embeds_only_the_configured_inputs(self) -> None:
        processor = embed.EmbedProcessor(StubLLM(), embed.Options(inputs=["markdown"]))

        self.assertEqual(
            self.annotations(processor, "embed"), {"markdown_embedding": [0.0]}
        )


class ConsumerPluginTests(unittest.TestCase):
    def test_consumers_use_the_requested_llm(self) -> None:
        first, second = StubLLM(), StubLLM()
        services = Services({"a": first, "b": second})

        for plugin, options, expected in (
            (summarize, {}, first),
            (tagger, {"llm": "b"}, second),
            (embed, {"llm": "a", "model": "e"}, first),
        ):
            with self.subTest(plugin=plugin.__name__):
                ((_, protocol, processor),) = plugin.__newsmerger_plugin__(
                    services, **options
                )
                self.assertIs(protocol, Processor)
                self.assertIs(processor.llm, expected)

    def test_consumers_without_their_llm_are_unavailable(self) -> None:
        for plugin, name in (
            (summarize, "summarize"),
            (tagger, "tagger"),
            (embed, "embed"),
        ):
            with self.subTest(plugin=name):
                ((object_name, _, processor),) = plugin.__newsmerger_plugin__(
                    Services({"a": StubLLM()}), llm="missing"
                )
                self.assertEqual(object_name, name)
                self.assertIsInstance(processor, UnavailableProcessor)
                self.assertIn("llm 'missing' is not loaded", processor.reason)


class OllamaTests(unittest.TestCase):
    def test_uses_the_default_models_unless_overridden(self) -> None:
        client = Mock()
        client.generate.return_value = Mock(response="ok")
        client.embed.return_value = Mock(embeddings=[(1.0, 2.0)])
        llm = ollama.OllamaLLM(client, "chat", "embedder")

        self.assertEqual(llm.prompt("hi"), "ok")
        llm.prompt("hi", model="other", json_mode=True)
        self.assertEqual(llm.embed(["text"]), [[1.0, 2.0]])

        self.assertEqual(
            [call.kwargs for call in client.generate.call_args_list],
            [
                {"model": "chat", "prompt": "hi", "stream": False, "format": None},
                {"model": "other", "prompt": "hi", "stream": False, "format": "json"},
            ],
        )
        client.embed.assert_called_once_with(model="embedder", input=["text"])

    def test_provides_one_llm_named_ollama(self) -> None:
        ((name, protocol, llm),) = ollama.__newsmerger_plugin__(
            Services(), chat_model="chat"
        )

        self.assertEqual((name, protocol), ("ollama", LLM))
        self.assertEqual(
            (llm.chat_model, llm.embed_model), ("chat", ollama.DEFAULT_EMBED_MODEL)
        )

    def test_api_key_is_not_shown(self) -> None:
        cfg = ollama.Options(api_key="secret")

        self.assertNotIn("secret", repr(cfg))


if __name__ == "__main__":
    unittest.main()
