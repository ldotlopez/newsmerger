# Graph Report - plugin-catalog  (2026-10-28)

## Corpus Check
- 72 files · ~121,853 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1541 nodes · 4435 edges · 72 communities (51 shown, 21 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 591 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5c865668`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- BaseProcessor
- Services
- ApplicationTests
- plugins/__init__.py
- TelegramSinkTests
- Application
- migrate_telegram_state.py
- TestFeedReader
- config.py
- DeleteCommandTests
- app_from_context
- PluginTypes
- RunSummary
- process_cmd
- models.py
- BaseSink
- TelegramChannelProvider
- ConfigError
- catalog.py
- 0009: Workflows and keyed entries
- Any
- SourceItem
- Database
- ProcessingScope
- HTTPClient
- telegram.py
- markdownify.py
- PrensaIbericaPlainProvider
- deliveries table (the ledger)
- DeliveryStatus
- delete_items_cmd
- CSJuntasGobiernoProvider
- Catalog
- plugins
- SourceData
- Config
- report_user_errors
- model_validator
- ADR 0007 Sinks and the delivery ledger
- ScoredItem
- options
- hooks
- Services object (services.llm(name))
- .process_item
- config.example.yaml
- SourceItemData
- inspect_items_cmd
- db.py
- GoogleChatSinkTests
- TestSourceItemDataContent
- cli.py
- LogLevelTests
- .send
- Processor
- El Periódico Mediterráneo
- Artifact
- get_section
- Database (db.py, only SQLite/storage access)
- foundation internal library
- 0010: Plugin classes and the configuration catalog
- Item
- DigestRemixer
- ClassRegisterTests
- .process_item
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- Artifact
- Grouping notes: NLP clustering pipeline
- news-aggregator
- ADR 0002 Processing state lifecycle

## God Nodes (most connected - your core abstractions)
1. `Database` - 158 edges
2. `ProcessingScope` - 138 edges
3. `SourceItem` - 119 edges
4. `SourceData` - 82 edges
5. `Services` - 75 edges
6. `Artifact` - 62 edges
7. `Application` - 60 edges
8. `SourceItemData` - 51 edges
9. `HTTPClient` - 46 edges
10. `ApplicationTests` - 42 edges

## Surprising Connections (you probably didn't know these)
- `Decision` --references--> `Application`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/app.py
- `Decision` --references--> `UsesLLMOptions`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/plugins/__init__.py
- `Decision` --references--> `Services`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/plugins/__init__.py
- `Decision` --references--> `ProcessorType`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/processors.py
- `Decision` --references--> `ProviderType`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/providers.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (72 total, 21 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.07
Nodes (13): DBSourceItem, AnnotationTests, ArtifactTests, ConnectionTests, ContentStorageTests, DatabaseTestCase, DeleteTests, GetItemsTests (+5 more)

### Community 1 - "BaseProcessor"
Cohesion: 0.13
Nodes (3): SummarizeProcessor, BaseProcessor, MissingAnnotationError

### Community 2 - "Services"
Cohesion: 0.06
Nodes (22): LLMUnavailableError, strip_code_fence(), DigestOptions, __newsmerger_plugin__(), EmbedOptions, EmbedProcessor, __newsmerger_plugin__(), Services (+14 more)

### Community 4 - "plugins/__init__.py"
Cohesion: 0.09
Nodes (9): Decision, LLM, LLMType, ClassRegister, __newsmerger_plugin__(), ollama_client(), OllamaLLM, Options (+1 more)

### Community 5 - "TelegramSinkTests"
Cohesion: 0.10
Nodes (11): merge_options(), post(), TelegramArtifactSink, TelegramError, TelegramSink, item_options(), ok_response(), PluginTests (+3 more)

### Community 7 - "migrate_telegram_state.py"
Cohesion: 0.06
Nodes (13): LockedError, write_lock(), Base, DBItemAnnotation, main(), migrate(), needs_autoincrement(), recreate() (+5 more)

### Community 8 - "TestFeedReader"
Cohesion: 0.19
Nodes (7): discover_feed_url(), entry_date(), FeedReaderProvider, fetch_feed(), find_image(), parse_entry(), TestFeedReader

### Community 9 - "config.py"
Cohesion: 0.18
Nodes (4): CacheConfig, DatabaseConfig, expand_variables(), MissingVariableError

### Community 11 - "app_from_context"
Cohesion: 0.15
Nodes (9): app_from_context(), cli(), deliver_cmd(), inspect_content_cmd(), inspect_deliveries_cmd(), parse_artifact_ids(), remix_cmd(), resolve_cmd() (+1 more)

### Community 12 - "PluginTypes"
Cohesion: 0.20
Nodes (12): __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), Options, PluginTypes, __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__() (+4 more)

### Community 13 - "RunSummary"
Cohesion: 0.07
Nodes (11): RunSummary, SelectionRequiredError, annotation(), CommandTests, InspectCommandTests, invoke(), ArtifactSinkTests, ItemSinkTests (+3 more)

### Community 14 - "process_cmd"
Cohesion: 0.15
Nodes (8): import_cmd(), import_sources(), print_import(), print_process(), process_cmd(), progress_rows(), run_cmd(), run_each()

### Community 15 - "models.py"
Cohesion: 0.13
Nodes (8): ItemKey, __newsmerger_plugin__(), Options, __newsmerger_plugin__(), NoOptions, PluginOptions, RemixerType, GroupingPluginTests

### Community 17 - "TelegramChannelProvider"
Cohesion: 0.13
Nodes (9): is_home_page(), page_title(), parse_article(), parse_preview(), Post, preview_url(), TelegramChannelProvider, read_sample() (+1 more)

### Community 18 - "ConfigError"
Cohesion: 0.10
Nodes (5): lookup(), check_section(), Run, share_sources(), ConfigError

### Community 19 - "catalog.py"
Cohesion: 0.11
Nodes (8): ids_of(), in_default(), Kind, Use, DeliveryEntry, Entry, ProcessEntry, RemixEntry

### Community 20 - "0009: Workflows and keyed entries"
Cohesion: 0.33
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 21 - "Any"
Cohesion: 0.12
Nodes (4): _configure_sqlite_connection(), CustomJSON, _encode_value(), UTCDateTime

### Community 22 - "SourceItem"
Cohesion: 0.18
Nodes (3): SourceItem, FeedGeneratorRemixer, SearchTests

### Community 23 - "Database"
Cohesion: 0.07
Nodes (3): backoff_seconds(), Database, DBProcessingState

### Community 24 - "ProcessingScope"
Cohesion: 0.14
Nodes (5): ProcessingScope, Remixer, Sink, DeliveryTests, DigestRemixerTests

### Community 25 - "HTTPClient"
Cohesion: 0.17
Nodes (8): HTTPClient, CastellonInformacionProvider, fetch_article(), PlazaProvider, TheGuardianProvider, IndexSiteProvider, URI, TestHTTPClient

### Community 26 - "telegram.py"
Cohesion: 0.15
Nodes (10): build_text(), __newsmerger_plugin__(), build_caption(), DocumentDeliveryOptions, ItemDeliveryOptions, __newsmerger_plugin__(), ArtifactDeliveryOptions, DeliveryOptions (+2 more)

### Community 27 - "markdownify.py"
Cohesion: 0.22
Nodes (4): MarkdownifyProcessor, SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 29 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 30 - "DeliveryStatus"
Cohesion: 0.09
Nodes (6): DBDelivery, DeliveryStatus, Delivery, BaseArtifactSink, BaseItemSink, migrate()

### Community 31 - "delete_items_cmd"
Cohesion: 0.19
Nodes (6): check_found(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), require_selection(), sort_option()

### Community 32 - "CSJuntasGobiernoProvider"
Cohesion: 0.25
Nodes (5): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, TestCSJuntasGobierno

### Community 33 - "Catalog"
Cohesion: 0.15
Nodes (3): Catalog, Profile, options_error()

### Community 34 - "plugins"
Cohesion: 0.11
Nodes (18): days, title, url, api_base, api_key, chat_model, embed_model, plugins (+10 more)

### Community 35 - "SourceData"
Cohesion: 0.15
Nodes (4): DBSource, SourceData, BaseProvider, Provider

### Community 37 - "report_user_errors"
Cohesion: 0.23
Nodes (7): annotation_options(), artifact_options(), inspect_annotations_cmd(), report_user_errors(), wrapper(), scope_options(), wrapper()

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.21
Nodes (14): Architecture, cli.py Click commands, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger (+6 more)

### Community 40 - "ScoredItem"
Cohesion: 0.06
Nodes (24): average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer, GroupingOptions (+16 more)

### Community 41 - "options"
Cohesion: 0.11
Nodes (19): options, sink, artifacts, chat_id, interval, item_image, item_url_preview, item_url_text (+11 more)

### Community 42 - "hooks"
Cohesion: 0.15
Nodes (12): exclude, args, entry, files, id, language, name, pass_filenames (+4 more)

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 45 - "config.example.yaml"
Cohesion: 0.11
Nodes (15): cache, expiration, llms, input, processors, options, processor, remixers (+7 more)

### Community 46 - "SourceItemData"
Cohesion: 0.25
Nodes (3): SourceItemData, PrensaIbericaProvider, TestPrensaIberica

### Community 47 - "inspect_items_cmd"
Cohesion: 0.12
Nodes (11): format_value(), inspect_artifacts_cmd(), inspect_items_cmd(), json_default(), preview(), print_deliver(), print_item(), print_json() (+3 more)

### Community 48 - "db.py"
Cohesion: 0.15
Nodes (3): ProcessingStatus, _sha256_column(), Annotation

### Community 49 - "GoogleChatSinkTests"
Cohesion: 0.05
Nodes (12): GoogleChatSink, WebhookOptions, Processor, GoogleChatSinkTests, OptionsTests, webhook_options(), build(), EmbedTests (+4 more)

### Community 51 - "cli.py"
Cohesion: 0.11
Nodes (6): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content()

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 56 - "Artifact"
Cohesion: 0.11
Nodes (5): DBArtifact, Artifact, BaseRemixer, MigrateFeedNamesTests, MigrateTelegramStateTests

### Community 57 - "get_section"
Cohesion: 0.29
Nodes (3): get_section(), parse_datetime(), SectionNotFoundError

### Community 58 - "Database (db.py, only SQLite/storage access)"
Cohesion: 0.17
Nodes (11): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention, AUTOINCREMENT integer ids, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage (+3 more)

### Community 59 - "foundation internal library"
Cohesion: 0.29
Nodes (7): foundation internal library, foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section, P1: plain logging and <APP>_LOG_LEVEL fix, P2: rich progress per stream (RICH_STDOUT_*/RICH_STDERR_*)

### Community 60 - "0010: Plugin classes and the configuration catalog"
Cohesion: 0.40
Nodes (4): 0010: Plugin classes and the configuration catalog, Consequences, Context, Rejected options

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 453 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_db.py`, `BaseProcessor`, `Services`, `TelegramSinkTests`, `Application`, `migrate_telegram_state.py`, `DeleteCommandTests`, `RunSummary`, `models.py`, `BaseSink`, `Any`, `SourceItem`, `ProcessingScope`, `telegram.py`, `markdownify.py`, `DeliveryStatus`, `SourceData`, `Config`, `ScoredItem`, `.process_item`, `db.py`, `GoogleChatSinkTests`, `.send`, `Artifact`, `DigestRemixer`, `.get_stored_content`, `.process_item`?**
  _High betweenness centrality (0.167) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 43 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06882882882882883 - nodes in this community are weakly interconnected._
- **Why does `SourceItem` connect `SourceItem` to `test_db.py`, `BaseProcessor`, `Services`, `ApplicationTests`, `plugins/__init__.py`, `TelegramSinkTests`, `Application`, `migrate_telegram_state.py`, `DeleteCommandTests`, `RunSummary`, `models.py`, `BaseSink`, `Database`, `ProcessingScope`, `telegram.py`, `markdownify.py`, `DeliveryStatus`, `SourceData`, `ScoredItem`, `.process_item`, `inspect_items_cmd`, `db.py`, `GoogleChatSinkTests`, `cli.py`, `.send`, `DigestRemixer`, `.process_item`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Are the 38 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Should `BaseProcessor` be split into smaller, more focused modules?**
  _Cohesion score 0.13157894736842105 - nodes in this community are weakly interconnected._