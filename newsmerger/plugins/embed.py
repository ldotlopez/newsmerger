"""Embeds the item's tags or markdown with an LLM, for the `embeddings`
grouping remixer."""

from typing import Any, Literal

from ..db import Database
from ..llms import LLM, LLMUnavailableError
from ..models import SourceItem
from ..processors import BaseProcessor, Processor, UnavailableProcessor
from . import PluginObjects, PluginOptions, Services


class EmbedOptions(PluginOptions):
    """Per `process:` entry; the section sets their defaults."""

    input: Literal["tags", "markdown"] = "tags"  # the annotation embedded
    model: str | None = None


class Options(EmbedOptions):
    llm: str | None = None
    max_retries: int = 3


class EmbedProcessor(BaseProcessor):
    """Annotates `<input>_embedding`: the embedding of the `tags` (as
    `tags_text`) or the `markdown` annotation, as the run's `input` option
    says (default `tags`)."""

    name = "embed"
    key = "tags_embedding"
    options_model = EmbedOptions

    def __init__(self, llm: LLM, cfg: Options) -> None:
        super().__init__(cfg, max_retries=cfg.max_retries)
        self.llm = llm

    @classmethod
    def output_key(cls, options: EmbedOptions) -> str:
        return f"{options.input}_embedding"

    def required_key(self, options: EmbedOptions) -> str | None:
        return options.input

    def process_item(
        self, db: Database, item: SourceItem, options: EmbedOptions
    ) -> list[float]:
        value = self.require_annotation(db, item, options.input)
        text = tags_text(value) if options.input == "tags" else value
        return self.llm.embed([text], model=options.model)[0]


def tags_text(tags: list[str]) -> str:
    """The text embedded for an item's tags: sorted and comma-separated."""
    return ", ".join(sorted(tags, key=str.lower))


def __newsmerger_plugin__(services: Services, **options: Any) -> PluginObjects:
    cfg = Options.model_validate(options)
    name = EmbedProcessor.name
    try:
        processor = EmbedProcessor(services.llm(cfg.llm), cfg)
    except LLMUnavailableError as e:
        unavailable = UnavailableProcessor(name, str(e), EmbedProcessor, cfg)
        return [(name, Processor, unavailable)]
    return [(name, Processor, processor)]
