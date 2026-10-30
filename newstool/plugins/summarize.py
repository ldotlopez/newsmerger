"""Summarizes the article's markdown with an LLM."""

from ..errors import PluginFailure
from ..models import SourceItem
from ..processors import BaseProcessor, ProcessorOptions, ProcessorType
from . import PluginTypes, Services, UsesLLMOptions

SUMMARY_PROMPT = """Summarize the following news article in the same language as the
article. Return only a concise summary of 3 to 5 sentences.

Article:
"""


class SummarizeOptions(ProcessorOptions, UsesLLMOptions):
    model: str | None = None
    # Followed by the article's markdown.
    prompt: str = SUMMARY_PROMPT


class SummarizeProcessor(BaseProcessor):
    name = "summarize"
    key = "summary"
    requires = "markdown"
    options_model = SummarizeOptions
    options: SummarizeOptions

    def __init__(self, options: SummarizeOptions, services: Services) -> None:
        super().__init__(options, services)
        self.llm = services.llm(options.llm)

    def process_item(self, item: SourceItem) -> str:
        markdown = self.require_annotation(item, "markdown")

        summary = self.llm.prompt(
            self.options.prompt + markdown, model=self.options.model
        ).strip()
        if not summary:
            raise PluginFailure("LLM returned an empty summary")

        return summary


def __newstool_plugin__() -> PluginTypes:
    return [(SummarizeProcessor.name, ProcessorType, SummarizeProcessor)]
