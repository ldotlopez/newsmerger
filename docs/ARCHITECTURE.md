# Architecture

```
config.yaml ─► Config ─► App (app.py) ◄── cli.py, scripts/
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
                     process / pipeline-url            ▼
                     Processor ◄── Database.get_unprocessed_items / get_content
                        ├─ ItemProcessor ─────► annotations + processing state
                        └─ ArtifactProcessor ─► artifacts
```

## Modules

| Module | Responsibility |
| :--- | :--- |
| `app.py` | `App`, the application core: wires config, HTTP cache, database, providers and processors, and runs imports, processors and pipelines. Front ends use it instead of building their own wiring; reads go through `App.db`. |
| `cli.py` | Click commands only; builds an `App` per invocation. |
| `config.py` | Pydantic models for `config.yaml`: sources, database, cache, processors, pipelines. |
| `models.py` | Domain models: `SourceData` (a configured source), `SourceItemData` (provider output, validated) and `SourceItem` (the item DTO used everywhere else). |
| `httpclient.py` | `requests` session with browser headers and a `foundation` cache. |
| `db.py` | SQLAlchemy models and `Database`, the only code that touches SQLite or the content storage. |
| `providers/` | One module per site, each exposing `Provider`. |
| `processors/` | One module per processor, each exposing `Processor`. |
| `scripts/` | Standalone tools built on `App`: grouping experiments. |

## Providers

`BaseProvider.retrieve_items()` yields `SourceItemData`. Most sites are
`IndexSiteProvider`s: fetch the index page, `parse_index` it into article
URLs, fetch each article and `parse_item` it. `import-url` uses
`retrieve_item` to skip the index.

HTML providers keep the article's cleaned HTML rather than converting it:
`foundation.scrapelib.prune_to_spine` keeps the main node and its ancestors,
and `drop_selectors` removes known cruft (ads, related links). Converting
to other formats is a processor's job.

Every item carries `content: bytes` and a `mimetype` without parameters.
`SourceItemData` rejects `text/*` content that isn't UTF-8, so text is
always UTF-8 and no charset is stored.

## Persistence

SQLite tables:

- `sources`: one row per configured source, keyed by a uid derived from
  `(provider, url)`.
- `source_items`: metadata of each item (`uid`, `uri`, `title`, `mimetype`,
  `content_sha256`, `data`, `published_at`, `modified_at`). `uid` and `uri`
  are unique.
- `processing_state`: per item and processor, the status (`done`, `error`,
  `ignored`), attempts, processor version and the `content_sha256` the run
  used.
- `item_annotations`: per item and processor, key/value results (e.g.
  `markdownify.text`, `summarize.summary`).
- `artifacts`: whole-dataset outputs, unique per `(processor, name)`.

SQLAlchemy models never leave `db.py`: `Database` takes and returns DTOs.
Every SQLite connection gets the settings `foundation.dblib.SQLite3DB` uses
(`SQLITE_PRAGMAS`): foreign keys on, WAL, `busy_timeout`, `synchronous=NORMAL`,
in-memory temp store. Item foreign keys are `ON DELETE CASCADE`.
`Base.metadata.create_all` creates missing tables only; it never alters an
existing schema.

### Content storage

Item contents are stored outside SQLite, in a `foundation.storage.DiskStorage`
at `db.content_dir`, keyed by the sha256 of the bytes. The database is the
only record of which item uses which content.

- `SourceItem` computes `content_sha256` once, when it is built with content.
  Items read from the database have `content=None`; processors load it with
  `Database.get_content(item)`.
- On upsert, content is written **before** the row that references it, and
  only when the hash is new or changed. A crash leaves an unused file, never
  a row pointing at nothing.
- After the commit, the replaced hashes that no row references any more are
  deleted. Identical contents are stored once and shared.
- Known limit: two imports running at the same time can delete a content
  the other one has just started to reference. Imports are expected to run
  one at a time.

### Change detection

`upsert_source_items` assigns `title`, `uri`, `mimetype`, `content_sha256`
and `data`, then asks `session.is_modified()` whether anything changed. Only
then does it touch `modified_at` (never moved backwards) and fill
`published_at` (set once, never overwritten). Re-importing identical items is
a no-op.

## Processors

- `ItemProcessor.process_item(item)` returns annotations for one item.
  `Database.get_unprocessed_items` selects items that were never processed,
  whose content changed since the last run, that failed with retries left and
  backoff elapsed, or that were done by an older processor version. Raising
  `SkipItem` marks the item `ignored`; `PartialFailure` saves partial results
  and marks it `error`; any other exception marks it `error`.
- `Database.record_result` saves a run's annotations and state in one
  transaction, recording the item's `content_sha256`. A content change resets
  the retry count.
- `ItemProcessor.REQUIRES` names the processor whose output it reads. Only
  items that processor finished on their current content are picked up (even
  with `--force`), so an upstream skip is never a downstream error.
  `require_annotation()` reads the upstream value.
- Dependencies: `summarize` and `tagger` read `markdownify.markdown`;
  `telegram` reads `summarize.summary` and stores the posted `message_id`,
  which also keeps it from ever posting an item twice.
- `ArtifactProcessor.produce(scope)` yields `(name, content, content_type)`
  for the whole scope, regenerated on each run and stored as an `Artifact`
  DTO, unique per `(processor, name)`. Artifacts feed RSS feeds and
  newsletters built by external scripts, which read them with
  `Database.get_artifact`.
- Bulk reads such as `Database.get_annotation_values` (one annotation for many
  items, one query) back whole-dataset processors like the groupings.

## Pipelines

A pipeline is an ordered, linear list of processor steps run on one item
(`pipeline-url`). Each step's params override the processor's configured
defaults. There is no dependency graph and no idempotency guarantee for
external side effects such as Telegram messages.
