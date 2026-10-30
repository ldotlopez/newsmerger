import hashlib
import logging
import re
from collections.abc import Iterator
from datetime import datetime
from typing import cast
from urllib.parse import urljoin, urlsplit

import bs4
from foundation.scrapelib import (
    drop_selectors,
    find_canonical_url,
    head_meta_get_value,
    prune_to_spine,
    soupify,
)

from ..errors import PluginFailure
from ..models import PreflightSourceItemData, SourceData, SourceItemData
from ..providers import BaseProvider, ProviderType
from . import PluginOptions, PluginTypes

LOGGER = logging.getLogger(__name__)

# Article URLs end in their numeric id: `.../slug-135898589.html`.
ARTICLE_HREF = re.compile(r"-\d+\.html$")


class Options(PluginOptions):
    # Index sections whose articles are left out, by header title, compared
    # case-insensitively. An empty list excludes none.
    exclude_sections: tuple[str, ...] = (
        "Comarcas",
        "Vídeos y galerías de Castellón",
    )


class PrensaIbericaProvider(BaseProvider):
    options_model = Options
    options: Options

    def iter_items(self, source: SourceData) -> Iterator[PreflightSourceItemData[str]]:
        # The index dates each article (dateModified): the core skips the
        # stored ones that did not change.
        url = str(source.url)
        soup = soupify(self.fetcher.get(url).decode("utf-8"))
        parts = urlsplit(url)
        site_prefix = f"{parts.scheme}://{parts.netloc}/"

        excluded_ids = {id(c) for c in self._find_excluded_containers(soup)}
        seen: set[str] = set()
        # Innermost articles are the cards; outer ones are layout rows.
        for article in soup.find_all("article"):
            if article.find("article") is not None:
                continue
            if self._is_in_excluded_section(article, excluded_ids):
                continue

            href = _extract_href(article, url)
            if href is None or not href.startswith(site_prefix) or href in seen:
                continue
            seen.add(href)

            yield PreflightSourceItemData(
                uid=hashlib.sha256(href.encode()).hexdigest(),
                ref=href,
                modified_at=_get_modified_at(article),
            )

    def retrieve_item(
        self, preflight_item: PreflightSourceItemData[str]
    ) -> SourceItemData:
        return self.parse_item(self.fetcher.get(preflight_item.ref))

    def parse_item(self, content: bytes) -> SourceItemData:
        soup = soupify(content.decode("utf-8"))

        title = head_meta_get_value(soup, {"property": "og:title"})
        image = head_meta_get_value(soup, {"property": "og:image"})
        author = head_meta_get_value(soup, {"name": "author"})
        if (url := find_canonical_url(soup)) is None:
            raise PluginFailure("no canonical URL")
        tags = head_meta_get_value(soup, {"property": "article:tag"}).split(",")
        section = head_meta_get_value(soup, {"property": "article:section"})
        pub_time = datetime.fromisoformat(
            head_meta_get_value(soup, {"property": "article:published_time"})
        )
        mod_time = datetime.fromisoformat(
            head_meta_get_value(soup, {"property": "article:modified_time"})
        )

        if (main := soup.select_one("#main-content")) is None:
            raise PluginFailure("Could not find main content container")

        for div in main.find_all("div", recursive=False):
            if div.get_text().find("Lo más leído") != -1:
                div.decompose()  # Remove the "Lo más leído" section

        drop_selectors(
            main,
            [
                "#paywall",
                ".ft-mol-rrss-column",
                ".ft-mol-advice",
                ".ft-ad",
                ".closedContent",
                ".ft-mol-writer",
                ".ft-mol-tagsNews",
                ".ft-mol-related",
                ".ft-mol-related__header",
                ".bloque_bajo_noticia",
                "a#comments",
                ".ft-mol-btnGroup",
                ".disqus_thread",
            ],
        )

        root = prune_to_spine(main)

        return SourceItemData(
            uid=hashlib.sha256(url.encode()).hexdigest(),
            title=title,
            uri=url,
            content=str(root).encode("utf-8"),
            mimetype="text/html",
            published_at=pub_time,
            modified_at=mod_time,
            data={
                "author": author,
                "image": image,
                "section": section,
                "tags": tags,
            },
        )

    # --- Section exclusion helpers -------------------------------------

    def _find_excluded_containers(self, soup: bs4.BeautifulSoup) -> list[bs4.Tag]:
        """Find the container divs for sections we want to exclude entirely,
        identified by their header title (e.g. 'Comarcas', 'Vídeos y galerías de Castellón')."""
        containers = []
        excluded = {title.casefold() for title in self.options.exclude_sections}

        # Section headers of the two index templates the sites serve.
        for header in soup.select("h3.grp__header__title, h2.ft-mol-headband__title"):
            title = self._get_section_title(header)
            if title.casefold() not in excluded:
                continue

            container = self._get_section_container(header)
            if container is None:
                LOGGER.warning(
                    f"Could not find container for excluded section: {title}"
                )
                continue

            containers.append(container)

        return containers

    def _get_section_title(self, header: bs4.Tag) -> str:
        """Extract the visible title text from a section header."""
        link = header.find("a")
        return link.get_text(strip=True) if link else header.get_text(strip=True)

    def _get_section_container(self, header: bs4.Tag) -> bs4.Tag | None:
        """Climb from a section header to the first ancestor holding articles."""
        return next((p for p in header.parents if p.find("article")), None)

    def _is_in_excluded_section(self, article: bs4.Tag, excluded_ids: set[int]) -> bool:
        """Check whether an article lives inside any excluded section container."""
        return any(id(parent) in excluded_ids for parent in article.parents)


def _extract_href(article: bs4.Tag, page_url: str) -> str | None:
    """The absolute URL of the article link carrying the card's headline.

    None for blocks that are not article cards (menus, footer link lists).
    """
    headlines = {h.get_text(strip=True) for h in article.find_all(["h1", "h2"])}
    headlines.discard("")
    for a_tag in article.find_all("a", href=True):
        href = cast(str, a_tag["href"])
        texts = {a_tag.get_text(strip=True), cast(str, a_tag.get("title", "")).strip()}
        if ARTICLE_HREF.search(href) and headlines & texts:
            return urljoin(page_url, href)
    return None


def _get_modified_at(article: bs4.Tag) -> datetime | None:
    meta = article.find("meta", {"itemprop": "dateModified"})
    if meta is None or not meta.get("content"):
        return None
    return datetime.fromisoformat(cast(str, meta.get("content")))


def __newstool_plugin__() -> PluginTypes:
    return [("prensaiberica", ProviderType, PrensaIbericaProvider)]
