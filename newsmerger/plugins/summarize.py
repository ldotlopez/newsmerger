"""Summarizes the article's markdown with an LLM."""

from typing import Any

from ..db import Database
from ..llms import LLM, LLMUnavailableError
from ..models import SourceItem
from ..processors import BaseProcessor, Processor, UnavailableProcessor
from . import PluginObjects, PluginOptions, Services

SUMMARY_PROMPT = """Summarize the following news article in the same language as the
article. Return only a concise summary of 3 to 5 sentences.

Article:
"""


class Options(PluginOptions):
    llm: str | None = None
    model: str | None = None
    max_retries: int = 3


class SummarizeProcessor(BaseProcessor):
    name = "summarize"
    requires = "markdownify"

    def __init__(self, llm: LLM, cfg: Options) -> None:
        super().__init__(max_retries=cfg.max_retries)
        self.llm = llm
        self.model = cfg.model

    def process_item(self, db: Database, item: SourceItem) -> dict[str, Any]:
        markdown = self.require_annotation(db, item, "markdownify", "markdown")

        summary = self.llm.prompt(SUMMARY_PROMPT + markdown, model=self.model).strip()
        if not summary:
            raise ValueError("LLM returned an empty summary")

        return {"summary": summary}


def __newsmerger_plugin__(services: Services, **options: Any) -> PluginObjects:
    cfg = Options.model_validate(options)
    name = SummarizeProcessor.name
    try:
        processor = SummarizeProcessor(services.llm(cfg.llm), cfg)
    except LLMUnavailableError as e:
        return [(name, Processor, UnavailableProcessor(name, str(e)))]
    return [(name, Processor, processor)]
