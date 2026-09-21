import unittest

import pydantic

from newsmerger.config import Config


class PipelineConfigTests(unittest.TestCase):
    def test_loads_named_pipeline_and_steps(self) -> None:
        config = Config.from_text(
            """
            processors:
              - name: markdownify
                params: {}
              - name: summarize
                params:
                  model: small
            pipelines:
              - name: publish
                steps:
                  - processor: markdownify
                  - processor: summarize
                    params:
                      model: fast
            """
        )

        pipeline = config.get_pipeline("publish")

        self.assertEqual(
            [step.processor for step in pipeline.steps],
            ["markdownify", "summarize"],
        )
        self.assertEqual(pipeline.steps[1].params.model_dump(), {"model": "fast"})

    def test_rejects_unknown_processor(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            Config.from_text(
                """
                processors:
                  - name: markdownify
                    params: {}
                pipelines:
                  - name: publish
                    steps:
                      - processor: missing
                """
            )

    def test_rejects_duplicate_pipeline_step(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            Config.from_text(
                """
                processors:
                  - name: markdownify
                    params: {}
                pipelines:
                  - name: publish
                    steps:
                      - processor: markdownify
                      - processor: markdownify
                """
            )

    def test_unknown_pipeline_has_clear_error(self) -> None:
        config = Config()

        with self.assertRaisesRegex(ValueError, "pipeline 'missing' is not configured"):
            config.get_pipeline("missing")
