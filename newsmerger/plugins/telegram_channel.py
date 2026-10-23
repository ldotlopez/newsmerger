"""Imports the articles linked from a public Telegram channel, read from its
web preview (https://t.me/s/<channel>), one item per linked article."""

import dataclasses
import hashlib
import logging
from collections.abc import Iterator
from datetime import datetime
from typing import Any
from urllib.parse import urljoin, urlparse

import bs4
from foundation.scrapelib import head_meta_get_value_by_property, soupify
from pydantic import PositiveInt

from ..httpclient import HTTPClient
from ..models import SourceData, SourceItemData
from ..providers import URLProvider
from . import PluginObjects, PluginOptions, Services

LOGGER = logging.getLogger(__name__)

TELEGRAM_HOSTS = {"t.me", "telegram.me", "telegram.org"}


class Options(PluginOptions):
    pages: PositiveInt = 1  # preview pages to read, 20 posts each, newest first


@dataclasses.dataclass(slots=True)
class Post:
    id: str  # "<channel>/<message number>"
    published_at: datetime
    text: str
    links: list[str]


def preview_url(source: SourceData) -> str:
    """The web preview of the source's channel, from https://t.me/<channel> or
    https://t.me/s/<channel>."""
    channel = (source.url.path or "").rstrip("/").rsplit("/", 1)[-1]
    if not channel:
        raise ValueError(f"no channel name in '{source.url}'")
    return f"https://t.me/s/{channel}"


def parse_preview(content: bytes, page_url: str) -> tuple[list[Post], str | None]:
    """Return the posts of a preview page and the URL of the older page, if any."""
    soup = soupify(content.decode("utf-8"))
    posts = []
    for message in soup.select(".tgme_widget_message[data-post]"):
        if (time_tag := message.select_one(".tgme_widget_message_date time")) is None:
            continue
        text_tag = message.select_one(".tgme_widget_message_text")
        anchors = message.select(
            ".tgme_widget_message_text a[href], a.tgme_widget_message_link_preview"
        )
        links = [
            href
            for href in dict.fromkeys(str(a["href"]) for a in anchors)
            if urlparse(href).scheme in ("http", "https")
            and urlparse(href).hostname not in TELEGRAM_HOSTS
        ]
        posts.append(
            Post(
                id=str(message["data-post"]),
                published_at=datetime.fromisoformat(str(time_tag["datetime"])),
                text=text_tag.get_text("\n", strip=True) if text_tag else "",
                links=links,
            )
        )

    older = soup.select_one('link[rel="prev"][href]')
    return posts, urljoin(page_url, str(older["href"])) if older else None


def canonical_url(soup: bs4.BeautifulSoup) -> str:
    try:
        return head_meta_get_value_by_property(soup, "og:url")
    except ValueError:
        pass
    if (link := soup.select_one('link[rel="canonical"][href]')) is not None:
        return str(link["href"]).strip()
    raise ValueError("no canonical URL: not an article page")


def page_title(soup: bs4.BeautifulSoup) -> str:
    try:
        return head_meta_get_value_by_property(soup, "og:title")
    except ValueError:
        pass
    if soup.title is not None and (title := soup.title.get_text(strip=True)):
        return title
    raise ValueError("no title")


def parse_article(content: bytes, post: Post | None = None) -> SourceItemData:
    """Build one item from a linked page. Raises ValueError for pages that
    aren't HTML articles (binary files, error pages)."""
    # shortcut: sniffs the bytes because HTTPClient drops the content type; skips PDFs and other non-HTML links.
    if b"<html" not in content[:4096].lower():
        raise ValueError("not an HTML page")
    soup = soupify(content.decode("utf-8"))
    url = canonical_url(soup)
    return SourceItemData(
        uid=hashlib.sha256(url.encode()).hexdigest(),
        title=page_title(soup),
        uri=url,
        content=content,
        mimetype="text/html",
        published_at=post.published_at if post else None,
        data={"telegram_post": post.id, "message": post.text} if post else {},
    )


class TelegramChannelProvider:
    def __init__(self, pages: int) -> None:
        self.pages = pages

    def iter_posts(self, source: SourceData, fetcher: HTTPClient) -> Iterator[Post]:
        page_url: str | None = preview_url(source)
        for _ in range(self.pages):
            if page_url is None:
                return
            # New posts must show up on every run, not after the cache expires.
            content = fetcher.get(page_url, use_cache=False)
            posts, page_url = parse_preview(content, page_url)
            if not posts:
                raise ValueError(f"no posts in '{source.url}': not a public channel?")
            yield from posts

    def retrieve_item(self, url: str, fetcher: HTTPClient) -> SourceItemData:
        return parse_article(fetcher.get(url))

    def retrieve_items(
        self, source: SourceData, fetcher: HTTPClient
    ) -> Iterator[SourceItemData]:
        for post in self.iter_posts(source, fetcher):
            for url in post.links:
                try:
                    yield parse_article(fetcher.get(url), post)
                except ValueError as e:
                    LOGGER.error(f"error '{e}' while parsing '{url}' ({post.id})")


def __newsmerger_plugin__(services: Services, **options: Any) -> PluginObjects:
    cfg = Options.model_validate(options)
    return [("telegram_channel", URLProvider, TelegramChannelProvider(cfg.pages))]
