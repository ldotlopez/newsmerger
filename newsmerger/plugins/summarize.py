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


class SummarizeOptions(PluginOptions):
    """Per `process:` entry; the section sets their defaults."""

    model: str | None = None
    # Followed by the article's markdown.
    prompt: str = SUMMARY_PROMPT


class Options(SummarizeOptions):
    llm: str | None = None
    max_retries: int = 3


class SummarizeProcessor(BaseProcessor):
    name = "summarize"
    key = "summary"
    requires = "markdown"
    options_model = SummarizeOptions

    def __init__(self, llm: LLM, cfg: Options) -> None:
        super().__init__(cfg, max_retries=cfg.max_retries)
        self.llm = llm

    def process_item(
        self, db: Database, item: SourceItem, options: SummarizeOptions
    ) -> str:
        markdown = self.require_annotation(db, item, "markdown")

        summary = self.llm.prompt(
            options.prompt + markdown, model=options.model
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
        unavailable = UnavailableProcessor(name, str(e), SummarizeProcessor, cfg)
        return [(name, Processor, unavailable)]
    return [(name, Processor, processor)]
