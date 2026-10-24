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
                     deliver
                     Sink ◄── items, artifacts, the ledger
                        └─► outside world + deliveries (the ledger)
```

## Modules

| Module | Responsibility |
| :--- | :--- |
| `app.py` | `Application`, the single entry point: loads the configured plugins, wires config, HTTP cache and database, runs the phases one unit at a time (`import_source`, `run_processor`, `run_remixer`, `run_sink`; `sources`, `processors`, `remixers` and `sinks` list them in configuration order), answers queries and deletes. The database is private to it. `write_lock`, the exclusive lock every writing command takes. |
| `cli.py` | Click commands only: the phases (`import`, `import-url`, `enrich`, `remix`, `deliver`, and `run` for all four), read-only `inspect items\|annotations\|artifacts\|content\|deliveries`, `delete items\|annotations\|artifacts` and `deliveries resolve`; builds an `Application` per invocation, locked for the commands that write, and runs each unit through it with its own progress row. `inspect` and `delete` share their selection options, so `inspect` is `delete`'s dry run. Results go to stdout and progress and logs to stderr, each rich only when it is a terminal (`RICH_STDOUT_*`/`RICH_STDERR_*` from `foundation.clilib`); summaries print after the progress ends. Global logging options and the log handler come from `foundation.clilib` and `foundation.loglib`. |
| `config.py` | Pydantic models for `config.yaml` (log level, sources, plugins, cache, database), `${VAR}` expansion from the environment and a `.env` next to the config file, and the formatting of plugin option errors. |
| `models.py` | Domain models: `SourceData` (a configured source), `SourceItemData` (provider output, validated), the DTOs `SourceItem`, `Annotation`, `Artifact` and `Delivery` (each with its database `id`), and `ProcessingScope`. |
| `httpclient.py` | `requests` session with browser headers and a `foundation` cache, which `get(url, use_cache=False)` skips. |
| `db.py` | SQLAlchemy models and `Database`, the only code that touches SQLite or the content storage. |
| `providers.py` | The `Provider` and `URLProvider` protocols and `IndexSiteProvider`, an optional base class. |
| `processors.py` | The `Processor` protocol, `BaseProcessor`, `UnavailableProcessor`, `SkipItem`, `PartialFailure` and `RunSummary`. |
| `remixers.py` | The `Remixer` protocol, `BaseRemixer` and `UnavailableRemixer`. |
| `sinks.py` | The `Sink` protocol, `BaseItemSink`, `BaseArtifactSink`, `UnavailableSink` and `SelectionRequiredError`. |
| `llms.py` | The `LLM` protocol, `LLMUnavailableError` and `strip_code_fence`, for answers wrapped in a code fence. |
| `plugins/` | The plugin bundles: one module per site provider (`telegram_channel` included), `markdownify`, the `ollama` LLM, `summarize`, `tagger`, `embed`, `digest`, `grouping` (`singlelink`, `avglink`, `embeddings`), `rssfeed` and `telegram` (the `telegram` and `telegram_artifacts` sinks). `PluginOptions`, `PluginObjects` and `Services` live in its `__init__`. |
| `scripts/` | Standalone tools: the URL pipeline, built on `Application`, and the one-shot migrations `migrate_autoincrement.py` and `migrate_telegram_state.py`. |

## Plugins

Plugins are loaded with `foundation.plugin.Register` (decision 0003). The
core knows only the protocols in `providers.py`, `processors.py`,
`remixers.py`, `sinks.py` and `llms.py`, never a plugin's code or option
models:

1. `Application.__init__` calls `register(name, services, **section)` for
   every entry of `plugins:`, in order, on the `newsmerger.plugins`
   namespace. A plugin without a section is never imported. An empty
   section is `{}`.
2. The module's `__newsmerger_plugin__(services, **options)` validates the options
   with its own pydantic model (a `PluginOptions` subclass, so unknown keys
   are errors), builds its objects with the validated model and returns
   `[(name, Protocol, object), ...]`: one triple per object, declared under
   `Provider`, `URLProvider`, `Processor`, `Remixer`, `Sink` or `LLM`.
3. `Application` indexes the objects by name per protocol, with
   `get_by_protocol` (hierarchy-aware: a `URLProvider` is also a
   `Provider`), and checks that names are unique per protocol and that every
   source's `provider` is loaded.

Everything fails at construction, before the database is opened, so a broken
plugin fails every command. A `pydantic.ValidationError` from an entry point
(wrapped by foundation in `EntryPointError`) becomes a `ConfigError` with one
`plugins.<plugin>.<path>: <message>` line per error; other plugin failures
are `PluginError`s. Both are user errors in the CLI. `name` and `self`
cannot be options, because they are `register()`'s own parameters.

The objects are built once and receive what each task needs as method
arguments: providers get the source and the `HTTPClient`, processors,
remixers and sinks the `Database` and the scope. Each protocol has its own
method (`retrieve_items`, `enrich`, `remix`, `deliver`) and none declares
`name` (decision 0003 explains why). Processors, remixers and sinks own
their name, a class attribute that keys their annotations, state,
artifacts or deliveries; entry points register each one under
`obj.name`. Providers' names exist only in their
triples.

`services` is what the core shares with entry points (decision 0006): the
LLMs of the plugins registered so far, by name, in configuration order.
`services.llm(name)` returns the named one, or the first for `None`, and
raises `LLMUnavailableError` if it is not loaded. An LLM consumer catches it
and returns an `UnavailableProcessor` (or `UnavailableRemixer`) under its
name, whose `enrich` (or `remix`) logs the reason as an error and does
nothing.

Bundles (`grouping`, `telegram`) give each object a subsection of their
options.
With none, the entry point enables every object with its defaults; with
some, only those, in their order. This is the plugins' convention, not the
core's: an entry point is free to decide what its options enable.

Bundles never import each other. `grouping.embeddings` reads the vectors
`embed` stores as annotations, the same way every grouping remixer
reads `tagger.tags`.

## Providers

`Provider.retrieve_items(source, fetcher)` yields `SourceItemData`. Most
sites are `IndexSiteProvider`s, which are `URLProvider`s: fetch
`index_url(source)` (the source's URL unless the provider overrides it),
`parse_index` it into article URLs, fetch each article and `parse_item` it.
`import-url` uses `retrieve_item(url, fetcher)` to skip the index, and needs
a `URLProvider`.

HTML providers keep the article's cleaned HTML rather than converting it:
`foundation.scrapelib.prune_to_spine` keeps the main node and its ancestors,
and `drop_selectors` removes known cruft (ads, related links). Converting
to other formats is a processor's job.

Every item carries `content: bytes` and a `mimetype` without parameters.
`SourceItemData` rejects `text/*` content that isn't UTF-8, so text is
always UTF-8 and no charset is stored.

### Writing a plugin

A plugin is a module in `newsmerger/plugins/` that exposes
`__newsmerger_plugin__(**options) -> PluginObjects`; the module name is its
key under `plugins:`. A provider for a site with an index page (a section,
an RSS feed) that links to one article per item:

```python
import hashlib
from collections.abc import Iterator
from typing import Any

import bs4
from foundation.scrapelib import drop_selectors, prune_to_spine

from ..httpclient import HTTPClient
from ..models import SourceData, SourceItemData
from ..providers import URI, IndexSiteProvider, URLProvider
from . import PluginObjects, PluginOptions


class ExampleProvider(IndexSiteProvider):
    def index_url(self, source: SourceData) -> str:
        # Optional: defaults to the source's url.
        return str(source.url).rstrip("/") + "/feed/"

    def parse_index(
        self, content: bytes, source: SourceData, fetcher: HTTPClient
    ) -> Iterator[URI]:
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


def __newsmerger_plugin__(**options: Any) -> PluginObjects:
    PluginOptions.model_validate(options)  # no options: reject any
    return [("example", URLProvider, ExampleProvider())]
```

`retrieve_items` fetches the index and each article; a `ValueError` from
`parse_item` is logged and that article is skipped, so raise it for pages
that aren't articles. For anything else (several items in one page, binary
files), implement `retrieve_items(source, fetcher)` yourself, fetching with
`fetcher.get(url)`, and declare the object as a `Provider`;
`csjuntasgobierno` is an example.

A plugin with options declares a `PluginOptions` subclass with defaults for
the general case, so an empty section is enough to enable it, and passes the
validated model to its objects' constructors; `markdownify`, `rssfeed` and
`telegram` are examples, `grouping` shows a bundle with subsections and
`summarize` an LLM consumer. Use `pydantic.SecretStr` for secrets, so they never show in a
`repr` or a traceback. Processors and remixers usually subclass
`BaseProcessor` (`process_item(db, item)`) and `BaseRemixer`
(`produce(db, scope)`), set `name` as a class attribute and are returned as
`(obj.name, Processor, obj)`.

Rules every provider follows:

- `uid` is deterministic and stable across runs (decision 0001). The
  sha256 of the canonical article URL is the usual choice.
- Keep the site's cleaned HTML; never convert it (that is `markdownify`'s
  job). Text content must be UTF-8 and `mimetype` must have no parameters.
- Only report dates the site gives you; missing ones take the import time.
- `parse_item` works on bytes only, so it can be tested offline: save
  sample pages in `tests/samples/` and add a case to
  `tests/test_providers.py`.

While developing, set `NEWSMERGER_PICKLE_CACHE=1` to cache each source's
fetched items in a local `<source id>.pkl` file and skip re-scraping. Add the
plugin to the README's tables.

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
- `deliveries`: the ledger, one row per `(sink, subject)`, the subject an
  item or an artifact (two nullable foreign keys, a `CHECK` that exactly
  one is set), with status, attempts, last error, the subject's
  `content_sha256` when delivered and an `external_ref` (JSON).

Every table with an integer id uses `AUTOINCREMENT`, so a deleted id is
never reused: the CLI selects items and annotations by id (decision 0008).
The DTOs carry it; `upsert_source_items` sets it on the items it saves.

SQLAlchemy models never leave `db.py`: `Database` takes and returns DTOs.
Every SQLite connection gets `SQLITE_PRAGMAS` from a SQLAlchemy `connect`
listener: foreign keys on, WAL, `busy_timeout`, `synchronous=NORMAL`,
in-memory temp store. newsmerger does not use `foundation.dblib`, which is a
shortcut for code that uses `sqlite3` directly. Item and artifact foreign
keys are `ON DELETE CASCADE`, so `delete_items` and `delete_artifacts`
only delete the subjects, then release their contents.
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
- Two writers running at the same time could delete a content the other
  one has just started to reference. `write_lock` prevents it: every
  command that writes takes an exclusive `flock` on `<database>.lock` and
  fails at once if another process holds it (POSIX only).

### Change detection

`upsert_source_items` applies the compared fields with `DBSourceItem.update`,
then asks `session.is_modified()` whether anything changed; only then does it
touch `modified_at` (spec §4.1).

## Processors

The eligibility and retry rules are in spec §4.2; this is where they live:

- `BaseProcessor.process_item(db, item)` returns annotations for one item.
  `Database.get_unprocessed_items` selects the eligible items (backoff in
  `backoff_seconds`, `max_retries` from the plugin's options, version in
  `version`). Raising `SkipItem` marks the item `ignored`;
  `PartialFailure` saves partial results and marks it `error`; any other
  exception marks it `error`. `enrich()` returns a `RunSummary` (done,
  ignored, failed).
- `Database.record_result` saves a run's annotations and state in one
  transaction, recording the item's `content_sha256`.
- `BaseProcessor.requires` names the upstream processor;
  `require_annotation()` reads its value.
- Dependencies: `summarize` and `tagger` read `markdownify.markdown`;
  `embed` requires `tagger` and reads `tagger.tags` and, through `tagger`'s
  own dependency, `markdownify.markdown`.
- `Database.delete_annotations` removes annotations by processor, item id
  or both, together with their processing state, so the items become
  pending. `delete annotations` calls it per (item, processor).

## Remixers

`BaseRemixer.produce(db, scope)` yields `(name, content, content_type)` for
the whole scope, regenerated on each run and stored as an `Artifact`, unique
per `(remixer, name)`. Remixers read items, bulk annotations
(`Database.get_annotation_values`, one query for many items) and other
remixers' artifacts. The three `grouping` remixers share `GroupingRemixer`
and differ only in their clustering step: single-link and average-link over
tag overlap, and single-link over tag overlap blended with the cosine
similarity of the `embed` vectors (`embeddings`, which reads
`embed.tags_embedding` or `embed.markdown_embedding` and leaves out items
without one).

`digest` writes one markdown artifact per source in scope, named
`<source id>/<since>_<until>` (YYYY-MM-DD), so each period is delivered
once. It reads `markdownify.markdown` of the newest `max_items` items
per source published since `since` (default: the last `days`), cuts each to
`max_article_chars`, sends them oldest first in one prompt with a
`context_length` window and prepends a `# <source name>: <since> – <until>`
title to the model's answer.

Remixers have no external side effects; that is the sinks' job.

## Sinks

Decision 0007. `BaseSink.deliver(db, scope, artifacts, requeue, force)`
runs one cycle over the ledger:

1. queue the candidates: `queue_item_deliveries` or
   `queue_artifact_deliveries` insert `queued` rows for the subjects in
   scope without one (by default, those of the last `lookback` hours; item
   sinks only take items their `requires` processor finished);
2. read the sink's `queued`, `error` and `sending` rows with their subjects
   (`get_item_deliveries`, `get_artifact_deliveries`), in FIFO order; warn
   about `sending` ones, and pass `queued` ones and `error` ones with
   attempts left to `select(db, pending, now)`, which picks what goes now;
3. for each selected row: save it `sending`, call `send(db, subject)`, then
   save it `done` with the returned `external_ref` and the subject's
   `content_sha256`, or `error` with one more attempt. Errors are logged
   with their traceback, so `send` raises without chaining secrets.

Every state change is a `Database.save_delivery(delivery)` in its own
transaction; eligibility and backoff (`backoff_seconds`, as processors) live
in the sinks. `BaseItemSink.select` keeps strict FIFO per source: a row
that is not due holds back the rest of its source. `--requeue` turns the
`error` rows in scope back into `queued`; `force` needs an explicit
selection (`SelectionRequiredError`), gives the selected subjects a row and
sends them whatever their state. `Application.resolve_deliveries` settles
`sending` rows as `done` or `queued`.

`telegram` bundles two sinks sharing a `TelegramClient` (bot token and
chat). `TelegramSink` reads `summarize.summary` and its `select` takes the
head of each source's queue once that source's last `done` delivery
(`last_delivery_by_source`) is `interval` old. `TelegramArtifactSink`
sends the artifacts of its `artifacts` remixers with `sendDocument`.
Request errors are re-raised `from None` with their class only, since the
URL embeds the bot token.

## Pipelines

Pipelines stay outside the core (decision 0003). `scripts/pipeline_url.py`
takes the write lock, imports one URL into a configured source and runs a
linear list of processors on it, stopping at the first one without output. There is no
dependency graph and no idempotency guarantee for external side effects.
