"""Application end to end on a temp database, with real plugins that need no
network (markdownify, feedgenerator) and a stubbed HTTP fetcher."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock, patch

from foundation.plugin import PluginError, ProtocolConformanceError

from newstool.app import (
    PLUGIN_ENTRY_POINT,
    PLUGINS_NAMESPACE,
    Application,
    LockedError,
)
from newstool.config import Config, ConfigError
from newstool.db import DeliveryStatus, ProcessingStatus
from newstool.errors import PluginFailure
from newstool.models import (
    PreflightSourceItemData,
    ProcessingScope,
    SourceItem,
    SourceItemData,
)
from newstool.plugins import ClassRegister, Services, feedreader, markdownify
from newstool.plugins.markdownify import MarkdownifyProcessor
from newstool.plugins.ollama import OllamaLLM
from newstool.processors import ProcessorOptions, ProcessorType

SAMPLE = Path(__file__).parent / "samples" / "prensaiberica-item-132310503.html"
SAMPLE_UID = "ec16b09f034ca03296e75d7e5c304f10337f2e77a0327b0d045c54f0a1d970e8"

APRIL = datetime(2026, 4, 30, 10, tzinfo=UTC)
MAY = datetime(2026, 5, 28, 10, tzinfo=UTC)
JUNE = datetime(2026, 6, 25, 10, tzinfo=UTC)


def listed(
    uid: str, modified_at: datetime | None = None
) -> PreflightSourceItemData[str]:
    return PreflightSourceItemData(
        uid=uid, ref=f"https://x.test/{uid}.pdf", modified_at=modified_at
    )


def retrieved(
    item: PreflightSourceItemData[str],
    fetcher: object,
    *,
    uid: str | None = None,
    modified_at: datetime | None = None,
) -> SourceItemData:
    modified_at = modified_at or item.modified_at
    return SourceItemData(
        uid=uid or item.uid,
        title=item.uid,
        uri=item.ref,
        # A new date is a new revision: the store only updates changed content.
        content=f"%PDF {modified_at}".encode(),
        mimetype="application/pdf",
        modified_at=modified_at,
    )


class ApplicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="newstool-test-"))
        self.app = self.make_app()

    def tearDown(self) -> None:
        self.app.close()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def make_app(
        self,
        plugins: str = "  feedgenerator: {title: Test feed}\n",
        catalog: str = "processors: [markdownify]\nremixers: [feedgenerator]\n",
        workflows: str = "",
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
{plugins}
{catalog}
{workflows}
storage_dir: {self.tmp_dir}
cache_dir: {self.tmp_dir}/cache
"""
        )
        return Application(config)

    def object_of(self, workflow: str, key: str) -> object:
        """The object of the workflow's process run that writes `key`."""
        run = self.app._catalog.process[workflow, key]
        return self.app._object(run.profile)

    def import_sample(self) -> SourceItem:
        provider = self.app._object(self.app._catalog.sources["mediterraneo"])
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

    def import_preflight(
        self,
        listed: list[PreflightSourceItemData[str]],
        retrieve: Callable[..., SourceItemData] | None = None,
    ) -> tuple[list[SourceItem], Mock]:
        """Import `juntas` from a stubbed listing; `retrieve` stands for
        `retrieve_item` and defaults to an item dated as listed."""
        provider = self.app._object(self.app._catalog.sources["juntas"])
        retrieve_item = Mock(side_effect=retrieve or retrieved)
        with (
            patch.object(provider, "iter_items", return_value=iter(listed)),
            patch.object(provider, "retrieve_item", retrieve_item),
        ):
            items = self.app.import_source("juntas")
        return items, retrieve_item

    def test_stored_items_listed_as_unchanged_are_not_fetched(self) -> None:
        self.import_preflight([listed("new", MAY)])
        # A late upload of an older session lands behind the stored one.
        (imported,), retrieve_item = self.import_preflight(
            [listed("new", MAY), listed("late", APRIL)]
        )

        self.assertEqual(imported.uid, "late")
        retrieve_item.assert_called_once()
        self.assertEqual({item.uid for item in self.app.get_items()}, {"new", "late"})

    def test_items_listed_without_a_date_are_always_fetched(self) -> None:
        self.import_preflight([listed("a")])
        (imported,), _ = self.import_preflight([listed("a")])
        self.assertEqual(imported.uid, "a")

    def test_stored_items_listed_as_newer_are_updated(self) -> None:
        self.import_preflight([listed("a", APRIL)])
        (imported,), _ = self.import_preflight([listed("a", MAY)])

        self.assertEqual(imported.modified_at, MAY)
        (stored,) = self.app.get_items()
        self.assertEqual(stored.modified_at, MAY)

    def test_items_not_newer_once_retrieved_are_not_updated(self) -> None:
        self.import_preflight([listed("a", MAY)])
        stale = lambda item, fetcher: retrieved(item, fetcher, modified_at=MAY)
        with self.assertLogs("newstool.app", "WARNING") as logs:
            imported, _ = self.import_preflight([listed("a", JUNE)], stale)

        self.assertEqual(imported, [])
        self.assertIn("not newer once retrieved", logs.output[0])

    def test_a_uid_other_than_listed_is_warned_about_and_stored(self) -> None:
        renamed = lambda item, fetcher: retrieved(item, fetcher, uid="other")
        with self.assertLogs("newstool.app", "WARNING") as logs:
            (imported,), _ = self.import_preflight([listed("a")], renamed)

        self.assertEqual(imported.uid, "other")
        self.assertIn("retrieved as 'other'", logs.output[0])

    def test_a_bad_item_is_skipped(self) -> None:
        def retrieve(item, fetcher) -> SourceItemData:
            if item.uid == "bad":
                raise PluginFailure("not a PDF")
            return retrieved(item, fetcher)

        with self.assertLogs("newstool.app", "ERROR"):
            (imported,), _ = self.import_preflight(
                [listed("bad"), listed("good")], retrieve
            )
        self.assertEqual(imported.uid, "good")

    def test_items_fetched_before_a_failure_are_stored(self) -> None:
        def retrieve(item, fetcher) -> SourceItemData:
            if item.uid == "second":
                raise ConnectionError("timed out")
            return retrieved(item, fetcher)

        with self.assertRaises(ConnectionError):
            self.import_preflight([listed("first"), listed("second")], retrieve)
        self.assertEqual([item.uid for item in self.app.get_items()], ["first"])

    def test_listed_dates_must_be_timezone_aware(self) -> None:
        with self.assertRaises(ValueError):
            listed("a", MAY.replace(tzinfo=None))

    def test_source_options_over_the_section_build_its_provider(self) -> None:
        for options, expected in (
            ("{}", "nav"),
            ("{article_selector: .body}", ".body"),
        ):
            with self.subTest(options=options):
                app = self.make_rss_app(options)
                provider = app._object(app._catalog.sources["blog"])
                with patch.object(
                    provider, "retrieve_items", return_value=iter([])
                ) as call:
                    app.import_source("blog")
                app.close()

                self.assertEqual(
                    provider.options, feedreader.Options(article_selector=expected)
                )
                call.assert_called_once_with(
                    app.config.get_source("blog"), app._fetcher
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
  feedreader: {{article_selector: nav}}
storage_dir: {self.tmp_dir}/rss
cache_dir: {self.tmp_dir}/cache
"""
            )
        )

    def test_unknown_source_is_a_config_error(self) -> None:
        with self.assertRaises(ConfigError):
            self.app.import_source("missing")

    def test_objects_are_built_when_a_run_needs_them(self) -> None:
        self.assertEqual(self.app._objects, {})
        self.import_sample()
        self.app.run_process("markdown")

        self.assertEqual(
            sorted(profile.name for profile in self.app._objects),
            ["markdownify", "prensaiberica"],
        )

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

        (annotation,) = self.app.find_annotations(key="markdown")
        self.assertEqual(self.app.delete_annotations([annotation.id]), 1)

        self.assertEqual(self.app.get_annotations(item), {})
        scope = ProcessingScope(source="mediterraneo")
        self.assertEqual(self.app.run_process("markdown", scope=scope).done, 1)

    def test_write_lock_is_exclusive_until_close(self) -> None:
        self.app.lock()
        other = self.make_app()

        with self.assertRaisesRegex(LockedError, "another newstool command"):
            other.lock()
        self.app.close()
        other.lock()
        self.app = other

    def test_only_configured_runs_run(self) -> None:
        with self.assertRaisesRegex(ConfigError, "processor 'nope' does not exist"):
            self.app.process_keys("nope")
        with self.assertRaisesRegex(
            ConfigError, "no process run of workflow 'default' writes the key"
        ):
            self.app.run_process("summary")
        with self.assertRaisesRegex(
            ConfigError, "no workflow has a remix run 'avglink'"
        ):
            self.app.run_remix("avglink")
        with self.assertRaisesRegex(ConfigError, "has no delivery 'telegram'"):
            self.app.run_delivery("telegram")
        with self.assertRaisesRegex(ConfigError, "workflow 'nope' is not configured"):
            self.app.process_keys(workflow="nope")

    def test_default_runs_the_catalog_in_order_without_skip_default(self) -> None:
        self.app.close()
        self.app = self.make_app(
            catalog="""
processors:
  - markdownify
  - {processor: markdownify, key: markdown/copy, skip_default: true}
remixers:
  - singlelink
  - {remixer: feedgenerator, skip_default: true}
  - {remixer: feedgenerator, key: short}
"""
        )

        self.assertEqual(self.app.process_keys(), ["markdown"])
        self.assertEqual(self.app.remix_keys(), ["singlelink", "short"])
        self.assertEqual(self.app.delivery_keys(), [])

    def test_remix_entries_save_their_artifacts_under_their_key(self) -> None:
        self.app.close()
        self.app = self.make_app(
            catalog="""
remixers:
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

    def test_invalid_entries_are_config_errors(self) -> None:
        workflow = "workflows:\n  - {name: w, sources: [juntas], %s}\n"
        for workflows, message in (
            (
                "remixers: [nope]\n",
                r"remixers\.0: no plugin provides the remixer 'nope'",
            ),
            (
                "remixers: [{remixer: feedgenerator, options: {color: red}}]\n",
                r"remixers\.0\.options\.color: Extra inputs are not permitted",
            ),
            (
                workflow % "remix: [feedgenerator]",
                (
                    r"workflows\.w\.remix\.0: remix key 'feedgenerator' is used by"
                    r" remixers\.0 too \(workflow 'default'\); a remix key belongs to"
                    r" one workflow"
                ),
            ),
            (
                workflow % "process: [{processor: tagger, key: markdown}]",
                (
                    r"workflows\.w\.process\.0: key 'markdown' is written by"
                    r" markdownify too \(processors\.0\) on the same sources"
                ),
            ),
            (
                workflow % "deliver: [feedgenerator]",
                r"workflows\.w\.deliver\.0: no sink has the id or type 'feedgenerator'",
            ),
            (
                "processors:\n  - {processor: markdownify, id: tagger}\n",
                r"processors\.0: the id 'tagger' is a processor type's name",
            ),
        ):
            with (
                self.subTest(workflows=workflows),
                self.assertRaisesRegex(ConfigError, message),
            ):
                self.make_app(workflows=workflows)

    @patch("newstool.plugins.telegram.requests.post")
    def test_workflows_run_on_their_sources_and_deliver_under_their_name(
        self, post
    ) -> None:
        post.return_value.json.return_value = {"ok": True, "result": {"message_id": 1}}
        self.app.close()
        self.app = self.make_app(
            "  telegram: {bot_token: t}\n",
            catalog="""
llms: [ollama]
processors: [markdownify, summarize]
sinks:
  - {sink: telegram, id: main, options: {chat_id: main}}
""",
            workflows="""
workflows:
  - name: channel
    sources: [mediterraneo]
    deliver: [main]
  - name: juntas-channel
    sources: [juntas]
    process: [markdownify, summarize]
    deliver:
      - {sink: telegram, options: {chat_id: juntas, interval: 30m, max_per_run: 1}}
""",
        )
        item = self.import_sample()  # a `mediterraneo` item
        self.app._db.record_result(
            item, "summarize", "summary", ProcessingStatus.DONE, value="S"
        )

        self.assertEqual(self.app.process_keys(), ["markdown", "summary"])
        self.assertEqual(self.app.process_keys(workflow="channel"), [])
        self.assertEqual(self.app.delivery_keys(), [])
        # An id names the profile; the key is still the sink's.
        self.assertEqual(self.app.delivery_keys("channel"), ["telegram"])
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
        self.assertEqual(
            self.app.run_delivery("telegram", workflow="channel", scope=scope).done, 1
        )
        (row,) = self.app.find_deliveries()
        self.assertEqual(row.sink, "channel/telegram")
        self.assertEqual(row.external_ref, {"chat_id": "main", "message_id": 1})

    @patch("newstool.plugins.telegram.requests.post")
    def test_deliveries_are_marked_and_sent_again_by_id(self, post) -> None:
        post.return_value.json.return_value = {"ok": True, "result": {"message_id": 1}}
        self.app.close()
        self.app = self.make_app(
            "  telegram: {bot_token: t}\n",
            catalog="""
llms: [ollama]
processors: [markdownify, summarize]
sinks:
  - {sink: telegram, id: main, options: {chat_id: main}}
""",
            workflows="""
workflows:
  - name: channel
    sources: [mediterraneo]
    process: [markdownify, summarize]
    deliver: [main]
""",
        )
        item = self.import_sample()
        self.app._db.record_result(
            item, "summarize", "summary", ProcessingStatus.DONE, value="S"
        )
        scope = ProcessingScope(item_ids=(item.id,))
        self.app.run_delivery("telegram", workflow="channel", scope=scope, force=True)
        (row,) = self.app.find_deliveries()

        summaries = self.app.send_deliveries([row])

        self.assertEqual(summaries["channel/telegram"].done, 1)
        self.assertEqual(post.call_count, 2)

        marked = self.app.set_delivery_status(
            self.app.find_deliveries(delivery_ids=[row.id]), DeliveryStatus.QUEUED
        )

        self.assertEqual(marked, 1)
        (row,) = self.app.find_deliveries(status=DeliveryStatus.QUEUED)
        self.assertEqual(row.attempts, 0)
        with self.assertRaises(ValueError):
            self.app.set_delivery_status([row], DeliveryStatus.SENDING)
        row.sink = "gone/telegram"
        self.assertEqual(self.app.send_deliveries([row]), {})
        self.assertEqual(post.call_count, 2)

    def test_what_runs_read_must_be_written_on_their_sources(self) -> None:
        for catalog, workflows, message in (
            (
                "llms: [ollama]\nprocessors: [summarize]\n",
                "",
                (
                    r"processors\.0: summarize reads 'markdown', and no process run"
                    r" writes it on the sources of workflow 'default'"
                ),
            ),
            (
                "processors: [markdownify]\n",
                (
                    "workflows:\n  - {name: w, sources: [juntas], deliver:"
                    " [{sink: telegram, options: {bot_token: t, chat_id: c}}]}\n"
                ),
                r"workflows\.w\.deliver\.0: telegram reads 'summary'",
            ),
        ):
            with (
                self.subTest(catalog=catalog),
                self.assertRaisesRegex(ConfigError, message),
            ):
                self.make_app(catalog=catalog, workflows=workflows)

    def test_workflows_with_disjoint_sources_may_write_a_key_differently(
        self,
    ) -> None:
        self.app.close()
        self.app = self.make_app(
            catalog="",
            workflows="""
workflows:
  - {name: a, sources: [juntas], process: [markdownify]}
  - name: b
    sources: [mediterraneo]
    process: [{processor: markdownify, options: {max_retries: 1}}]
""",
        )
        item = self.import_sample()  # a `mediterraneo` item

        self.assertEqual(self.app.run_process("markdown", workflow="a").done, 0)
        self.assertEqual(self.app.run_process("markdown", workflow="b").done, 1)
        self.assertIn("markdown", self.app.get_annotations(item))

    def test_other_options_for_a_key_on_shared_sources_are_a_warning(self) -> None:
        self.app.close()
        with self.assertLogs("newstool.catalog", "WARNING") as logs:
            self.app = self.make_app(
                workflows="workflows:\n  - name: a\n    sources: [mediterraneo]\n"
                "    process: [{processor: markdownify, options: {max_retries: 5}}]\n"
            )

        self.assertIn(
            "workflows.a.process.0: key 'markdown' is written with other options"
            " too (processors.0) on the same sources",
            logs.output[0],
        )

    def test_references_to_an_entry_share_its_run(self) -> None:
        self.app.close()
        self.app = self.make_app(
            catalog="processors: [{processor: markdownify, id: md}]\n",
            workflows="workflows:\n  - {name: a, sources: [mediterraneo], process: [md]}\n",
        )
        item = self.import_sample()  # a `mediterraneo` item

        self.assertIs(
            self.object_of("a", "markdown"), self.object_of("default", "markdown")
        )
        self.assertEqual(self.app.run_process("markdown", workflow="a").done, 1)
        # The same run: `default` finds it done.
        self.assertEqual(self.app.run_process("markdown").done, 0)
        self.assertIn("markdown", self.app.get_annotations(item))

    def test_default_uses_the_sources_not_skipped(self) -> None:
        config = Config.from_text(
            """
sources:
  - {id: a, name: A, url: 'https://a.test/', provider: plaza}
  - {id: b, name: B, url: 'https://b.test/', provider: plaza, skip_default: true}
workflows:
  - {name: only-b, sources: [b]}
"""
        )
        self.assertEqual(
            [(workflow.name, workflow.sources) for workflow in config.all_workflows()],
            [("default", ["a"]), ("only-b", ["b"])],
        )
        self.assertEqual(config.workflows[0].ledger_key("telegram"), "only-b/telegram")

    def test_process_entries_run_in_order_each_with_its_key(self) -> None:
        self.app.close()
        self.app = self.make_app(
            catalog="processors:\n  - markdownify\n"
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
        for processors, message in (
            (
                "[grouping]",
                r"processors\.0: no plugin provides the processor 'grouping'",
            ),
            (
                "[{processor: markdownify, options: {model: m}}]",
                r"processors\.0\.options\.model: Extra inputs are not permitted",
            ),
            (
                "[{processor: markdownify, options: {key: copy}}]",
                r"processors\.0\.options\.key: Extra inputs are not permitted",
            ),
            (
                "[{processor: markdownify, key: Mark Down}]",
                r"processors\.0: invalid key 'Mark Down'",
            ),
            (
                "[markdownify, markdownify]",
                r"processors\.1: key 'markdown' is written by another entry",
            ),
        ):
            with (
                self.subTest(processors=processors),
                self.assertRaisesRegex(ConfigError, message),
            ):
                self.make_app(catalog=f"processors: {processors}\n")

    def test_invalid_plugin_sections_report_their_config_path(self) -> None:
        with self.assertRaisesRegex(
            ConfigError,
            r"plugins\.markdownify\.version: no such option\n"
            r"plugins\.markdownify\.max_retries: Input should be a valid integer",
        ):
            self.make_app("  markdownify: {version: '2', max_retries: many}\n")
        with self.assertRaisesRegex(
            ConfigError, r"plugins\.nonexistent: no plugin provides 'nonexistent'"
        ):
            self.make_app("  nonexistent:\n")

    def test_sections_hold_the_defaults_of_every_use(self) -> None:
        self.app.close()
        self.app = self.make_app(
            "  markdownify: {max_retries: 7}\n",
            catalog="processors:\n  - markdownify\n"
            "  - {processor: markdownify, key: copy, options: {max_retries: 1}}\n",
        )

        self.assertEqual(self.object_of("default", "markdown").options.max_retries, 7)
        self.assertEqual(self.object_of("default", "copy").options.max_retries, 1)

    def test_llm_consumers_get_the_llm_they_name(self) -> None:
        self.app.close()
        self.app = self.make_app(
            "  ollama: {chat_model: small}\n",
            catalog="""
llms:
  - ollama
  - {llm: ollama, id: big, options: {chat_model: big}}
processors:
  - markdownify
  - summarize
  - {processor: summarize, key: summary/big, options: {llm: big}}
  - {processor: tagger, options: {llm: ollama}}
""",
        )

        default = self.object_of("default", "summary").llm
        self.assertIsInstance(default, OllamaLLM)
        self.assertEqual(default.chat_model, "small")
        self.assertEqual(self.object_of("default", "summary/big").llm.chat_model, "big")
        # A type name: the type with its section's options, built once.
        by_type = self.object_of("default", "tags").llm
        self.assertEqual(by_type.chat_model, "small")
        self.assertIs(self.app._llm("ollama"), by_type)

    def test_a_missing_llm_is_a_config_error(self) -> None:
        for catalog, message in (
            (
                "processors: [markdownify, summarize]\n",
                r"processors\.1: uses an llm, and `llms` is empty",
            ),
            (
                (
                    "llms: [ollama]\nprocessors:\n  - markdownify\n"
                    "  - {processor: summarize, options: {llm: nope}}\n"
                ),
                r"processors\.1: no llm has the id or type 'nope'",
            ),
        ):
            with (
                self.subTest(catalog=catalog),
                self.assertRaisesRegex(ConfigError, message),
            ):
                self.make_app(catalog=catalog)

    def test_a_name_no_plugin_provides_is_a_config_error(self) -> None:
        for config, message in (
            (
                "sources:\n  - {id: a, name: A, url: 'https://a.test/', provider: nope}\n",
                r"sources\.a: no plugin provides the provider 'nope'",
            ),
            (
                "sources:\n  - {id: a, name: A, url: 'https://a.test/', provider: singlelink}\n",
                r"sources\.a: no plugin provides the provider 'singlelink'",
            ),
            (
                "processors: [nope]\n",
                r"processors\.0: no plugin provides the processor 'nope'",
            ),
        ):
            with (
                self.subTest(config=config),
                self.assertRaisesRegex(ConfigError, message),
            ):
                Application(Config.from_text(config))


class ClassRegisterTests(unittest.TestCase):
    def register(self, registered: list) -> ClassRegister:
        register = ClassRegister(PLUGINS_NAMESPACE, PLUGIN_ENTRY_POINT)
        with patch.object(markdownify, PLUGIN_ENTRY_POINT, return_value=registered):
            register.register("markdownify")
        return register

    def test_every_module_registers_conforming_classes(self) -> None:
        register = ClassRegister(PLUGINS_NAMESPACE, PLUGIN_ENTRY_POINT)
        register.register_found()

        self.assertEqual(
            sorted(register.classes(ProcessorType)),
            ["embed", "markdownify", "summarize", "tagger"],
        )

    def test_entry_points_must_return_classes(self) -> None:
        instance = MarkdownifyProcessor(ProcessorOptions(), Services())
        register = self.register([("markdownify", ProcessorType, instance)])

        with self.assertRaisesRegex(PluginError, "as an instance, not a class"):
            register.classes(ProcessorType)

    def test_classes_must_conform_to_their_protocol(self) -> None:
        register = self.register([("markdownify", ProcessorType, object)])

        with self.assertRaisesRegex(ProtocolConformanceError, "does not conform"):
            register.classes(ProcessorType)


if __name__ == "__main__":
    unittest.main()
