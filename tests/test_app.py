"""Application end to end on a temp database, with real plugins that need no
network (markdownify, feedgenerator) and a stubbed HTTP fetcher."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from foundation.plugin import PluginError, PluginNotFoundError, Register

from newsmerger.app import (
    PLUGIN_ENTRY_POINT,
    PLUGINS_NAMESPACE,
    Application,
    LockedError,
    objects_by_name,
)
from newsmerger.config import Config, ConfigError
from newsmerger.db import DeliveryStatus, ProcessingStatus
from newsmerger.models import ProcessingScope, SourceItem
from newsmerger.plugins import Services, feedreader
from newsmerger.plugins.markdownify import MarkdownifyProcessor
from newsmerger.plugins.ollama import OllamaLLM
from newsmerger.processors import Processor, RunSummary
from newsmerger.providers import Provider

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
        self,
        plugins: str = "  markdownify:\n  feedgenerator: {title: Test feed}\n",
        process: str = "process: [markdownify]\n",
        workflows: str = "remix: [feedgenerator]\n",
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
{process}
{workflows}
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
            app.config.get_source("blog"),
            app._fetcher,
            feedreader.Options(article_selector=".body"),
        )

    def test_unknown_provider_option_is_a_config_error(self) -> None:
        with self.assertRaisesRegex(
            ConfigError, r"sources\.blog\.options\.selector: Extra inputs"
        ):
            self.make_rss_app("{selector: .body}")

    def make_rss_app(self, options: str) -> Application:
        return Application(
            Config.from_text(
                f"""
sources:
  - id: blog
    name: Blog
    provider: feedreader
    url: https://blog.test/feed
    options: {options}
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

    def test_process_then_remix(self) -> None:
        item = self.import_sample()

        self.assertEqual(self.app.run_process("markdown").done, 1)
        self.assertEqual(self.app.run_process("markdown").done, 0)
        markdown = self.app.get_annotations(item)["markdown"]
        self.assertIn("asedio carlista", markdown)

        self.assertEqual(self.app.run_remix("feedgenerator"), ["feed"])
        feed = self.app.get_artifact("feedgenerator", "feed")
        self.assertIn("<title>Test feed</title>", feed.content)
        self.assertIn(f"mediterraneo/{SAMPLE_UID}", feed.content)

    def test_delete_annotations_makes_the_item_pending_again(self) -> None:
        item = self.import_sample()
        self.app.run_process("markdown")

        self.assertEqual(
            self.app.delete_annotations(processor="markdownify", item_id=item.id), 1
        )

        self.assertEqual(self.app.get_annotations(item), {})
        scope = ProcessingScope(source="mediterraneo")
        self.assertEqual(self.app.run_process("markdown", scope=scope).done, 1)

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
            self.app.process_keys("summarize")
        with self.assertRaisesRegex(
            ConfigError, "no process entry of workflow 'default' writes the key"
        ):
            self.app.run_process("summary")
        with self.assertRaisesRegex(
            ConfigError, "no workflow has a remix entry 'avglink'"
        ):
            self.app.run_remix("avglink")
        with self.assertRaisesRegex(ConfigError, "has no delivery 'telegram'"):
            self.app.run_delivery("telegram")
        with self.assertRaisesRegex(ConfigError, "workflow 'nope' is not loaded"):
            self.app.process_keys(workflow="nope")

    def test_remix_entries_follow_configuration_order(self) -> None:
        self.app.close()
        self.app = self.make_app(
            "  feedgenerator:\n  grouping: {avglink: {}, singlelink: {}}\n  markdownify:\n",
            workflows="remix: [singlelink, feedgenerator]\n",
        )

        self.assertEqual(self.app.processors, ["markdownify"])
        self.assertEqual(self.app.remix_keys(), ["singlelink", "feedgenerator"])

    def test_remix_entries_save_their_artifacts_under_their_key(self) -> None:
        self.app.close()
        self.app = self.make_app(
            workflows="""
remix:
  - feedgenerator
  - {remixer: feedgenerator, key: short, options: {title: Short, max_items: 1}}
"""
        )
        self.import_sample()

        self.assertEqual(self.app.remix_keys(), ["feedgenerator", "short"])
        self.assertEqual(self.app.run_remix("short"), ["feed"])
        self.assertIn(
            "<title>Short</title>", self.app.get_artifact("short", "feed").content
        )
        self.assertIsNone(self.app.get_artifact("feedgenerator", "feed"))

    def test_invalid_workflow_entries_are_config_errors(self) -> None:
        workflow = "workflows:\n  - {name: w, sources: [juntas], %s}\n"
        for workflows, message in (
            ("remix: [nope]\n", r"remix\.0\.remixer: no plugin provides 'nope'"),
            (
                "remix: [{remixer: feedgenerator, options: {color: red}}]\n",
                r"remix\.0\.options\.color: Extra inputs are not permitted",
            ),
            (
                "remix: [feedgenerator]\n" + workflow % "remix: [feedgenerator]",
                (
                    r"workflows\.w\.remix\.0: key 'feedgenerator' is used by"
                    r" another remix entry; give one a `key`"
                ),
            ),
            (
                workflow % "process: [{processor: summarize, key: markdown}]",
                r"workflows\.w\.process\.0: key 'markdown' is written differently",
            ),
            (
                workflow % "deliver: [{sink: feedgenerator}]",
                r"workflows\.w\.deliver\.0: sink 'feedgenerator' is not loaded",
            ),
        ):
            with (
                self.subTest(workflows=workflows),
                self.assertRaisesRegex(ConfigError, message),
            ):
                self.make_app(workflows=workflows)

    @patch("newsmerger.plugins.telegram.requests.post")
    def test_workflows_run_on_their_sources_and_deliver_under_their_name(
        self, post
    ) -> None:
        post.return_value.json.return_value = {"ok": True, "result": {"message_id": 1}}
        self.app.close()
        self.app = self.make_app(
            "  markdownify:\n  feedgenerator:\n  telegram: {bot_token: t}\n",
            process="",
            workflows="""
deliver: [{sink: telegram, options: {chat_id: main}}]
workflows:
  - name: juntas-channel
    sources: [juntas]
    process: [markdownify]
    deliver:
      - {sink: telegram, options: {chat_id: juntas, interval: 30, max_per_run: 1}}
""",
        )
        item = self.import_sample()  # a `mediterraneo` item
        self.app._db.record_result(
            item, "summarize", "summary", ProcessingStatus.DONE, value="S"
        )

        self.assertEqual(self.app.process_keys(), [])
        self.assertEqual(self.app.process_keys(workflow="juntas-channel"), ["markdown"])
        # The item is not of the workflow's sources.
        self.assertEqual(
            self.app.run_process("markdown", workflow="juntas-channel").done, 0
        )
        self.assertEqual(
            [source.id for source in self.app.sources("juntas-channel")], ["juntas"]
        )
        # The sample is older than the lookback window: name it.
        scope = ProcessingScope(item_ids=(item.id,))
        self.assertEqual(
            self.app.run_delivery(
                "telegram", workflow="juntas-channel", scope=scope
            ).done,
            0,
        )
        self.assertEqual(self.app.run_delivery("telegram", scope=scope).done, 1)
        (row,) = self.app.find_deliveries()
        self.assertEqual(row.sink, "telegram")
        self.assertEqual(row.external_ref, {"chat_id": "main", "message_id": 1})

    def test_workflows_with_disjoint_sources_may_write_the_same_key(self) -> None:
        self.app.close()
        # `default` uses both sources, so it shares `juntas` with `a`.
        with self.assertRaisesRegex(
            ConfigError,
            r"workflows\.a\.process\.0: key 'markdown' is written differently by"
            r" another entry \(workflow 'default'\) on the same sources",
        ):
            self.make_app(
                process="process: [markdownify]\n",
                workflows="workflows:\n  - {name: a, sources: [juntas], process:"
                " [{processor: summarize, key: markdown}]}\n",
            )
        self.app = self.make_app(
            process="",
            workflows="""
workflows:
  - {name: a, sources: [juntas], process: [markdownify]}
  - {name: b, sources: [mediterraneo], process: [markdownify]}
""",
        )
        item = self.import_sample()  # a `mediterraneo` item

        self.assertEqual(self.app.run_process("markdown", workflow="a").done, 0)
        self.assertEqual(self.app.run_process("markdown", workflow="b").done, 1)
        self.assertIn("markdown", self.app.get_annotations(item))

    def test_workflows_sharing_a_source_share_identical_entries(self) -> None:
        self.app.close()
        self.app = self.make_app(
            process="process: [markdownify]\n",
            workflows="workflows:\n"
            "  - {name: a, sources: [mediterraneo], process: [markdownify]}\n",
        )
        item = self.import_sample()  # a `mediterraneo` item

        self.assertEqual(self.app.run_process("markdown", workflow="a").done, 1)
        # The same run: `default` finds it done.
        self.assertEqual(self.app.run_process("markdown").done, 0)
        self.assertIn("markdown", self.app.get_annotations(item))

    def test_default_uses_the_sources_not_opted_out(self) -> None:
        config = Config.from_text(
            """
sources:
  - {id: a, name: A, url: 'https://a.test/', provider: plaza}
  - {id: b, name: B, url: 'https://b.test/', provider: plaza, default: false}
workflows:
  - {name: only-b, sources: [b]}
"""
        )
        self.assertEqual(
            [(workflow.name, workflow.sources) for workflow in config.all_workflows()],
            [("default", ["a"]), ("only-b", ["b"])],
        )
        self.assertEqual(config.workflows[0].ledger_key("telegram"), "only-b/telegram")
        self.assertEqual(config.all_workflows()[0].ledger_key("telegram"), "telegram")

    def test_process_entries_run_in_order_each_with_its_key(self) -> None:
        self.app.close()
        self.app = self.make_app(
            process="process:\n  - markdownify\n"
            "  - {processor: markdownify, key: markdown/copy}\n"
        )
        item = self.import_sample()

        self.assertEqual(self.app.process_keys(), ["markdown", "markdown/copy"])
        self.assertEqual(self.app.process_keys("markdownify"), self.app.process_keys())
        self.assertEqual(self.app.run_process("markdown").done, 1)
        # Its own state: the first run being done does not skip it.
        self.assertEqual(self.app.run_process("markdown/copy").done, 1)
        annotations = self.app.get_annotations(item)
        self.assertEqual(annotations["markdown"], annotations["markdown/copy"])

    def test_invalid_process_entries_are_config_errors(self) -> None:
        for process, message in (
            ("process: [grouping]\n", "processor 'grouping' is not loaded"),
            (
                "process: [{processor: markdownify, options: {model: m}}]\n",
                r"process\.0\.options\.model: Extra inputs are not permitted",
            ),
            (
                "process: [{processor: markdownify, options: {key: copy}}]\n",
                r"process\.0\.options\.key: Extra inputs are not permitted",
            ),
            (
                "process: [{processor: markdownify, key: Mark Down}]\n",
                r"process\.0: invalid key 'Mark Down'",
            ),
            (
                "process: [markdownify, markdownify]\n",
                r"process\.1: key 'markdown' is written by another entry",
            ),
        ):
            with (
                self.subTest(process=process),
                self.assertRaisesRegex(ConfigError, message),
            ):
                self.make_app(process=process)

    def test_unlisted_processors_load_but_never_run(self) -> None:
        self.app.close()
        self.app = self.make_app(process="")

        self.assertEqual(self.app.processors, ["markdownify"])
        self.assertEqual(self.app.process_keys(), [])

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
        self.app = self.make_app(
            "  ollama:\n  summarize:\n  embed: {llm: ollama}\n", process=""
        )

        llm = self.app._processors["summarize"].llm
        self.assertIsInstance(llm, OllamaLLM)
        self.assertIs(self.app._processors["embed"].llm, llm)

    def test_llm_consumers_without_their_llm_load_but_process_nothing(self) -> None:
        self.app.close()
        self.app = self.make_app(
            "  markdownify:\n  tagger:\n  ollama:\n",
            process="process: [markdownify, tagger]\n",
        )
        self.import_sample()

        with self.assertLogs("newsmerger.processors", "ERROR") as logs:
            summaries = {key: self.app.run_process(key) for key in ("markdown", "tags")}

        self.assertEqual(summaries["markdown"].done, 1)
        self.assertEqual(summaries["tags"], RunSummary())
        self.assertIn(
            "tagger: no llm is loaded (llm plugins must be listed before the plugins that use them); nothing processed",
            logs.output[0],
        )

    def test_missing_plugin_module_is_a_plugin_error(self) -> None:
        with self.assertRaises(PluginNotFoundError):
            self.make_app("  nonexistent:\n")

    def test_unprovided_providers_and_processors_load_their_plugin(self) -> None:
        config = Config.from_text(
            f"""
sources:
  - {{id: a, name: A, url: 'https://a.test/', provider: plaza}}
process: [markdownify, tagger]
db:
  uri: sqlite:///{self.tmp_dir}/auto.db
  content_dir: {self.tmp_dir}/auto-content
"""
        )
        with Application(config) as app:
            self.assertEqual(list(app._providers), ["plaza"])
            self.assertEqual(app.processors, ["markdownify", "tagger"])
            self.assertEqual(app.process_keys(), ["markdown", "tags"])

    def test_autoloaded_plugins_come_after_the_listed_ones(self) -> None:
        self.app.close()
        self.app = self.make_app("  ollama:\n", process="process: [summarize]\n")

        self.assertIsInstance(self.app._processors["summarize"].llm, OllamaLLM)

    def test_a_name_no_plugin_provides_is_a_config_error(self) -> None:
        for config, message in (
            (
                "sources:\n  - {id: a, name: A, url: 'https://a.test/', provider: nope}\n",
                r"sources\.a\.provider: no plugin provides 'nope'",
            ),
            ("process: [nope]\n", r"process\.0\.processor: no plugin provides 'nope'"),
        ):
            with (
                self.subTest(config=config),
                self.assertRaisesRegex(ConfigError, message),
            ):
                Application(Config.from_text(config))

    def test_a_listed_plugin_without_the_object_is_not_loaded_again(self) -> None:
        config = Config.from_text(
            "sources:\n  - {id: a, name: A, url: 'https://a.test/', provider: grouping}\n"
            "plugins:\n  grouping:\n"
        )
        with self.assertRaisesRegex(ConfigError, "provider 'grouping' is not loaded"):
            Application(config)

    def test_entry_points_must_return_instances(self) -> None:
        plugins = Register(PLUGINS_NAMESPACE, PLUGIN_ENTRY_POINT)
        with (
            patch.object(
                plugins,
                "get_by_protocol",
                return_value=[("markdownify", "markdownify", MarkdownifyProcessor)],
            ),
            self.assertRaisesRegex(PluginError, "the class of Processor 'markdownify'"),
        ):
            objects_by_name(plugins, Processor)

    def test_providers_and_processors_load_with_defaults_under_their_module_name(
        self,
    ) -> None:
        # Autoloading registers them with no options, by the name they are used with.
        plugins = Register(PLUGINS_NAMESPACE, PLUGIN_ENTRY_POINT)
        for module in plugins.discover():
            if module == "telegram":  # it needs its bot token
                continue
            with self.subTest(module=module):
                plugins.register(module, Services())
                names = {
                    name
                    for protocol in (Provider, Processor)
                    for plugin, name, _ in plugins.get_by_protocol(protocol)
                    if plugin == module
                }
                self.assertIn(names, (set(), {module}))


if __name__ == "__main__":
    unittest.main()
