"""Extracts the article's markdown from HTML and PDF items, for downstream
processors. PDFs give plain text, which is valid markdown."""

import pymupdf
import trafilatura

from ..models import SourceItem
from ..processors import BaseProcessor, ProcessorType, SkipItem
from . import PluginTypes


class MarkdownifyProcessor(BaseProcessor):
    name = "markdownify"
    key = "markdown"

    def process_item(self, item: SourceItem) -> str:
        match item.mimetype:
            case "text/html":
                markdown = self.extract_html(self.db.get_content(item))
            case "application/pdf":
                markdown = self.extract_pdf(self.db.get_content(item))
            case _:
                raise SkipItem(f"unsupported mimetype '{item.mimetype}'")

        if not markdown:
            raise SkipItem("empty extract")

        if item.title and item.title not in markdown:
            markdown = f"# {item.title}\n\n{markdown}"

        return markdown

    @staticmethod
    def extract_html(content: bytes) -> str | None:
        # Parse a str, not bytes: content is UTF-8 whatever its <meta charset> says.
        html = content.decode("utf-8")
        if not html.strip():
            raise SkipItem("empty content")
        return trafilatura.extract(html, output_format="markdown")

    @staticmethod
    def extract_pdf(content: bytes) -> str:
        # Default reading order: column by column, page by page. A scanned PDF
        # has no text layer and extracts empty.
        with pymupdf.open(stream=content, filetype="pdf") as doc:
            return "\n".join(page.get_text() for page in doc).strip()


def __newstool_plugin__() -> PluginTypes:
    return [(MarkdownifyProcessor.name, ProcessorType, MarkdownifyProcessor)]
