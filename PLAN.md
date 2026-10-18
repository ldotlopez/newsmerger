# newsmerger — Working Plan

Ordered smallest-and-most-necessary → biggest-and-least-necessary.
Update statuses as we progress: `[ ]` todo, `[x]` done, `[~]` in progress.

1. [ ] **Move secrets out of `config.yaml`.** It is tracked in git and holds an
   Ollama API key, a Telegram bot token and a chat id. Rotate them and read
   them from environment variables or an untracked file.

2. [ ] **Remove `ipdb.set_trace()` from `providers/theguardian.py`** (`parse_index`). Flagged by ruff (T100); the provider stops on every import.

3. [ ] **Remove `_get_or_create_source` (singular)** in `db.py`: no callers;
   `upsert_source_items` uses `_get_or_create_source_bulk` directly.

4. [ ] **Fix the `markdownify.py` module docstring.** It is copied from
   `rssfeed.py` and describes an RSS feed.

5. [ ] **`castelloninformacion.py` cosmetic cleanup**: stray commented-out
   `tags`/`section` extraction lines; wire them up or drop them.

6. [ ] **Re-import `csjuntasgobierno` deliberately.** The provider now
   downloads each PDF. Its 1234 existing rows were migrated with empty
   content labelled `text/html`; the next import fetches every PDF and
   updates them to `application/pdf`. The source is commented out in
   `config.yaml` until then.

7. [ ] **Reclaim space in the migrated database.** `DROP COLUMN` does not
   shrink the SQLite file; run `VACUUM` once. Delete `data.db.bak` when the
   migration is confirmed good.

8. [ ] **Add `--verbose` / `--log-level` options to `cli.py`.**
   `LOGGER.setLevel(logging.DEBUG)` is hardcoded with no flags.

9. [ ] **Add `DISABLE_RICH` environment variable support.**

10. [ ] **Introduce `rich` for CLI output** (progress during import, error
    summaries) via `rich_click`, which `cli.py` already uses.

---

## Done

- [x] **Content storage.** Item contents moved out of SQLite into a
  `foundation.storage.DiskStorage` keyed by sha256 (`db.content_dir`).
  `source_items.content` replaced by `mimetype` + `content_sha256`; text is
  always UTF-8; processors load content on demand via `Database.get_content`.
  Real database migrated with `scripts/migrate_content_to_storage.py`
  (1888 items, 655 distinct contents).
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

- **Constraints on migrated databases.** SQLite `ALTER TABLE` cannot add
  NOT NULL or CHECK constraints, so the migrated `source_items` lacks the
  ones a fresh schema has. Rebuild the table if they ever matter.
- **Concurrent imports.** Releasing replaced contents can race with another
  process starting to reference the same content. Add a lock if imports ever
  run in parallel.
- **PDF text extraction.** `markdownify` skips non-HTML items; PDF items need
  their own extraction step before `summarize`/`tagger` can use them.
- **Pipeline idempotency.** Pipelines are linear with no durable Telegram
  idempotency and no dependency graph.
- **Alembic migrations.** One-shot scripts are enough until schema changes
  become frequent.
- **Generalizing `BaseProvider`/`IndexSiteProvider`** for non-news sources:
  wait for a second concrete use case.

---

*Last updated: 2026-10-18*
