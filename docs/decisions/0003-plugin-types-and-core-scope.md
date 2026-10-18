# 0003: Plugin types and core scope

- **Status:** accepted
- **Date:** 2026-10-18

## Context

Artifact generators (`rssfeed`, `grouping_*`) live among the processors as
`ArtifactProcessor`s. The core also runs configured pipelines. Plugins are
loaded by hand-written `importlib` factories.

## Decision

- There are three plugin types: provider, processor and remixer.
- Remixers read items, annotations and other remixers' artifacts, and produce
  artifacts. For now they are run manually from the CLI.
- All three types are loaded with `foundation.plugin.ClassLoader`: one module
  per plugin, exposing its entry class. `Register` does not fit, because it
  stores ready-built instances and plugins need per-use constructor arguments
  (source, database, params).
- Pipelines (processor chains over one item) stay outside the core. They are
  scripts in `scripts/` built on `Application` while the feature is in
  development.

## Consequences

- The configuration gains a `remixers` section, and processors are left with
  per-item work only.
