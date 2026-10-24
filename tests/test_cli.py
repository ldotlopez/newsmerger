import json
import logging
import re
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock, patch

from click.testing import CliRunner
from foundation.storage import EntryNotFoundError

from newsmerger.cli import cli
from newsmerger.config import ConfigError
from newsmerger.db import DeliveryStatus
from newsmerger.models import (
    Annotation,
    Artifact,
    Delivery,
    ProcessingScope,
    SourceData,
    SourceItem,
)
from newsmerger.processors import RunSummary

SOURCE = SourceData(
    id="plaza", name="Plaza", url="https://plaza.test/", provider="plaza"
)


def invoke(app: Mock, *args: str):
    with patch("newsmerger.cli.app_from_context", return_value=app):
        return CliRunner().invoke(cli, list(args))


class CommandTests(unittest.TestCase):
    def test_import_url_passes_source_id_and_url(self) -> None:
        app = Mock()
        app.import_url.return_value = SourceItem(
            source=SOURCE, uid="1", title="Imported title", uri="https://plaza.test/1"
        )

        result = invoke(app, "import-url", "--source", "plaza", "https://plaza.test/1")

        self.assertEqual(result.exit_code, 0, result.output)
        app.import_url.assert_called_once_with("plaza", "https://plaza.test/1")
        self.assertIn("Imported 'Imported title'", result.output)

    def test_import_reports_failed_sources_and_exits_with_error(self) -> None:
        app = Mock()
        app.sources = [SOURCE]
        app.import_source.side_effect = RuntimeError("site down")

        result = invoke(app, "import")

        self.assertEqual(result.exit_code, 1)
        self.assertIn("site down", result.output)
        self.assertIn("1 source(s) failed", result.output)

    def test_enrich_runs_one_processor_with_scope_and_force(self) -> None:
        app = Mock()
        app.run_processor.return_value = RunSummary(done=2)

        result = invoke(
            app,
            "enrich",
            "markdownify",
            "--source",
            "plaza",
            "--item",
            "3",
            "--item",
            "4",
            "--limit",
            "5",
            "--force",
        )

        self.assertEqual(result.exit_code, 0, result.output)
        app.run_processor.assert_called_once_with(
            "markdownify",
            scope=ProcessingScope(source="plaza", item_ids=(3, 4), limit=5),
            force=True,
        )

    def test_enrich_without_processor_runs_every_configured_one(self) -> None:
        app = Mock()
        app.enrich.return_value = {"markdownify": RunSummary(done=1)}

        result = invoke(app, "enrich")

        self.assertEqual(result.exit_code, 0, result.output)
        app.enrich.assert_called_once_with(scope=ProcessingScope(), force=False)
        self.assertIn("markdownify", result.output)

    def test_remix_runs_one_or_every_remixer(self) -> None:
        app = Mock()
        app.run_remixer.return_value = ["feed"]
        app.remix.return_value = {"rssfeed": ["feed"]}

        self.assertEqual(invoke(app, "remix", "rssfeed").exit_code, 0)
        self.assertEqual(invoke(app, "remix").exit_code, 0)

        app.run_remixer.assert_called_once_with("rssfeed", scope=ProcessingScope())
        app.remix.assert_called_once_with(scope=ProcessingScope())

    def test_writing_commands_take_the_write_lock(self) -> None:
        app = Mock()
        app.remix.return_value = {}

        with patch("newsmerger.cli.Application", return_value=app):
            result = CliRunner().invoke(cli, ["remix"])

        self.assertEqual(result.exit_code, 0, result.output)
        app.lock.assert_called_once_with()

    def test_deliver_runs_one_sink_with_selection_requeue_and_force(self) -> None:
        app = Mock()
        app.run_sink.return_value = RunSummary(done=1)

        result = invoke(
            app,
            "deliver",
            "telegram_artifacts",
            "--artifact",
            "digest/a/2026-10-01_2026-10-08",
            "--force",
        )

        self.assertEqual(result.exit_code, 0, result.output)
        app.run_sink.assert_called_once_with(
            "telegram_artifacts",
            scope=ProcessingScope(),
            artifacts=(("digest", "a/2026-10-01_2026-10-08"),),
            requeue=False,
            force=True,
        )

    def test_deliver_without_sink_runs_every_one_but_cannot_force(self) -> None:
        app = Mock()
        app.deliver.return_value = {"telegram": RunSummary(done=2, failed=1)}

        result = invoke(app, "deliver", "--requeue")
        forced = invoke(app, "deliver", "--force", "--item", "1")

        self.assertEqual(result.exit_code, 0, result.output)
        app.deliver.assert_called_once_with(
            scope=ProcessingScope(), artifacts=(), requeue=True
        )
        self.assertEqual(forced.exit_code, 2)
        self.assertIn("--force needs a SINK", forced.output)

    def test_run_goes_on_after_a_failed_phase_and_exits_with_error(self) -> None:
        app = Mock()
        app.sources = []
        app.enrich.side_effect = RuntimeError("llm down")
        app.remix.return_value = {"rssfeed": ["feed"]}
        app.deliver.return_value = {"telegram": RunSummary(done=1)}

        with self.assertLogs("newsmerger", "ERROR"):
            result = invoke(app, "run")

        self.assertEqual(result.exit_code, 1)
        app.remix.assert_called_once_with()
        app.deliver.assert_called_once_with()
        self.assertIn("1 failure(s)", result.output)

    def test_resolve_settles_interrupted_deliveries(self) -> None:
        app = Mock()
        app.resolve_deliveries.return_value = 2

        result = invoke(
            app, "deliveries", "resolve", "telegram", "--as", "queued", "--item", "4"
        )

        self.assertEqual(result.exit_code, 0, result.output)
        app.resolve_deliveries.assert_called_once_with(
            "telegram",
            DeliveryStatus.QUEUED,
            scope=ProcessingScope(item_ids=(4,)),
            artifact_names=None,
        )
        self.assertIn("Resolved 2 interrupted delivery(ies)", result.output)

    def test_user_errors_are_reported_without_traceback(self) -> None:
        app = Mock()
        app.run_processor.side_effect = ConfigError(
            "processor 'nope' is not configured"
        )

        result = invoke(app, "enrich", "nope")

        self.assertEqual(result.exit_code, 1)
        self.assertIn("processor 'nope' is not configured", result.output)
        self.assertNotIn("Traceback", result.output)


NOW = datetime(2026, 10, 18, 12, 0, tzinfo=UTC)
ITEM = SourceItem(
    source=SOURCE,
    uid="abc",
    title="Title",
    uri="https://plaza.test/1",
    published_at=NOW,
    id=7,
)


def annotation(annotation_id: int, key: str, value: object) -> Annotation:
    return Annotation(annotation_id, 7, "tagger", key, NOW, value)


class LogLevelTests(unittest.TestCase):
    """Precedence: --log-level and -v/-q, then NEWSMERGER_LOG_LEVEL, then the
    config's log_level, then warning."""

    def setUp(self) -> None:
        logging.getLogger("newsmerger").setLevel(logging.NOTSET)
        self.config_dir = Path(tempfile.mkdtemp(prefix="newsmerger-test-"))

    def level(self, *args: str, env: str | None = None, config: str = "") -> int:
        config_path = self.config_dir / "config.yaml"
        config_path.write_text(config)
        app = Mock()
        app.remix.return_value = {}
        with patch("newsmerger.cli.Application", return_value=app):
            result = CliRunner().invoke(
                cli,
                ["-c", str(config_path), *args, "remix"],
                env={"NEWSMERGER_LOG_LEVEL": env},
            )
        self.assertEqual(result.exit_code, 0, result.output)
        return logging.getLogger("newsmerger").level

    def test_defaults_to_warning(self) -> None:
        self.assertEqual(self.level(), logging.WARNING)

    def test_config_applies(self) -> None:
        self.assertEqual(self.level(config="log_level: info\n"), logging.INFO)

    def test_env_var_beats_config(self) -> None:
        level = self.level(env="error", config="log_level: info\n")
        self.assertEqual(level, logging.ERROR)

    def test_verbose_beats_env_var(self) -> None:
        self.assertEqual(self.level("-v", env="debug"), logging.INFO)

    def test_log_level_option_beats_env_var(self) -> None:
        self.assertEqual(self.level("--log-level", "error", env="info"), logging.ERROR)


class InspectCommandTests(unittest.TestCase):
    def test_items_lists_ids_and_annotation_keys(self) -> None:
        app = Mock()
        app.get_items.return_value = [ITEM]
        app.get_annotation_keys.return_value = {7: [(12, "summarize", "summary")]}

        result = invoke(app, "inspect", "items", "--source", "plaza")

        self.assertEqual(result.exit_code, 0, result.output)
        app.get_items.assert_called_once_with(
            ProcessingScope(source="plaza"), sort="updated"
        )
        self.assertEqual(list(app.get_annotation_keys.call_args.args[0]), [7])
        self.assertIn("Title", result.output)
        self.assertIn("12 summarize.summary", result.output)

    def test_one_item_shows_its_fields_and_a_row_per_annotation(self) -> None:
        app = Mock()
        app.get_items.return_value = [
            SourceItem(
                source=SOURCE,
                uid="abc",
                title="Title",
                uri="https://plaza.test/1",
                content=b"<p>hi</p>",
                data={"author": "Ana"},
                id=7,
            )
        ]
        app.get_annotation_keys.return_value = {
            7: [(12, "summarize", "summary"), (13, "tagger", "tags")]
        }

        result = invoke(app, "inspect", "items", "--item", "7")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("Annotation #12", result.output)
        self.assertIn("summarize.summary", result.output)
        self.assertIn("Annotation #13", result.output)
        self.assertIn("Ana", result.output)
        sha256 = app.get_items.return_value[0].content_sha256
        self.assertIn("inspect content --sha256", result.output)
        # the hash folds across lines in a narrow terminal
        self.assertIn(sha256, re.sub(r"[\s│]", "", result.output))

    def test_content_prints_the_stored_bytes(self) -> None:
        app = Mock()
        app.get_stored_content.return_value = b"<p>hi</p>"

        result = invoke(app, "inspect", "content", "--sha256", "ab12")

        self.assertEqual(result.exit_code, 0, result.output)
        app.get_stored_content.assert_called_once_with("ab12")
        self.assertEqual(result.output, "<p>hi</p>")

    def test_missing_content_is_an_error(self) -> None:
        app = Mock()
        app.get_stored_content.side_effect = EntryNotFoundError("ab12")

        result = invoke(app, "inspect", "content", "--sha256", "ab12")

        self.assertEqual(result.exit_code, 1)
        self.assertIn("no content ab12", result.output)

    def test_items_as_json(self) -> None:
        app = Mock()
        app.get_items.return_value = [ITEM]
        app.get_annotation_keys.return_value = {7: [(12, "summarize", "summary")]}

        result = invoke(app, "inspect", "items", "--format", "json")

        self.assertEqual(result.exit_code, 0, result.output)
        (record,) = json.loads(result.output)
        self.assertEqual(record["id"], 7)
        self.assertEqual(record["uid"], "abc")
        self.assertEqual(record["published_at"], "2026-10-18T12:00:00+00:00")
        self.assertEqual(
            record["annotations"],
            [{"id": 12, "processor": "summarize", "key": "summary"}],
        )

    def test_sort_takes_a_key_of_the_entity(self) -> None:
        app = Mock()
        app.get_items.return_value = []
        app.get_annotation_keys.return_value = {}

        result = invoke(app, "inspect", "items", "--sort", "source", "--limit", "5")
        wrong = invoke(app, "inspect", "items", "--sort", "processor")

        self.assertEqual(result.exit_code, 0, result.output)
        app.get_items.assert_called_once_with(ProcessingScope(limit=5), sort="source")
        self.assertEqual(wrong.exit_code, 2)
        self.assertIn("'processor' is not one of", wrong.output)

    def test_missing_item_is_an_error(self) -> None:
        app = Mock()
        app.get_items.return_value = []

        result = invoke(app, "inspect", "items", "--item", "99")

        self.assertEqual(result.exit_code, 1)
        self.assertIn("no item 99 in the selection", result.output)

    def test_annotations_previews_long_values(self) -> None:
        app = Mock()
        app.find_annotations.return_value = [
            annotation(1, "markdown", "# Title\n\n" + "body " * 100),
            annotation(2, "tags", ["a", "b"]),
        ]

        result = invoke(
            app, "inspect", "annotations", "--item", "7", "--processor", "tagger"
        )

        self.assertEqual(result.exit_code, 0, result.output)
        app.find_annotations.assert_called_once_with(
            ProcessingScope(item_ids=(7,)),
            processor="tagger",
            key=None,
            annotation_ids=None,
            sort="updated",
        )
        self.assertIn("# Title…", result.output)
        self.assertNotIn("body body", result.output)
        self.assertIn('["a", "b"]', result.output)

    def test_one_annotation_prints_its_full_value(self) -> None:
        app = Mock()
        app.find_annotations.return_value = [annotation(2, "tags", ["a", "b"])]

        result = invoke(app, "inspect", "annotations", "--annotation", "2")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.stdout.strip(), '[\n  "a",\n  "b"\n]')
        self.assertIn("2 · item 7 · tagger.tags", result.stderr)

    def test_annotations_as_json_carry_full_values(self) -> None:
        app = Mock()
        app.find_annotations.return_value = [annotation(2, "tags", ["a", "b"])]

        result = invoke(app, "inspect", "annotations", "--format", "json")

        self.assertEqual(
            json.loads(result.output),
            [
                {
                    "id": 2,
                    "item_id": 7,
                    "processor": "tagger",
                    "key": "tags",
                    "updated_at": "2026-10-18T12:00:00+00:00",
                    "value": ["a", "b"],
                }
            ],
        )

    def test_artifacts_lists_metadata(self) -> None:
        app = Mock()
        app.list_artifacts.return_value = [
            Artifact("rssfeed", "feed", None, "application/rss+xml", updated_at=NOW)
        ]

        result = invoke(app, "inspect", "artifacts", "--remixer", "rssfeed")

        self.assertEqual(result.exit_code, 0, result.output)
        app.list_artifacts.assert_called_once_with(
            "rssfeed", names=None, limit=None, sort="updated"
        )
        self.assertIn("rssfeed/feed", result.output)
        self.assertIn("application/rss+xml", result.output)
        app.get_artifact.assert_not_called()

    def test_one_artifact_prints_content_to_stdout_and_metadata_to_stderr(
        self,
    ) -> None:
        app = Mock()
        listed = Artifact("digest", "a/2026-10-01_2026-10-08", None, "text/markdown")
        app.list_artifacts.return_value = [listed]
        app.get_artifact.return_value = Artifact(
            "digest", listed.name, "# Week", "text/markdown", updated_at=NOW
        )

        result = invoke(
            app, "inspect", "artifacts", "--artifact", "digest/a/2026-10-01_2026-10-08"
        )

        self.assertEqual(result.exit_code, 0, result.output)
        app.list_artifacts.assert_called_once_with(
            None,
            names=(("digest", "a/2026-10-01_2026-10-08"),),
            limit=None,
            sort="updated",
        )
        self.assertEqual(result.stdout, "# Week")
        self.assertIn("digest/a/2026-10-01_2026-10-08 · text/markdown", result.stderr)

    def test_missing_artifact_is_an_error(self) -> None:
        app = Mock()
        app.list_artifacts.return_value = []

        result = invoke(app, "inspect", "artifacts", "--artifact", "rssfeed/nope")

        self.assertEqual(result.exit_code, 1)
        self.assertIn("no artifact rssfeed/nope in the selection", result.output)

    def test_deliveries_show_their_subject_and_state(self) -> None:
        app = Mock()
        app.find_deliveries.return_value = [
            Delivery(
                "telegram",
                "error",
                item_id=7,
                attempts=2,
                updated_at=NOW,
                last_error="chat not found",
            ),
            Delivery(
                "telegram_artifacts",
                "done",
                artifact_id=1,
                updated_at=NOW,
                artifact_name="digest/a/1",
            ),
        ]

        result = invoke(
            app, "inspect", "deliveries", "--sink", "telegram", "--status", "error"
        )

        self.assertEqual(result.exit_code, 0, result.output)
        app.find_deliveries.assert_called_once_with(
            ProcessingScope(),
            sink="telegram",
            status=DeliveryStatus.ERROR,
            artifact_names=None,
            sort="updated",
        )
        self.assertIn("item 7", result.output)
        self.assertIn("digest/a/1", result.output)
        self.assertIn("chat not", result.output)

    def test_malformed_artifact_id_is_a_usage_error(self) -> None:
        result = invoke(Mock(), "inspect", "artifacts", "--artifact", "rssfeed")

        self.assertEqual(result.exit_code, 2)
        self.assertIn("'rssfeed' is not <remixer>/<name>", result.output)


if __name__ == "__main__":
    unittest.main()
