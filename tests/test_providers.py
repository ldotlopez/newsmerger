import datetime
import unittest
from pathlib import Path
from pprint import pprint as pp

from newsmerger.models import SourceEntryData
from newsmerger.providers.prensaiberica import Provider as PrensaIbericaProvider


def read_sample(name: str) -> bytes:
    filepath = Path(__file__).parent / "samples" / name
    return filepath.read_bytes()


class TestPrensaIberica(unittest.TestCase):
    NAME = "prensaiberica"

    def setUp(self) -> None:
        self.provider = PrensaIbericaProvider()

    def check_parser(self, filename: str, expected: SourceEntryData):
        buff = read_sample(filename)
        entry_data = self.provider.parse_item(buff)
        self.assertEqual(entry_data.id, expected.id)
        self.assertEqual(entry_data.uri, expected.uri)
        self.assertEqual(entry_data.title, expected.title)
        self.assertTrue(len(entry_data.content) > 1000)
        self.assertEqual(entry_data.data["image"], expected.data["image"])
        self.assertEqual(entry_data.data["section"], expected.data["section"])
        self.assertEqual(entry_data.data["author"], expected.data["author"])
        self.assertEqual(set(entry_data.data["tags"]), set(expected.data["tags"]))

    def dump_entry_data(self, entry_data: SourceEntryData) -> None:
        # entry_data.content = entry_data.content[0:50]
        pp(entry_data)

    def test_parse_item_0(self) -> None:
        self.check_parser(
            "prensaiberica-item-132310503.html",
            SourceEntryData(
                id="ec16b09f034ca03296e75d7e5c304f10337f2e77a0327b0d045c54f0a1d970e8",
                title="El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón",
                uri="https://www.elperiodicomediterraneo.com/castello/2026/07/11/eco-perdido-fiestas-julio-castellon-ribalta-carlista-historia-132310503.html",
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
            SourceEntryData(
                id="1cdcc387ffb74bf5aac47f4362155338180c7c2a791ace14068a3dc7eecfd436",
                title="El Grau se vuelca en las fiestas en honor a la Virgen "
                "del Carmen: los 22 actos del programa y todas las "
                "novedades",
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
            SourceEntryData(
                id="12cd5c47e09f096cdb188afee9bd8d25ee06d40ee41feb1c2ec2d11f1679f96b",
                title="Castellón apoya a la selección española desde la plaza Mayor",
                uri="https://www.elperiodicomediterraneo.com/deportes/2026/07/10/castellon-apoya-seleccion-espanola-plaza-belgica-mayor-132344288.html",
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


if __name__ == "__main__":
    unittest.main()
