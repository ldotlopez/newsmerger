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
        self,
        prompt: str,
        *,
        model: str | None = None,
        json_mode: bool = False,
        context_length: int | None = None,
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
        for processor, key, value in (
            ("markdownify", "markdown", "# T\n\nBody"),
            ("tagger", "tags", ["pleno", "BCE"]),
        ):
            self.db.record_result(
                self.item, processor, key, ProcessingStatus.DONE, value=value
            )

    def tearDown(self) -> None:
        self.db.close()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def annotation(self, processor: Processor, key: str, **options) -> object:
        """Run `processor` with `options`, writing `key`; return its value."""
        summary = processor.enrich(self.db, key=key, force=True, **options)
        self.assertEqual(summary.done, 1)
        return self.db.get_annotations(self.item, key=key)[key]


class SummarizeTests(ProcessorTestCase):
    def test_summarizes_with_the_backend_model_unless_overridden(self) -> None:
        llm = StubLLM(" A summary. ")
        processor = summarize.SummarizeProcessor(llm, summarize.Options())

        self.assertEqual(self.annotation(processor, "summary"), "A summary.")
        self.assertEqual(llm.calls[0][2], {"model": None, "json_mode": False})

        processor.model = "small"
        self.annotation(processor, "summary")
        self.assertEqual(llm.calls[1][2]["model"], "small")

    def test_run_options_override_the_section_and_write_their_own_key(
        self,
    ) -> None:
        llm = StubLLM("Resumen.")
        processor = summarize.SummarizeProcessor(
            llm, summarize.Options(model="small", prompt="Summarize: ")
        )

        self.annotation(processor, "summary")
        self.annotation(processor, "summary/es", prompt="Resume: ", model="big")

        self.assertEqual(
            [(call[1], call[2]["model"]) for call in llm.calls],
            [("Summarize: # T\n\nBody", "small"), ("Resume: # T\n\nBody", "big")],
        )
        self.assertEqual(
            self.db.get_annotations(self.item).keys() & {"summary", "summary/es"},
            {"summary", "summary/es"},
        )

    def test_output_key_rejects_options_the_processor_does_not_take(self) -> None:
        self.assertEqual(summarize.SummarizeProcessor.output_key(), "summary")
        with self.assertRaises(TypeError):
            summarize.SummarizeProcessor.output_key(temperature=1)


class TaggerTests(ProcessorTestCase):
    def test_merges_json_tags_with_the_item_tags(self) -> None:
        llm = StubLLM('```json\n{"items": ["BCE", "Pleno"]}\n```')
        processor = tagger.TaggerProcessor(llm, tagger.Options(model="small"))

        self.assertEqual(self.annotation(processor, "tags"), ["BCE", "Pleno"])
        self.assertEqual(llm.calls[0][2], {"model": "small", "json_mode": True})


class EmbedTests(ProcessorTestCase):
    def test_embeds_the_tags_text_by_default(self) -> None:
        llm = StubLLM()
        processor = embed.EmbedProcessor(llm, embed.Options(model="embedder"))

        self.assertEqual(self.annotation(processor, "tags_embedding"), [0.0])
        self.assertEqual(llm.calls, [("embed", ["BCE, pleno"], {"model": "embedder"})])

    def test_embeds_the_input_each_run_names(self) -> None:
        llm = StubLLM()
        processor = embed.EmbedProcessor(llm, embed.Options())

        self.annotation(processor, "markdown_embedding", input="markdown")

        self.assertEqual(llm.calls, [("embed", ["# T\n\nBody"], {"model": None})])
        self.assertEqual(processor.required_key(input="markdown"), "markdown")

    def test_output_key_follows_the_input(self) -> None:
        self.assertEqual(embed.EmbedProcessor.output_key(), "tags_embedding")
        self.assertEqual(
            embed.EmbedProcessor.output_key(input="markdown"), "markdown_embedding"
        )
        with self.assertRaisesRegex(ValueError, "input must be one of"):
            embed.EmbedProcessor.output_key(input="title")


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
        llm.prompt("hi", model="other", json_mode=True, context_length=8192)
        self.assertEqual(llm.embed(["text"]), [[1.0, 2.0]])

        self.assertEqual(
            [call.kwargs for call in client.generate.call_args_list],
            [
                {
                    "model": "chat",
                    "prompt": "hi",
                    "stream": False,
                    "format": None,
                    "options": None,
                },
                {
                    "model": "other",
                    "prompt": "hi",
                    "stream": False,
                    "format": "json",
                    "options": {"num_ctx": 8192},
                },
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
