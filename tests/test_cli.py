import unittest
from datetime import UTC, datetime
from unittest.mock import Mock, patch

from click.testing import CliRunner

from newsmerger.cli import cli
from newsmerger.config import ConfigError
from newsmerger.models import Artifact, ProcessingScope, SourceData, SourceItem
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
            app, "enrich", "markdownify", "--source", "plaza", "--limit", "5", "--force"
        )

        self.assertEqual(result.exit_code, 0, result.output)
        app.run_processor.assert_called_once_with(
            "markdownify", scope=ProcessingScope(source="plaza", limit=5), force=True
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
    source=SOURCE, uid="1", title="Title", uri="https://plaza.test/1", published_at=NOW
)


class InspectionCommandTests(unittest.TestCase):
    def test_items_lists_items_in_scope(self) -> None:
        app = Mock()
        app.get_items.return_value = [ITEM]

        result = invoke(app, "items", "--source", "plaza")

        self.assertEqual(result.exit_code, 0, result.output)
        app.get_items.assert_called_once_with(ProcessingScope(source="plaza"))
        self.assertIn("Title", result.output)

    def test_annotations_previews_long_values(self) -> None:
        app = Mock()
        app.get_items.return_value = [ITEM]
        app.get_annotations.return_value = {
            "markdownify": {"markdown": "# Title\n\n" + "body " * 100},
            "tagger": {"tags": ["a", "b"]},
        }

        result = invoke(app, "annotations", "--source", "plaza", "--uid", "1")

        self.assertEqual(result.exit_code, 0, result.output)
        app.get_items.assert_called_once_with(
            ProcessingScope(source="plaza", uids=("1",))
        )
        self.assertIn("# Title…", result.output)
        self.assertNotIn("body body", result.output)
        self.assertIn('["a", "b"]', result.output)

    def test_annotations_with_key_prints_the_full_value(self) -> None:
        app = Mock()
        app.get_items.return_value = [ITEM]
        app.get_annotations.return_value = {"tagger": {"tags": ["a", "b"]}}

        result = invoke(
            app, "annotations", "--source", "plaza", "--uid", "1", "--key", "tags"
        )

        self.assertEqual(result.exit_code, 0, result.output)
        app.get_annotations.assert_called_once_with(ITEM, processor=None, key="tags")
        self.assertEqual(result.output.strip(), '[\n  "a",\n  "b"\n]')

    def test_annotations_of_a_missing_item_is_an_error(self) -> None:
        app = Mock()
        app.get_items.return_value = []

        result = invoke(app, "annotations", "--source", "plaza", "--uid", "nope")

        self.assertEqual(result.exit_code, 1)
        self.assertIn("item 'plaza/nope' not found", result.output)

    def test_artifacts_lists_metadata(self) -> None:
        app = Mock()
        app.list_artifacts.return_value = [
            Artifact("rssfeed", "feed", None, "application/rss+xml", updated_at=NOW)
        ]

        result = invoke(app, "artifacts", "--remixer", "rssfeed")

        self.assertEqual(result.exit_code, 0, result.output)
        app.list_artifacts.assert_called_once_with("rssfeed")
        self.assertIn("application/rss+xml", result.output)

    def test_artifact_prints_content_to_stdout_and_metadata_to_stderr(self) -> None:
        app = Mock()
        app.get_artifact.return_value = Artifact(
            "rssfeed", "feed", "<rss/>", "application/rss+xml", updated_at=NOW
        )

        with patch("newsmerger.cli.app_from_context", return_value=app):
            result = CliRunner().invoke(cli, ["artifact", "rssfeed", "feed"])

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.stdout, "<rss/>")
        self.assertIn("rssfeed/feed · application/rss+xml", result.stderr)

    def test_missing_artifact_is_an_error(self) -> None:
        app = Mock()
        app.get_artifact.return_value = None

        result = invoke(app, "artifact", "rssfeed", "nope")

        self.assertEqual(result.exit_code, 1)
        self.assertIn("artifact 'rssfeed/nope' does not exist", result.output)


if __name__ == "__main__":
    unittest.main()
