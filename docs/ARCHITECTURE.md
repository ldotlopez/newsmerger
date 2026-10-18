# Architecture

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
| `cli.py` | Click commands only: the phases (`import`, `import-url`, `enrich`, `remix`) and read-only inspection (`items`, `annotations`, `artifacts`, `artifact`); builds an `Application` per invocation. |
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

Each provider derives its items' `uid`, which must be deterministic and
stable within its source (decision 0001).

HTML providers keep the article's cleaned HTML rather than converting it:
`foundation.scrapelib.prune_to_spine` keeps the main node and its ancestors,
and `drop_selectors` removes known cruft (ads, related links). Converting
to other formats is a processor's job.

Every item carries `content: bytes` and a `mimetype` without parameters.
`SourceItemData` rejects `text/*` content that isn't UTF-8, so text is
always UTF-8 and no charset is stored.

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

`upsert_source_items` applies `title`, `uri`, `mimetype`, `content_sha256`
and `data` (`DBSourceItem.update`), then asks `session.is_modified()` whether
anything changed. Only then does it touch `modified_at` (never moved
backwards). `published_at` is set on creation and never overwritten. Missing
dates take the import time. Re-importing identical items is a no-op.

## Processors

- `BaseProcessor.process_item(item)` returns annotations for one item.
  `Database.get_unprocessed_items` selects items that were never processed,
  whose content changed since the last run, that failed with retries left and
  backoff elapsed, or that were done by another processor `VERSION`. Raising
  `SkipItem` marks the item `ignored`; `PartialFailure` saves partial results
  and marks it `error`; any other exception marks it `error`. `run()` returns
  a `RunSummary` (done, ignored, failed).
- `Database.record_result` saves a run's annotations and state in one
  transaction, recording the item's `content_sha256`. A content change or a
  forced run resets the retry count.
- `BaseProcessor.REQUIRES` names the processor whose output it reads. Only
  items that processor finished on their current content are picked up (even
  with `--force`), so an upstream skip is never a downstream error.
  `require_annotation()` reads the upstream value.
- Dependencies: `summarize` and `tagger` read `markdownify.markdown`;
  `telegram` reads `summarize.summary` and stores the posted `message_id`,
  which also keeps it from ever posting an item twice.
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

## Pipelines

Pipelines stay outside the core (decision 0003). `scripts/pipeline_url.py`
imports one URL into a configured source and runs a linear list of
processors on it, stopping at the first one without output. There is no
dependency graph and no idempotency guarantee for external side effects
beyond `telegram`'s own `message_id` check.
