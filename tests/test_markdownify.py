"""markdownify on PDF items, with a PDF built in memory."""

import unittest
from unittest.mock import Mock

import pymupdf

from newstool.models import SourceData, SourceItem
from newstool.plugins import Services
from newstool.plugins.markdownify import MarkdownifyProcessor
from newstool.processors import ProcessorOptions, SkipItem


def make_pdf(*pages: str) -> bytes:
    with pymupdf.open() as doc:
        for text in pages:
            doc.new_page().insert_text((72, 72), text)
        return doc.tobytes()


class MarkdownifyPdfTests(unittest.TestCase):
    def process(self, content: bytes) -> dict:
        db = Mock(get_content=Mock(return_value=content))
        item = SourceItem(
            source=SourceData(
                id="juntas",
                name="Juntas",
                url="https://www.castello.es/es/sesiones",
                provider="csjuntasgobierno",
            ),
            uid="acta",
            title="Acta",
            uri="https://example.test/acta.pdf",
            mimetype="application/pdf",
        )
        processor = MarkdownifyProcessor(
            ProcessorOptions(), Services(db=db, fetcher=Mock())
        )
        return processor.process_item(item)

    def test_extracts_the_text_of_every_page(self) -> None:
        content = make_pdf("Primera pagina", "Segunda pagina")
        markdown = self.process(content)

        self.assertEqual(markdown, "# Acta\n\nPrimera pagina\n\nSegunda pagina")

    def test_pdf_without_text_is_skipped(self) -> None:
        with self.assertRaisesRegex(SkipItem, "empty extract"):
            self.process(make_pdf(""))


if __name__ == "__main__":
    unittest.main()
