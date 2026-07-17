"""Example ItemProcessor: derives simple per-item annotations.

This is a placeholder implementation (naive text heuristics, no external
LLM call) meant to demonstrate the processor contract — multiple
annotation keys per item, each computed independently so a failure in one
doesn't lose the other (see `PartialFailure`). Swap `_extract_tags` /
`_summarize` for real LLM calls when wiring this up for real.
"""

import re
from typing import Any

from ..models import SourceItem
from . import ItemProcessor, PartialFailure, SkipItem

STOPWORDS = {
    "de",
    "la",
    "el",
    "en",
    "y",
    "a",
    "los",
    "las",
    "un",
    "una",
    "por",
    "con",
    "para",
    "que",
    "se",
    "del",
    "al",
}
WORD_RE = re.compile(r"[A-ZÀ-Ú][\wÀ-ÿ]+")


class Processor(ItemProcessor):
    NAME = "tagger"
    VERSION = "v1"

    def __init__(self, *args, max_tags: int = 5, summary_length: int = 200, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_tags = max_tags
        self.summary_length = summary_length

    def process_item(self, item: SourceItem) -> dict[str, Any]:
        if not item.content.strip():
            raise SkipItem("empty content")

        results: dict[str, Any] = {}
        errors: dict[str, str] = {}

        try:
            results["tags"] = self._extract_tags(item.title, item.content)
        except Exception as e:
            errors["tags"] = str(e)

        try:
            results["summary"] = self._summarize(item.content)
        except Exception as e:
            errors["summary"] = str(e)

        if errors:
            raise PartialFailure(results, errors)

        return results

    def _extract_tags(self, title: str, content: str) -> list[str]:
        candidates = WORD_RE.findall(f"{title} {content[:2000]}")
        seen: dict[str, int] = {}
        for word in candidates:
            if word.lower() in STOPWORDS:
                continue
            seen[word] = seen.get(word, 0) + 1

        ranked = sorted(seen.items(), key=lambda kv: kv[1], reverse=True)
        return [word for word, _ in ranked[: self.max_tags]]

    def _summarize(self, content: str) -> str:
        text = content.strip().replace("\n", " ")
        if len(text) <= self.summary_length:
            return text
        return text[: self.summary_length].rsplit(" ", 1)[0] + "…"
