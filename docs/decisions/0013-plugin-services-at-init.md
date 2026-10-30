# 0013: Plugin services at init

- **Status:** accepted
- **Date:** 2026-10-30
- **Revises:** 0010 (what objects receive per call, which runs' keys are
  checked)

## Context

Decision 0010 builds one object per use and keeps its options, but every
call still received the shared resources: providers the `HTTPClient`,
processors, remixers and sinks the `Database`, threaded through every verb
and hook (`process_item(db, item)`, `produce(db, scope)`,
`send(db, subject)`). Both are the same for every call of an object. Remixers
read annotations too, yet only process and delivery runs declared the key
they read, so a remix run without its process run failed at run time, not at
startup.

## Decision

- **`Services` carries the database and the HTTP client.** It holds `db`,
  `fetcher` and the `llm_factory`, all keyword-only; `Application` builds it
  once.
- **Objects keep them.** `BaseProvider` keeps `self.fetcher`;
  `BaseProcessor`, `BaseRemixer` and the sinks keep `self.db`. Methods take
  only per-run arguments: `retrieve_items(source)`, `iter_items(source)`,
  `retrieve_item(preflight_item)`, `process(key=...)`, `remix(key=...)`,
  `deliver(key=...)`, and the hooks `process_item(item)`, `produce(scope)`,
  `send(subject)`.
- **Remixers declare what they read.** `RemixerType.required_key(options)`
  and `BaseRemixer.requires`, as processors and sinks; the catalog checks
  remix runs with the others at startup. `digest` reads `markdown`, the
  `grouping` remixers `tags`.

## Rejected options

- **Passing them per call (as before).** Every signature repeated an
  argument that never changes for an object.
- **One argument per resource in the constructor.** Each new resource would
  change every plugin's constructor; `Services` grows instead.

## Consequences

- Every plugin's methods change signature; out-of-tree plugins must drop
  the `db` and `fetcher` arguments.
- Tests build plugins with `Services(db=..., fetcher=...)`, fakes included.
- A configuration whose remix run reads a key no process run writes now
  fails at startup.
