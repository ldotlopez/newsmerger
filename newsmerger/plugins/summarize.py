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
    # Followed by the article's markdown.
    prompt: str = SUMMARY_PROMPT
    max_retries: int = 3


class SummarizeProcessor(BaseProcessor):
    name = "summarize"
    key = "summary"
    requires = "markdown"

    def __init__(self, llm: LLM, cfg: Options) -> None:
        super().__init__(max_retries=cfg.max_retries)
        self.llm = llm
        self.model = cfg.model
        self.prompt = cfg.prompt

    def process_item(
        self,
        db: Database,
        item: SourceItem,
        prompt: str | None = None,
        model: str | None = None,
    ) -> str:
        markdown = self.require_annotation(db, item, "markdown")

        summary = self.llm.prompt(
            (prompt or self.prompt) + markdown, model=model or self.model
        ).strip()
        if not summary:
            raise ValueError("LLM returned an empty summary")

        return summary


def __newsmerger_plugin__(services: Services, **options: Any) -> PluginObjects:
    cfg = Options.model_validate(options)
    name = SummarizeProcessor.name
    try:
        processor = SummarizeProcessor(services.llm(cfg.llm), cfg)
    except LLMUnavailableError as e:
        unavailable = UnavailableProcessor(name, str(e), SummarizeProcessor.output_key)
        return [(name, Processor, unavailable)]
    return [(name, Processor, processor)]
