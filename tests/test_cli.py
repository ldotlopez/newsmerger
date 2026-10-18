import unittest
from unittest.mock import Mock, patch

from click.testing import CliRunner

from newsmerger.cli import cli
from newsmerger.config import ConfigError
from newsmerger.models import ProcessingScope, SourceData, SourceItem
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


if __name__ == "__main__":
    unittest.main()
