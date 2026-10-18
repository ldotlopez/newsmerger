# 0002: Processing state lifecycle

- **Status:** accepted
- **Date:** 2026-10-18

## Context

The technical definition allowed one annotation per `(item, processor)`,
treated a missing upstream annotation as a retryable failure, and said no
configuration change regenerates anything. The code writes several keys per
processor, waits for upstream processors, and reprocesses on a version bump.

## Decision

- **Annotations** are keyed by `(item, processor, key)`. A processor may emit
  several keys. A partial failure saves the keys it obtained and counts as a
  retryable failure.
- **Dependencies:** a processor names the processor it reads from
  (`REQUIRES`). Only items that processor finished on their current content
  are picked up, even when forced. Items still waiting spend no attempts.
  A finished upstream that lacks the needed annotation is a retryable failure.
- **Outcomes:** done, ignored (permanent for that content), or error with
  exponential backoff and a retry limit (`max_retries`).
- **Reprocessing triggers**, and nothing else:
  - The item's content changes: every state becomes eligible with zero
    attempts.
  - The processor's `VERSION` changes: done items are reprocessed.
    `VERSION` is set in code only.
  - A forced regeneration, which resets attempts.
  - Deleting annotations, which also deletes the processing state.
- Changing a processor's configuration never regenerates anything.

## Consequences

- Running processors out of order does not exhaust retries.
- An item ignored upstream never reaches its dependants, and they keep no
  record of it.
