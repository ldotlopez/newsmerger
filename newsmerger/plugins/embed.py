"""Embeds the item's tags or markdown with an LLM, for the `embeddings`
grouping remixer."""

from typing import Any, Literal, get_args

from ..db import Database
from ..llms import LLM, LLMUnavailableError
from ..models import SourceItem
from ..processors import BaseProcessor, Processor, UnavailableProcessor
from . import PluginObjects, PluginOptions, Services

type Input = Literal["tags", "markdown"]


class Options(PluginOptions):
    llm: str | None = None
    model: str | None = None
    max_retries: int = 3


class EmbedProcessor(BaseProcessor):
    """Annotates `<input>_embedding`: the embedding of the `tags` (as
    `tags_text`) or the `markdown` annotation, as the run's `input` option
    says (default `tags`)."""

    name = "embed"
    key = "tags_embedding"

    def __init__(self, llm: LLM, cfg: Options) -> None:
        super().__init__(max_retries=cfg.max_retries)
        self.llm = llm
        self.model = cfg.model

    @classmethod
    def output_key(cls, **options: Any) -> str:
        super().output_key(**options)  # checks the option names
        source_key = options.get("input", "tags")
        if source_key not in get_args(Input.__value__):
            raise ValueError(f"input must be one of {get_args(Input.__value__)}")
        return f"{source_key}_embedding"

    def required_key(self, **options: Any) -> str | None:
        return options.get("input", "tags")

    def process_item(
        self,
        db: Database,
        item: SourceItem,
        input: Input = "tags",
        model: str | None = None,
    ) -> list[float]:
        value = self.require_annotation(db, item, input)
        text = tags_text(value) if input == "tags" else value
        return self.llm.embed([text], model=model or self.model)[0]


def tags_text(tags: list[str]) -> str:
    """The text embedded for an item's tags: sorted and comma-separated."""
    return ", ".join(sorted(tags, key=str.lower))


def __newsmerger_plugin__(services: Services, **options: Any) -> PluginObjects:
    cfg = Options.model_validate(options)
    name = EmbedProcessor.name
    try:
        processor = EmbedProcessor(services.llm(cfg.llm), cfg)
    except LLMUnavailableError as e:
        unavailable = UnavailableProcessor(name, str(e), EmbedProcessor.output_key)
        return [(name, Processor, unavailable)]
    return [(name, Processor, processor)]
