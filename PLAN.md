# newsmerger — Working Plan

Ordered smallest-and-most-necessary → biggest-and-least-necessary.
Update statuses as we progress: `[ ]` todo, `[x]` done, `[~]` in progress.

1. [ ] **Rotate the leaked secrets** (owner). The Ollama API key and the
   Telegram bot token are in git history; `config.yaml` now reads them from
   `${OLLAMA_API_KEY}`, `${TELEGRAM_BOT_TOKEN}` and `${TELEGRAM_CHAT_ID}`.

2. [ ] **Rebuild the real database** (owner). The schema changed (source ids,
   `(source_id, uid)` keys, contents on disk, `artifacts.remixer`) and is
   never migrated. No database exists at the default path on this machine;
   where it does, rename `data.db` (with `-wal`/`-shm`) and `content/` to
   `*.old-2026-10-18`, then `import`. Warning: `enrich` runs `telegram` and
   reposts every summarized item in scope; use `--since`.

3. [ ] **Fix the external artifact scripts** that read the removed
   `summary:<uid>` artifacts, `markdownify.text` or the database directly;
   move them onto `Application`.

---

## Done

- [x] **CLI inspection commands**: `items` (scope options), `annotations`
  (preview table; `--key` prints full values), `artifacts` (metadata, via
  the new `Application.list_artifacts`) and `artifact` (content to stdout,
  metadata to stderr; missing is an error). Plain under `DISABLE_RICH`,
  syntax-highlighted on a terminal otherwise.
- [x] **Tests updated** to the reworked core, plus `Application`, remixer and
  identity coverage (73 tests).
- [x] **`foundation.dblib.configure_connection`** applies `SQLITE_PRAGMAS` to
  any connection; `Database` uses it instead of a copied list.
  `foundation.dblib` and `foundation.plugin` now declare `__all__`.
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

*Last updated: 2026-10-18*
