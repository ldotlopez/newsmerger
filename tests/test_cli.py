import json
import logging
import re
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock, call, patch

import requests
from click.testing import CliRunner
from foundation.storage import EntryNotFoundError

from newstool.app import MarkSummary
from newstool.cli import cli
from newstool.config import ConfigError
from newstool.db import DeliveryStatus
from newstool.errors import PluginFailure
from newstool.models import (
    Annotation,
    Artifact,
    Delivery,
    ProcessingScope,
    SourceData,
    SourceItem,
)
from newstool.processors import RunSummary
from newstool.sinks import SubjectKindError

SOURCE = SourceData(
    id="plaza", name="Plaza", url="https://plaza.test/", provider="plaza"
)


def invoke(app: Mock, *args: str):
    with patch("newstool.cli.app_from_context", return_value=app):
        return CliRunner().invoke(cli, list(args))


class ExternalErrorTests(unittest.TestCase):
    """Failures outside the program show as a message; the traceback needs
    debug logging. Anything else keeps its traceback."""

    def setUp(self) -> None:
        logger = logging.getLogger("newstool")
        self.addCleanup(logger.setLevel, logger.level)
        logger.setLevel(logging.WARNING)

    def remix_failing_with(self, error: Exception):
        app = Mock()
        app.remix_keys.return_value = ["digest"]
        app.run_remix.side_effect = error
        return invoke(app, "remix")

    def test_external_failure_is_a_message_without_traceback(self) -> None:
        result = self.remix_failing_with(requests.ConnectionError("llm down"))

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error: ConnectionError: llm down", result.output)
        self.assertIsInstance(result.exception, SystemExit)

    def test_external_failure_keeps_its_traceback_with_debug(self) -> None:
        logging.getLogger("newstool").setLevel(logging.DEBUG)

        result = self.remix_failing_with(requests.ConnectionError("llm down"))

        self.assertIsInstance(result.exception, requests.ConnectionError)

    def test_plugin_failure_is_a_message_without_traceback(self) -> None:
        result = self.remix_failing_with(PluginFailure("empty digest"))

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error: empty digest", result.output)
        self.assertIsInstance(result.exception, SystemExit)

    def test_other_failures_keep_their_traceback(self) -> None:
        result = self.remix_failing_with(ValueError("bug?"))

        self.assertIsInstance(result.exception, ValueError)


class CommandTests(unittest.TestCase):
    def test_import_reports_failed_sources_and_exits_with_error(self) -> None:
        app = Mock()
        app.sources.return_value = [SOURCE]
        app.import_source.side_effect = RuntimeError("site down")

        result = invoke(app, "import")

        self.assertEqual(result.exit_code, 1)
        self.assertIn("site down", result.output)
        self.assertIn("1 source(s) failed", result.output)

    def test_process_runs_every_entry_of_one_processor_with_scope_and_force(
        self,
    ) -> None:
        app = Mock()
        app.process_keys.return_value = ["summary/es", "summary/en"]
        app.run_process.return_value = RunSummary(done=2)

        result = invoke(
            app,
            "process",
            "summarize",
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
        app.process_keys.assert_called_once_with("summarize", workflow="default")
        scope = ProcessingScope(source="plaza", item_ids=(3, 4), limit=5)
        self.assertEqual(
            app.run_process.call_args_list,
            [
                call("summary/es", workflow="default", scope=scope, force=True),
                call("summary/en", workflow="default", scope=scope, force=True),
            ],
        )

    def test_process_without_processor_runs_every_entry(self) -> None:
        app = Mock()
        app.process_keys.return_value = ["markdown"]
        app.run_process.return_value = RunSummary(done=1)

        result = invoke(app, "process")

        self.assertEqual(result.exit_code, 0, result.output)
        app.process_keys.assert_called_once_with(None, workflow="default")
        app.run_process.assert_called_once_with(
            "markdown", workflow="default", scope=ProcessingScope(), force=False
        )
        self.assertIn("markdown", result.output)

    def test_remix_runs_one_or_every_remixer(self) -> None:
        app = Mock()
        app.remix_keys.return_value = ["feedgenerator", "digest"]
        app.run_remix.return_value = ["feed"]

        self.assertEqual(invoke(app, "remix", "feedgenerator").exit_code, 0)
        self.assertEqual(invoke(app, "remix").exit_code, 0)

        self.assertEqual(
            app.run_remix.call_args_list,
            [
                call("feedgenerator", scope=ProcessingScope()),
                call("feedgenerator", scope=ProcessingScope()),
                call("digest", scope=ProcessingScope()),
            ],
        )

    def test_writing_commands_take_the_write_lock(self) -> None:
        app = Mock()
        app.remix_keys.return_value = []

        with patch("newstool.cli.Application", return_value=app):
            result = CliRunner().invoke(cli, ["remix"])

        self.assertEqual(result.exit_code, 0, result.output)
        app.lock.assert_called_once_with()

    def test_run_goes_on_after_a_failed_phase_and_exits_with_error(self) -> None:
        app = Mock()
        app.sources.return_value = []
        app.process_keys.return_value = ["summary"]
        app.run_process.side_effect = RuntimeError("llm down")
        app.remix_keys.return_value = ["feedgenerator"]
        app.run_remix.return_value = ["feed"]
        app.delivery_keys.return_value = ["telegram"]
        app.run_delivery.return_value = RunSummary(done=1)

        with self.assertLogs("newstool", "ERROR"):
            result = invoke(app, "run")

        self.assertEqual(result.exit_code, 1)
        app.run_remix.assert_called_once_with("feedgenerator")
        app.run_delivery.assert_called_once_with("telegram", workflow="default")
        self.assertIn("1 failure(s)", result.output)
        # Summaries are results: stdout only, after the progress rows.
        self.assertIn("Remix", result.stdout)
        self.assertIn("Deliver", result.stdout)
        self.assertNotIn("Remix", result.stderr)

    def test_run_runs_the_named_workflow(self) -> None:
        app = Mock()
        app.sources.return_value = [SOURCE]
        app.import_source.return_value = []
        app.process_keys.return_value = []
        app.remix_keys.return_value = []
        app.delivery_keys.return_value = []

        result = invoke(app, "run", "--workflow", "juntas")

        self.assertEqual(result.exit_code, 0, result.output)
        app.sources.assert_called_once_with("juntas")
        app.process_keys.assert_called_once_with(workflow="juntas")
        app.remix_keys.assert_called_once_with("juntas")
        app.delivery_keys.assert_called_once_with("juntas")

    def test_user_errors_are_reported_without_traceback(self) -> None:
        app = Mock()
        app.process_keys.side_effect = ConfigError("processor 'nope' is not loaded")

        result = invoke(app, "process", "nope")

        self.assertEqual(result.exit_code, 1)
        self.assertIn("processor 'nope' is not loaded", result.output)
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


class SearchTests(unittest.TestCase):
    def test_lists_items_whose_markdown_contains_the_query(self) -> None:
        other = SourceItem(source=SOURCE, uid="def", title="Other", uri="u", id=8)
        app = Mock()
        app.get_items.return_value = [ITEM, other]
        app.get_annotation_values.return_value = {
            ITEM.key: "# Title\n\nLa Junta aprueba el PRESUPUESTO anual",
            other.key: "Nothing here",
        }

        result = invoke(app, "search", "presupuesto", "--source", "plaza")

        self.assertEqual(result.exit_code, 0, result.output)
        app.get_items.assert_called_once_with(ProcessingScope(source="plaza"))
        self.assertIn(
            "7\tplaza\tTitle\t# Title La Junta aprueba el PRESUPUESTO anual",
            result.output,
        )
        self.assertNotIn("Other", result.output)


class LogLevelTests(unittest.TestCase):
    """Precedence: --log-level and -v/-q, then NEWSTOOL_LOG_LEVEL, then the
    config's log_level, then warning."""

    def setUp(self) -> None:
        logging.getLogger("newstool").setLevel(logging.NOTSET)
        self.config_dir = Path(tempfile.mkdtemp(prefix="newstool-test-"))

    def level(self, *args: str, env: str | None = None, config: str = "") -> int:
        config_path = self.config_dir / "config.yaml"
        config_path.write_text(config)
        app = Mock()
        app.remix_keys.return_value = []
        with patch("newstool.cli.Application", return_value=app):
            result = CliRunner().invoke(
                cli,
                ["-c", str(config_path), *args, "remix"],
                env={"NEWSTOOL_LOG_LEVEL": env},
            )
        self.assertEqual(result.exit_code, 0, result.output)
        return logging.getLogger("newstool").level

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
            Artifact(
                "feedgenerator", "feed", None, "application/rss+xml", updated_at=NOW
            )
        ]

        result = invoke(app, "inspect", "artifacts", "--remixer", "feedgenerator")

        self.assertEqual(result.exit_code, 0, result.output)
        app.list_artifacts.assert_called_once_with(
            "feedgenerator", names=None, limit=None, sort="updated"
        )
        self.assertIn("feedgenerator/feed", result.output)
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

        result = invoke(app, "inspect", "artifacts", "--artifact", "feedgenerator/nope")

        self.assertEqual(result.exit_code, 1)
        self.assertIn("no artifact feedgenerator/nope in the selection", result.output)

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
            workflow=None,
            sink="telegram",
            status=DeliveryStatus.ERROR,
            artifact_names=None,
            delivery_ids=None,
            sort="updated",
        )
        self.assertIn("item 7", result.output)
        self.assertIn("digest/a/1", result.output)
        self.assertIn("chat not", result.output)

    def test_set_status_with_a_sink_marks_the_selected_subjects(self) -> None:
        app = Mock()
        app.mark_deliveries.return_value = MarkSummary(created=3, kept=2)

        result = invoke(
            app,
            "deliveries",
            "set-status",
            "-w",
            "channel",
            "--sink",
            "telegram",
            "--source",
            "plaza",
            "--as",
            "done",
        )

        self.assertEqual(result.exit_code, 0, result.output)
        app.mark_deliveries.assert_called_once_with(
            "telegram",
            DeliveryStatus.DONE,
            ProcessingScope(source="plaza"),
            (),
            workflow="channel",
            overwrite=False,
            dry_run=False,
        )
        self.assertIn("Marked 3 delivery(ies) as done: 3 new, 0 changed", result.stdout)
        self.assertIn("Left 2 existing delivery(ies)", result.stderr)

    def test_set_status_all_with_a_sink_marks_every_subject(self) -> None:
        app = Mock()
        app.mark_deliveries.return_value = MarkSummary(created=1)

        args = ("deliveries", "set-status", "-w", "channel", "--sink", "telegram")
        result = invoke(app, *args, "--all", "--as", "queued", "--dry-run")

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(
            app.mark_deliveries.call_args.kwargs,
            {"workflow": "channel", "overwrite": False, "dry_run": True},
        )
        self.assertIn("Would mark 1 delivery(ies)", result.stdout)

    def test_set_status_with_a_sink_and_row_filters_changes_rows(self) -> None:
        app = Mock()
        app.find_deliveries.return_value = []
        app.set_delivery_status.return_value = 0
        args = ("deliveries", "set-status", "-w", "channel", "--sink", "telegram")

        result = invoke(app, *args, "--status", "error", "--as", "queued")

        self.assertEqual(result.exit_code, 0, result.output)
        app.mark_deliveries.assert_not_called()
        self.assertEqual(app.find_deliveries.call_args.kwargs["workflow"], "channel")

    def test_set_status_usage_errors(self) -> None:
        app = Mock()
        set_status = ("deliveries", "set-status", "--as", "done")
        for args in (
            ("--sink", "telegram", "--all"),  # no -w
            ("-w", "channel", "--overwrite", "--item", "1"),  # no --sink
            ("-w", "channel", "--sink", "t", "--overwrite", "--delivery", "1"),
            ("-w", "channel", "--sink", "t", "--all", "--item", "1"),
            ("-w", "channel"),  # no selection
        ):
            with self.subTest(args=args):
                self.assertEqual(invoke(app, *set_status, *args).exit_code, 2)
        app.mark_deliveries.assert_not_called()
        app.set_delivery_status.assert_not_called()

    def test_a_kind_mismatch_is_a_message(self) -> None:
        app = Mock()
        app.mark_deliveries.side_effect = SubjectKindError("not --artifact")
        args = ("deliveries", "set-status", "-w", "c", "--sink", "telegram")

        result = invoke(app, *args, "--artifact", "digest/a", "--as", "done")

        self.assertEqual(result.exit_code, 1)
        self.assertIn("not --artifact", result.output)

    def test_malformed_artifact_id_is_a_usage_error(self) -> None:
        result = invoke(Mock(), "inspect", "artifacts", "--artifact", "feedgenerator")

        self.assertEqual(result.exit_code, 2)
        self.assertIn("'feedgenerator' is not <remixer>/<name>", result.output)


if __name__ == "__main__":
    unittest.main()
