# Architecture

How the current code implements [SPECIFICATION.md](SPECIFICATION.md). The
behavior rules (identity, change detection, retries, dependencies) are
defined there and not repeated here.

```
config.yaml ─► Config ─► Application (app.py) ◄── cli.py, scripts/, external tools
                          │
        HTTPClient ◄──────┤ import / import-url
        (cached)          ▼
                     Provider ──► SourceItemData ──► SourceItem
                                                       │
                                                       ▼
                                          Database.upsert_source_items
                                           ├─ content ─► DiskStorage (content_dir)
                                           └─ row ─────► SQLite (source_items)
                                                       │
                     enrich                            ▼
                     Processor ◄── Database.get_unprocessed_items / get_content
                        └─► annotations + processing state
                     remix
                     Remixer ◄── items, annotations, other artifacts
                        └─► artifacts
```

## Modules

| Module | Responsibility |
| :--- | :--- |
| `app.py` | `Application`, the single entry point: wires config, HTTP cache, database and plugins, runs the three phases and answers queries. The database is private to it. |
| `cli.py` | Click commands only: the phases (`import`, `import-url`, `enrich`, `remix`) and read-only inspection (`items`, `annotations`, `artifacts`, `artifact`); builds an `Application` per invocation. Global logging and output options come from `foundation.clilib` and `foundation.loglib`. |
| `config.py` | Pydantic models for `config.yaml` (sources, processors, remixers, cache, database) and `${VAR}` expansion from the environment and a `.env` next to the config file. |
| `models.py` | Domain models: `SourceData` (a configured source), `SourceItemData` (provider output, validated), `SourceItem` (the item DTO), `Artifact` and `ProcessingScope`. |
| `httpclient.py` | `requests` session with browser headers and a `foundation` cache. |
| `llm.py` | The Ollama client shared by the LLM processors. |
| `db.py` | SQLAlchemy models and `Database`, the only code that touches SQLite or the content storage. |
| `providers/` | One module per site, each exposing `Provider`. |
| `processors/` | One module per processor, each exposing `Processor`. |
| `remixers/` | One module per remixer, each exposing `Remixer`. |
| `scripts/` | Standalone tools built on `Application`: the URL pipeline. |

Plugins of the three types are loaded by module name with
`foundation.plugin.ClassLoader` (decision 0003). Processors and remixers run
only when configured, with their configured `params` as constructor
arguments.

## Providers

`BaseProvider.retrieve_items()` yields `SourceItemData`. Most sites are
`IndexSiteProvider`s: fetch `index_url` (the source's URL unless the provider
overrides it), `parse_index` it into article URLs, fetch each article and
`parse_item` it. `import-url` uses `retrieve_item` to skip the index.

HTML providers keep the article's cleaned HTML rather than converting it:
`foundation.scrapelib.prune_to_spine` keeps the main node and its ancestors,
and `drop_selectors` removes known cruft (ads, related links). Converting
to other formats is a processor's job.

Every item carries `content: bytes` and a `mimetype` without parameters.
`SourceItemData` rejects `text/*` content that isn't UTF-8, so text is
always UTF-8 and no charset is stored.

### Writing a provider

A provider is a module in `newsmerger/providers/` that exposes a class named
`Provider`; the module name is what sources put in `provider:`. It is built
with the configured `SourceData` and the shared cached `HTTPClient`
(`self.source`, `self.fetcher`), and needs no registration.

For a site with an index page (a section, an RSS feed) that links to one
article per item, subclass `IndexSiteProvider`:

```python
import hashlib
from collections.abc import Iterator

import bs4
from foundation.scrapelib import drop_selectors, prune_to_spine

from ..models import SourceItemData
from . import URI, IndexSiteProvider


class Provider(IndexSiteProvider):
    @property
    def index_url(self) -> str:
        # Optional: defaults to the source's url.
        return str(self.source.url).rstrip("/") + "/feed/"

    def parse_index(self, content: bytes) -> Iterator[URI]:
        """Yield the article URLs found in the index page."""
        ...

    def parse_item(self, content: bytes) -> SourceItemData:
        """Build one item from an article page."""
        soup = bs4.BeautifulSoup(content.decode("utf-8"), features="html5lib")
        if (article := soup.select_one("article")) is None:
            raise ValueError("Article not found")
        drop_selectors(article, [".ads", ".related"])
        url = ...
        return SourceItemData(
            uid=hashlib.sha256(url.encode()).hexdigest(),
            title=...,
            uri=url,
            content=str(prune_to_spine(article)).encode("utf-8"),
            mimetype="text/html",
            published_at=...,  # optional
            modified_at=...,   # optional
            data={"author": ..., "image": ...},  # any JSON-compatible extras
        )
```

`retrieve_items` fetches the index and each article; a `ValueError` from
`parse_item` is logged and that article is skipped, so raise it for pages
that aren't articles. Only `IndexSiteProvider`s support `import-url`.

For anything else (several items in one page, binary files), subclass
`BaseProvider` and implement `retrieve_items()` yourself, fetching with
`self.fetcher.get(url)`; `csjuntasgobierno` is an example.

Rules every provider follows:

- `uid` is deterministic and stable across runs (decision 0001). The
  sha256 of the canonical article URL is the usual choice.
- Keep the site's cleaned HTML; never convert it (that is `markdownify`'s
  job). Text content must be UTF-8 and `mimetype` must have no parameters.
- Only report dates the site gives you; missing ones take the import time.
- `parse_item` works on bytes only, so it can be tested offline: save
  sample pages in `tests/samples/` and add a case to
  `tests/test_providers.py` (`fetcher=None` is enough for parsing).

While developing, set `NEWSMERGER_PICKLE_CACHE=1` to cache each source's
fetched items in a local `<source id>.pkl` file and skip re-scraping. Add the
provider to the README's providers table.

## Persistence

SQLite tables:

- `sources`: one row per configured source, keyed by its configured `id`.
- `source_items`: metadata of each item (`uid`, `uri`, `title`, `mimetype`,
  `content_sha256`, `data`, `published_at`, `modified_at`), unique per
  `(source_id, uid)`. `uri` is not unique.
- `processing_state`: per item and processor, the status (`done`, `error`,
  `ignored`), attempts, processor version and the `content_sha256` the run
  used.
- `item_annotations`: per item, processor and key, the `content_sha256` of
  the value (e.g. `markdownify.markdown`, `summarize.summary`).
- `artifacts`: remixer outputs, unique per `(remixer, name)`, with the
  `content_sha256` of their content.

SQLAlchemy models never leave `db.py`: `Database` takes and returns DTOs.
Every SQLite connection gets `SQLITE_PRAGMAS` from a SQLAlchemy `connect`
listener: foreign keys on, WAL, `busy_timeout`, `synchronous=NORMAL`,
in-memory temp store. newsmerger does not use `foundation.dblib`, which is a
shortcut for code that uses `sqlite3` directly. Item foreign keys are `ON DELETE CASCADE`.
`Base.metadata.create_all` creates missing tables only; it never alters an
existing schema.

### Content storage

Item contents, annotation values (as JSON) and artifact contents are stored
outside SQLite, in one `foundation.storage.DiskStorage` at `db.content_dir`,
keyed by the sha256 of the bytes (decision 0004). The database is the only
record of which row uses which content.

- `SourceItem` and `Artifact` compute `content_sha256` when built with
  content. Items read back have `content=None`; processors load it with
  `Database.get_content(item)`.
- Content is written **before** the row that references it, so a crash
  leaves an unused file, never a row pointing at nothing.
- After the commit, replaced hashes that no row (item, annotation or
  artifact) references any more are deleted. Identical contents are stored
  once and shared.
- Known limit: two writers running at the same time can delete a content
  the other one has just started to reference. Runs are expected to happen
  one at a time.

### Change detection

`upsert_source_items` applies the compared fields with `DBSourceItem.update`,
then asks `session.is_modified()` whether anything changed; only then does it
touch `modified_at` (spec §4.1).

## Processors

The eligibility and retry rules are in spec §4.2; this is where they live:

- `BaseProcessor.process_item(item)` returns annotations for one item.
  `Database.get_unprocessed_items` selects the eligible items (backoff in
  `_backoff_seconds`, `MAX_RETRIES` overridable by the `max_retries` param,
  version in `VERSION`). Raising `SkipItem` marks the item `ignored`;
  `PartialFailure` saves partial results and marks it `error`; any other
  exception marks it `error`. `run()` returns a `RunSummary` (done, ignored,
  failed).
- `Database.record_result` saves a run's annotations and state in one
  transaction, recording the item's `content_sha256`.
- `BaseProcessor.REQUIRES` names the upstream processor;
  `require_annotation()` reads its value.
- Dependencies: `summarize` and `tagger` read `markdownify.markdown`.
- `Database.delete_annotations` removes annotations by processor, item or
  both, together with their processing state, so the items become pending.

## Remixers

`BaseRemixer.produce(scope)` yields `(name, content, content_type)` for the
whole scope, regenerated on each run and stored as an `Artifact`, unique per
`(remixer, name)`. Remixers read items, bulk annotations
(`Database.get_annotation_values`, one query for many items) and other
remixers' artifacts. The three grouping remixers share `GroupingRemixer`
and differ only in their clustering step: single-link and average-link over
tag overlap, and single-link over tag overlap blended with tag embeddings
(`grouping_embeddings`, computed with Ollama on every run).

`telegram` is the remixer with an external side effect (decision 0005). It
reads `summarize.summary` and keeps its state in its own `state` artifact,
read back on every run: the first run's time (`watermark`), a FIFO queue of
item keys, the posted items with their `message_id`, and each source's last
post time. Without `since` or `uids` in the scope it queues only items
published since `watermark`. It posts at most one item per source per
`interval`; posting errors keep the item queued and are logged without the
request URL, which embeds the bot token.

## Pipelines

Pipelines stay outside the core (decision 0003). `scripts/pipeline_url.py`
imports one URL into a configured source and runs a linear list of
processors on it, stopping at the first one without output. There is no
dependency graph and no idempotency guarantee for external side effects.
