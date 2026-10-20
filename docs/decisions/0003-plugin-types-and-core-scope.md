# 0003: Plugin types and core scope

- **Status:** accepted
- **Date:** 2026-10-18
- **Revised:** 2026-10-20 (plugin bundles loaded with `Register`)
- **Amended by:** 0006 (LLM plugins and the `services` argument)

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
  `URLProvider`, `Processor`, `Remixer`). Remixers read items, annotations
  and other remixers' artifacts, and produce artifacts; they run on demand
  from the CLI.
- **Loading.** Plugins live in one namespace, `newsmerger.plugins`, and are
  loaded with `foundation.plugin.Register`, unmodified. A module is a bundle:
  it can provide any number of objects of any type.
- **Enabling.** The `plugins` config section lists the plugins to load, each
  with its options, in the order phases run them. A plugin without a section
  is not loaded. All of them are loaded when `Application` is built, before
  the database is opened.
- **Options.** The entry point, `__newsmerger_plugin__(**options)`, receives
  its section as keyword arguments, validates it with its own pydantic model
  (unknown keys rejected, defaults for the general case, so an empty section
  is enough), builds its objects and returns `(name, Protocol, object)`
  triples. The core never sees a plugin's models; it reports a
  `ValidationError` raised by an entry point as a configuration error with
  the options' path (`plugins.<plugin>.<option>`).
- **Objects.** Objects are built once and receive what each task needs as
  method arguments: providers the source and HTTP client, processors and
  remixers the database and the scope.
- **Names.** Object names are unique per type across plugins and are what
  sources, annotations, artifacts and the CLI refer to. Processors and
  remixers own their name, a class attribute, and are registered under it;
  providers' names exist only in their triples.
- **Methods.** Each protocol has a method of its own (`retrieve_items`,
  `enrich`, `remix`), named after the phase that calls it. foundation matches
  declared protocols with `issubclass()`, which compares method names only.
- **Bundles.** Bundles enable all their objects unless their options name
  some; this is a convention of the plugins, not a rule of the core. Bundles
  never import each other: they share data through annotations (`llm.embed`
  stores the vectors `grouping.embeddings` reads). Code used by a single
  bundle, such as clustering, lives in that bundle.
- **Pipelines.** Processor chains over one item stay outside the core, as
  scripts in `scripts/` built on `Application`.

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
  renaming an object from the configuration, but `requires` and the
  annotations other plugins read already fix every name in code.
- **A common `run` method.** `issubclass()` cannot tell protocols with the
  same methods apart, so remixers were loaded as processors and vice versa.
  A marker method per protocol would be noise, and registering against base
  classes instead of protocols would force inheritance.
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
  are a subset of another's is taken as its parent, which is only intended
  for `URLProvider` and `Provider`.
- `name` and `self` cannot be plugin options: they are `register()`'s own
  parameters.
- Grouping with embeddings needs `enrich` to have run `embed` first.
