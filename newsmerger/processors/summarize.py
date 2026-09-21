from __future__ import annotations

import os
from typing import Any

import ollama

from ..models import SourceItem
from . import ItemProcessor, PartialFailure

PROMPT = """Summarize the following news article in the same language as the
article. Return only a concise summary of 3 to 5 sentences.

Article:
"""


class Processor(ItemProcessor):
    NAME = "summarize"

    def __init__(
        self,
        *args: Any,
        api_base: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.model = model or os.environ.get("OLLAMA_MODEL", "gemma3:4b")
        host = api_base or os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else None
        self.client = ollama.Client(host=host, headers=headers)

    def process_item(self, item: SourceItem) -> dict[str, Any]:
        annotations = self.db.get_annotations(item, processor="markdownify", key="text")
        text = annotations.get("markdownify", {}).get("text")
        if not text:
            raise PartialFailure(
                {},
                {"summary": "markdownify text annotation is not available"},
            )

        response = self.client.generate(
            model=self.model,
            prompt=PROMPT + text,
            stream=False,
        )
        summary = response.response.strip()
        if not summary:
            raise PartialFailure({}, {"summary": "LLM returned an empty summary"})

        self.db.save_artifact(
            self.NAME,
            f"summary:{item.uid}",
            summary,
            "text/plain",
        )
        return {"summary": summary}
