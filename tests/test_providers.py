import datetime
import unittest
from pathlib import Path
from pprint import pprint as pp
from unittest.mock import Mock

import pydantic

from newsmerger.models import SourceData, SourceItemData
from newsmerger.plugins.prensaiberica import PrensaIbericaProvider
from newsmerger.plugins.telegram_channel import (
    TelegramChannelProvider,
    parse_article,
    parse_preview,
    preview_url,
)


def read_sample(name: str) -> bytes:
    filepath = Path(__file__).parent / "samples" / name
    return filepath.read_bytes()


class TestPrensaIberica(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = PrensaIbericaProvider()

    def check_parser(self, filename: str, expected: SourceItemData):
        buff = read_sample(filename)
        entry_data = self.provider.parse_item(buff)
        self.assertEqual(entry_data.uid, expected.uid)
        self.assertEqual(entry_data.uri, expected.uri)
        self.assertEqual(entry_data.title, expected.title)
        self.assertTrue(len(entry_data.content) > 1000)
        self.assertEqual(entry_data.data["image"], expected.data["image"])
        self.assertEqual(entry_data.data["section"], expected.data["section"])
        self.assertEqual(entry_data.data["author"], expected.data["author"])
        self.assertEqual(set(entry_data.data["tags"]), set(expected.data["tags"]))

    def dump_entry_data(self, entry_data: SourceItemData) -> None:
        # entry_data.content = entry_data.content[0:50]
        pp(entry_data)

    def test_parse_item_0(self) -> None:
        self.check_parser(
            "prensaiberica-item-132310503.html",
            SourceItemData(
                uid="ec16b09f034ca03296e75d7e5c304f10337f2e77a0327b0d045c54f0a1d970e8",
                title="El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón",
                uri="https://www.elperiodicomediterraneo.com/castello/2026/07/11/eco-perdido-fiestas-julio-castellon-ribalta-carlista-historia-132310503.html",
                content=b"[ignore]",
                mimetype="text/html",
                data={
                    "author": "Ximo Górriz",
                    "image": "https://estaticos-cdn.prensaiberica.es/clip/66d17ffb-8e7c-43cf-9a9f-40d50ef6654d_16-9-discover-aspect-ratio_default_0_x683y256.png",
                    "section": "Castelló Ciutat",
                    "tags": [
                        "Banda Municipal de Castelló",
                        "Castellón",
                        "cultura",
                        "Democracia",
                        "dictadura",
                        "Educación",
                        "Fiestas",
                        "guerras",
                        "Hemeroteca",
                        "historia",
                        "julio",
                        "Liberalismo",
                        "Parque Ribalta",
                        "Política",
                        "prensa",
                        "Religión",
                        "Tráfico",
                        "Urbanismo",
                    ],
                },
            ),
        )

    def test_parse_item_1(self) -> None:
        self.check_parser(
            "prensaiberica-item-132340038.html",
            SourceItemData(
                uid="1cdcc387ffb74bf5aac47f4362155338180c7c2a791ace14068a3dc7eecfd436",
                title="El Grau se vuelca en las fiestas en honor a la Virgen "
                "del Carmen: los 22 actos del programa y todas las "
                "novedades",
                content=b"[ignore]",
                mimetype="text/html",
                uri="https://www.elperiodicomediterraneo.com/castello/2026/07/11/grau-vuelca-fiestas-honor-virgen-carmen-actos-castello-castellon-132340038.html",
                data={
                    "author": "Paloma Aguilar",
                    "image": "https://estaticos-cdn.prensaiberica.es/clip/dc0a25d9-fc1d-4d2b-9b47-59120753422c_16-9-discover-aspect-ratio_default_0_x783y366.jpg",
                    "mod_date": datetime.datetime(
                        2026,
                        7,
                        11,
                        6,
                        10,
                        18,
                        tzinfo=datetime.timezone(datetime.timedelta(seconds=7200)),
                    ),
                    "pub_date": datetime.datetime(
                        2026,
                        7,
                        11,
                        6,
                        10,
                        18,
                        tzinfo=datetime.timezone(datetime.timedelta(seconds=7200)),
                    ),
                    "section": "Castelló Ciutat",
                    "tags": [
                        "Castelló",
                        "novedades",
                        "La Virgen",
                        "Fiestas",
                        "El Grau",
                    ],
                },
            ),
        )

    def test_parse_item_2(self) -> None:
        self.check_parser(
            "prensaiberica-item-132344288.html",
            SourceItemData(
                uid="12cd5c47e09f096cdb188afee9bd8d25ee06d40ee41feb1c2ec2d11f1679f96b",
                title="Castellón apoya a la selección española desde la plaza Mayor",
                uri="https://www.elperiodicomediterraneo.com/deportes/2026/07/10/castellon-apoya-seleccion-espanola-plaza-belgica-mayor-132344288.html",
                content=b"[ignore]",
                mimetype="text/html",
                data={
                    "author": "David Oliver",
                    "image": "https://estaticos-cdn.prensaiberica.es/clip/2e7b2496-8242-4717-b9ed-738592c3f461_16-9-discover-aspect-ratio_default_0_x731y325.jpg",
                    "mod_date": datetime.datetime(
                        2026,
                        7,
                        10,
                        22,
                        17,
                        29,
                        tzinfo=datetime.timezone(datetime.timedelta(seconds=7200)),
                    ),
                    "pub_date": datetime.datetime(
                        2026,
                        7,
                        10,
                        22,
                        17,
                        29,
                        tzinfo=datetime.timezone(datetime.timedelta(seconds=7200)),
                    ),
                    "section": "Deportes",
                    "tags": [
                        "Deportes",
                        "Castellón",
                        "Selección Española",
                        "plaza Mayor",
                        "Ayuntamiento",
                        "En directo",
                    ],
                },
            ),
        )

    def test_retrieve_item_fetches_and_parses_url(self) -> None:
        content = read_sample("prensaiberica-item-132310503.html")
        fetcher = Mock()
        fetcher.get.return_value = content
        item = self.provider.retrieve_item("https://example.test/article", fetcher)

        fetcher.get.assert_called_once_with("https://example.test/article")
        self.assertEqual(
            item.uid,
            "ec16b09f034ca03296e75d7e5c304f10337f2e77a0327b0d045c54f0a1d970e8",
        )


ARTICLE = b"""<!DOCTYPE html><html><head>
<meta property="og:url" content="https://example.test/news/a.html">
<meta property="og:title" content="A title">
</head><body><article><p>Body</p></article></body></html>"""


class TestTelegramChannel(unittest.TestCase):
    PAGE_URL = "https://t.me/s/mediterraneoelperiodico"

    def source(self, url: str = "https://t.me/mediterraneoelperiodico") -> SourceData:
        return SourceData(id="tg", name="tg", url=url, provider="telegram_channel")

    def test_preview_url_accepts_channel_and_preview_urls(self) -> None:
        self.assertEqual(preview_url(self.source()), self.PAGE_URL)
        self.assertEqual(preview_url(self.source(self.PAGE_URL + "/")), self.PAGE_URL)
        with self.assertRaises(ValueError):
            preview_url(self.source("https://t.me/"))

    def test_parse_preview(self) -> None:
        content = read_sample("telegram-channel-mediterraneoelperiodico.html")
        posts, older = parse_preview(content, self.PAGE_URL)

        self.assertEqual(len(posts), 20)
        self.assertEqual(older, self.PAGE_URL + "?before=5154")
        first = posts[0]
        self.assertEqual(first.id, "mediterraneoelperiodico/5154")
        self.assertEqual(first.links, ["https://mrf.lu/2vjWp"])
        self.assertEqual(
            first.published_at,
            datetime.datetime(2026, 10, 22, 7, 34, 7, tzinfo=datetime.UTC),
        )
        self.assertTrue(first.text.startswith("Amenaza con un machete"))
        for post in posts:
            self.assertFalse(any("t.me/" in link for link in post.links))

    def test_parse_article_uses_canonical_url(self) -> None:
        item = parse_article(ARTICLE)
        self.assertEqual(item.uri, "https://example.test/news/a.html")
        self.assertEqual(item.title, "A title")
        self.assertEqual(item.mimetype, "text/html")

    def test_parse_article_rejects_non_articles(self) -> None:
        with self.assertRaises(ValueError):
            parse_article(b"%PDF-1.7 \xff\xfe")
        with self.assertRaises(ValueError):
            parse_article(b"<html><head><title>406</title></head></html>")

    def test_retrieve_items_one_item_per_link_and_skips_bad_pages(self) -> None:
        pages = {
            self.PAGE_URL: read_sample("telegram-channel-mediterraneoelperiodico.html"),
            "https://mrf.lu/2vjWp": ARTICLE,
        }
        fetcher = Mock()
        fetcher.get.side_effect = lambda url, use_cache=True: pages.get(
            url, b"not html"
        )

        with self.assertLogs("newsmerger.plugins.telegram_channel", "ERROR"):
            items = list(
                TelegramChannelProvider(pages=1).retrieve_items(self.source(), fetcher)
            )

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].data["telegram_post"], "mediterraneoelperiodico/5154")
        self.assertEqual(items[0].published_at.hour, 7)
        # One uncached preview page plus one cached fetch per linked article.
        self.assertEqual(fetcher.get.call_count, 21)
        self.assertEqual(fetcher.get.call_args_list[0].kwargs, {"use_cache": False})
        self.assertEqual(fetcher.get.call_args_list[1].kwargs, {})

    def test_retrieve_items_skips_the_front_page(self) -> None:
        front_page = ARTICLE.replace(
            b"https://example.test/news/a.html",
            b"https://example.test/?utm_source=telegram&amp;mrfcid=1",
        )
        pages = {
            self.PAGE_URL: read_sample("telegram-channel-mediterraneoelperiodico.html"),
            "https://mrf.lu/2vjWp": ARTICLE,
            "https://mrf.lu/2NbpV": front_page,
        }
        fetcher = Mock()
        fetcher.get.side_effect = lambda url, use_cache=True: pages.get(
            url, b"not html"
        )

        with self.assertLogs("newsmerger.plugins.telegram_channel", "ERROR"):
            items = list(
                TelegramChannelProvider(pages=1).retrieve_items(self.source(), fetcher)
            )

        self.assertEqual(
            [item.uri for item in items], ["https://example.test/news/a.html"]
        )

    def test_retrieve_items_rejects_non_public_channels(self) -> None:
        fetcher = Mock()
        fetcher.get.return_value = b"<html><head></head><body></body></html>"
        with self.assertRaises(ValueError):
            list(
                TelegramChannelProvider(pages=1).retrieve_items(self.source(), fetcher)
            )


class TestSourceItemDataContent(unittest.TestCase):
    def make(self, content: bytes, mimetype: str) -> SourceItemData:
        return SourceItemData(
            uid="u",
            title="t",
            uri="https://example.test/a",
            content=content,
            mimetype=mimetype,
        )

    def test_text_must_be_utf8(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            self.make("ñ".encode("latin-1"), "text/html")

    def test_mimetype_must_not_carry_charset(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            self.make(b"<p>", "text/html; charset=utf-8")

    def test_binary_is_not_decoded(self) -> None:
        self.assertEqual(self.make(b"\xff\xfe", "application/pdf").content, b"\xff\xfe")


if __name__ == "__main__":
    unittest.main()
