# 0008: The `inspect` and `delete` commands and numeric ids

- **Status:** accepted
- **Date:** 2026-10-23
- **Revises:** 0001 (a numeric id per item), 0007 (`--item`, `inspect
  deliveries`)

## Context

Stored data is read with four commands (`items`, `annotations`,
`artifacts`, `artifact`), each with its own options, and an item is
selected with `--source` and `--uid`. Every provider's uid is a sha256: 64
characters, plus the source id, to type for each item. A `delete` command
is planned; it needs the same selection as reading, and a way to name one
item, annotation or artifact that a person can type.

The database already has an integer `id` on every row except `sources`,
but it never leaves `db.py`. Items and annotations are updated in place
(`upsert_source_items`, `_save_annotations`, `enrich --force` included),
so their ids only change when rows are deleted or the database is rebuilt.
Without `AUTOINCREMENT`, SQLite gives a new row `max(id) + 1`, so deleting
the newest rows lets their ids be reused.

## Decision

- **Ids.** Items and annotations are selected by their numeric database
  `id` (`--item 4127`, `--annotation 512`). Artifacts keep `remixer/name`
  (`--artifact feedgenerator/feed`), split at the first `/`, so dated
  `digest` names (`digest/<source>/<since>_<until>`) work. Deliveries are selected
  by their subject. The identity of an item is still `(source id, uid)`
  (decision 0001); the numeric id is a local handle of one database.
- **`AUTOINCREMENT`.** Every table with an integer id uses it
  (`sqlite_autoincrement=True`), so a deleted id is never reused.
  `create_all` does not alter existing tables: a one-shot
  `scripts/migrate_autoincrement.py` recreates them with `AUTOINCREMENT`,
  keeping every row and id.
- **DTOs.** `SourceItem`, `Artifact` and the delivery DTO carry `id: int |
  None` (`None` before the first save). Annotations get an `Annotation` DTO
  (`id`, item id, `processor`, `key`, `updated_at`, `value`).
- **Selection.** `--item ID` (repeatable) replaces `--source`/`--uid`
  wherever an item is selected: `enrich`, `remix`, `deliver`, `inspect`
  and `delete`. `--uid` goes away; `--source` stays as a filter.
  `ProcessingScope` takes item ids instead of uids. `inspect` and `delete`
  share the same option decorators and the same `Application` queries
  (`get_items`, `find_annotations`, `list_artifacts`, `find_deliveries`),
  so `inspect X <args>` lists exactly what `delete X <args>` would delete.
  Filters combine with AND:

  | Filter | items | annotations | artifacts | deliveries |
  | :--- | :---: | :---: | :---: | :---: |
  | `--source`, `--since`, `--until` (of the item) | ✓ | ✓ | | ✓ |
  | `--limit` | ✓ | ✓ (`delete`: no) | ✓ | ✓ |
  | `--item ID` | ✓ | ✓ | | ✓ |
  | `--processor`, `--key`, `--annotation ID` | | ✓ (`delete`: only `--processor`) | | |
  | `--remixer`, `--artifact ID` | | | ✓ | ✓ |
  | `--sink`, `--status` | | | | ✓ |

  An explicit id that does not exist is an error; filters that match
  nothing give an empty result.
- **`inspect`.** `inspect items|annotations|artifacts|deliveries`, read
  only, with `--format table` (default) or `--format json`.
  - Tables: items as `ID · Source · Published · Title · Annotations`, the
    last column listing each annotation as `<id> <processor>.<key>`;
    annotations as `ID · Item · Processor.Key · Updated · Value` (a
    one-line preview); artifacts as `ID · Type · Updated`; deliveries as
    `Sink · Subject · Status · Attempts · Updated`.
  - One `--annotation` or `--artifact` in table format prints the full
    value or content to stdout and its metadata to stderr, so it can be
    redirected
    (`inspect artifacts --artifact feedgenerator/feed > feed.xml`).
  - JSON is always a list on stdout, dates in ISO 8601 UTC. Items carry
    every stored field but `content`, plus `annotations: [{id, processor,
    key}]`. Annotations carry their full value. Artifacts carry `content`
    only when selected with `--artifact`, so listings stay light.
- **`delete`.** `delete items|annotations|artifacts`, with the same
  selection as `inspect`.
  - Non-interactive: no prompts and no `--yes`. A selection that names no
    filter or id is an error. It prints what it deleted and skipped, and
    takes the write lock of decision 0007.
  - Deleting cascades: an item takes its processing state, annotations and
    deliveries with it; replaced contents are released as usual.
  - Without `--force`, items and artifacts with delivery rows are skipped
    with a warning naming them, and the rest of the selection is deleted.
    `--force` deletes them and their ledger rows, so they can be delivered
    again.
  - Annotations are deleted per processor: every key that processor wrote
    on the item, together with their processing state, so every run of it
    finds the item pending (`Database.delete_annotations`). `delete annotations` takes no
    `--key`, `--annotation` or `--limit` (which counts annotations): a
    selection names whole processors, so `inspect` with the same arguments
    lists exactly what is deleted.
- **Removed.** `items`, `annotations`, `artifacts`, `artifact` and 0007's
  `deliveries list`. `deliveries resolve` stays.

## Rejected options

- **Natural keys as ids** (`<source>/<uid>`,
  `<source>/<uid>/<processor>.<key>`). Stable across rebuilds, but too long
  to type with sha256 uids.
- **Abbreviated uids, as git does** (`castellonplaza/3fa9c1`). Prefix
  resolution and ambiguity errors for less gain than a number.
- **Numeric ids for artifacts.** `remixer/name` is short, meaningful and
  used from scripts and cron, where an id changing on a rebuild would break
  them.
- **Accepting reused ids instead of `AUTOINCREMENT`.** An id copied from an
  old listing could delete another item.
- **Rebuilding the database to get `AUTOINCREMENT`.** Loses the LLM
  annotations and the delivery ledger.
- **Deleting a single annotation key.** When the processing state was per
  (item, processor), it would have stayed `done` with a key missing. State
  is now per (item, key) (decision 0002), so that reason is gone; deleting
  per processor stays, for simplicity.
- **Widening a `--key`/`--annotation` selection to its processor, with a
  warning.** Discarded before release: the warning came after the delete,
  and `inspect` listed less than what was deleted. `--limit` was dropped
  from `delete annotations` for the same reason.
- **Confirmation prompts.** The CLI is meant for scripts and cron.
- **Rejecting the whole request when part of it has deliveries.**
  Impractical with broad filters; skipping those elements is visible in
  the output.
- **Keeping `--uid` next to `--item`, or the old commands as aliases.** Two
  ways to say the same thing.

## Consequences

- Item and annotation ids are stable while the database is; a rebuild
  renumbers them. A deleted item that is still in its source's index comes
  back on the next `import`, with a new id: deleting is not ignoring.
- `scripts/migrate_autoincrement.py` must run once on existing databases;
  new ones get `AUTOINCREMENT` from `create_all`.
- Scripts that call `items`, `annotations`, `artifact` or `--uid` must
  change; the RSS feed is written with `inspect artifacts --artifact
  feedgenerator/feed > feed.xml`.
- `delete` needs the ledger of decision 0007 to know what was delivered,
  so it comes after it; `inspect` comes before it, and `inspect
  deliveries` with it.
