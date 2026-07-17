"""Example ItemProcessor: derives simple per-item annotations.

This is a placeholder implementation (naive text heuristics, no external
LLM call) meant to demonstrate the processor contract — multiple
annotation keys per item, each computed independently so a failure in one
doesn't lose the other (see `PartialFailure`). Swap `_extract_tags` /
`_summarize` for real LLM calls when wiring this up for real.
"""

import json
import logging
import os
from typing import Any

import ollama

from ..models import SourceItem
from . import ItemProcessor, PartialFailure

LOGGER = logging.getLogger(__name__)

PROMPT = """
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


### Example Output Format:

["Category", "Person Name", "Location Name", "Organization"]

### Input Text:

"""


class Processor(ItemProcessor):
    NAME = "tagger"

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

        self.client = ollama.Client(
            host=api_base,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    def process_item(self, item: SourceItem) -> dict[str, Any]:
        resp = self.client.generate(
            model=self.model, prompt=PROMPT + item.content, stream=False
        )

        results = {}
        errors = {}

        try:
            results["tags"] = json.loads(resp.response)
        except json.JSONDecodeError as e:
            errors["tags"] = str(e) + f"(content={resp.response!r})"

        if errors:
            raise PartialFailure(results, errors)

        item_tags = item.data.get("tags", [])
        if isinstance(item_tags, list):
            results["tags"] = list(set(results["tags"] + item_tags))

        LOGGER.debug(f"Tags for {item.title}: {results['tags']!r}")
        return results
