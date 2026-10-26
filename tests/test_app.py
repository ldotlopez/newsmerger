"""Application end to end on a temp database, with real plugins that need no
network (markdownify, feedgenerator) and a stubbed HTTP fetcher."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from foundation.plugin import PluginNotFoundError

from newsmerger.app import Application, LockedError
from newsmerger.config import Config, ConfigError
from newsmerger.db import DeliveryStatus
from newsmerger.models import ProcessingScope, SourceItem
from newsmerger.plugins.ollama import OllamaLLM
from newsmerger.processors import RunSummary

SAMPLE = Path(__file__).parent / "samples" / "prensaiberica-item-132310503.html"
SAMPLE_UID = "ec16b09f034ca03296e75d7e5c304f10337f2e77a0327b0d045c54f0a1d970e8"


class ApplicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="newsmerger-test-"))
        self.app = self.make_app()

    def tearDown(self) -> None:
        self.app.close()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def make_app(
        self, plugins: str = "  markdownify:\n  feedgenerator: {title: Test feed}\n"
    ) -> Application:
        config = Config.from_text(
            f"""
sources:
  - id: mediterraneo
    name: Mediterraneo
    provider: prensaiberica
    url: https://www.elperiodicomediterraneo.com/castello
  - id: juntas
    name: Juntas
    provider: csjuntasgobierno
    url: https://www.castello.es/es/sesiones
plugins:
  prensaiberica:
  csjuntasgobierno:
{plugins}
db:
  uri: sqlite:///{self.tmp_dir}/data.db
  content_dir: {self.tmp_dir}/content
cache:
  base_dir: {self.tmp_dir}/cache
"""
        )
        return Application(config)

    def import_sample(self) -> SourceItem:
        provider = self.app._providers["prensaiberica"]
        item_data = provider.parse_item(SAMPLE.read_bytes())
        with patch.object(provider, "retrieve_items", return_value=iter([item_data])):
            (item,) = self.app.import_source("mediterraneo")
        return item

    def test_import_stores_the_item_in_the_configured_source(self) -> None:
        item = self.import_sample()

        (stored,) = self.app.get_items()
        self.assertEqual(stored.key, ("mediterraneo", SAMPLE_UID))
        self.assertEqual(self.app.get_content(stored), item.content)
        self.assertEqual(item.key, stored.key)
        self.assertEqual(item.id, stored.id)

    def test_provider_options_reach_the_provider(self) -> None:
        app = self.make_rss_app("{article_selector: .body}")
        provider = app._providers["feedreader"]
        with patch.object(provider, "retrieve_items", return_value=iter([])) as call:
            app.import_source("blog")
        app.close()

        call.assert_called_once_with(
            app.config.get_source("blog"), app._fetcher, article_selector=".body"
        )

    def test_unknown_provider_option_is_a_config_error(self) -> None:
        with self.assertRaisesRegex(ConfigError, "sources.blog.provider_options"):
            self.make_rss_app("{selector: .body}")

    def make_rss_app(self, provider_options: str) -> Application:
        return Application(
            Config.from_text(
                f"""
sources:
  - id: blog
    name: Blog
    provider: feedreader
    url: https://blog.test/feed
    provider_options: {provider_options}
plugins:
  feedreader:
db:
  uri: sqlite:///{self.tmp_dir}/rss.db
  content_dir: {self.tmp_dir}/rss-content
cache:
  base_dir: {self.tmp_dir}/cache
"""
            )
        )

    def test_unknown_source_is_a_config_error(self) -> None:
        with self.assertRaises(ConfigError):
            self.app.import_source("missing")

    def test_enrich_then_remix(self) -> None:
        item = self.import_sample()

        self.assertEqual(self.app.run_processor("markdownify").done, 1)
        self.assertEqual(self.app.run_processor("markdownify").done, 0)
        markdown = self.app.get_annotations(item)["markdownify"]["markdown"]
        self.assertIn("asedio carlista", markdown)

        self.assertEqual(self.app.run_remixer("feedgenerator"), ["feed"])
        feed = self.app.get_artifact("feedgenerator", "feed")
        self.assertIn("<title>Test feed</title>", feed.content)
        self.assertIn(f"mediterraneo/{SAMPLE_UID}", feed.content)

    def test_delete_annotations_makes_the_item_pending_again(self) -> None:
        item = self.import_sample()
        self.app.run_processor("markdownify")

        self.assertEqual(
            self.app.delete_annotations(processor="markdownify", item_id=item.id), 1
        )

        self.assertEqual(self.app.get_annotations(item), {})
        scope = ProcessingScope(source="mediterraneo")
        self.assertEqual(self.app.run_processor("markdownify", scope=scope).done, 1)

    def test_write_lock_is_exclusive_until_close(self) -> None:
        self.app.lock()
        other = self.make_app()

        with self.assertRaisesRegex(LockedError, "another newsmerger command"):
            other.lock()
        self.app.close()
        other.lock()
        self.app = other

    def test_resolve_settles_interrupted_deliveries(self) -> None:
        self.import_sample()
        self.app._db.queue_item_deliveries("telegram", ProcessingScope())
        ((row, _),) = self.app._db.get_item_deliveries("telegram")
        row.status = DeliveryStatus.SENDING
        row.attempts = 1
        self.app._db.save_delivery(row)

        resolved = self.app.resolve_deliveries("telegram", DeliveryStatus.DONE)

        self.assertEqual(resolved, 1)
        (row,) = self.app.find_deliveries(sink="telegram")
        self.assertEqual((row.status, row.attempts), (DeliveryStatus.DONE, 0))
        self.assertEqual(
            self.app.resolve_deliveries("telegram", DeliveryStatus.DONE), 0
        )

    def test_only_loaded_plugins_run(self) -> None:
        with self.assertRaisesRegex(ConfigError, "processor 'summarize' is not loaded"):
            self.app.run_processor("summarize")
        with self.assertRaisesRegex(ConfigError, "remixer 'avglink' is not loaded"):
            self.app.run_remixer("avglink")
        with self.assertRaisesRegex(ConfigError, "sink 'telegram' is not loaded"):
            self.app.run_sink("telegram")

    def test_loaded_names_follow_configuration_order(self) -> None:
        self.app.close()
        self.app = self.make_app(
            "  feedgenerator:\n  grouping: {avglink: {}, singlelink: {}}\n  markdownify:\n"
        )

        self.assertEqual(self.app.processors, ["markdownify"])
        self.assertEqual(self.app.remixers, ["feedgenerator", "avglink", "singlelink"])

    def test_invalid_plugin_options_report_their_config_path(self) -> None:
        with self.assertRaisesRegex(
            ConfigError,
            r"plugins\.markdownify\.max_retries: Input should be a valid integer.*\n"
            r"plugins\.markdownify\.version: Extra inputs are not permitted",
        ):
            self.make_app("  markdownify: {version: '2', max_retries: many}\n")

    def test_register_parameters_are_reserved_plugin_options(self) -> None:
        for option in ("name", "self"):
            with (
                self.subTest(option=option),
                self.assertRaisesRegex(
                    ConfigError, f"'{option}' is a reserved option name"
                ),
            ):
                self.make_app(f"  feedgenerator: {{{option}: feed}}\n")

    def test_llm_consumers_get_the_llm_of_a_plugin_listed_before(self) -> None:
        self.app.close()
        self.app = self.make_app("  ollama:\n  summarize:\n  embed: {llm: ollama}\n")

        llm = self.app._processors["summarize"].llm
        self.assertIsInstance(llm, OllamaLLM)
        self.assertIs(self.app._processors["embed"].llm, llm)

    def test_llm_consumers_without_their_llm_load_but_process_nothing(self) -> None:
        self.app.close()
        self.app = self.make_app("  markdownify:\n  tagger:\n  ollama:\n")
        self.import_sample()

        with self.assertLogs("newsmerger.processors", "ERROR") as logs:
            summaries = {
                name: self.app.run_processor(name) for name in ("markdownify", "tagger")
            }

        self.assertEqual(summaries["markdownify"].done, 1)
        self.assertEqual(summaries["tagger"], RunSummary())
        self.assertIn(
            "tagger: no llm is loaded (llm plugins must be listed before the plugins that use them); nothing processed",
            logs.output[0],
        )

    def test_missing_plugin_module_is_a_plugin_error(self) -> None:
        with self.assertRaises(PluginNotFoundError):
            self.make_app("  nonexistent:\n")

    def test_sources_need_a_loaded_provider(self) -> None:
        config = Config.from_text(
            "sources:\n  - {id: a, name: A, url: 'https://a.test/', provider: plaza}\n"
        )
        with self.assertRaisesRegex(ConfigError, "provider 'plaza' is not loaded"):
            Application(config)


if __name__ == "__main__":
    unittest.main()
