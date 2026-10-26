# newsmerger — Working Plan

Ordered smallest-and-most-necessary → biggest-and-least-necessary.
Update statuses as we progress: `[ ]` todo, `[x]` done, `[~]` in progress.
Ideas and plans not scheduled yet go to the backlog at the end.

## Per-source provider options (`provider_options`)

Agreed 2026-10-26. A source passes options to its provider:

```yaml
- id: some-blog
  provider: rssparser
  provider_options:
    article_selector: .article
```

Convention for every plugin: its `plugins.<name>` section holds defaults,
and each use overrides only what its verb declares. `import-url` goes for
now; it comes back later on a model that fits (an ad hoc source).
External pipelines go too: they will be replaced, not kept as scripts.

- [x] **1. Remove `import-url`:** the command and its CLI test,
  `Application.import_url`, `URLProvider` and `UnsupportedProviderError`
  (the plugins register as `Provider`), `scripts/pipeline_url.py` (the
  only pipeline).
  `import_sample()` in `tests/test_app.py` imports another way.
- [x] **2. Remove the pickle cache** (`NEWSMERGER_PICKLE_CACHE`) from
  `Application.import_source`.
- [x] **3. `provider_options` on sources**, from the config only: not stored
  in the database (`DBSource` unchanged). `import_source` passes them to
  `retrieve_items(source, fetcher, **provider_options)`.
- [x] **4. Validate at startup:** `Application` binds each source's options
  against its provider's `retrieve_items` signature; a failed bind is a
  `ConfigError` naming `sources.<id>.provider_options`. Providers declare
  their options explicitly, never `**kwargs` (it would accept anything).
- [x] **5. `rssparser`:** `article_selector` becomes a `retrieve_items`
  keyword, defaulting to the plugin section's `article_selector`; the
  `article_selectors` map goes. Tests.
- [x] **6. Docs**, each edit approved first: rewrite decision 0003 (options
  convention; the pipelines point goes); 0001 (the single-URL import line);
  SPECIFICATION (§4.1 and the external pipelines note); ARCHITECTURE (the
  `scripts/` row and the Pipelines section); README (`import-url` and
  `pipeline_url.py`); `config.example.yaml`; the backlog's *Pipeline
  dependency graph* entry.
- [x] **7. Naming review:** `provider`/`provider_options` stay. `rssparser`
  is now `feedreader` and the `rssfeed` remixer `feedgenerator`;
  `scripts/migrate_feed_names.py` renames the stored artifacts (run once).
- [x] **8. Docs for the renames.**

## P1 — Plain logging and the `<APP>_LOG_LEVEL` fix

Precedence: CLI (`--log-level`, `-v`/`-q`) > `NEWSMERGER_LOG_LEVEL` >
config `log_level` > `warning`. With `-v`/`-q` and no `--log-level`, they
step from `warning`, ignoring the env var: `-v` is always info, `-vv` debug.

Bug (confirmed 2026-10-24): `click_logging_options` gives `--log-level` a
`"warning"` default, so `setup_logger` never reads the env var, which it only
looks up when `log_level is None`.

foundation (`../foundation`, separate commits; its push is manual):

- [x] **1. `click_logging_options`:** `--log-level` defaults to `None`; the
  help names the `warning` default and the `<APP>_LOG_LEVEL` variable.
- [x] **2. `setup_logger` / `setup_logger_from_click`:** a
  `default_log_level` parameter (defaults to `DEFAULT_LOG_LEVEL`) for the
  app's config value; `-v`/`-q` without `--log-level` ignore the env var.
  Fix the stale `configure_handler` docstrings.
- [x] **3. `tests/test_loglib.py`:** nothing gives warning; the env var
  applies; `--log-level` and `-v` beat it; the app default applies when
  neither CLI nor env set a level.

newsmerger:

- [x] **4.** `uv lock --upgrade-package foundation` (foundation `main` at
  `96d6929`).
- [x] **5. `log_level: str = "warning"` in `Config`.** Low value (the level
  is a per-run concern; cron can pass `-v`); droppable without affecting the
  rest.
- [x] **6. Logger setup moves to `app_from_context`**, after the config is
  loaded: one `setup_logger_from_click(..., default_log_level=cfg.log_level)`
  call, with the logging options in `ctx.obj` like `config_path`. Without
  step 5, only pass the CLI values through.
- [x] **7. INFO logs per phase**, as `"{name}: …"`:
  - import: `"{source.id}: {uri}"` per item in `app.import_source`, for every
    provider, no source header (`db.py`'s `N new, M updated` closes it);
  - remix: start and end (duration, artifact count) in `BaseRemixer.remix`,
    like `BaseProcessor.enrich`;
  - deliver: `N to deliver` and `done/failed` with duration in `_send_all`;
  - enrich: already complete.
- [x] **8. Precedence tests** in `test_cli.py`: env var applies, `-v` beats
  it, config applies (with step 5).
- [x] **Docs, when done:** `README.md` (env var, config key, precedence),
  `ARCHITECTURE.md` (`config.py`) and `config.example.yaml`.

## P2 — Rich progress across the app

Progress bars complement the logs, never replace them. Each stream is rich
only when it is a terminal: stdout carries results (tables, `inspect`,
contents, `--help`, and the `run`/`import`/`enrich`/`remix`/`deliver`
summaries), stderr carries diagnostics (progress, logs).

| | stdout terminal | stdout redirected |
| :--- | :--- | :--- |
| **stderr terminal** | all rich | rich progress and logs, plain tables |
| **stderr redirected** | rich tables, no progress, plain logs | all plain (cron) |

Progress goes per phase and unit only, driven from `cli.py`: plugin
contracts stay untouched (per-item progress is in the backlog).

foundation:

- [x] **1. Per-stream rich in `clilib`.** `RICH_STDOUT_ENABLED` /
  `RICH_STDOUT_DISABLED` and `RICH_STDERR_ENABLED` / `RICH_STDERR_DISABLED`,
  computed at import from each stream's TTY; `DISABLE_RICH`,
  `RICH_DISABLED` and `TERM=dumb` disable both. `RICH_ENABLED` /
  `RICH_DISABLED` are removed, to avoid two ways of asking. `NO_COLOR` no
  longer disables rich: it only drops colors, which rich already honors.
- [x] **2. `setup_logger` picks the handler.** With `infect=True`, a
  `RichHandler` when stderr is rich, otherwise a plain `StreamHandler`
  (`%(asctime)s %(levelname)s %(name)s: %(message)s`), on the root logger,
  once. `infect=False` still attaches nothing.
- [x] **3. Tests**, reloading `clilib` with a patched environment and
  streams (computed at import), and both handler choices. Branch
  `p2-rich-per-stream` (`efc073c`), not merged yet.

newsmerger:

- [x] **4.** `uv lock --upgrade-package foundation`; the README test command
  becomes `DISABLE_RICH=1 uv run python -m unittest discover -s tests`, so
  the mode is fixed whoever runs it (unittest keeps the caller's stderr).
- [x] **5. Per-stream switches in `cli.py`.** `rich_click` vs `click` and
  `print_table` follow stdout; `print_content` uses `RICH_STDOUT_ENABLED`
  instead of its own `isatty`. `setup_logging` drops its plain-handler
  branch and the `infect` argument (it was on the package logger, so
  third-party logs fell to `logging.lastResort` in plain mode).
- [x] **6. `Application` exposes processor, remixer and sink names**, like
  `sources`; `app.enrich`/`remix`/`deliver` are deleted and `test_app.py`
  moves to `run_*` and the name lists (configuration order).
- [x] **7. One `Progress` in `cli.py`** on `get_stderr_console()`, with
  `disable=RICH_STDERR_DISABLED`, replacing `track`; the CLI calls `run_*`
  one unit at a time. `run` keeps a phase row (`n/4`); unit rows (spinner,
  elapsed) are removed when done (`remove_task`). `redirect_stdout=False`,
  so a redirected stdout keeps the tables, printed after the rows end.
- [x] **Docs, when done:** propose `ARCHITECTURE.md` (names on
  `Application`, no `enrich`/`remix`/`deliver`; output per stream) and
  `README.md` (terminal detection per stream, `NO_COLOR`, test command).

- [x] **Other foundation consumers** (karasync, intelligence, gvavivenda,
  photolib-tools' `immichtool`), workspace members on the editable
  foundation: migrated in their working copies, left uncommitted for the
  owner. Progress moves to the stderr console with `RICH_STDERR_*`;
  intelligence's plain `echo` lines become `LOGGER.info`/`LOGGER.error`.
  Checked against the branch: same test failures as before. gvavivenda
  already fails to import on foundation `main` (`StatValidator` is gone from
  `foundation.cache`), unrelated to P2.

Out of scope: `inspect`, `delete` and `scripts/` (fast, tables already rich).

## Numeric ids and `inspect` (decision 0008)

- [x] **1. `AUTOINCREMENT` and `scripts/migrate_autoincrement.py`.**
  `sqlite_autoincrement=True` on every table with an integer id; a
  one-shot script recreates the existing tables with it, keeping rows and
  ids, with a test on a copy of a populated database. Run on
  `~/.local/share/newsmerger/data.db` on 2026-10-23 (backup at
  `data.db.bak-20261023`); it had no `telegram/state` to migrate.
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
- [x] **Docs, when done:** propose the `README.md` (usage) and
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
- [x] **Docs, when done:** propose the `ARCHITECTURE.md`, `README.md` and
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

## Backlog: ideas and pending plans (flagged, not scheduled)

- **Force rich without a terminal** (e.g. for `watch` or `ssh` without a
  pty), in foundation. Only if P2's TTY detection gets in the way.
- **Per-item progress** inside processors, sinks and imports. P2 left it
  out to keep the plugin contracts as they are (a callback would change
  `Processor.enrich` and `Sink.deliver`); revisit if unit rows fall short.
- **Concurrent imports.** Releasing replaced contents can race with another
  process starting to reference the same content. Add a lock if imports ever
  run in parallel.
- **PDF text extraction.** `markdownify` skips non-HTML items; PDF items need
  their own extraction step before `summarize`/`tagger` can use them.
- **Alembic.** Not needed while the database can be rebuilt from the
  sources.
- **Generalizing `BaseProvider`/`IndexSiteProvider`** for non-news sources:
  wait for a second concrete use case.
- **Save annotations and artifacts as soon as possible**: they stay in
  memory until the loop finishes.
- **Define enrich process (and order) in its own section (`enrich`)**.
  Also make possible to override per source: `sources>enrich`
- **Automatic plugin loading**. Use definition of sources and enrich
  to detect which plugins to load
- **summary plugin: make prompt configurable**: Global and per-source
- **google chat deliver plugin**
- **LLM options per use (`llm` + `llm_options`)**, following the provider
  convention agreed on 2026-10-26: a plugin section holds defaults, each use
  overrides what its verb declares. Today consumers override `model` (and
  `digest` `context_length`); `json_mode`/`context_length` stay explicit in
  the `LLM` protocol. Review decision 0006 first; migrate when a
  backend-specific option needs a per-use override.

---

*Last updated: 2026-10-26*
