"""Extracts entity tags from the article's markdown with an Ollama model."""

import json
import logging
from typing import Any

import pydantic

from ..db import Database
from ..llm import DEFAULT_OLLAMA_URL, ollama_client
from ..models import SourceItem
from . import BaseProcessor

LOGGER = logging.getLogger(__name__)

ResponseBaseModel = pydantic.RootModel[list[str]]

RESPONSE_JSON_SCHEMA = json.dumps(ResponseBaseModel.model_json_schema())


PROMPT = f"""
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


class Processor(BaseProcessor):
    NAME = "tagger"
    REQUIRES = "markdownify"

    def __init__(
        self,
        db: Database,
        *,
        model: str,
        api_base: str = DEFAULT_OLLAMA_URL,
        api_key: str | None = None,
        max_retries: int | None = None,
    ) -> None:
        super().__init__(db, max_retries=max_retries)
        self.model = model
        self.client = ollama_client(api_base, api_key)

    def process_item(self, item: SourceItem) -> dict[str, Any]:
        markdown = self.require_annotation(item, "markdownify", "markdown")

        # https://gemma4-ai.com/blog/gemma4-json-output
        resp = self.client.generate(
            model=self.model, prompt=PROMPT + markdown, stream=False, format="json"
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
