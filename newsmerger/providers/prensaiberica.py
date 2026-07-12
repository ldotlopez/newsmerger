import hashlib
import logging
from datetime import datetime
from typing import Iterator, cast

import bs4
from readability import Document

from ..models import SourceEntryData
from . import URI, BaseProvider

logger = logging.getLogger(__name__)


class Provider(BaseProvider):
    EXCLUDED_SECTION_TITLES = {"Comarcas", "Vídeos y galerías de Castellón"}

    def parse_index(self, buffer: bytes) -> Iterator[URI]:
        soup = bs4.BeautifulSoup(buffer, "html5lib")

        excluded_containers = self._find_excluded_containers(soup)
        excluded_ids = {id(c) for c in excluded_containers}
        headlines = soup.find_all(["h1", "h2"], {"itemprop": "headline"})

        for headline in headlines:
            article = self._get_article_for_headline(headline)
            if article is None:
                continue
            if self._is_in_excluded_section(article, excluded_ids):
                continue

            yield self._extract_href(article)

    def _get_meta_property(self, soup: bs4.BeautifulSoup, property: str) -> str:
        if (head_tag := soup.find("head")) is None:
            raise ValueError()

        # if (meta_tag := head_tag.find("meta", property=property)) is None:
        if (meta_tag := head_tag.find("meta", attrs={"property": property})) is None:
            raise ValueError()

        try:
            content = meta_tag.attrs["content"]
        except KeyError as e:
            raise ValueError() from e

        return content.strip()

    def _get_meta_name(self, soup: bs4.BeautifulSoup, name: str) -> str:
        if (head_tag := soup.find("head")) is None:
            raise ValueError()

        if (meta_tag := head_tag.find("meta", attrs={"name": name})) is None:
            raise ValueError()

        try:
            content = meta_tag.attrs["content"]
        except KeyError as e:
            raise ValueError() from e

        return content.strip()

    def parse_item(self, buffer: bytes) -> SourceEntryData:
        html = buffer.decode("utf-8")

        soup = bs4.BeautifulSoup(html, features="html5lib")

        title = self._get_meta_property(soup, "og:title")
        image = self._get_meta_property(soup, "og:image")
        author = self._get_meta_name(soup, "author")
        url = self._get_meta_property(soup, "og:url")

        tags = self._get_meta_property(soup, "article:tag").split(",")
        section = self._get_meta_property(soup, "article:section")
        pub_time = datetime.fromisoformat(
            self._get_meta_property(soup, "article:published_time")
        )
        mod_time = datetime.fromisoformat(
            self._get_meta_property(soup, "article:modified_time")
        )

        doc = Document(html)
        content = doc.summary()

        return SourceEntryData(
            id=hashlib.sha256(url.encode("utf-8")).hexdigest(),
            title=title,
            uri=url,
            content=content,
            data={
                "author": author,
                "image": image,
                "section": section,
                "tags": tags,
                "pub_date": pub_time,
                "mod_date": mod_time,
            },
        )

    # def parse_listing(self, buffer: bytes) -> list[SourceEntryData]:
    #     soup = bs4.BeautifulSoup(buffer, "html5lib")

    #     excluded_containers = self._find_excluded_containers(soup)
    #     excluded_ids = {id(c) for c in excluded_containers}
    #     headlines = soup.find_all(["h1", "h2"], {"itemprop": "headline"})

    #     results = []
    #     for headline in headlines:
    #         article = self._get_article_for_headline(headline)
    #         if article is None:
    #             continue
    #         if self._is_in_excluded_section(article, excluded_ids):
    #             continue

    #         entry_data = self._build_entry_data(article, headline)
    #         if entry_data is None:
    #             continue
    #         import ipdb; ipdb.set_trace(); pass

    #         results.append(entry_data)

    #     return results

    # def _is_valid_article(self, node: bs4.Tag) -> bool:
    #     return True

    # # --- Section exclusion helpers -------------------------------------

    def _find_excluded_containers(self, soup: bs4.BeautifulSoup) -> list[bs4.Tag]:
        """Find the container divs for sections we want to exclude entirely,
        identified by their header title (e.g. 'Comarcas', 'Vídeos y galerías de Castellón')."""
        containers = []

        for h3 in soup.find_all("h3", class_="grp__header__title"):
            title = self._get_section_title(h3)
            if title not in self.EXCLUDED_SECTION_TITLES:
                continue

            container = self._get_section_container(h3)
            if container is None:
                logger.warning(
                    f"Could not find container for excluded section: {title}"
                )
                continue

            containers.append(container)

        return containers

    def _get_section_title(self, h3: bs4.Tag) -> str:
        """Extract the visible title text from a section header h3."""
        link = h3.find("a")
        return link.get_text(strip=True) if link else h3.get_text(strip=True)

    def _get_section_container(self, h3: bs4.Tag) -> bs4.Tag | None:
        """Climb from a header's h3 title up to the section's containing div."""
        header = h3.find_parent("header")
        return header.parent if header else None

    def _is_in_excluded_section(self, article: bs4.Tag, excluded_ids: set[int]) -> bool:
        """Check whether an article lives inside any excluded section container."""
        return any(id(parent) in excluded_ids for parent in article.parents)

    # # --- Article -> entry helpers ---------------------------------------

    def _get_article_for_headline(self, headline: bs4.Tag) -> bs4.Tag | None:
        """Climb parents to find the article tag wrapping a headline."""
        article = headline.find_parent("article")
        if article is None:
            logger.warning(f"No article parent found for headline: {headline.text}")

        return article

    # def _build_entry_data(self, article: bs4.Tag, headline: bs4.Tag) -> SourceEntryData | None:
    #     """Assemble a SourceEntryData from an article node, pulling in every
    #     piece of metadata available on the page (title, author, publish date, image)."""

    #     title = self._extract_title(headline)
    #     url = self._extract_href(article)
    #     entry_id = self._build_id(url)

    #     publish_date = self._extract_publish_date(article)
    #     return SourceEntryData(
    #         id=entry_id,
    #         title=title,
    #         uri=url,
    #         data={
    #             "title": title,
    #             "author": self._extract_author(article),
    #             "publish_date": publish_date.isoformat() if publish_date else None,
    #             "image": self._extract_image(article),
    #         },
    #     )

    def _build_id(self, url: str) -> str:
        """The site tags each article with a data-content-id attribute."""
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    def _extract_title(self, headline: bs4.Tag) -> str:
        return headline.get_text(strip=True)

    def _extract_href(self, article: bs4.Tag) -> str:
        a_tag = article.find(
            "a",
            class_="new__headline",
            href=lambda x: (
                x and x.startswith("https://www.elperiodicomediterraneo.com/")
            ),
        )
        if a_tag is None:
            raise ValueError(article)

        return cast(str, a_tag.get("href"))

    def _extract_author(self, article: bs4.Tag) -> str | None:
        """Author is either a <a class="new__author"> or, for wire-service pieces,
        a <span class="new__author"> (e.g. 'MEDITERRÁNEO')."""
        author_tag = article.find(class_="new__author")
        if author_tag is None:
            return None
        return author_tag.get_text(strip=True)

    # def _extract_publish_date(self, article: bs4.Tag) -> datetime.datetime | None:
    #     """Publish date lives in <meta itemprop="datePublished" content="...">
    #     as an ISO-8601 string with timezone offset."""
    #     meta_tag = article.find("meta", {"itemprop": "datePublished"})
    #     if meta_tag is None or not meta_tag.get("content"):
    #         return None

    #     raw_date = meta_tag["content"]
    #     try:
    #         return datetime.datetime.fromisoformat(raw_date)
    #     except ValueError:
    #         logger.warning(f"Could not parse publish date: {raw_date}")
    #         return None

    # def _extract_image(self, article: bs4.Tag) -> str | None:
    #     """Prefer the <picture><meta itemprop="url"> (the canonical, largest
    #     rendition); fall back to the <img src> if that's missing."""
    #     picture = article.find("picture", {"itemprop": "image"})
    #     if picture is not None:
    #         url_meta = picture.find("meta", {"itemprop": "url"})
    #         if url_meta is not None and url_meta.get("content"):
    #             return url_meta["content"]

    #         img_tag = picture.find("img")
    #         if img_tag is not None and img_tag.get("src"):
    #             return img_tag["src"]

    #     return None
    #


def _extract_image(container: bs4.Tag) -> str | None:
    """Prefer the <picture><meta itemprop="url"> (the canonical, largest
    rendition); fall back to the <img src> if that's missing."""
    picture = container.find("picture", {"itemprop": "image"})
    if picture is not None:
        url_meta = picture.find("meta", {"itemprop": "url"})
        if url_meta is not None and url_meta.get("content"):
            return url_meta["content"]

        img_tag = picture.find("img")
        if img_tag is not None and img_tag.get("src"):
            return img_tag["src"]

    return None
