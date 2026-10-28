# Graph Report - integrate-branches  (2026-10-28)

## Corpus Check
- 72 files · ~123,030 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1566 nodes · 4501 edges · 73 communities (46 shown, 27 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 603 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c1f778b4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- Database
- DeliveryStatus
- ApplicationTests
- ConfigError
- Artifact
- Application
- .from_text
- newsmerger CLAUDE.md agent guidelines
- StubLLM
- DeleteCommandTests
- app_from_context
- PluginTypes
- invoke
- run_cmd
- LLMType
- BaseSink
- test_providers.py
- migrate_autoincrement.py
- catalog.py
- 0009: Workflows and keyed entries
- Any
- SourceItem
- migrate_telegram_state.py
- ProcessingScope
- SourceData
- .record_result
- markdownify.py
- PrensaIbericaPlainProvider
- CSJuntasGobiernoProvider
- RunSummary
- inspect_annotations_cmd
- inspect_deliveries_cmd
- group
- plugins
- RecordingItemSink
- model_validator
- ClassRegister
- db.py
- ADR 0007 Sinks and the delivery ledger
- grouping.py
- options
- hooks
- Services object (services.llm(name))
- GoogleChatSinkTests
- config.example.yaml
- Config
- cli.py
- .get_annotation_values
- MissingAnnotationError
- Delivery
- migrate_feed_names.py
- LogLevelTests
- .__init__
- Processor
- El Periódico Mediterráneo
- TestSourceItemDataContent
- get_section
- cli.py Click commands
- Services
- DigestRemixer
- Item
- config.py
- ADR 0002 Processing state lifecycle
- TestFeedReader
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- Artifact
- Grouping notes: NLP clustering pipeline
- news-aggregator
- foundation.plugin.Register plugin loading

## God Nodes (most connected - your core abstractions)
1. `Database` - 160 edges
2. `ProcessingScope` - 134 edges
3. `SourceItem` - 119 edges
4. `SourceData` - 82 edges
5. `Services` - 76 edges
6. `Artifact` - 62 edges
7. `Application` - 61 edges
8. `SourceItemData` - 54 edges
9. `HTTPClient` - 47 edges
10. `ApplicationTests` - 43 edges

## Surprising Connections (you probably didn't know these)
- `Decision` --references--> `Application`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/app.py
- `Decision` --references--> `LLMType`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/llms.py
- `Decision` --references--> `ClassRegister`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/plugins/__init__.py
- `Decision` --references--> `ProviderType`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/providers.py
- `Decision` --references--> `SinkType`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/sinks.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (73 total, 27 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.07
Nodes (13): DBSource, DBSourceItem, AnnotationTests, ConnectionTests, ContentStorageTests, DatabaseTestCase, DeleteTests, GetItemsTests (+5 more)

### Community 1 - "Database"
Cohesion: 0.13
Nodes (6): Database, tags_text(), SummarizeProcessor, merge_tags(), TaggerProcessor, BaseProcessor

### Community 2 - "DeliveryStatus"
Cohesion: 0.14
Nodes (4): DeliveryStatus, ArtifactNames, BaseArtifactSink, BaseItemSink

### Community 4 - "ConfigError"
Cohesion: 0.09
Nodes (6): Catalog, Kind, Profile, Run, share_sources(), ConfigError

### Community 5 - "Artifact"
Cohesion: 0.06
Nodes (14): DBArtifact, Artifact, post(), TelegramArtifactSink, TelegramError, ArtifactTests, MigrateFeedNamesTests, ArtifactSinkTests (+6 more)

### Community 6 - "Application"
Cohesion: 0.05
Nodes (5): Application, lookup(), workflow_scope(), Workflow, LLM

### Community 8 - "newsmerger CLAUDE.md agent guidelines"
Cohesion: 0.29
Nodes (6): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention, SQLAlchemy models never leave db.py; DTOs cross the boundary

### Community 9 - "StubLLM"
Cohesion: 0.14
Nodes (7): Processor, build(), EmbedTests, ProcessorTestCase, StubLLM, SummarizeTests, TaggerTests

### Community 11 - "app_from_context"
Cohesion: 0.14
Nodes (8): app_from_context(), cli(), delete_deliveries_cmd(), inspect_content_cmd(), match_snippet(), parse_artifact_ids(), process_cmd(), search_cmd()

### Community 12 - "PluginTypes"
Cohesion: 0.17
Nodes (14): __newsmerger_plugin__(), __newsmerger_plugin__(), entry_date(), find_image(), __newsmerger_plugin__(), parse_entry(), PluginTypes, __newsmerger_plugin__() (+6 more)

### Community 13 - "invoke"
Cohesion: 0.22
Nodes (3): annotation(), InspectCommandTests, invoke()

### Community 14 - "run_cmd"
Cohesion: 0.16
Nodes (7): import_cmd(), import_sources(), print_remix(), progress_rows(), remix_cmd(), run_cmd(), run_each()

### Community 15 - "LLMType"
Cohesion: 0.16
Nodes (6): LLMType, __newsmerger_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 17 - "test_providers.py"
Cohesion: 0.11
Nodes (12): Options, merge_options(), PluginOptions, Options, page_title(), parse_article(), parse_preview(), Post (+4 more)

### Community 18 - "migrate_autoincrement.py"
Cohesion: 0.12
Nodes (7): Base, DBItemAnnotation, main(), migrate(), needs_autoincrement(), recreate(), MigrateAutoincrementTests

### Community 19 - "catalog.py"
Cohesion: 0.09
Nodes (9): check_section(), ids_of(), in_default(), Use, DeliveryEntry, Entry, own_entries(), ProcessEntry (+1 more)

### Community 20 - "0009: Workflows and keyed entries"
Cohesion: 0.33
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 21 - "Any"
Cohesion: 0.15
Nodes (4): CustomJSON, DBProcessingState, _encode_value(), UTCDateTime

### Community 22 - "SourceItem"
Cohesion: 0.11
Nodes (5): SourceItem, FeedGeneratorRemixer, GoogleChatError, TelegramSink, SearchTests

### Community 23 - "migrate_telegram_state.py"
Cohesion: 0.14
Nodes (4): LockedError, write_lock(), main(), migrate()

### Community 24 - "ProcessingScope"
Cohesion: 0.16
Nodes (5): wrapper(), ProcessingScope, DeliveryTests, DigestRemixerTests, MigrateTelegramStateTests

### Community 25 - "SourceData"
Cohesion: 0.08
Nodes (20): HTTPClient, LazySourceItemData, SourceData, SourceItemData, CastellonInformacionProvider, discover_feed_url(), FeedReaderProvider, fetch_article() (+12 more)

### Community 27 - "markdownify.py"
Cohesion: 0.06
Nodes (18): 0010: Plugin classes and the configuration catalog, Consequences, Context, Rejected options, EmbedOptions, EmbedProcessor, MarkdownifyProcessor, __newsmerger_plugin__() (+10 more)

### Community 29 - "CSJuntasGobiernoProvider"
Cohesion: 0.20
Nodes (6): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, NoOptions, TestCSJuntasGobierno

### Community 30 - "RunSummary"
Cohesion: 0.19
Nodes (3): RunSummary, Sink, CommandTests

### Community 31 - "inspect_annotations_cmd"
Cohesion: 0.14
Nodes (12): annotation_options(), artifact_options(), check_found(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), delivery_options(), inspect_annotations_cmd() (+4 more)

### Community 32 - "inspect_deliveries_cmd"
Cohesion: 0.28
Nodes (4): inspect_artifacts_cmd(), inspect_deliveries_cmd(), inspect_items_cmd(), sort_option()

### Community 34 - "plugins"
Cohesion: 0.11
Nodes (18): lookback, title, url, api_base, api_key, chat_model, embed_model, plugins (+10 more)

### Community 35 - "RecordingItemSink"
Cohesion: 0.10
Nodes (4): SelectionRequiredError, ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 38 - "db.py"
Cohesion: 0.09
Nodes (11): ProcessingStatus, _sha256_column(), Annotation, __newsmerger_plugin__(), DocumentDeliveryOptions, ItemDeliveryOptions, __newsmerger_plugin__(), ArtifactDeliveryOptions (+3 more)

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.18
Nodes (14): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0005 Remixers with external side effects, ADR 0006 LLM plugins (+6 more)

### Community 40 - "grouping.py"
Cohesion: 0.06
Nodes (26): Duration, average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer (+18 more)

### Community 41 - "options"
Cohesion: 0.11
Nodes (20): options, sink, artifacts, chat_id, interval, item_image, item_url_preview, item_url_text (+12 more)

### Community 42 - "hooks"
Cohesion: 0.15
Nodes (12): exclude, args, entry, files, id, language, name, pass_filenames (+4 more)

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "GoogleChatSinkTests"
Cohesion: 0.08
Nodes (11): build_card(), chat_image_url(), GoogleChatSink, WebhookOptions, build_caption(), card_widgets(), ChatImageUrlTests, GoogleChatSinkTests (+3 more)

### Community 45 - "config.example.yaml"
Cohesion: 0.11
Nodes (15): cache, expiration, llms, input, processors, options, processor, remixers (+7 more)

### Community 47 - "cli.py"
Cohesion: 0.10
Nodes (12): format_value(), json_default(), lexer_for(), preview(), print_content(), print_deliver(), print_import(), print_item() (+4 more)

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 57 - "get_section"
Cohesion: 0.29
Nodes (3): get_section(), parse_datetime(), SectionNotFoundError

### Community 58 - "cli.py Click commands"
Cohesion: 0.20
Nodes (12): BaseSink deliver cycle (queue, select, send), cli.py Click commands, Database (db.py, only SQLite/storage access), deliveries table (the ledger), foundation.storage.DiskStorage content-addressed storage, foundation internal library, Strict FIFO per source, inspect items|annotations|artifacts|deliveries (+4 more)

### Community 59 - "Services"
Cohesion: 0.08
Nodes (19): Decision, LLMUnavailableError, strip_code_fence(), DigestOptions, __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), Options (+11 more)

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 63 - "config.py"
Cohesion: 0.12
Nodes (6): CacheConfig, DatabaseConfig, expand_variables(), MissingVariableError, options_error(), parse_duration()

### Community 73 - "foundation.plugin.Register plugin loading"
Cohesion: 0.50
Nodes (4): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)`, `P1: plain logging and <APP>_LOG_LEVEL fix` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 458 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_db.py`, `DeliveryStatus`, `Artifact`, `Application`, `StubLLM`, `DeleteCommandTests`, `BaseSink`, `migrate_autoincrement.py`, `Any`, `SourceItem`, `migrate_telegram_state.py`, `ProcessingScope`, `SourceData`, `.record_result`, `markdownify.py`, `RunSummary`, `RecordingItemSink`, `ClassRegister`, `db.py`, `grouping.py`, `GoogleChatSinkTests`, `.get_annotation_values`, `Delivery`, `.__init__`, `Services`, `DigestRemixer`, `.session_scope`?**
  _High betweenness centrality (0.174) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 43 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `External pipelines (scripts/pipeline_url.py)`, `Annotation` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06918918918918919 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `ProcessingScope` to `test_db.py`, `Database`, `DeliveryStatus`, `ApplicationTests`, `Application`, `StubLLM`, `DeleteCommandTests`, `app_from_context`, `invoke`, `run_cmd`, `BaseSink`, `SourceItem`, `migrate_telegram_state.py`, `markdownify.py`, `RunSummary`, `inspect_annotations_cmd`, `inspect_deliveries_cmd`, `RecordingItemSink`, `db.py`, `grouping.py`, `GoogleChatSinkTests`, `cli.py`, `Delivery`, `Services`, `DigestRemixer`, `.session_scope`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Should `Database` be split into smaller, more focused modules?**
  _Cohesion score 0.13230769230769232 - nodes in this community are weakly interconnected._