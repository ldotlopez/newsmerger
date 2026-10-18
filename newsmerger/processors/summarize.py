"""Summarizes the article's markdown with an Ollama model."""

from typing import Any

from ..db import Database
from ..llm import DEFAULT_OLLAMA_URL, ollama_client
from ..models import SourceItem
from . import BaseProcessor

PROMPT = """Summarize the following news article in the same language as the
article. Return only a concise summary of 3 to 5 sentences.

Article:
"""


class Processor(BaseProcessor):
    NAME = "summarize"
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

        response = self.client.generate(
            model=self.model, prompt=PROMPT + markdown, stream=False
        )
        summary = response.response.strip()
        if not summary:
            raise ValueError("LLM returned an empty summary")

        return {"summary": summary}
