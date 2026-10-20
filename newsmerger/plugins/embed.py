"""Embeds the item's tags and markdown with an LLM, for the `embeddings`
grouping remixer."""

from typing import Any, Literal

import pydantic

from ..db import Database
from ..llms import LLM, LLMUnavailableError
from ..models import SourceItem
from ..processors import BaseProcessor, Processor, UnavailableProcessor
from . import PluginObjects, PluginOptions, Services


class Options(PluginOptions):
    llm: str | None = None
    model: str | None = None
    inputs: list[Literal["tags", "markdown"]] = pydantic.Field(
        default=["tags", "markdown"], min_length=1
    )
    max_retries: int = 3


class EmbedProcessor(BaseProcessor):
    """Annotates `<input>_embedding` per configured input, plus `tags_text`,
    the exact text the tags embedding was computed from."""

    name = "embed"
    requires = "tagger"  # which in turn requires markdownify

    def __init__(self, llm: LLM, cfg: Options) -> None:
        super().__init__(max_retries=cfg.max_retries)
        self.llm = llm
        self.model = cfg.model
        self.inputs = cfg.inputs

    def process_item(self, db: Database, item: SourceItem) -> dict[str, Any]:
        texts: dict[str, str] = {}
        if "tags" in self.inputs:
            tags = self.require_annotation(db, item, "tagger", "tags")
            texts["tags"] = tags_text(tags)
        if "markdown" in self.inputs:
            texts["markdown"] = self.require_annotation(
                db, item, "markdownify", "markdown"
            )

        embeddings = self.llm.embed(list(texts.values()), model=self.model)
        results: dict[str, Any] = {
            f"{name}_embedding": embedding
            for name, embedding in zip(texts, embeddings, strict=True)
        }
        if "tags" in texts:
            results["tags_text"] = texts["tags"]
        return results


def tags_text(tags: list[str]) -> str:
    """The text embedded for an item's tags: sorted and comma-separated."""
    return ", ".join(sorted(tags, key=str.lower))


def __newsmerger_plugin__(services: Services, **options: Any) -> PluginObjects:
    cfg = Options.model_validate(options)
    name = EmbedProcessor.name
    try:
        processor = EmbedProcessor(services.llm(cfg.llm), cfg)
    except LLMUnavailableError as e:
        return [(name, Processor, UnavailableProcessor(name, str(e)))]
    return [(name, Processor, processor)]
