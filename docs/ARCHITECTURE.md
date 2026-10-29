# Architecture

How the current code implements [SPECIFICATION.md](SPECIFICATION.md). The
behavior rules (identity, change detection, retries, dependencies) are
defined there and not repeated here.

```
config.yaml ─► Config ─► Application (app.py) ◄── cli.py, scripts/, external tools
                          │
        HTTPClient ◄──────┤ import
        (cached)          ▼
                     Provider ──► SourceItemData ──► SourceItem
                                                       │
                                                       ▼
                                          Database.upsert_source_items
                                           ├─ content ─► DiskStorage (content_dir)
                                           └─ row ─────► SQLite (source_items)
                                                       │
                     process                           ▼
                     Processor ◄── Database.get_unprocessed_items / get_content
                        └─► annotations + processing state
                     remix
                     Remixer ◄── items, annotations, other artifacts
                        └─► artifacts
                     deliver
                     Sink ◄── items, artifacts, the ledger
                        └─► outside world + deliveries (the ledger)
```

## Modules

| Module | Responsibility |
| :--- | :--- |
| `app.py` | `Application`, the single entry point: registers the plugin classes, resolves the configuration into a `Catalog`, wires config, HTTP cache and database, builds each profile's object on first use (`_object`), runs the phases one unit at a time, each on its workflow's sources (`import_source`, `run_process`, `run_remix`, `run_delivery`, `send_deliveries`; `sources()`, `process_keys()`, `remix_keys()` and `delivery_keys()` list a workflow's units in configuration order, `workflows` the workflows), answers queries and deletes. The database is private to it. `write_lock`, the exclusive lock every writing command takes. |
| `cli.py` | Click commands only: the phases (`import`, `process`, `remix`, and `run` for those plus delivery), each for one workflow (`-w`, default `default`), read-only `inspect items\|annotations\|artifacts\|content\|deliveries`, `delete items\|annotations\|artifacts\|deliveries`, `deliveries set-status\|send`; builds an `Application` per invocation, locked for the commands that write, and runs each unit through it with its own progress row. `inspect` and `delete` share their selection options, so `inspect` is `delete`'s dry run. Results go to stdout and progress and logs to stderr, each rich only when it is a terminal (`RICH_STDOUT_*`/`RICH_STDERR_*` from `foundation.clilib`); summaries print after the progress ends. Global logging options and the log handler come from `foundation.clilib` and `foundation.loglib`. |
| `catalog.py` | `Catalog`: the configuration resolved against the registered classes, at start-up. Every use becomes a `Profile` (class, validated options), every workflow's runs a `Run` (workflow, key, profile), with every check of decision 0010 (sections, ids, keys, what runs read, LLMs). Builds nothing. |
| `config.py` | Pydantic models for `config.yaml` (log level, `plugins` defaults per type, the catalog: `llms`, `sources`, `processors`, `remixers`, `sinks`; `workflows`, `cache`, `cache_dir`, `storage_dir`); `Config.all_workflows()` adds `default` (the sources without `skip_default`) and `Workflow.ledger_key` names a workflow's delivery records. `Duration`, a length of time as seconds or with a unit suffix (`5m`, `2h`, `3d`), parsed to seconds at load. `Config` is a pydantic-settings `BaseSettings`: `NEWSTOOL_*` variables, then a `.env` next to the config file, then the YAML, then the `ENV_ALIASES` variables (`OLLAMA_HOST`, `OLLAMA_API_KEY`), then defaults (`settings_customise_sources`). `ConfigPath`, a path relative to the config file's directory (the `LoadContext` of the load in progress); `storage_dir` holds `data.db` and `content/` (`database_uri`, `content_dir`). `${VAR}` expansion, in the YAML only, from the environment and a `.env` next to the config file, and the formatting of option errors with their config path. |
| `models.py` | Domain models: `SourceData` (a configured source), `SourceItemData` (provider output, validated), the DTOs `SourceItem`, `Annotation`, `Artifact` and `Delivery` (each with its database `id`), and `ProcessingScope` (`sources` holds a workflow's). |
| `httpclient.py` | `requests` session with browser headers and a `foundation` cache, which `get(url, use_cache=False)` skips. |
| `errors.py` | How failures reach the user: `PluginFailure`, the exception a plugin raises, with a message written for the user, when it cannot do its job in an expected way; `EXPECTED_ERRORS`, that and the failures of the network, the LLM backend and the database; `describe` (the message of a `PluginFailure`, `Type: message` for any other exception) and `log_failure` (error-level log; the traceback only with debug logging or when the exception is unexpected). |
| `db.py` | SQLAlchemy models and `Database`, the only code that touches SQLite or the content storage. |
| `providers.py` | The `Provider` and `ProviderType` protocols, `BaseProvider` and `IndexSiteProvider`, optional base classes. |
| `processors.py` | The `Processor` and `ProcessorType` protocols, `ProcessorOptions`, `BaseProcessor`, `SkipItem` and `RunSummary`. |
| `remixers.py` | The `Remixer` and `RemixerType` protocols and `BaseRemixer`. |
| `sinks.py` | The `Sink` and `SinkType` protocols, `BaseItemSink`, `BaseArtifactSink`, `DeliveryOptions` and `ArtifactDeliveryOptions`, and `SelectionRequiredError`. |
| `llms.py` | The `LLM` and `LLMType` protocols, `LLMUnavailableError` and `strip_code_fence`, for answers wrapped in a code fence. |
| `plugins/` | The plugin bundles: one module per site provider (`telegram_channel` included), `markdownify`, the `ollama` LLM, `summarize`, `tagger`, `embed`, `digest`, `grouping` (`singlelink`, `avglink`, `embeddings`), `feedgenerator`, `telegram` (the `telegram` and `telegram_artifacts` sinks) and `googlechat`. `PluginOptions`, `NoOptions`, `UsesLLMOptions`, `merge_options`, `PluginTypes`, `Services` and `ClassRegister` live in its `__init__`. |
| `scripts/` | The one-shot migrations `migrate_autoincrement.py`, `migrate_telegram_state.py` and `migrate_annotation_keys.sql`. |

## Plugins

Plugins register classes; the core builds one object per configured use
(decision 0010). The core knows only the protocols in `providers.py`,
`processors.py`, `remixers.py`, `sinks.py` and `llms.py`, never a plugin's
code:

1. `Application.__init__` registers every module of the `newstool.plugins`
   namespace with `ClassRegister.register_found()`. Each module's
   `__newstool_plugin__()` returns `[(type name, type Protocol, class),
   ...]`, declared under `ProviderType`, `ProcessorType`, `RemixerType`,
   `SinkType` or `LLMType`. `ClassRegister.classes(protocol)` indexes them
   by type name, checks that names are unique per protocol, that each is a
   class (an instance is a `PluginError`) and that it conforms
   (`isinstance(cls, protocol)`, else `ProtocolConformanceError`). A module
   that fails to import fails every command.
2. `Catalog` resolves the configuration (see *The catalog*): a `Profile`
   per use, with its options validated, and a `Run` per workflow unit. Every
   error is a `ConfigError` with its config path, before the database is
   opened.
3. A run builds its profile's object on first use, `cls(options,
   services)`, and keeps it for the other runs of the profile.

A type protocol declares `options_model` and `__call__(options, services)`;
`ProcessorType` adds `output_key(options)` and `required_key(options)`, and
`SinkType` `required_key(options)`, as class methods, so keys are worked
out without objects. An object keeps its options (`self.options`) and
receives what each task needs as method arguments: providers the source
and the `HTTPClient`, processors, remixers and sinks the `Database`, the
scope and the run's key. Each protocol has its own method
(`retrieve_items`, `process`, `remix`, `deliver`). Processors, remixers and
sinks own their name, a class attribute that records who wrote an
annotation; entry points register each class under it. Annotations and
processing state are keyed by the process run's key, artifacts by the
remix run's and deliveries by the delivery run's (see *Workflows*), never
by the type name, which is only their default.

`services` is what the core shares with objects: `services.llm(name)`
returns the LLM `name` refers to (an `llms` id or an LLM type; `None`, the
first `llms` entry), built on first use by `Application._llm`. Objects that
use one take `UsesLLMOptions` and ask for it in their constructor.

A bundle may register several classes per protocol under different names:
`grouping` registers its three remixers, `telegram` its two sinks.

### The catalog

`plugins.<type>` holds the defaults of a type's options for every use. It
builds nothing; `Catalog` checks its keys and each value against the
type's `options_model` (`check_section`), and rules across options when a
use is validated. The catalog lists the uses: `llms`, `sources`,
`processors`, `remixers` and `sinks`, each a type name or `{<type>, id,
key, options}`. A use's options are `merge_options(section, options)`,
merged key by key in nested mappings, any other value replacing, validated
with `options_model`. A rejected option is a `ConfigError` with its path
(`workflows.<name>.deliver.0.options.chat_id: Field required`).

An `id` lets workflows refer to a catalog entry; it cannot be a type's name
of its kind. A workflow entry is an id, a type name (the type with its
section's options: one profile per type), or an entry of the workflow's own
(no `id`, no `skip_default`). Every profile of the catalog is validated,
whether a workflow runs it or not.

## Workflows

`config.all_workflows()` returns `default`, with every source not marked
`skip_default`, then the `workflows` list. `Catalog` gives `default` the
catalog's processors and remixers without `skip_default`, in order, and no
deliveries; the other workflows resolve their entries. Each run is a `Run`
(workflow, key, profile, location), and every phase method restricts the
scope to its workflow's sources (`workflow_scope`, `ProcessingScope.sources`).

Identity follows ownership:

- Process runs are keyed `(workflow, key)`, one per key in a workflow. On
  shared sources, two processor types cannot write one key (each would see
  the other's `processor_version` and process every item again); the same
  type with other options gets a warning, since the first run to process an
  item writes it. Annotations and processing state are per `(item, key)`.
- Remix runs are keyed by their key, which belongs to one workflow, since
  an artifact belongs to no source. It is stored as the artifact's
  `remixer`.
- Delivery runs are keyed by `Workflow.ledger_key(key)`, `<workflow>/<key>`,
  stored as the delivery's `sink`. A key is unique within its workflow; `/`
  is not allowed in workflow names or keys.

Every key a process or delivery run reads (`required_key`) must be written
by a process run on its workflow's sources, in any workflow, so a workflow
may deliver what others process.

Bundles never import each other. `grouping.embeddings` reads the vectors
`embed` stores as `<input>_embedding` annotations, the same way every
grouping remixer reads `tags`.

## Providers

`Provider.retrieve_items(source, fetcher)` yields `SourceItemData`. Each
source builds its own provider object, with the source's options. Most
sites are `IndexSiteProvider`s, which take no options: fetch `index_url(source)` (the source's URL unless the provider
overrides it), `parse_index` it into article URLs, fetch each article and
`parse_item` it.

A source's `options` override its provider's plugin section (see *The
catalog*):

```yaml
sources:
  - id: some-blog
    provider: feedreader
    options:
      fetch_article: true   # overrides plugins.feedreader.fetch_article
```

An unknown or invalid option fails every command at start-up as a
configuration error (`sources.<id>.options.<option>`). The options live in
the configuration only, like `skip_default`; the database stores neither.

HTML providers keep the article's cleaned HTML rather than converting it:
`foundation.scrapelib.prune_to_spine` keeps the main node and its ancestors,
and `drop_selectors` removes known cruft (ads, related links). Converting
to other formats is a processor's job.

Every item carries `content: bytes` and a `mimetype` without parameters.
`SourceItemData` rejects `text/*` content that isn't UTF-8, so text is
always UTF-8 and no charset is stored.

### Writing a plugin

A plugin is a module in `newstool/plugins/` that exposes
`__newstool_plugin__() -> PluginTypes`, the classes it provides under
their type names, which are what `plugins:` sections, sources and entries
name. A provider for a site with an index page (a section, an RSS feed)
that links to one article per item (a plugin reports an expected failure,
such as a page without the expected structure or an empty LLM response, by
raising `PluginFailure` from `..errors` with a message for the user; any
other exception is unexpected and shows its traceback):

```python
import hashlib
from collections.abc import Iterator

import bs4
from foundation.scrapelib import drop_selectors, prune_to_spine

from ..httpclient import HTTPClient
from ..models import SourceData, SourceItemData
from ..providers import URI, IndexSiteProvider, ProviderType
from . import PluginTypes


class ExampleProvider(IndexSiteProvider):
    def index_url(self, source: SourceData) -> str:
        # Optional: defaults to the source's url.
        return str(source.url).rstrip("/") + "/feed/"

    def parse_index(
        self, content: bytes, source: SourceData, fetcher: HTTPClient
    ) -> Iterator[URI]:
        """Yield the article URLs found in the index page."""
        ...

    def parse_item(self, content: bytes) -> SourceItemData:
        """Build one item from an article page."""
        soup = bs4.BeautifulSoup(content.decode("utf-8"), features="html5lib")
        if (article := soup.select_one("article")) is None:
            raise ValueError("Article not found")
        drop_selectors(article, [".ads", ".related"])
        url = ...
        return SourceItemData(
            uid=hashlib.sha256(url.encode()).hexdigest(),
            title=...,
            uri=url,
            content=str(prune_to_spine(article)).encode("utf-8"),
            mimetype="text/html",
            published_at=...,  # optional
            modified_at=...,  # optional
            data={"author": ..., "image": ...},  # any JSON-compatible extras
        )


def __newstool_plugin__() -> PluginTypes:
    return [("example", ProviderType, ExampleProvider)]
```

`retrieve_items` fetches the index and each article; a `ValueError` from
`parse_item` is logged and that article is skipped, so raise it for pages
that aren't articles. For anything else (several items in one page, binary
files), subclass `BaseProvider` and implement
`retrieve_items(source, fetcher)` yourself, fetching with
`fetcher.get(url)`; `csjuntasgobierno` is an example, and `feedreader` and
`telegram_channel` ones with options (`self.options`).

A class with options sets `options_model` to a `PluginOptions` subclass
with defaults for the general case, so a use needs no options; its
constructor takes `(options, services)`. `feedgenerator` and `telegram` are
examples, `grouping` shows a bundle with several classes and `summarize` an
LLM consumer (`UsesLLMOptions`). Use `pydantic.SecretStr` for secrets, so
they never show in a `repr` or a traceback. Processors, remixers and sinks
usually subclass `BaseProcessor` (`process_item(db, item)`, plus `key` and
`requires` class attributes, options from `ProcessorOptions`),
`BaseRemixer` (`produce(db, scope)`) or `BaseItemSink`/`BaseArtifactSink`
(`send(db, subject)`), set `name` and `options_model` as class attributes
and are returned as `(cls.name, ProcessorType, cls)`.

Rules every provider follows:

- `uid` is deterministic and stable across runs (decision 0001). The
  sha256 of the canonical article URL is the usual choice.
- Keep the site's cleaned HTML; never convert it (that is `markdownify`'s
  job). Text content must be UTF-8 and `mimetype` must have no parameters.
- Only report dates the site gives you; missing ones take the import time.
- `parse_item` works on bytes only, so it can be tested offline: save
  sample pages in `tests/samples/` and add a case to
  `tests/test_providers.py`.

Add the plugin to the README's tables.

## Persistence

SQLite tables:

- `sources`: one row per configured source, keyed by its configured `id`.
- `source_items`: metadata of each item (`uid`, `uri`, `title`, `mimetype`,
  `content_sha256`, `data`, `published_at`, `modified_at`), unique per
  `(source_id, uid)`. `uri` is not unique.
- `processing_state`: per item and annotation key, the processor that ran,
  the status (`done`, `error`, `ignored`), attempts, processor version and
  the `content_sha256` the run used.
- `item_annotations`: per item and key, the processor that wrote it and the
  `content_sha256` of the value (e.g. `markdown`, `summary`, `summary/es`).
- `artifacts`: remixer outputs, unique per `(remixer, name)`, `remixer`
  being the remix entry's key, with the `content_sha256` of their content.
- `deliveries`: the ledger, one row per `(sink, subject)`, `sink` being the
  deliver entry's ledger key (see *Workflows*), the subject an
  item or an artifact (two nullable foreign keys, a `CHECK` that exactly
  one is set), with status, attempts, last error, the subject's
  `content_sha256` when delivered and an `external_ref` (JSON).

Every table with an integer id uses `AUTOINCREMENT`, so a deleted id is
never reused: the CLI selects items and annotations by id (decision 0008).
The DTOs carry it; `upsert_source_items` sets it on the items it saves.

SQLAlchemy models never leave `db.py`: `Database` takes and returns DTOs.
Every SQLite connection gets `SQLITE_PRAGMAS` from a SQLAlchemy `connect`
listener: foreign keys on, WAL, `busy_timeout`, `synchronous=NORMAL`,
in-memory temp store. newstool does not use `foundation.dblib`, which is a
shortcut for code that uses `sqlite3` directly. Item and artifact foreign
keys are `ON DELETE CASCADE`, so `delete_items` and `delete_artifacts`
only delete the subjects, then release their contents.
`Base.metadata.create_all` creates missing tables only; it never alters an
existing schema.

### Content storage

Item contents, annotation values (as JSON) and artifact contents are stored
outside SQLite, in one `foundation.storage.DiskStorage` in `content/` under `storage_dir`,
keyed by the sha256 of the bytes (decision 0004). The database is the only
record of which row uses which content.

- `SourceItem` and `Artifact` compute `content_sha256` when built with
  content. Items read back have `content=None`; processors load it with
  `Database.get_content(item)`.
- Content is written **before** the row that references it, so a crash
  leaves an unused file, never a row pointing at nothing.
- After the commit, replaced hashes that no row (item, annotation or
  artifact) references any more are deleted. Identical contents are stored
  once and shared.
- Two writers running at the same time could delete a content the other
  one has just started to reference. `write_lock` prevents it: every
  command that writes takes an exclusive `flock` on `<database>.lock` and
  fails at once if another process holds it (POSIX only).

### Change detection

`upsert_source_items` applies the compared fields with `DBSourceItem.update`,
then asks `session.is_modified()` whether anything changed; only then does it
touch `modified_at` (spec §4.1).

## Processors

The eligibility and retry rules are in spec §4.2; this is where they live:

- A workflow's process runs come from the catalog or its own entries: a
  processor, an optional `key` and its options. At start-up `Catalog`
  validates the options, asks the class for its `output_key(options)` when
  the entry names no key, and checks the keys (see *Workflows*).
  `run_process(key, workflow=...)` calls
  `processor.process(db, key=key, scope=..., force=...)`.
- `BaseProcessor.process_item(db, item)` returns the value of one
  annotation for one item, with its options in `self.options`.
  `Database.get_unprocessed_items(key, ...)` selects the eligible items
  (backoff in `backoff_seconds`, `max_retries` from `ProcessorOptions`,
  version in `version`). Raising `SkipItem` marks the item `ignored`; any
  other exception marks it `error`. `process()` returns a `RunSummary`
  (done, ignored, failed).
- `Database.record_result` saves a run's state and, when `done`, its
  annotation in one transaction, recording the item's `content_sha256`.
- `BaseProcessor.requires` (or `required_key(options)`, which `embed`
  overrides with its `input`) names the key the run reads;
  `require_annotation()` reads its value.
- Dependencies: `summarize` and `tagger` read `markdown`; `embed` reads
  `tags` or `markdown`.
- `Database.delete_annotations` removes annotations by id, each with the
  processing state of its (item, key), so their runs find the items
  pending. `delete annotations` passes what `find_annotations` selects.

## Remixers

`BaseRemixer.produce(db, scope, options)` yields `(name, content,
content_type)` for the whole scope, regenerated on each run and stored by
`remix(db, key=..., options=..., scope=...)` as an `Artifact` of the
entry's key, unique per `(key, name)`. Remixers read items, bulk annotations by key
(`Database.get_annotation_values`, one query for many items) and other
remixers' artifacts. The three `grouping` remixers share `GroupingRemixer`
and differ only in their clustering step: single-link and average-link over
tag overlap, and single-link over tag overlap blended with the cosine
similarity of the `embed` vectors (`embeddings`, which reads
`tags_embedding` or `markdown_embedding` and leaves out items without
one).

`digest` writes one markdown artifact per source in scope, named
`<source id>/<since>_<until>` (YYYY-MM-DD), so each period is delivered
once. It reads `markdown` of the newest `max_items` items
per source published since `since` (default: the last `lookback`), cuts each to
`max_article_chars`, sends them oldest first in one prompt with a
`context_length` window and prepends a `# <source name>: <since> – <until>`
title to the model's answer.

Remixers have no external side effects; that is the sinks' job.

## Sinks

Decision 0007. `BaseSink.deliver(db, key=..., options=..., scope,
artifacts, requeue, force)` runs one cycle over the ledger rows of `key`,
the entry's ledger key:

1. queue the candidates: `queue_item_deliveries` or
   `queue_artifact_deliveries` insert `queued` rows for the subjects in
   scope without one (by default, those of the last `lookback`; item
   sinks only take items whose run of their `requires` key finished);
2. read the sink's `queued`, `error` and `sending` rows with their subjects
   (`get_item_deliveries`, `get_artifact_deliveries`), in FIFO order; warn
   about `sending` ones, and pass `queued` ones and `error` ones with
   attempts left to `select(pending, now)`, which picks what is due, then
   to `pace`: with an `interval`, only the first one, once the key's last
   `done` delivery (`last_delivered_at`) is that old; then at most
   `max_per_run`;
3. for each selected row: save it `sending`, call `send(db, subject,
   options)`, then
   save it `done` with the returned `external_ref` and the subject's
   `content_sha256`, or `error` with one more attempt. Errors are logged
   with their traceback, so `send` raises without chaining secrets.

Every state change is a `Database.save_delivery(delivery)` in its own
transaction; eligibility and backoff (`backoff_seconds`, as processors) live
in the sinks. `BaseItemSink.select` keeps strict FIFO per source: a row
that is not due holds back the rest of its source. `requeue` turns the
`error` rows in scope back into `queued`; `force` needs an explicit
selection (`SelectionRequiredError`), gives the selected subjects a row and
sends them whatever their state, without pacing.
`Database.delete_deliveries` drops ledger rows (`delete deliveries`), so
their subjects can be queued again. Decision 0012: ledger rows are selected
by id (`Database.find_deliveries(delivery_ids=...)`);
`Application.set_delivery_status` rewrites the state of rows
(`deliveries set-status`), and `Application.send_deliveries` groups rows by
ledger key and calls `deliver(force=True)` once per key with the rows'
subjects (`deliveries send`).

A sink's options are a `DeliveryOptions` subclass (`interval`,
`max_per_run`, `max_retries`, `lookback`; `ArtifactDeliveryOptions` adds
`artifacts`, remix keys), and each use builds its own sink object: where
it delivers is an option. `telegram` bundles two sinks that post through
`post(bot_token, method, ...)`; each use's `bot_token` and `chat_id`
default to its type's section, which is optional. `item_image` picks
`sendPhoto` for items with an image, `item_url_text` and
`item_url_preview` set the article link's text and whether
`sendMessage` shows its preview, and `markdown` posts in Telegram's legacy
`Markdown`, the summary unescaped, instead of HTML. `TelegramSink` reads the annotation its
`summary` option names (its `required_key`) and
`TelegramArtifactSink` sends artifacts with `sendDocument`; both record
`{"chat_id", "message_id"}`, since a message id is only unique in its chat.
`googlechat` posts summarized items to the webhook of its entry as one
`cardsV2` card: the title and the annotation its `summary` option names (its
`required_key`) in a paragraph of Chat's HTML subset, the item's image under
`item_image`, and a button labelled `item_url_text`. Chat renders no image
from `blogger.googleusercontent.com`, so `chat_image_url` asks Blogger for
the full size and routes it through the `wsrv.nl` proxy. Request
errors are re-raised `from None` with their class only, since the URLs
embed the secrets.
