import unittest
from unittest.mock import Mock, patch

from click.testing import CliRunner

from newsmerger.cli import cli
from newsmerger.config import PipelineConfig, PipelineStepConfig
from newsmerger.models import SourceItem


class ImportUrlCommandTests(unittest.TestCase):
    def test_import_url_passes_provider_and_url_to_app(self) -> None:
        item = SourceItem(
            source=Mock(),
            uid="item-1",
            title="Imported title",
            uri="https://example.test/article",
        )
        app = Mock()
        app.import_url.return_value = item

        with patch("newsmerger.cli.App.from_click_context", return_value=app):
            result = CliRunner().invoke(
                cli,
                [
                    "import-url",
                    "--provider",
                    "prensaiberica_plain",
                    "https://example.test/article",
                ],
            )

        self.assertEqual(result.exit_code, 0, result.output)
        source = app.import_url.call_args.args[0]
        self.assertEqual(source.provider, "prensaiberica_plain")
        self.assertEqual(str(source.url), "https://example.test/article")
        self.assertIn("Imported item 'Imported title'", result.output)

    def test_pipeline_url_runs_configured_pipeline(self) -> None:
        item = SourceItem(
            source=Mock(),
            uid="item-1",
            title="Imported title",
            uri="https://example.test/article",
        )
        app = Mock()
        app.import_url.return_value = item
        pipeline = PipelineConfig(
            name="publish-news",
            steps=[
                PipelineStepConfig(processor="markdownify"),
                PipelineStepConfig(processor="summarize"),
            ],
        )
        app.config.get_pipeline.return_value = pipeline

        with patch("newsmerger.cli.App.from_click_context", return_value=app):
            result = CliRunner().invoke(
                cli,
                [
                    "pipeline-url",
                    "publish-news",
                    "--provider",
                    "prensaiberica_plain",
                    "https://example.test/article",
                ],
            )

        self.assertEqual(result.exit_code, 0, result.output)
        app.run_pipeline.assert_called_once_with(item, pipeline, force=False)
        self.assertIn("Processed 'Imported title'", result.output)


if __name__ == "__main__":
    unittest.main()
