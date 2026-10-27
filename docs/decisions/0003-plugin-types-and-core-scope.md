# 0003: Plugin types and core scope

- **Status:** accepted
- **Date:** 2026-10-18
- **Revised:** 2026-10-20 (plugin bundles loaded with `Register`);
  2026-10-26 (per-use options); 2026-10-27 (autoloading, `process`; see
  *Revisions*)
- **Amended by:** 0006 (LLM plugins and the `services` argument), 0007
  (sinks and the `deliver` phase)

## Context

Artifact generators (`rssfeed`, `grouping_*`) lived among the processors as
`ArtifactProcessor`s, the core ran configured pipelines, and plugins were
loaded by hand-written `importlib` factories.

A first revision split them into three types, each loaded from its own
package with `foundation.plugin.ClassLoader` and built on every use with its
constructor arguments. That made every new plugin type a new package and
loader, kept related plugins apart (`summarize`, `tagger` and
`grouping_embeddings` each built an Ollama client from the same options and
declared the same option models) and left each plugin's options unchecked
until it was first used.

## Decision

- **Types.** There are three plugin types: provider, processor and remixer,
  each defined by a `typing.Protocol` the core consumes (`Provider`,
  `Processor`, `Remixer`). Remixers read items, annotations
  and other remixers' artifacts, and produce artifacts; they run on demand
  from the CLI.
- **Loading.** Plugins live in one namespace, `newsmerger.plugins`, and are
  loaded with `foundation.plugin.Register`, unmodified. A module is a bundle:
  it can provide any number of objects of any type.
- **Enabling.** The `plugins` config section lists plugins with their
  options, in the order `remix` and `deliver` run them; `process` runs the
  entries of the `process` section instead (decision 0002). After them, a
  provider that a source names or a processor that a `process` entry names,
  if no loaded plugin provides it, loads the plugin of the same name with
  its defaults; a name no plugin provides is a configuration error with its
  path (`sources.<id>.provider`, `process.<n>.processor`). Remixers and
  sinks, which nothing names, load only from `plugins`, and a plugin neither
  listed nor named is never imported. All of them are loaded when
  `Application` is built, before the database is opened.
- **Options.** The entry point, `__newsmerger_plugin__(**options)`, receives
  its section as keyword arguments, validates it with its own pydantic model
  (unknown keys rejected, defaults for the general case, so an empty section
  is enough), builds its objects and returns `(name, Protocol, object)`
  triples. Objects are instances, never classes: the core rejects a class as
  a plugin error. Every provider and processor builds with no options, since
  it can be loaded by name alone. The core never sees a plugin's models; it reports a
  `ValidationError` raised by an entry point as a configuration error with
  the options' path (`plugins.<plugin>.<option>`).
- **Per-use options.** A plugin's section holds its defaults; each use
  overrides only the options its method declares as keyword arguments. A
  source's `options` reach its provider's `retrieve_items`, which
  declares each one (never `**kwargs`) and falls back to its section's value.
  When `Application` is built, the core binds every source's options to that
  signature and reports a mismatch as a configuration error
  (`sources.<id>.options`). Processors work the same way: a `process`
  entry's `options` reach `process_item`, checked at start-up through the
  processor's `output_key(**options)`, which also gives the run's default
  key (`process.<n>.options`); the entry's `key`, outside `options`,
  overrides it. They live in the
  configuration only: the database does not store them.
- **Objects.** Objects are built once and receive what each task needs as
  method arguments: providers the source, the HTTP client and the source's
  provider options, processors the database, the scope, the run's key and
  options, and remixers the database and the scope.
- **Names.** Object names are unique per type across plugins and are what
  sources, `process` entries, artifacts and the CLI refer to. A provider or
  processor is named after its plugin module, so naming it loads it. Processors and
  remixers own their name, a class attribute, and are registered under it;
  providers' names exist only in their triples. Annotations are keyed by
  the run's key, which the configuration may rename (decision 0002).
- **Methods.** Each protocol has a method of its own (`retrieve_items`,
  `process`, `remix`), named after the phase that calls it. foundation matches
  declared protocols with `issubclass()`, which compares method names only.
- **Bundles.** Bundles enable all their objects unless their options name
  some; this is a convention of the plugins, not a rule of the core. Bundles
  never import each other: they share data through annotations (`llm.embed`
  stores the vectors `grouping.embeddings` reads). Code used by a single
  bundle, such as clustering, lives in that bundle.

## Rejected options

- **One package and `ClassLoader` per type, objects built per use** (the
  first revision of this decision). Every new type needs a new loader, and
  related plugins cannot share a client or an options model.
- **Registering factories (or `Lazy` objects) built with each task's
  arguments.** Objects are built once; per-task inputs are method arguments.
- **Loading plugins on first use.** Invalid options would surface only when
  the plugin first runs; loading everything on start-up fails at once.
- **Option models declared or validated by the core.** The core would have
  to know every plugin; each entry point validates its own options instead.
- **Separate `summarize`, `tagger` and Ollama helper modules.** They
  duplicated the connection options and models; they are one `llm` bundle
  with a shared connection and a subsection per processor.
- **Embeddings computed by the grouping remixer on every `remix`.** They are
  computed once per item by `llm.embed` and stored as annotations.
- **`name` in the protocols.** As a data attribute, `issubclass()` rejects
  the protocol. As a `name()` method, it adds API noise only to let the core
  compare it with the triple. Injected by the entry point, it would allow
  renaming an object from the configuration; annotation keys are what the
  configuration renames instead.
- **A common `run` method.** `issubclass()` cannot tell protocols with the
  same methods apart, so remixers were loaded as processors and vice versa.
  A marker method per protocol would be noise, and registering against base
  classes instead of protocols would force inheritance.
- **Per-use options checked when the provider is called**, a `TypeError`
  as the error. It would surface only on import, and a `TypeError` raised
  inside the provider would read as a bad option.
- **A map of per-source values in the plugin's section** (source id →
  value). A mistyped source id goes unnoticed, since a plugin never sees the
  sources, and a source's settings end up in two places.
- **Options passed as one positional dict.** It avoids reserved option
  names, but entry points take keyword arguments. Making `register()`'s
  `name` positional-only would also avoid them, but foundation stays as is.

## Consequences

- The configuration has a single `plugins` section; config files written
  for the `processors` and `remixers` sections must be rewritten.
- Annotations and the `telegram` state keep their names; the old
  `grouping_*` artifacts are left behind, and the grouping remixers produce
  theirs under `singlelink`, `avglink` and `embeddings`.
- Every loaded plugin is imported and built on start-up, so a broken plugin
  or invalid options fail every command, including read-only ones.
- A new plugin type needs a method name of its own: a protocol whose methods
  are a subset of another's is taken as its parent.
- `name` and `self` cannot be plugin options: they are `register()`'s own
  parameters.
- Grouping with embeddings needs `process` to have run `embed` first.
- A plugin needs a section only for options, or to enable its remixers and
  sinks. Config files with `enrich:` or `provider_options:` must be
  rewritten as `process:` (with `key` moved out of `options`) and
  `options:`.
- A source that gives its provider an option it does not declare fails
  every command at start-up, like invalid plugin options.

## Revisions

- **2026-10-27.** Providers and processors named by sources and `process`
  entries load their plugin on their own, after the listed plugins; entry
  points return instances. `enrich` renamed `process` (section, phase, CLI
  command and `Processor.process`), `provider_options` renamed `options`,
  and an entry's `key` moved out of its `options`. Discarded: "a plugin
  without a section is not loaded"; loading every module to find which one
  provides a name (it imports every plugin on every command); and a root
  `llm:` list of LLM plugins next to `plugins` (two places to declare one
  plugin; listed plugins loading first already orders LLMs before their
  consumers, see 0006).

- **2026-10-26.** Per-use options extended to processors through the
  `enrich` section; the `plugins` section no longer orders `enrich`.
  Discarded: running every loaded processor once, in the order of `plugins`.
- **2026-10-26.** Added per-use options. Discarded: `URLProvider`, the
  single-URL import (`import-url`) that used it, and external pipelines
  (processor chains over one item as scripts in `scripts/`, built on that
  import). Neither was in use; both may return on a model that fits
  sources defined on the fly.
