"""Writes a markdown digest of the highlights of each source in scope with an
LLM. Every remix run sends a week of articles to the model."""

import dataclasses
import logging
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

from ..config import Duration
from ..db import Database
from ..llms import strip_code_fence
from ..models import ProcessingScope, SourceData, SourceItem
from ..remixers import BaseRemixer, RemixerType
from . import PluginTypes, Services, UsesLLMOptions

LOGGER = logging.getLogger(__name__)

DIGEST_PROMPT = """You are the editor of a weekly news digest. Below are the articles
a news source published in the period, numbered, each with its title, date, link
and text. Write the digest in Markdown, in the same language as the articles:

- Open with one paragraph that sums up the period.
- Then pick the 5 to 10 most relevant stories, merging the articles about the
  same story into one entry.
- Give each story a `##` heading and a paragraph of 2 to 4 sentences, followed
  by the links of its articles as Markdown links.
- Return only the digest: no title, preface or closing remarks.

Articles:

"""


class DigestOptions(UsesLLMOptions):
    model: str | None = None
    lookback: Duration = 7 * 86400  # scope when it sets no `since`
    max_items: int = 50  # newest items per source
    max_article_chars: int = 3000  # each article's markdown is cut to this
    context_length: int = 32768  # the model's context window, in tokens


class DigestRemixer(BaseRemixer):
    """Writes a markdown digest of each source in scope from the markdown of
    its newest items of the last `lookback`; one artifact per source, named
    `<source id>/<since>_<until>` (YYYY-MM-DD), so each period is a new
    artifact and rebuilding one overwrites it. Items without
    `markdownify.markdown` are left out."""

    name = "digest"
    options_model = DigestOptions
    options: DigestOptions

    def __init__(self, options: DigestOptions, services: Services) -> None:
        super().__init__(options, services)
        self.llm = services.llm(options.llm)

    def produce(
        self, db: Database, scope: ProcessingScope
    ) -> Iterator[tuple[str, str, str]]:
        options = self.options
        now = datetime.now(UTC)
        since = scope.since or now - timedelta(seconds=options.lookback)
        until = scope.until or now
        items = db.get_items(dataclasses.replace(scope, since=since), newest_first=True)
        markdowns = db.get_annotation_values(items, key="markdown")

        items_by_source: dict[str, list[SourceItem]] = {}
        for item in items:
            if item.key in markdowns:
                items_by_source.setdefault(item.source.id, []).append(item)
        if not items_by_source:
            LOGGER.info(f"{self.name}: no items with markdown in scope")

        for source_id, source_items in items_by_source.items():
            articles = [
                (item, markdowns[item.key])
                for item in reversed(source_items[: options.max_items])
            ]
            digest = self._write(source_items[0].source, articles, since, until)
            name = f"{source_id}/{since:%Y-%m-%d}_{until:%Y-%m-%d}"
            yield name, digest, "text/markdown"

    def _write(
        self,
        source: SourceData,
        articles: list[tuple[SourceItem, str]],
        since: datetime,
        until: datetime,
    ) -> str:
        options = self.options
        prompt = DIGEST_PROMPT + "\n\n".join(
            self._article_text(number, item, markdown, options.max_article_chars)
            for number, (item, markdown) in enumerate(articles, start=1)
        )
        response = self.llm.prompt(
            prompt, model=options.model, context_length=options.context_length
        )
        body = strip_code_fence(response)
        if not body:
            raise ValueError(f"LLM returned an empty digest for '{source.id}'")

        return f"# {source.name}: {since:%Y-%m-%d} – {until:%Y-%m-%d}\n\n{body}\n"

    def _article_text(
        self, number: int, item: SourceItem, markdown: str, max_chars: int
    ) -> str:
        published = f"{item.published_at:%Y-%m-%d}" if item.published_at else "-"
        return (
            f"### {number}. {item.title}\n"
            f"Date: {published}\n"
            f"Link: {item.uri}\n\n"
            f"{markdown[:max_chars].strip()}"
        )


def __newstool_plugin__() -> PluginTypes:
    return [(DigestRemixer.name, RemixerType, DigestRemixer)]
