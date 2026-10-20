"""Extracts the article's markdown from HTML items, for downstream processors."""

from typing import Any

import trafilatura

from ..db import Database
from ..models import SourceItem
from ..processors import BaseProcessor, Processor, SkipItem
from . import PluginObjects, PluginOptions, Services


class Options(PluginOptions):
    max_retries: int = 3


class MarkdownifyProcessor(BaseProcessor):
    name = "markdownify"

    def process_item(self, db: Database, item: SourceItem) -> dict[str, Any]:
        if item.mimetype != "text/html":
            raise SkipItem(f"unsupported mimetype '{item.mimetype}'")

        # Parse a str, not bytes: content is UTF-8 whatever its <meta charset> says.
        html = db.get_content(item).decode("utf-8")
        if not html.strip():
            raise SkipItem("empty content")

        markdown = trafilatura.extract(html, output_format="markdown")
        if not markdown:
            raise SkipItem("empty extract")

        if item.title and item.title not in markdown:
            markdown = f"# {item.title}\n\n{markdown}"

        return {"markdown": markdown}


def __newsmerger_plugin__(services: Services, **options: Any) -> PluginObjects:
    cfg = Options.model_validate(options)
    processor = MarkdownifyProcessor(max_retries=cfg.max_retries)
    return [(processor.name, Processor, processor)]
