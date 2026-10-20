"""Processors and a remixer backed by one Ollama server: `summarize` and
`tagger` read the markdown, `embed` turns the tags and the markdown into
vectors, and the `digest` remixer writes a markdown digest of the highlights
of each source in scope.

Without sections the three processors are enabled with their defaults; with
sections, only the listed objects are. `digest` is enabled only by its
section, since every remix run sends a week of articles to the model.
"""

import dataclasses
import json
import logging
from collections.abc import Callable, Iterator
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import ollama
import pydantic

from ..db import Database
from ..models import ProcessingScope, SourceData, SourceItem
from ..processors import BaseProcessor, Processor
from ..remixers import BaseRemixer, Remixer
from . import PluginObjects, PluginOptions

LOGGER = logging.getLogger(__name__)

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "gemma4:12b"
DEFAULT_EMBEDDING_MODEL = "mxbai-embed-large:latest"

SUMMARY_PROMPT = """Summarize the following news article in the same language as the
article. Return only a concise summary of 3 to 5 sentences.

Article:
"""

DIGEST_PROMPT = """You are the editor of a weekly news digest. Below are the articles
a news source published in the period, numbered, each with its title, date, link
and text. Write the digest in Markdown, in the same language as the articles:

- Open with one paragraph that sums up the period.
- Then pick the 5 to 10 most relevant stories, merging the articles about the
  same story into one entry.
- Give each story a `##` heading and a paragraph of 2 to 4 sentences, followed
  by the links of its articles as Markdown links.
- Return only the digest: no title, preface or closing remarks.

Articles:

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


class DigestOptions(PluginOptions):
    model: str = DEFAULT_MODEL
    days: int = 7  # scope when it sets no `since`
    max_items: int = 50  # newest items per source
    max_article_chars: int = 3000  # each article's markdown is cut to this
    context_length: int = 32768  # the model's context window, in tokens


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
    digest: DigestOptions = DigestOptions()

    @pydantic.field_validator("summarize", "tagger", "embed", "digest", mode="before")
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
            parsed = json.loads(strip_code_fence(resp.response))
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


class DigestRemixer(BaseRemixer):
    """Writes a markdown digest of each source in scope from the markdown of
    its newest items of the last `days`; one artifact per source, named by
    the source id. Items without `markdownify.markdown` are left out."""

    name = "digest"

    def __init__(self, client: ollama.Client, cfg: DigestOptions) -> None:
        self.client = client
        self.model = cfg.model
        self.days = cfg.days
        self.max_items = cfg.max_items
        self.max_article_chars = cfg.max_article_chars
        self.context_length = cfg.context_length

    def produce(
        self, db: Database, scope: ProcessingScope
    ) -> Iterator[tuple[str, str, str]]:
        now = datetime.now(UTC)
        since = scope.since or now - timedelta(days=self.days)
        until = scope.until or now
        items = db.get_items(dataclasses.replace(scope, since=since), newest_first=True)
        markdowns = db.get_annotation_values(
            items, processor="markdownify", key="markdown"
        )

        items_by_source: dict[str, list[SourceItem]] = {}
        for item in items:
            if item.key in markdowns:
                items_by_source.setdefault(item.source.id, []).append(item)
        if not items_by_source:
            LOGGER.info(f"{self.name}: no items with markdown in scope")

        for source_id, source_items in items_by_source.items():
            articles = [
                (item, markdowns[item.key])
                for item in reversed(source_items[: self.max_items])
            ]
            digest = self._write(source_items[0].source, articles, since, until)
            yield source_id, digest, "text/markdown"

    def _write(
        self,
        source: SourceData,
        articles: list[tuple[SourceItem, str]],
        since: datetime,
        until: datetime,
    ) -> str:
        prompt = DIGEST_PROMPT + "\n\n".join(
            self._article_text(number, item, markdown)
            for number, (item, markdown) in enumerate(articles, start=1)
        )
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            stream=False,
            options={"num_ctx": self.context_length},
        )
        body = strip_code_fence(response.response)
        if not body:
            raise ValueError(f"LLM returned an empty digest for '{source.id}'")

        return f"# {source.name}: {since:%Y-%m-%d} – {until:%Y-%m-%d}\n\n{body}\n"

    def _article_text(self, number: int, item: SourceItem, markdown: str) -> str:
        published = f"{item.published_at:%Y-%m-%d}" if item.published_at else "-"
        return (
            f"### {number}. {item.title}\n"
            f"Date: {published}\n"
            f"Link: {item.uri}\n\n"
            f"{markdown[: self.max_article_chars].strip()}"
        )


def tags_text(tags: list[str]) -> str:
    """The text embedded for an item's tags: sorted and comma-separated."""
    return ", ".join(sorted(tags, key=str.lower))


def strip_code_fence(text: str) -> str:
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
    builders: dict[str, tuple[type, Callable[[], Any]]] = {
        "summarize": (Processor, lambda: SummarizeProcessor(client, cfg.summarize)),
        "tagger": (Processor, lambda: TaggerProcessor(client, cfg.tagger)),
        "embed": (Processor, lambda: EmbedProcessor(client, cfg.embed)),
        "digest": (Remixer, lambda: DigestRemixer(client, cfg.digest)),
    }
    enabled = [name for name in options if name in builders] or [
        "summarize",
        "tagger",
        "embed",
    ]
    objects: PluginObjects = []
    for name in enabled:
        protocol, build = builders[name]
        objects.append((name, protocol, build()))
    return objects
