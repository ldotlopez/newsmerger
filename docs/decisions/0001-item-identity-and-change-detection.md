# 0001: Item identity and change detection

- **Status:** accepted
- **Date:** 2026-10-18

## Context

The code keys items by a database-wide `uid` and a database-wide `uri`, and
identifies sources by `sha256(provider:url)`. Every provider happens to derive
`uid = sha256(uri)` today, but that is a provider's internal choice and may
change. Sources without dates would be reimported on every run under a
date-based change rule.

## Decision

- A source is identified by the `id` it is given in the configuration. The
  `id` is required and must be stable.
- An item is identified by `(source id, uid)`. Each source is its own uid
  space; how the provider derives the uid is up to the provider, as long as
  it is deterministic and stable across runs.
- `uri` is item data, not an identifier: it is not unique.
- An item has changed when any of `title`, `uri`, `mimetype`,
  `content_sha256` or `data` differs from the stored row. Dates play no part.
  - `published_at` is set once: from the provider, or the current time.
  - `modified_at` follows the provider when newer and never moves backwards.
    It takes the current time when the provider gives none.

## Consequences

- The same story in two sources is two items, even with the same provider.
  Deduplication, if wanted, belongs to the remixers, and processors pay for
  duplicates twice.
- A source's `url` or `provider` can change without losing its items;
  renaming its `id` orphans them.
- Single-URL imports must name a configured source.
- Re-importing an identical item writes nothing. Sources without dates are
  no longer reimported on every run.
- A content change makes every processing state of the item eligible again.
  A title-only change does not.
