# newsmerger — Working Plan

Ordered smallest-and-most-necessary → biggest-and-least-necessary.
Update statuses as we progress: `[ ]` todo, `[x]` done, `[~]` in progress.

1. [ ] **Move secrets out of `config.yaml`.** It is tracked in git and holds an
   Ollama API key, a Telegram bot token and a chat id. Rotate them and read
   them from environment variables or an untracked file.

2. [ ] **Check the external artifact scripts.** Do they read the
   `markdownify.text` annotation or the `summarize` `summary:<uid>`
   artifacts? If not, drop `text` and stop `summarize` writing those
   artifacts (the `summarize.summary` annotation holds the same value). Move
   the scripts onto `App` / `Database.get_artifact` instead of raw SQL.

3. [ ] **Remove `ipdb.set_trace()` from `providers/theguardian.py`** (`parse_index`). Flagged by ruff (T100); the provider stops on every import.

4. [ ] **Remove `_get_or_create_source` (singular)** in `db.py`: no callers;
   `upsert_source_items` uses `_get_or_create_source_bulk` directly.

5. [ ] **Fix the `markdownify.py` module docstring.** It is copied from
   `rssfeed.py` and describes an RSS feed.

6. [ ] **`castelloninformacion.py` cosmetic cleanup**: stray commented-out
   `tags`/`section` extraction lines; wire them up or drop them.

7. [ ] **Propose `foundation.dblib.configure_connection(conn)`** (separately,
   in foundation): a public function applying the SQLite PRAGMAs, used by
   both `SQLite3DB` and newsmerger's `connect` listener, so the settings live
   in one place instead of being copied into `db.SQLITE_PRAGMAS`.

8. [ ] **Add `--verbose` / `--log-level` options to `cli.py`.**
   `LOGGER.setLevel(logging.DEBUG)` is hardcoded with no flags.

9. [ ] **Add `DISABLE_RICH` environment variable support.**

10. [ ] **Introduce `rich` for CLI output** (progress during import, error
    summaries) via `rich_click`, which `cli.py` already uses.

---

## Done

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
