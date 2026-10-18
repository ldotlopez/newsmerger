"""Extracts the article's markdown from HTML items, for downstream processors."""

from typing import Any

import trafilatura

from ..models import SourceItem
from . import BaseProcessor, SkipItem


class Processor(BaseProcessor):
    NAME = "markdownify"

    def process_item(self, item: SourceItem) -> dict[str, Any]:
        if item.mimetype != "text/html":
            raise SkipItem(f"unsupported mimetype '{item.mimetype}'")

        # Parse a str, not bytes: content is UTF-8 whatever its <meta charset> says.
        html = self.db.get_content(item).decode("utf-8")
        if not html.strip():
            raise SkipItem("empty content")

        markdown = trafilatura.extract(html, output_format="markdown")
        if not markdown:
            raise SkipItem("empty extract")

        if item.title and item.title not in markdown:
            markdown = f"# {item.title}\n\n{markdown}"

        return {"markdown": markdown}
