import json
import logging
import os
from typing import Any

import ollama
import pydantic

from ..models import SourceItem
from . import ItemProcessor

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


class Processor(ItemProcessor):
    NAME = "tagger"
    REQUIRES = "markdownify"

    def __init__(
        self,
        *args,
        api_base: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.model = model

        api_base = api_base or os.environ.get(
            "OLLAMA_API_BASE", "http://localhost:11343"
        )
        api_key = api_key or os.environ.get("OLLAMA_API_KEY")

        headers = {}
        if api_key:
            headers.update({"Authorization": f"Bearer {api_key}"})

        self.client = ollama.Client(host=api_base, headers=headers)

    def process_item(self, item: SourceItem) -> dict[str, Any]:
        markdown = self.require_annotation(item, "markdownify", "markdown")

        # https://gemma4-ai.com/blog/gemma4-json-output
        resp = self.client.generate(
            model=self.model, prompt=PROMPT + markdown, stream=False, format="json"
        )

        try:
            data = json.loads(clean_json(resp.response))
            llm_tags = ResponseBaseModel(data["items"]).root
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
    """Merge two lists of tags, ensuring uniqueness and preserving order."""

    all_tags = existing_tags + new_tags

    # create table with lowercased tags to ensure case-insensitive uniqueness
    tlb = {x.lower(): [] for x in all_tags}

    for tag in all_tags:
        tlb[tag.lower()].append(tag)

    # take the first occurrence of each tag (preserving original case)
    merged = [tags[0] for tags in tlb.values()]

    return merged
