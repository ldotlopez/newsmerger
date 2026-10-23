# 0005: Remixers with external side effects

- **Status:** superseded by 0007
- **Date:** 2026-10-18

## Context

`telegram` was a processor: it posted each summarized item as soon as it
was processed. A burst of new items flooded the chat, and a processor works
one item at a time, so it cannot rate-limit across items.

## Decision

- `telegram` becomes a remixer: it sees every item in scope, so it can post
  at most one item per source every `interval` minutes, from a FIFO queue.
- Remixers may have external side effects. A remixer that has them keeps
  what it has done in an artifact of its own (`telegram/state`) and reads
  its previous version on each run, so nothing is done twice.
- By default `telegram` queues only items published after its first run;
  `--since` and `--uid` queue older ones explicitly.

## Consequences

- Posting needs periodic `remix telegram` runs (e.g. cron).
- The `telegram.message_id` annotations of the old processor are no longer
  read.
- A crash between a post and saving the state can post that item again.
- An item that keeps failing holds back its source's queue.
