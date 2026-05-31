import re
from abc import abstractmethod
from datetime import datetime
from logging import getLogger
from typing import Iterator
from zoneinfo import ZoneInfo

import bs4

from ..models import SourceEntryData
from . import BaseProvider

LOGGER = getLogger(__name__)
LOCAL_TZ = ZoneInfo("Europe/Madrid")

MONTH_TABLE = {
    "ene": 1,
    "feb": 2,
    "mar": 3,
    "abr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dic": 12,
}

DATE_RE = re.compile(r"(\d{1,2}) (?:de )?(\S+) (?:de )?(\d{4})", re.IGNORECASE)


def extract_date(text: str) -> datetime:
    match = DATE_RE.search(text)
    if not match:
        raise ValueError(f"Unable to extract date from: {text!r}")

    day_str, month_str, year_str = match.groups()
    month_key = month_str[:3].lower()
    try:
        month = MONTH_TABLE[month_key]
    except KeyError as exc:
        raise ValueError(f"Unknown month: {month_str!r}") from exc

    return datetime(
        year=int(year_str),
        month=month,
        day=int(day_str),
        hour=12,
        tzinfo=LOCAL_TZ,
    )


class Provider(BaseProvider):
    def parse_listing(self, buffer: bytes) -> list[SourceEntryData]:
        return list(self._parse_listing_g(buffer))

    def _parse_listing_g(self, buffer: bytes) -> Iterator[SourceEntryData]:
        soup = bs4.BeautifulSoup(buffer, "html5lib")

        for link in soup.select("a[href]"):
            href = link.get("href") or ""
            if ".pdf/" not in href:
                continue

            li_parent = self.find_parent_by_tag_name(link, "li")
            if li_parent is None:
                continue

            dt_text = li_parent.get_text(" ", strip=True)
            try:
                dt = extract_date(dt_text)
            except ValueError:
                # LOGGER.warning(f"unable to parse {dt_text}")
                continue

            href = f"https://castello.es{href}"

            yield SourceEntryData(
                id=href,
                title=li_parent.text,
                data={
                    "uri": href,
                    "published_at": dt.isoformat(),
                },
            )

    @abstractmethod
    def parse_item(self, buffer: bytes) -> SourceEntryData: ...

    def find_parent_by_tag_name(
        self,
        node: bs4.element.Tag,
        name: str,
    ) -> bs4.element.Tag | None:
        current = node
        while current is not None and current.name != name:
            current = current.parent
        return current
