# newsmerger: specification

Consolidated version · 20 October 2026

This document defines what newsmerger does, independently of how it is
implemented. It is self-contained: it is the reference for rebuilding the
application. [ARCHITECTURE.md](ARCHITECTURE.md) describes the current
implementation and [decisions/](decisions/) records why it is that way.

## 1. Purpose and scope

newsmerger is a pipeline for **acquiring, enriching and remixing** content,
built for news and meant to grow into a personal collector of generic
information. External tools that consume its results are outside the project
and reach it only through the `Application` class.

Pipelines (chains of processors over one item) are external and still in
development: for now they are scripts built on `Application` and are not part
of this definition.

## 2. Glossary

| Term | Definition |
| --- | --- |
| **Source** | An entry of the `sources` configuration section, with `id`, `name`, `provider` and `url`. Its identity is its `id`. |
| **Plugin** | A bundle enabled by an entry of the `plugins` configuration section. It provides one or more named providers, processors and remixers. |
| **Provider** | Object that knows how to handle one kind of site. One implementation serves every URL with the same structure. |
| **Item** | A unit of acquired content. Key: `(source id, uid)`. Its `uri` is just another field and is not unique. |
| **uid** | The item's identifier within its source, produced by the provider. It must be deterministic and stable across runs; how it is computed is up to the provider. |
| **Annotation** | Data derived from an item by a processor. Key: `(item, processor, key)`; a processor can emit several keys per item. |
| **Processor** | Object that produces annotations for one item at a time. |
| **Remixer** | Object that builds artifacts from many items. |
| **Artifact** | Aggregated output of a remixer (newsletter, RSS, web page...). Key: `(remixer, name)`. |

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
bundles enable all of them unless the options name some. Provider, processor
and remixer names are unique per type across the loaded plugins; sources
refer to providers, and annotations and artifacts to processors and
remixers, by those names.

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
- **Importing a single URL:** it must name a configured source, whose
  provider is used.
- **Source removed from the YAML:** its items are kept and stop being
  updated. Remixers still see them.

### 4.2 Enrichment

Processors create annotations on items.

- **Dependencies:** a processor declares the processor it depends on. It
  only picks up items that processor finished successfully on their current
  content; the rest wait without spending attempts, also under forced
  regeneration. If the upstream processor finished but the needed annotation
  is missing, the result is a retryable failure.
- **Possible results:**
  - **Success:** the annotations are saved.
  - **Skip:** the item does not apply to this processor. It is permanent for
    that content: it is only re-evaluated if the item's content changes or
    regeneration is forced.
  - **Retryable failure:** no annotations.
  - **Partial failure:** the keys obtained are saved and the item counts as
    a retryable failure.
- **Retries:** at most 3 attempts by default, configurable with
  `max_retries`. Attempts are spaced by an exponential backoff of
  `60 s · 2^(n-1)`, capped at 24 h.
- **Attempt counter:** reset to zero on success or skip, when the item's
  content changes, when its annotations are deleted and when regeneration is
  forced from `Application`.
- **Cardinality:** one annotation per `(item, processor, key)`; regenerating
  overwrites the emitted keys.
- **Processor version:** each processor can declare a version in its code.
  When it changes, the items it had finished successfully are processed
  again without forcing; skipped items and exhausted failures are not.
- Changing a processor's configuration regenerates **nothing**. Annotations
  are kept until the item changes, the processor's version is bumped, or
  they are regenerated or deleted from `Application`.
- `enrich` runs every loaded processor, in the order of the YAML.

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
- **External side effects** (e.g. posting to a chat) are allowed. The
  remixer must record what it has done in its own state, so a later run does
  not repeat it.
- **Required artifact that does not exist:** the remixer decides (build
  without it or abort). Cycles between artifacts are the remixers'
  responsibility: each one reads the other's previous version.

## 5. API: the `Application` class

The single entry point for external tools: a Python API used in the same
process, not a network service. It offers:

- **Queries** of items, annotations and artifacts. Querying an artifact that
  does not exist returns an explicit "does not exist".
- **Running** each of the three phases (import, enrich, remix).
- **Forced regeneration** of annotations, which resets the attempt counter.
- **Deletion** of annotations, by processor, by item or both. Deleting also
  removes the processing state, so the item becomes pending again with
  attempts at zero.

The database is not exposed: every query goes through `Application`.

## 6. Storage

- **Items:** content on disk through `foundation.storage.DiskStorage`, keyed
  by its sha256. Metadata goes in the database (title, URI, MIME type,
  `content_sha256`, `data`, `published_at`, `modified_at`).
- **Processing state:** in the database, per `(item, processor)`: status,
  attempts, last error, processor version and the `content_sha256` used.
- **Annotations and artifacts:** content is stored on disk through
  `foundation.storage.DiskStorage` and the database keeps the reference it
  returns. Their metadata:
  - Annotation: producer, referenced item, key, `created_at` and
    `updated_at`.
  - Artifact: producer, name, content type, `created_at` and `updated_at`.

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

## 8. Confirmed assumptions

1. `Application` is a Python API used in the same process, not a network
   service.
2. Deleting an annotation removes the processing state and, with it, the
   attempt counter.
