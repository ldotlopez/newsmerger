import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from newsmerger.config import Config, ConfigError

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
            config = Config.from_text("# needs ${API_KEY}\nplugins:\n  rssfeed:\n")

        self.assertEqual(config.plugins, {"rssfeed": None})

    def test_double_dollar_is_a_literal_dollar(self) -> None:
        config = Config.from_text("plugins:\n  rssfeed: {title: costs $$5}\n")

        self.assertEqual(config.plugins["rssfeed"], {"title": "costs $5"})

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
        for section in ("pipelines: []\n", "processors: []\n", "remixers: []\n"):
            with self.subTest(section=section), self.assertRaises(ConfigError):
                Config.from_text(section)

    def test_empty_plugin_section_enables_the_plugin(self) -> None:
        config = Config.from_text("plugins:\n  markdownify:\n  rssfeed: {}\n")

        self.assertEqual(config.plugins, {"markdownify": None, "rssfeed": {}})

    def test_plugin_section_must_be_a_mapping(self) -> None:
        with self.assertRaises(ConfigError):
            Config.from_text("plugins:\n  rssfeed: [title]\n")

    def test_unconfigured_source_has_clear_error(self) -> None:
        with self.assertRaisesRegex(ConfigError, "source 'missing' is not configured"):
            Config().get_source("missing")


if __name__ == "__main__":
    unittest.main()
