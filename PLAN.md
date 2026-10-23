# newsmerger — Working Plan

Ordered smallest-and-most-necessary → biggest-and-least-necessary.
Update statuses as we progress: `[ ]` todo, `[x]` done, `[~]` in progress.

## Numeric ids and `inspect` (decision 0008)

- [x] **1. `AUTOINCREMENT` and `scripts/migrate_autoincrement.py`.**
  `sqlite_autoincrement=True` on every table with an integer id; a
  one-shot script recreates the existing tables with it, keeping rows and
  ids, with a test on a copy of a populated database. Run it on
  `~/.local/share/newsmerger/data.db` only after asking, once everything is
  implemented.
- [x] **2. Ids in the DTOs.** `id: int | None` on `SourceItem` and
  `Artifact`; an `Annotation` DTO (`id`, item id, `processor`, `key`,
  `updated_at`, `value`).
- [x] **3. `--item` replaces `--uid`.** `ProcessingScope` takes item ids;
  `scope_options` drops `--uid` and adds a repeatable `--item`, in
  `enrich`, `remix` and `inspect`.
- [x] **4. Shared selection queries** in `Database` and `Application`:
  `get_items(scope)` as it was, `find_annotations(scope, processor, key,
  annotation_ids)`, `list_artifacts(remixer, names=, limit=)`, plus
  `get_annotation_keys(items)`, the annotation ids and keys of many items
  in one query for the items listing.
- [x] **5. `inspect items|annotations|artifacts`** with `--format
  table|json`; remove `items`, `annotations`, `artifacts` and `artifact`.
  Tests for id parsing, JSON output and missing ids.
- [ ] **Docs, when done:** propose the `README.md` (usage) and
  `ARCHITECTURE.md` (`cli.py`, `models.py`) updates.

## Sinks and the delivery ledger (decision 0007)

- [x] **1. `deliveries` table and its `db.py` API**, with tests. DTOs, as
  in the rest of the module:
  - `queue_item_deliveries(sink, scope, requires)` (reuses the `requires`
    join of `get_unprocessed_items`) and `queue_artifact_deliveries(sink,
    remixers, since, names)`: rows for the candidates without one.
  - `get_item_deliveries(sink, scope, statuses)` and
    `get_artifact_deliveries(sink, statuses, names)`: rows with their
    subjects, in FIFO order. Eligibility, backoff and every state change
    (`sending`, `done`, `error`, requeue, resolve) live in the sinks and
    `Application`, saved with `save_delivery(delivery)`.
  - `find_deliveries(scope, sink, status, artifact_names)`, for `inspect
    deliveries`, `deliveries resolve` and `delete`.
  - `last_delivery_by_source(sink)`: time of the last `done` delivery per
    source (replaces `last_post`).
- [x] **2. `sinks.py`, `Application` and CLI.** `Sink`, `BaseItemSink`,
  `BaseArtifactSink`, `UnavailableSink`; `Application.run_sink` and
  `Application.deliver`, in configuration order; `deliver [SINK]` with
  `--requeue`, `--force` (requires `--item` or `--artifact`) and the scope
  options; `inspect deliveries` and `deliveries resolve`; `run` (all four phases, non-zero
  exit on failures); the exclusive lock file for writing commands.
- [x] **3. `telegram` item sink and `scripts/migrate_telegram_state.py`**
  (`posted` → `done` rows with `message_id`, `queue` → `queued` rows;
  `watermark` and `last_post` dropped). Run it before the first
  `deliver telegram`.
- [x] **4. Dated `digest` names** (`<source>/<since>_<until>`) **and the
  `telegram_artifacts` sink** (`sendDocument`, option `artifacts`).
- [ ] **Docs, when done:** propose the `ARCHITECTURE.md`, `README.md` and
  `SPECIFICATION.md` updates.

- [x] **5. `delete items|annotations|artifacts`** (decision 0008), with the
  `inspect` selection: non-interactive, cascading, items and artifacts with
  deliveries skipped with a warning unless `--force`, annotations per
  processor; takes the write lock.

Risks:

- If the migration fails, the chat gets the last `lookback` hours again.
- `migrate_autoincrement.py` rewrites every table of the real database:
  back it up first, with the SQLite backup API (README, *Data and backups*).
- An existing `telegram:` section with `interval` at the top level is now
  rejected: it moves to the `telegram:` subsection (`config.example.yaml`).

---

## Done

- [x] **Plugin bundles with `foundation.plugin.Register`** (decision 0003, revised):
  one `plugins` namespace and config section; entry points validate their
  own options (pydantic, with defaults) and return objects declared under
  the `Provider`/`URLProvider`/`Processor`/`Remixer` protocols. `llm`
  bundles `summarize`, `tagger` and the new `embed`; `grouping` bundles
  `singlelink`, `avglink` and `embeddings`, which now reads stored
  embeddings.
- [x] **LLM plugins** (decision 0006): the `LLM` protocol (`prompt`,
  `embed`) and the `ollama` backend; `llm` split into the `summarize`,
  `tagger` and `embed` plugins, which pick an LLM by name and get it from
  the `services` every entry point receives.
- [x] **Secrets**: no rotation needed (never committed; owner's call).
- [x] **External scripts**: none existed outside `scripts/`. The embeddings
  experiment became the `grouping_embeddings` remixer (single-link over tag
  overlap blended with tag embeddings), sharing `single_link_groups` with
  `grouping_singlelink`; the script is gone.
- [x] **`.env` support** (`python-dotenv`): `${VAR}` reads the environment,
  then a `.env` next to the config file.
- [x] **No database rebuild needed** (owner's call).
- [x] **CLI inspection commands**: `items` (scope options), `annotations`
  (preview table; `--key` prints full values), `artifacts` (metadata, via
  the new `Application.list_artifacts`) and `artifact` (content to stdout,
  metadata to stderr; missing is an error). Plain under `DISABLE_RICH`,
  syntax-highlighted on a terminal otherwise.
- [x] **Tests updated** to the reworked core, plus `Application`, remixer and
  identity coverage (73 tests).
- [x] **`foundation.dblib` and `foundation.plugin` declare `__all__`.** The
  shared `configure_connection` was tried and dropped: `dblib` is a shortcut
  for direct `sqlite3` use, and newsmerger, on SQLAlchemy, keeps its own
  `SQLITE_PRAGMAS`.
- [x] **`rssfeed`** takes the newest `max_items` items, newest first, and
  emits the required channel `<description>` (plus `<link>` when configured).
- [x] **TECH-DOC reconciliation** (decisions 0001–0004): source `id` required
  and items keyed by `(source id, uid)`, `uri` not unique; `${VAR}`
  expansion for secrets in `config.yaml`; plugins loaded with
  `foundation.plugin.ClassLoader`; remixers as their own plugin type and
  config section (`rssfeed`, `grouping_*`, sharing `GroupingRemixer`);
  `Application` as the single entry point with a private database, query
  facade, `enrich`/`remix` phases in config order and annotation deletion
  (which also deletes the state); `--force` resets attempts; `version` no
  longer accepted from config, and unknown plugin params rejected;
  annotation and artifact contents in the shared `DiskStorage`; pipelines
  moved to `scripts/pipeline_url.py`.
- [x] **One output rule**: `summarize` no longer writes artifacts and
  `markdownify` emits only `markdown`.
- [x] **CLI**: `import`, `import-url --source`, `enrich [PROCESSOR]`,
  `remix [REMIXER]`; `--log-level`/`-v`; `DISABLE_RICH` plain output;
  import progress and per-source error summary; run summaries as tables.
- [x] **Cleanup**: removed `ipdb.set_trace()` from `theguardian`, unused
  provider `NAME`s and constants, dead commented code, the `markdownify`
  docstring copied from `rssfeed`, `_get_or_create_source(_bulk)`, unused
  HTTP exceptions and the env-var fallbacks in processors; one Ollama client
  helper (`llm.py`, default port 11434); `castelloninformacion` no longer
  mutates its source; the `group_events*.py` scripts duplicated by the
  grouping remixers are gone.
- [x] **Application core (`newsmerger/app.py`).** `App` moved out of the CLI:
  wiring plus `import_source`, `import_url`, `run_processor`, `run_pipeline`;
  reads go through `App.db`. `cli.py` and the `group_events*` scripts use it.
- [x] **Reprocess changed content.** `processing_state.content_sha256` records
  the content each run used; a different one makes the item eligible again
  with fresh retries.
- [x] **Processor dependencies (`REQUIRES`).** `summarize`/`tagger` need
  `markdownify`, `telegram` needs `summarize`; only items the upstream
  finished on current content are picked up, so upstream skips no longer
  become downstream errors. Full failures raise plain exceptions.
- [x] **One transaction per processor result** (`Database.record_result`).
- [x] **`summarize` and `tagger` read `markdownify.markdown`.**
- [x] **SQLite connection settings** match `foundation.dblib.SQLite3DB`
  (foreign keys, WAL, ...); item foreign keys are `ON DELETE CASCADE` in the
  models.
- [x] **Bulk annotation reads** (`Database.get_annotation_values`); the three
  scripts share `load_tagged_items` from `_grouping_scoring`.
- [x] **Artifacts.** `Artifact` DTO, `DBArtifact.from_dto/to_dto/update`,
  `Database.get_artifact`. `telegram` stores `message_id` as an annotation
  and never posts an item twice.
- [x] **Re-imported `csjuntasgobierno`.** Fixed the HTTP client advertising
  `br`/`zstd` without decoders (castello.es answered with raw brotli); 1246
  items now hold their PDFs.
- [x] **Content storage.** Item contents moved out of SQLite into a
  `foundation.storage.DiskStorage` keyed by sha256 (`db.content_dir`).
  `source_items.content` replaced by `mimetype` + `content_sha256`; text is
  always UTF-8; processors load content on demand via `Database.get_content`.
- [x] **Removed `save_source_items`** and its tests; `upsert_source_items` is
  the only write path. The commented-out block in `_get_or_create_source_bulk`
  is gone too.
- [x] **Removed `newsmerger/filestore.py`** (`BufferedStore`), superseded by
  `foundation.storage`.
- [x] **Keep cleaned HTML at ingestion instead of markdown.** Providers keep
  `main_node` and its ancestors with `prune_to_spine`, drop cruft with
  `drop_selectors`, and store the HTML. Markdown is the `markdownify`
  processor's job.
- [x] **Use `SourceItem.from_data()`** in `App.import_source`.
- [x] **Swap `save_source_items` → `upsert_source_items`** in `App.import_source`.
- [x] **Gate the debug pickle dump behind `NEWSMERGER_PICKLE_CACHE`.**
- [x] **Configuration-defined pipelines.** `pipeline-url` runs an ordered list
  of configured processor steps; step params override processor defaults.
- [x] **Telegram message formatting.** `sendPhoto` with an escaped HTML caption
  (title, summary, link) when the item has an image, `sendMessage` otherwise.

---

## Bigger, not really necessary yet (flagged, not scheduled)

- **Concurrent imports.** Releasing replaced contents can race with another
  process starting to reference the same content. Add a lock if imports ever
  run in parallel.
- **PDF text extraction.** `markdownify` skips non-HTML items; PDF items need
  their own extraction step before `summarize`/`tagger` can use them.
- **Pipeline dependency graph.** Pipelines are linear; `REQUIRES` covers
  single upstream dependencies only.
- **Alembic.** Not needed while the database can be rebuilt from the
  sources.
- **Generalizing `BaseProvider`/`IndexSiteProvider`** for non-news sources:
  wait for a second concrete use case.

---

*Last updated: 2026-10-23*
