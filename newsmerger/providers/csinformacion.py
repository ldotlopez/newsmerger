from pprint import pprint as pp

import bs4

from ..models import SourceEntryData
from . import BaseProvider


class Provider(BaseProvider):
    def parse_listing(self, buffer: bytes) -> list[SourceEntryData]:
        soup = bs4.BeautifulSoup(buffer, "html5lib")
        items = soup.select("p.entry-title a")
        pp([x.text[0:50] for x in items])

        import ipdb

        ipdb.set_trace()
        pass
