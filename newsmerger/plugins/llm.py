"""Processors backed by one Ollama server: `summarize` and `tagger` read
the markdown, `embed` turns the tags and the markdown into vectors.

Without per-processor sections all three are enabled with their defaults;
with sections, only the listed ones are.
"""

import json
import logging
from typing import Any, Literal

import ollama
import pydantic

from ..db import Database
from ..models import SourceItem
from ..processors import BaseProcessor, Processor
from . import PluginObjects, PluginOptions

LOGGER = logging.getLogger(__name__)

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "gemma4:12b"
DEFAULT_EMBEDDING_MODEL = "mxbai-embed-large:latest"

SUMMARY_PROMPT = """Summarize the following news article in the same language as the
article. Return only a concise summary of 3 to 5 sentences.

Article:
"""

ResponseBaseModel = pydantic.RootModel[list[str]]

RESPONSE_JSON_SCHEMA = json.dumps(ResponseBaseModel.model_json_schema())


TAGS_PROMPT = f"""
You are an expert entity extraction and content tagging assistant. Your sole task is to analyze the provided text and extract relevant tags.

### Extraction Rules:

1.  **Tag Volume:** Extract between 3 and 10 tags maximum. Choose the most significant ones if the text is long.

2.  **Tag Categories:** Extract categories, locations, people, organizations, institutions, concepts, and themes.

3.  **Explicit Tags:** If the text explicitly mentions existing tags or keywords, prioritize and include them.

4.  **Language Matching:** Generate the tags in the exact same language as the source text.


### Output Formatting (Strict Constraint):

*   Return the output **ONLY** as a valid JSON array of strings.

*   Do **NOT** include any conversational filler, prefaces, introductions, or footnotes.

*   Do **NOT** wrap the JSON in markdown code blocks unless specifically requested. Output nothing but the raw JSON structure.

*  Respond with JSON matching this exact schema: {RESPONSE_JSON_SCHEMA}

### Example Output Format:

{{"items": ["Category", "Topic", "Persona Name", "Location Name", "Organization"]}}

### Input Text:

"""


class SummarizeOptions(PluginOptions):
    model: str = DEFAULT_MODEL
    max_retries: int = 3


class TaggerOptions(PluginOptions):
    model: str = DEFAULT_MODEL
    max_retries: int = 3


class EmbedOptions(PluginOptions):
    model: str = DEFAULT_EMBEDDING_MODEL
    inputs: list[Literal["tags", "markdown"]] = pydantic.Field(
        default=["tags", "markdown"], min_length=1
    )
    max_retries: int = 3


class Options(PluginOptions):
    api_base: str = DEFAULT_OLLAMA_URL
    api_key: pydantic.SecretStr | None = None
    summarize: SummarizeOptions = SummarizeOptions()
    tagger: TaggerOptions = TaggerOptions()
    embed: EmbedOptions = EmbedOptions()

    @pydantic.field_validator("summarize", "tagger", "embed", mode="before")
    @classmethod
    def empty_section_takes_defaults(cls, value: Any) -> Any:
        return {} if value is None else value


def ollama_client(cfg: Options) -> ollama.Client:
    """An Ollama client, authenticated with a bearer token when one is given."""
    api_key = cfg.api_key.get_secret_value() if cfg.api_key else ""
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else None
    return ollama.Client(host=cfg.api_base, headers=headers)


class SummarizeProcessor(BaseProcessor):
    name = "summarize"
    requires = "markdownify"

    def __init__(self, client: ollama.Client, cfg: SummarizeOptions) -> None:
        super().__init__(max_retries=cfg.max_retries)
        self.client = client
        self.model = cfg.model

    def process_item(self, db: Database, item: SourceItem) -> dict[str, Any]:
        markdown = self.require_annotation(db, item, "markdownify", "markdown")

        response = self.client.generate(
            model=self.model, prompt=SUMMARY_PROMPT + markdown, stream=False
        )
        summary = response.response.strip()
        if not summary:
            raise ValueError("LLM returned an empty summary")

        return {"summary": summary}


class TaggerProcessor(BaseProcessor):
    name = "tagger"
    requires = "markdownify"

    def __init__(self, client: ollama.Client, cfg: TaggerOptions) -> None:
        super().__init__(max_retries=cfg.max_retries)
        self.client = client
        self.model = cfg.model

    def process_item(self, db: Database, item: SourceItem) -> dict[str, Any]:
        markdown = self.require_annotation(db, item, "markdownify", "markdown")

        # https://gemma4-ai.com/blog/gemma4-json-output
        resp = self.client.generate(
            model=self.model, prompt=TAGS_PROMPT + markdown, stream=False, format="json"
        )

        try:
            parsed = json.loads(clean_json(resp.response))
            llm_tags = ResponseBaseModel(parsed["items"]).root
        except (
            pydantic.ValidationError,
            KeyError,
            AttributeError,
            json.JSONDecodeError,
        ) as e:
            raise ValueError(f"invalid tags response {resp.response!r}: {e}") from e

        results = {}

        item_tags = item.data.get("tags", [])
        if isinstance(item_tags, list):
            results["tags"] = merge_tags(llm_tags, item_tags)
        else:
            results["tags"] = llm_tags

        LOGGER.debug(f"Tags for {item.title}: {results['tags']!r}")
        return results


class EmbedProcessor(BaseProcessor):
    """Annotates `<input>_embedding` per configured input, plus `tags_text`,
    the exact text the tags embedding was computed from."""

    name = "embed"
    requires = "tagger"  # which in turn requires markdownify

    def __init__(self, client: ollama.Client, cfg: EmbedOptions) -> None:
        super().__init__(max_retries=cfg.max_retries)
        self.client = client
        self.model = cfg.model
        self.inputs = cfg.inputs

    def process_item(self, db: Database, item: SourceItem) -> dict[str, Any]:
        texts: dict[str, str] = {}
        if "tags" in self.inputs:
            tags = self.require_annotation(db, item, "tagger", "tags")
            texts["tags"] = tags_text(tags)
        if "markdown" in self.inputs:
            texts["markdown"] = self.require_annotation(
                db, item, "markdownify", "markdown"
            )

        response = self.client.embed(model=self.model, input=list(texts.values()))
        results: dict[str, Any] = {
            f"{name}_embedding": list(embedding)
            for name, embedding in zip(texts, response.embeddings, strict=True)
        }
        if "tags" in texts:
            results["tags_text"] = texts["tags"]
        return results


def tags_text(tags: list[str]) -> str:
    """The text embedded for an item's tags: sorted and comma-separated."""
    return ", ".join(sorted(tags, key=str.lower))


def clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]  # Remove first line
        text = text.rsplit("```", 1)[0]  # Remove last ```
    return text.strip()


def merge_tags(existing_tags: list[str], new_tags: list[str]) -> list[str]:
    """Merge two tag lists case-insensitively, keeping the first spelling and order."""
    merged: dict[str, str] = {}
    for tag in existing_tags + new_tags:
        merged.setdefault(tag.lower(), tag)
    return list(merged.values())


def __newsmerger_plugin__(**options: Any) -> PluginObjects:
    cfg = Options.model_validate(options)
    client = ollama_client(cfg)
    builders = {
        "summarize": lambda: SummarizeProcessor(client, cfg.summarize),
        "tagger": lambda: TaggerProcessor(client, cfg.tagger),
        "embed": lambda: EmbedProcessor(client, cfg.embed),
    }
    enabled = [name for name in options if name in builders] or list(builders)
    processors = [builders[name]() for name in enabled]
    return [(processor.name, Processor, processor) for processor in processors]
