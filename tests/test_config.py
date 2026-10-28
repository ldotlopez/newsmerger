import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from newstool.config import Config, ConfigError

SOURCE = """
sources:
  - id: plaza
    name: Castellón Plaza
    provider: plaza
    url: https://castellonplaza.com/castellon9/
"""


class ConfigTests(unittest.TestCase):
    def test_expands_environment_variables(self) -> None:
        with patch.dict("os.environ", {"API_KEY": "secret"}):
            config = Config.from_text("plugins:\n  llm:\n    api_key: ${API_KEY}\n")

        self.assertEqual(config.plugins["llm"], {"api_key": "secret"})

    def test_missing_environment_variable_is_a_clear_error(self) -> None:
        with (
            patch.dict("os.environ", clear=True),
            self.assertRaisesRegex(
                ConfigError,
                r"^plugins\.x\.k: environment variable 'API_KEY' is not set$",
            ),
        ):
            Config.from_text("plugins:\n  x: {k: '${API_KEY}'}\n")

    def test_missing_variable_names_the_file_and_where_to_set_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.yaml"
            config_path.write_text("plugins:\n  x:\n    k: ${API_KEY}\n")

            with (
                patch.dict("os.environ", clear=True),
                self.assertRaises(ConfigError) as caught,
            ):
                Config.from_file(config_path)

        self.assertEqual(
            str(caught.exception),
            f"{config_path}: plugins.x.k: environment variable 'API_KEY' is not set\n"
            f"Set API_KEY in the environment or in {Path(directory) / '.env'}.",
        )

    def test_dotenv_next_to_the_config_fills_variables(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.yaml"
            config_path.write_text("plugins:\n  x: {k: '${API_KEY}', m: '${MODEL}'}\n")
            (Path(directory) / ".env").write_text("API_KEY=from-dotenv\nMODEL=small\n")

            with patch.dict("os.environ", {"MODEL": "from-environment"}, clear=True):
                config = Config.from_file(config_path)

        # The real environment wins over .env.
        self.assertEqual(
            config.plugins["x"], {"k": "from-dotenv", "m": "from-environment"}
        )

    def test_config_without_dotenv_uses_the_environment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.yaml"
            config_path.write_text("plugins:\n  x: {k: '${API_KEY}'}\n")

            with patch.dict("os.environ", {"API_KEY": "env"}, clear=True):
                config = Config.from_file(config_path)

        self.assertEqual(config.plugins["x"], {"k": "env"})

    def test_comments_are_not_expanded(self) -> None:
        with patch.dict("os.environ", clear=True):
            config = Config.from_text(
                "# needs ${API_KEY}\nplugins:\n  feedgenerator:\n"
            )

        self.assertEqual(config.plugins, {"feedgenerator": None})

    def test_double_dollar_is_a_literal_dollar(self) -> None:
        config = Config.from_text("plugins:\n  feedgenerator: {title: costs $$5}\n")

        self.assertEqual(config.plugins["feedgenerator"], {"title": "costs $5"})

    def test_sources_are_found_by_id(self) -> None:
        source = Config.from_text(SOURCE).get_source("plaza")

        self.assertEqual(source.provider, "plaza")

    def test_source_id_is_required(self) -> None:
        with self.assertRaises(ConfigError):
            Config.from_text(SOURCE.replace("  - id: plaza\n    name", "  - name"))

    def test_source_rejects_unknown_fields(self) -> None:
        with self.assertRaises(ConfigError):
            Config.from_text(SOURCE + "    uid: legacy\n")

    def test_source_ids_must_be_unique(self) -> None:
        duplicated = SOURCE + SOURCE.removeprefix("\nsources:\n")
        with self.assertRaisesRegex(ConfigError, "source ids must be unique"):
            Config.from_text(duplicated)

    def test_unknown_sections_are_rejected(self) -> None:
        # `process`, `remix` and `deliver` were the default workflow's runs.
        for section in ("pipelines: []\n", "process: []\n", "deliver: []\n"):
            with self.subTest(section=section), self.assertRaises(ConfigError):
                Config.from_text(section)

    def test_durations_are_seconds_or_take_a_unit_suffix(self) -> None:
        for text, seconds in (("90", 90), ("5m", 300), ("2h", 7200), ("3d", 259200)):
            with self.subTest(text=text):
                config = Config.from_text(f"cache:\n  expiration: {text}\n")
                self.assertEqual(config.cache.expiration, seconds)

    def test_invalid_durations_are_rejected(self) -> None:
        for text in ("soon", "-5m", "-1"):
            with self.subTest(text=text), self.assertRaises(ConfigError):
                Config.from_text(f"cache:\n  expiration: {text}\n")

    def test_empty_plugin_section_enables_the_plugin(self) -> None:
        config = Config.from_text("plugins:\n  markdownify:\n  feedgenerator: {}\n")

        self.assertEqual(config.plugins, {"markdownify": None, "feedgenerator": {}})

    def test_plugin_section_must_be_a_mapping(self) -> None:
        with self.assertRaises(ConfigError):
            Config.from_text("plugins:\n  feedgenerator: [title]\n")

    def test_catalog_entries_are_a_name_or_a_type_with_id_key_and_options(
        self,
    ) -> None:
        config = Config.from_text(
            "processors:\n  - markdownify\n"
            "  - {processor: summarize, id: summary-es, key: summary/es,"
            " options: {model: m}}\n"
        )

        self.assertEqual(
            [
                (entry.processor, entry.id, entry.key, entry.options)
                for entry in config.processors
            ],
            [
                ("markdownify", None, None, {}),
                ("summarize", "summary-es", "summary/es", {"model": "m"}),
            ],
        )

    def test_catalog_entries_reject_unknown_fields(self) -> None:
        with self.assertRaises(ConfigError):
            Config.from_text("processors:\n  - {enricher: summarize}\n")

    def test_catalog_ids_are_unique_per_section(self) -> None:
        with self.assertRaisesRegex(ConfigError, "processors: id.s. a used twice"):
            Config.from_text(
                "processors:\n  - {processor: summarize, id: a}\n"
                "  - {processor: tagger, id: a}\n"
                "remixers:\n  - {remixer: digest, id: a}\n"
            )
        with self.assertRaisesRegex(ConfigError, "invalid id 'A b'"):
            Config.from_text("sinks:\n  - {sink: telegram, id: A b}\n")

    def test_workflow_entries_are_references_or_entries_of_its_own(self) -> None:
        config = Config.from_text(
            SOURCE + "workflows:\n  - name: w\n    sources: [plaza]\n"
            "    process: [markdownify, {processor: summarize, key: s}]\n"
        )

        (workflow,) = config.workflows
        reference, own = workflow.process
        self.assertEqual(reference, "markdownify")
        self.assertEqual((own.processor, own.key), ("summarize", "s"))

    def test_workflow_entries_have_no_id_nor_skip_default(self) -> None:
        for entry in (
            "{processor: summarize, id: s}",
            "{remixer: digest, skip_default: true}",
        ):
            section = "remix" if "remixer" in entry else "process"
            with (
                self.subTest(entry=entry),
                self.assertRaisesRegex(ConfigError, "only catalog entries do"),
            ):
                Config.from_text(
                    SOURCE + f"workflows:\n  - name: w\n    sources: [plaza]\n"
                    f"    {section}: [{entry}]\n"
                )

    def test_default_workflow_has_the_sources_without_skip_default(self) -> None:
        config = Config.from_text(
            SOURCE + "  - {id: other, name: O, provider: plaza, url: 'https://o.test/',"
            " skip_default: true}\n"
        )

        (default,) = config.all_workflows()
        self.assertEqual((default.name, default.sources), ("default", ["plaza"]))
        self.assertEqual((default.process, default.deliver), ([], []))

    def test_unconfigured_source_has_clear_error(self) -> None:
        with self.assertRaisesRegex(ConfigError, "source 'missing' is not configured"):
            Config().get_source("missing")


if __name__ == "__main__":
    unittest.main()
