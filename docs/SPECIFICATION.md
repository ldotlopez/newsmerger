# newsmerger: specification

Consolidated version · 23 October 2026

This document defines what newsmerger does, independently of how it is
implemented. It is self-contained: it is the reference for rebuilding the
application. [ARCHITECTURE.md](ARCHITECTURE.md) describes the current
implementation and [decisions/](decisions/) records why it is that way.

## 1. Purpose and scope

newsmerger is a pipeline for **acquiring, enriching, remixing and
delivering** content,
built for news and meant to grow into a personal collector of generic
information. External tools that consume its results are outside the project
and reach it only through the `Application` class.


## 2. Glossary

| Term | Definition |
| --- | --- |
| **Source** | An entry of the `sources` configuration section, with `id`, `name`, `provider` and `url`. Its identity is its `id`. |
| **Plugin** | A bundle enabled by an entry of the `plugins` configuration section. It provides one or more named providers, processors, remixers and sinks. |
| **Provider** | Object that knows how to handle one kind of site. One implementation serves every URL with the same structure. |
| **Item** | A unit of acquired content. Key: `(source id, uid)`. Its `uri` is just another field and is not unique. It also has a numeric id, a local handle to select it that is never reused but changes if the database is rebuilt. |
| **uid** | The item's identifier within its source, produced by the provider. It must be deterministic and stable across runs; how it is computed is up to the provider. |
| **Annotation** | Data derived from an item by a processor run. Key: `(item, key)`; the processor that wrote it is recorded but is not part of the key. |
| **Processor** | Object that produces annotations for one item at a time. Each entry of the `enrich` configuration section is a run of a processor with its own options, and writes one key. |
| **Remixer** | Object that builds artifacts from many items. |
| **Artifact** | Aggregated output of a remixer (newsletter, RSS, web page...). Key: `(remixer, name)`. |
| **Sink** | Object that delivers items or artifacts to the outside world (e.g. posts them to a chat). |
| **Delivery** | A sink's record of delivering one subject, an item or an artifact. Key: `(sink, subject)`. It records an external fact and is never regenerated. |

## 3. Configuration

A single YAML file with the sections `sources`, `plugins`, `cache` and `db`.
All of them are optional. Each source names its provider explicitly:

```yaml
sources:
  - id: <stable id>        # required
    name: <readable name>
    provider: <provider name>
    url: <url>
plugins:
  <plugin>: {...}          # its options; empty for the plugin's defaults
cache:
  expiration: <seconds>    # HTTP cache lifetime
db:
  uri: <sqlalchemy uri>    # default: <user data dir>/newsmerger/data.db
  content_dir: <path>      # default: <user data dir>/newsmerger/content
```

`${VAR}` references in values are replaced with environment variables when
the file is loaded; comments and keys are not expanded. Secrets (API keys,
tokens) are always passed this way.

Only plugins with an entry in `plugins` are loaded. Each plugin validates
its own options and fills in defaults for the missing ones; invalid options
are a configuration error that names their path (`plugins.<plugin>.<option>`).
A plugin decides which of its objects its options enable; the built-in
bundles enable all of them unless the options name some. Provider,
processor, remixer and sink names are unique per type across the loaded
plugins; sources refer to providers, `enrich` entries to processors, and
annotations, artifacts and deliveries to processors, remixers and sinks, by
those names.

A source's `id` is part of its items' key, so it must be stable; its `url`
and `provider` can change without losing items.

## 4. Phases

### 4.1 Import

Each source is queried through its provider's plugin, which lists the
articles, extracts their content and creates or updates one item per
article.

- **Dates:** each item stores `published_at` and `modified_at`.
  - New item: both come from the provider; a missing one takes the current
    time.
  - Changed item: `modified_at` takes the provider's value if it is newer
    than the stored one (it never moves backwards); if the provider does not
    emit it, it takes the current time. `published_at` is set once and never
    overwritten.
- **Change detection:** an item is changed if any of `title`, `uri`,
  `mimetype`, content (`content_sha256`) or `data` differs. Dates do not
  count. Re-importing an identical item writes nothing.
- **Changed item:** it is overwritten. Its annotations are kept, but if its
  content changed, all its processing states become eligible again with
  attempts reset to zero. Artifacts are not invalidated.
- **Duplicates:** the same article in two sources is two items, even if both
  sources use the same provider. Deduplication, if wanted, is the remixers'
  job.
- **Source removed from the YAML:** its items are kept and stop being
  updated. Remixers still see them.

### 4.2 Enrichment

Processors create annotations on items. `enrich` runs the entries of the
`enrich` section in order; each run writes one key, by default the
processor's own, and keeps its own processing state per item under that
key. A key is written by one entry only. A run's options override those of
the processor's plugin section for that run.

- **Dependencies:** a run declares the key it reads. It only picks up items
  whose run of that key finished successfully on their current content; the
  rest wait without spending attempts, also under forced regeneration. If
  the upstream run finished but the needed annotation is missing, the
  result is a retryable failure.
- **Possible results:**
  - **Success:** the annotation is saved.
  - **Skip:** the item does not apply to this processor. It is permanent for
    that content: it is only re-evaluated if the item's content changes or
    regeneration is forced.
  - **Retryable failure:** no annotation.
- **Retries:** at most 3 attempts by default, configurable with
  `max_retries`. Attempts are spaced by an exponential backoff of
  `60 s · 2^(n-1)`, capped at 24 h.
- **Attempt counter:** reset to zero on success or skip, when the item's
  content changes, when its annotations are deleted and when regeneration is
  forced from `Application`.
- **Cardinality:** one annotation per `(item, key)`; regenerating overwrites
  it.
- **Processor version:** each processor can declare a version in its code.
  When it changes, the items it had finished successfully are processed
  again without forcing; skipped items and exhausted failures are not.
- Changing a processor's or an entry's configuration regenerates
  **nothing**. Annotations are kept until the item changes, the processor's
  version is bumped, or they are regenerated or deleted from `Application`.
- A loaded processor that no entry lists never runs.

### 4.3 Remix

Remixers are a plugin type of their own. They read items, annotations and
other remixers' artifacts and produce artifacts. They run on demand, from
the CLI.

- **When to regenerate** is up to each remixer, on its next run. There is no
  invalidation or staleness flag, so an artifact can lag behind its items
  between two runs.
- With the artifact's `updated_at` and the items' dates, a remixer can be
  incremental without state of its own. A remixer that needs state keeps it
  in an artifact of its own and reads its previous version.
- Remixers have **no external side effects**: running one again only
  rebuilds its artifacts. Acting on the outside world is the sinks' job.
- **Required artifact that does not exist:** the remixer decides (build
  without it or abort). Cycles between artifacts are the remixers'
  responsibility: each one reads the other's previous version.

### 4.4 Deliver

Sinks deliver items or artifacts and record every delivery. They run after
remix, so they see freshly built artifacts.

- **Candidates:** the subjects that have no delivery for the sink yet. By
  default, those of the last `lookback` hours (24; items by publication,
  artifacts by creation); an explicit date or selection replaces that
  window. An item sink can depend on an annotation key, like processor runs
  do, and then only queues items whose run of that key finished on their
  current content.
- **States:** `queued`, `sending`, `done`, `error`. A delivery is marked
  `sending` before the external call; one still `sending` when a run starts
  was interrupted, its outcome is unknown, and it is never retried
  automatically: it is settled by hand as `done` or `queued`.
- **Retries:** failures are retried with the processors' backoff and
  `max_retries` (3 by default). Requeuing gives failures fresh attempts.
- **Order:** items are delivered first in, first out per source. A failure
  at the head of a source's queue holds the source back until it is
  delivered or exhausts its attempts.
- **Rate limits** are the sink's: it chooses which pending deliveries go now.
- **Forced delivery** sends explicitly selected subjects now, whatever their
  state, with no backoff and no rate limit. It needs an explicit selection.
- A subject is delivered at most once, unless an interrupted delivery is
  settled as `queued` or a delivery is forced.
- `deliver` runs every loaded sink, in the order of the YAML; `run` runs the
  four phases in turn, and a failure in one does not stop the next.

## 5. API: the `Application` class

The single entry point for external tools: a Python API used in the same
process, not a network service. It offers:

- **Queries** of items, annotations, artifacts and deliveries. Querying an
  artifact that does not exist returns an explicit "does not exist".
- **Running** each of the four phases (import, enrich, remix, deliver).
- **Forced regeneration** of annotations, which resets the attempt counter.
- **Deletion** of annotations, by processor, by item or both. Deleting also
  removes the processing state, so the item becomes pending again with
  attempts at zero.
- **Deletion** of items and artifacts, with everything that references them
  (processing state, annotations, deliveries).
- **Settling** interrupted deliveries as `done` or `queued`.
- A **write lock**: commands that write take it, so two of them never run
  at the same time; the second fails at once.

The database is not exposed: every query goes through `Application`.

## 6. Storage

- **Items:** content on disk through `foundation.storage.DiskStorage`, keyed
  by its sha256. Metadata goes in the database (title, URI, MIME type,
  `content_sha256`, `data`, `published_at`, `modified_at`).
- **Processing state:** in the database, per `(item, key)`: the processor
  that ran, status, attempts, last error, processor version and the
  `content_sha256` used.
- **Annotations and artifacts:** content is stored on disk through
  `foundation.storage.DiskStorage` and the database keeps the reference it
  returns. Their metadata:
  - Annotation: producer, referenced item, key, `created_at` and
    `updated_at`.
  - Artifact: producer, name, content type, `created_at` and `updated_at`.
- **Deliveries:** in the database, per `(sink, subject)`: status, attempts,
  last error, the subject's `content_sha256` when delivered, an external
  reference (e.g. a message id) and timestamps. Deleting the subject deletes
  its deliveries.

## 7. Known limitations

1. Duplicates across sources are processed twice, with the cost that implies
   for expensive processors.
2. Renaming a source's `id` orphans its previous items and re-imports
   everything under another key.
3. Artifacts can lag behind their items between two runs of their remixer.
4. Items of a removed source keep appearing in artifacts unless the remixer
   filters them out.
5. An item skipped by an upstream processor never reaches the processors
   that depend on it, and those processors keep no record of it.
6. A deleted item that is still in its source's index comes back on the
   next import, with a new id. Deleting it with its deliveries lets it be
   delivered again.

## 8. Confirmed assumptions

1. `Application` is a Python API used in the same process, not a network
   service.
2. Deleting an annotation removes the processing state and, with it, the
   attempt counter.
