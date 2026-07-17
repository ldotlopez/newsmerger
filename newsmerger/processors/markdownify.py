"""Example ArtifactProcessor: builds a single RSS feed from scoped items.

Scope (--source/--since/--until/--limit) controls which items go into the
feed. Produces one artifact named "feed".
"""

import trafilatura

from ..models import SourceItem
from . import ItemProcessor, SkipItem


class Processor(ItemProcessor):
    NAME = "markdownify"

    def __init__(
        self, *args, title: str = "newsmerger feed", max_items: int = 100, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.title = title
        self.max_items = max_items

    def process_item(self, item: SourceItem) -> dict[str, Any]:
        if not item.content.strip():
            raise SkipItem("empty content")

        title = item.title

        md = trafilatura.extract(item.content, output_format="markdown")
        txt = trafilatura.extract(item.content, output_format="txt")

        if not txt or not md:
            raise SkipItem("empty extract")

        add_title = title and (title not in txt[: len(txt) * 2])
        if add_title:
            txt = f"# {title}\n\n{txt}"
            md = f"# {title}\n\n{md}"

        results = {
            "text": txt,
            "markdown": md,
        }

        return results
