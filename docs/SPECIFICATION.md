# newstool: specification

Consolidated version · 23 October 2026

This document defines what newstool does, independently of how it is
implemented. It is self-contained: it is the reference for rebuilding the
application. [ARCHITECTURE.md](ARCHITECTURE.md) describes the current
implementation and [decisions/](decisions/) records why it is that way.

## 1. Purpose and scope

newstool is a pipeline for **acquiring, enriching, remixing and
delivering** content,
built for news and meant to grow into a personal collector of generic
information. External tools that consume its results are outside the project
and reach it only through the `Application` class.


## 2. Glossary

| Term | Definition |
| --- | --- |
| **Source** | An entry of the `sources` configuration section, with `id`, `name`, `provider` and `url`. Its identity is its `id`. |
| **Workflow** | Which sources to use and the process, remix and deliver runs on them. `default` is built from the catalog; `workflows` adds more. |
| **Plugin** | A bundle of plugin types: named classes of providers, processors, remixers, sinks and LLMs. Every bundle is loaded; nothing is built until a run needs it. |
| **Catalog** | The configured uses of the plugin types (`llms`, `sources`, `processors`, `remixers`, `sinks`), each with its options; an `id` lets workflows refer to one. |
| **Provider** | Object that knows how to handle one kind of site. One implementation serves every URL with the same structure. |
| **Item** | A unit of acquired content. Key: `(source id, uid)`. Its `uri` is just another field and is not unique. It also has a numeric id, a local handle to select it that is never reused but changes if the database is rebuilt. |
| **uid** | The item's identifier within its source, produced by the provider. It must be deterministic and stable across runs; how it is computed is up to the provider. |
| **Annotation** | Data derived from an item by a processor run. Key: `(item, key)`; the processor that wrote it is recorded but is not part of the key. |
| **Processor** | Object that produces annotations for one item at a time. Each process run uses a processor with its own options, and writes one key. |
| **Remixer** | Object that builds artifacts from many items. Each remix run uses a remixer with its own options, under its own key. |
| **Artifact** | Aggregated output of a remix run (newsletter, RSS, web page...). Key: `(remix key, name)`. |
| **Sink** | Object that delivers items or artifacts to the outside world (e.g. posts them to a chat). Each delivery run uses a sink with its own options (where to deliver, how often), under its own key. |
| **Delivery** | The record of a delivery run delivering one subject, an item or an artifact. Key: `(ledger key, subject)`, the ledger key naming who asked for it: `<workflow>/<key>`. It records an external fact and is never regenerated. |

## 3. Configuration

A single YAML file with the sections `plugins`, `llms`, `sources`,
`processors`, `remixers`, `sinks`, `workflows`, `cache` and `db`. All of
them are optional. Each source names its provider explicitly:

```yaml
plugins:
  <type>: {...}            # defaults of the type's options in every use
llms:
  - <llm type>             # the first serves the uses that name none, or
  - {llm: <type>, id: <id>, options: {...}}
sources:
  - id: <stable id>        # required
    name: <readable name>
    provider: <provider type>
    url: <url>
    options: {...}         # over the provider's plugin section
    skip_default: false    # true: only the workflows that name it use it
processors:
  - <processor type>       # a run with the section's options, or
  - processor: <processor type>
    id: <id>               # lets workflows refer to it
    key: <annotation key>  # default: the processor's own
    options: {...}         # over the processor's plugin section
    skip_default: false    # true: left out of `default`
remixers:
  - <remixer type>         # or {remixer, id, key, options, skip_default}
sinks:
  - <sink type>            # or {sink, id, key, options}
workflows:
  - name: <name>
    sources: [<source id>, ...]
    process: [...]         # catalog ids, type names or entries without id
    remix: [...]
    deliver: [...]
cache:
  expiration: <duration>   # HTTP cache lifetime: seconds, or 5m, 2h, 3d
db:
  uri: <sqlalchemy uri>    # default: <user data dir>/newstool/data.db
  content_dir: <path>      # default: <user data dir>/newstool/content
```

`${VAR}` references in values are replaced with environment variables when
the file is loaded; comments and keys are not expanded. Secrets (API keys,
tokens) are always passed this way.

Every plugin is loaded; its types are named, uniquely per kind, and
`plugins.<type>` sets the defaults of the type's options for every use. A
use's options are the type's defaults, then its section, then its own
`options`, merged key by key in nested mappings (any other value, lists
included, replaces). Every section and use is checked at start-up, whatever
the workflow, so a bad option fails every command with its path
(`plugins.<type>.<option>`, `sources.<id>.options.<option>`,
`workflows.<name>.deliver.<n>.options.<option>`). An object is built only
when a run needs it.

An `id` names a catalog entry so that workflows can refer to it; it cannot
be a type's name. A workflow entry is a catalog id, a type name (the type
with its section's options) or an entry of its own, without `id`; a
reference cannot change the entry's options. An object that uses an LLM
names it by id or type (`llm:`), or takes the first of `llms`; a name that
resolves to none is a configuration error.

### 3.1 Workflows

`default` uses every source without `skip_default: true` and runs, in
order, every catalog processor and remixer without it; it delivers
nothing. Each entry of `workflows` names its sources and its runs. A command
runs one workflow, `default` unless another is named, and each phase only
touches that workflow's sources: their items, and in remix the artifacts
built from them.

- A process key is written by one run within a workflow. On sources shared
  by workflows, one processor type writes it; other options for it are a
  warning (the first run to process an item writes it). Workflows with
  disjoint sources may write the same key, since annotations belong to
  items.
- A remix key belongs to one workflow, since artifacts belong to no source.
- A deliver key is unique within its workflow; its deliveries are recorded
  under its ledger key, so two workflows delivering the same item each
  deliver it, and renaming a workflow or a key starts its record anew.
- Every key a run reads must be written by a process run on its workflow's
  sources, in any workflow: a workflow may deliver what others process.
- Ids, workflow names and remix and deliver keys are lowercase letters,
  digits, `_` and `-`; `default` is reserved.

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

### 4.2 Processing

Processors create annotations on items. `process` runs the workflow's
process runs in order; each run writes one key, by default the processor's
own, and keeps its own processing state per item under that key (§3.1). A
run's options override those of the processor's plugin section.

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
- A processor that no workflow runs is never built.

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

- **Candidates:** the subjects that have no delivery for the entry yet. By
  default, those of the last `lookback` (24h; items by publication,
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
- **Order:** items are delivered oldest first. A failure at the head of a
  source's queue holds the source back until it is delivered or exhausts
  its attempts.
- **Pacing** is the entry's: with an `interval`, one delivery once the
  entry's last one is that old, whatever its source; and never more than
  `max_per_run` in a run, so a new entry does not flood its destination.
- **Forced delivery** sends explicitly selected subjects now, whatever their
  state, with no backoff and no pacing. It needs an explicit selection.
- A subject is delivered at most once per entry, unless its delivery
  record is deleted (it is queued again while within `lookback`) or a
  delivery is forced.
- `run` runs the four phases in turn, the workflow's delivery entries in
  the order of the YAML, and a failure in one does not stop the next.

## 5. API: the `Application` class

The single entry point for external tools: a Python API used in the same
process, not a network service. It offers:

- **Queries** of items, annotations, artifacts and deliveries. Querying an
  artifact that does not exist returns an explicit "does not exist".
- **Running** each of the four phases (import, process, remix, deliver).
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
  - Artifact: remix key, name, content type, `created_at` and `updated_at`.
- **Deliveries:** in the database, per `(ledger key, subject)`: status, attempts,
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
