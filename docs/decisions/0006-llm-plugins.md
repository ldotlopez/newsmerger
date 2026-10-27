# 0006: LLM plugins

- **Status:** accepted
- **Date:** 2026-10-20
- **Revised:** 2026-10-27 (LLMs load before autoloaded consumers; decision 0003)

## Context

The `llm` bundle held the Ollama connection and the three processors that
use it (`summarize`, `tagger`, `embed`). Any new processor that needed a
model had to join the bundle, and the connection could not be swapped for
another backend. Decision 0003 forbids bundles from importing each other, so
the processors could not simply be split out and share the client.

## Decision

- **Type.** `LLM` is a fourth plugin type, defined by a `typing.Protocol` in
  `llms.py` with two methods: `prompt(prompt, *, model, json_mode)` and
  `embed(texts, *, model)`. Without `model`, the backend uses its own
  default for each method. `prompt` also takes `context_length`, for long
  prompts such as `digest`'s.
- **Backends.** An LLM backend is a plugin providing one `LLM` object named
  after the plugin; `ollama` is the first, with `chat_model` and
  `embed_model` as its defaults.
- **Consumers.** `summarize`, `tagger`, `embed` and the `digest` remixer are
  separate plugins. Each takes `llm` (the backend's name; `None`, the
  default, means no preference) and `model` (overrides the backend's
  default).
- **Services.** The core passes a `Services` object as the first positional
  argument of every entry point: `__newsmerger_plugin__(services,
  **options)`. It holds the LLMs of the plugins registered before, by name,
  in configuration order. `services.llm(name)` returns the named LLM, or the
  first one for `None`, and raises `LLMUnavailableError` when none is loaded
  or the named one is not.
- **Unavailable LLM.** A consumer that cannot get its LLM still loads: it
  registers an `UnavailableProcessor` (`UnavailableRemixer` for `digest`)
  under its name, which logs the reason as an error when run and does
  nothing; a processor's items stay pending. Error, not warning: the work
  is not done and nothing replaces it.
- **Optional.** No LLM is needed to import, convert to markdown or build the
  RSS feed. Plugins that read LLM output (`grouping`, `telegram`) read
  annotations, not the `LLM`, and run on whatever is there.

## Rejected options

- **An `llm` core section, like `db`.** Backends could not be added as
  plugins, and the core would carry an `LLM | None` for configurations
  without one.
- **The LLM as a method argument** (`enrich(db, llm, ...)`). It changes the
  `Processor` protocol and every `process_item` for the few processors that
  need it.
- **Setting the LLM on objects after loading.** Objects would be incomplete
  between construction and injection; 0003 builds them once.
- **Passing `services` only to entry points that declare it.** The core
  would inspect signatures; one uniform signature is simpler.
- **Loading in two passes so order does not matter.** The core cannot tell
  which plugin provides an LLM before loading it.
- **A failed LLM lookup as a configuration error.** A configuration without
  an LLM is valid; its consumers report why they do nothing when run.
- **Separate `LLM` and `Embedder` protocols.** One backend serves both today.

## Consequences

- LLM plugins must be listed in `plugins`, before the listed plugins that
  use them; consumers loaded by name alone (decision 0003) load after every
  listed plugin, so they always see the listed LLMs. Otherwise the consumer
  logs `llm '<name>' is not loaded` on every `process`.
- Every entry point takes `services`, used or not.
- Configurations with an `llm:` plugin section must be rewritten as
  `ollama:` plus `summarize:`, `tagger:` and `embed:` sections; per-processor
  models move to `ollama.chat_model`/`embed_model` or stay as `model:` in each
  processor's section. Annotation names do not change.
- One section per plugin module means one connection per backend type.
