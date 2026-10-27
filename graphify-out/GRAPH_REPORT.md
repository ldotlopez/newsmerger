# Graph Report - newsmerger  (2026-10-27)

## Corpus Check
- 68 files · ~120,018 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .lock 1)

## Summary
- 1457 nodes · 4302 edges · 79 communities (47 shown, 32 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 584 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a56bb6f9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- make_item
- test_app.py
- test_cli.py
- ApplicationTests
- TelegramSinkTests
- Application
- migrate_autoincrement.py
- FeedGeneratorRemixer
- LockedError
- DeleteCommandTests
- app_from_context
- ProcessingTests
- ProcessingScope
- Services
- .select
- Sink Delivery Cycle
- Telegram Channel Parsing
- DeliveryStatus
- DeliveryTests
- run_cmd
- db.py
- test_db.py
- Database
- SourceData
- BaseProcessor
- Markdownify Processor
- Prensa Iberica Plain Provider
- Inspect/Delete CLI Decision
- TestFeedReader
- PluginOptions
- CSJuntasGobiernoProvider
- feedreader.py
- AnnotationTests
- DatabaseTestCase
- .close
- .queue_item_deliveries
- migrate_autoincrement.py
- Architecture & Processing ADRs
- db.py
- Selection CLI Options
- telegram_channel.py
- Processor & Remixer Bundles
- ollama.py
- Plugin System Docs
- telegram.py
- Provider
- SourceItem
- expand_variables
- .__init__
- inspect_annotations_cmd
- single_link_groups
- inspect_artifacts_cmd
- Spec Glossary Entities
- Sample Pages & Formats
- config.py
- PluginOptions
- Agent Conventions
- migrate_feed_names.py
- Side-Effect Remixers ADR
- Item Identity ADR
- .send
- .get_artifact
- RecordingArtifactSink
- GetItemsTests
- .__init__
- Example Sources
- Artifact & Remixer
- Grouping Notes
- News Aggregator
- LogLevelTests
- TelegramArtifactSink
- MigrateAutoincrementTests
- __newsmerger_plugin__
- _sha256_column
- ADR 0002 Processing state lifecycle

## God Nodes (most connected - your core abstractions)
1. `Database` - 161 edges
2. `ProcessingScope` - 142 edges
3. `SourceItem` - 119 edges
4. `SourceData` - 81 edges
5. `Artifact` - 62 edges
6. `Services` - 61 edges
7. `Application` - 59 edges
8. `SourceItemData` - 49 edges
9. `PluginOptions` - 49 edges
10. `ApplicationTests` - 49 edges

## Surprising Connections (you probably didn't know these)
- `newsmerger README` --references--> `Phases: import, enrich, remix, deliver`  [INFERRED]
  README.md → docs/SPECIFICATION.md
- `main()` --uses--> `LockedError`  [INFERRED]
  scripts/migrate_autoincrement.py → newsmerger/app.py
- `main()` --uses--> `LockedError`  [INFERRED]
  scripts/migrate_feed_names.py → newsmerger/app.py
- `ApplicationTests` --uses--> `LockedError`  [INFERRED]
  tests/test_app.py → newsmerger/app.py
- `ApplicationTests` --uses--> `Application`  [INFERRED]
  tests/test_app.py → newsmerger/app.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (79 total, 32 thin omitted)

### Community 0 - "make_item"
Cohesion: 0.24
Nodes (4): ContentStorageTests, make_item(), make_source(), UpsertSourceItemsTests

### Community 2 - "test_app.py"
Cohesion: 0.08
Nodes (13): LLM, LLMUnavailableError, strip_code_fence(), __newsmerger_plugin__(), __newsmerger_plugin__(), Services, __newsmerger_plugin__(), __newsmerger_plugin__() (+5 more)

### Community 5 - "TelegramSinkTests"
Cohesion: 0.27
Nodes (5): Options, TelegramSink, ok_response(), TelegramSinkTests, TelegramTestCase

### Community 7 - "migrate_autoincrement.py"
Cohesion: 0.17
Nodes (4): main(), migrate(), needs_autoincrement(), recreate()

### Community 8 - "FeedGeneratorRemixer"
Cohesion: 0.16
Nodes (9): discover_feed_url(), entry_date(), FeedReaderProvider, fetch_feed(), find_image(), __newsmerger_plugin__(), Options, parse_entry() (+1 more)

### Community 9 - "LockedError"
Cohesion: 0.17
Nodes (3): LockedError, write_lock(), main()

### Community 11 - "app_from_context"
Cohesion: 0.16
Nodes (9): app_from_context(), cli(), deliver_cmd(), inspect_content_cmd(), inspect_deliveries_cmd(), parse_artifact_ids(), process_cmd(), resolve_cmd() (+1 more)

### Community 13 - "ProcessingScope"
Cohesion: 0.06
Nodes (14): workflow_scope(), wrapper(), ConfigError, ProcessingScope, DigestOptions, DigestRemixer, Options, RunSummary (+6 more)

### Community 14 - "Services"
Cohesion: 0.15
Nodes (8): import_cmd(), import_sources(), print_import(), print_remix(), progress_rows(), remix_cmd(), run_cmd(), run_each()

### Community 15 - ".select"
Cohesion: 0.11
Nodes (10): delivery_runs(), entry_location(), load_plugins(), objects_by_name(), process_runs(), remix_runs(), Run, source_options() (+2 more)

### Community 17 - "Telegram Channel Parsing"
Cohesion: 0.11
Nodes (12): CSJuntasGobiernoProvider, __newsmerger_plugin__(), Options, page_title(), parse_article(), parse_preview(), Post, preview_url() (+4 more)

### Community 18 - "DeliveryStatus"
Cohesion: 0.12
Nodes (4): DeliveryStatus, BaseArtifactSink, BaseItemSink, migrate()

### Community 20 - "run_cmd"
Cohesion: 0.12
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 21 - "db.py"
Cohesion: 0.12
Nodes (4): backoff_seconds(), CustomJSON, _encode_value(), UTCDateTime

### Community 22 - "test_db.py"
Cohesion: 0.10
Nodes (6): Base, DBItemAnnotation, DBProcessingState, DBSource, DBSourceItem, ConnectionTests

### Community 25 - "SourceData"
Cohesion: 0.08
Nodes (11): HTTPClient, SourceData, CastellonInformacionProvider, __newsmerger_plugin__(), fetch_article(), __newsmerger_plugin__(), PlazaProvider, is_home_page() (+3 more)

### Community 26 - "BaseProcessor"
Cohesion: 0.09
Nodes (3): merge_options(), BaseProcessor, MissingAnnotationError

### Community 27 - "Markdownify Processor"
Cohesion: 0.18
Nodes (5): MarkdownifyProcessor, __newsmerger_plugin__(), SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 28 - "Prensa Iberica Plain Provider"
Cohesion: 0.15
Nodes (3): _extract_href(), __newsmerger_plugin__(), PrensaIbericaPlainProvider

### Community 29 - "Inspect/Delete CLI Decision"
Cohesion: 0.23
Nodes (10): cli.py Click commands, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage, SQLAlchemy models never leave db.py; DTOs cross the boundary, foundation internal library, inspect items|annotations|artifacts|deliveries, Application class (single entry point), Phases: import, enrich, remix, deliver (+2 more)

### Community 30 - "TestFeedReader"
Cohesion: 0.13
Nodes (4): DBArtifact, Artifact, ArtifactTests, MigrateTelegramStateTests

### Community 31 - "PluginOptions"
Cohesion: 0.10
Nodes (6): __newsmerger_plugin__(), NoOptions, PluginOptions, Options, __newsmerger_plugin__(), __newsmerger_plugin__()

### Community 32 - "CSJuntasGobiernoProvider"
Cohesion: 0.33
Nodes (3): find_parent_by_tag_name(), get_date_from_text(), PreparseData

### Community 33 - "feedreader.py"
Cohesion: 0.18
Nodes (5): __newsmerger_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 35 - "DatabaseTestCase"
Cohesion: 0.31
Nodes (3): DatabaseTestCase, DeleteTests, IdentityTests

### Community 36 - ".close"
Cohesion: 0.24
Nodes (4): SelectionRequiredError, ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 37 - ".queue_item_deliveries"
Cohesion: 0.19
Nodes (6): check_found(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), require_selection(), sort_option()

### Community 38 - "migrate_autoincrement.py"
Cohesion: 0.08
Nodes (7): CacheConfig, DatabaseConfig, DeliveryEntry, expand_variables(), MissingVariableError, ProcessEntry, RemixEntry

### Community 39 - "Architecture & Processing ADRs"
Cohesion: 0.23
Nodes (12): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger, deliver SINK --force with explicit selection (+4 more)

### Community 40 - "db.py"
Cohesion: 0.05
Nodes (29): FeedGeneratorRemixer, Options, average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions (+21 more)

### Community 41 - "Selection CLI Options"
Cohesion: 0.21
Nodes (7): annotation_options(), artifact_options(), inspect_annotations_cmd(), inspect_artifacts_cmd(), report_user_errors(), wrapper(), scope_options()

### Community 43 - "Processor & Remixer Bundles"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "ollama.py"
Cohesion: 0.08
Nodes (16): EmbedOptions, EmbedProcessor, Options, tags_text(), Options, SummarizeOptions, SummarizeProcessor, merge_tags() (+8 more)

### Community 45 - "Plugin System Docs"
Cohesion: 0.25
Nodes (5): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), ollama LLM backend, plugins configuration section

### Community 46 - "telegram.py"
Cohesion: 0.12
Nodes (10): build_text(), build_caption(), DocumentDeliveryOptions, ItemDeliveryOptions, __newsmerger_plugin__(), ArtifactDeliveryOptions, DeliveryOptions, Sink (+2 more)

### Community 47 - "Provider"
Cohesion: 0.25
Nodes (5): inspect_items_cmd(), print_deliver(), print_item(), print_process(), print_table()

### Community 48 - "SourceItem"
Cohesion: 0.12
Nodes (5): ProcessingStatus, Annotation, SourceItem, Remixer, make_item()

### Community 49 - "expand_variables"
Cohesion: 0.10
Nodes (8): GoogleChatError, GoogleChatSink, image_card(), __newsmerger_plugin__(), Options, WebhookOptions, GoogleChatSinkTests, OptionsTests

### Community 50 - ".__init__"
Cohesion: 0.22
Nodes (4): SourceItemData, PrensaIbericaProvider, TestPrensaIberica, TestSourceItemDataContent

### Community 51 - "inspect_annotations_cmd"
Cohesion: 0.10
Nodes (6): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content()

### Community 53 - "inspect_artifacts_cmd"
Cohesion: 0.27
Nodes (5): format_value(), json_default(), preview(), print_json(), setup_logging()

### Community 54 - "Spec Glossary Entities"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "Sample Pages & Formats"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 57 - "PluginOptions"
Cohesion: 0.29
Nodes (3): get_section(), parse_datetime(), SectionNotFoundError

### Community 58 - "Agent Conventions"
Cohesion: 0.33
Nodes (5): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention

### Community 60 - "Side-Effect Remixers ADR"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 61 - "Item Identity ADR"
Cohesion: 0.40
Nodes (4): IndexSiteProvider / URLProvider, ADR 0001 Item identity and change detection, Item, Provider

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)`, `PluginOptions (pydantic, unknown keys rejected)`, `Annotation` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 418 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `make_item`, `Services`, `test_app.py`, `TelegramSinkTests`, `Application`, `LockedError`, `DeleteCommandTests`, `ProcessingScope`, `.select`, `Sink Delivery Cycle`, `DeliveryStatus`, `run_cmd`, `db.py`, `test_db.py`, `SourceData`, `BaseProcessor`, `Markdownify Processor`, `TestFeedReader`, `DatabaseTestCase`, `.close`, `db.py`, `ollama.py`, `telegram.py`, `SourceItem`, `expand_variables`, `config.py`, `.send`, `.get_artifact`, `RecordingArtifactSink`, `.__init__`, `TelegramArtifactSink`, `MigrateAutoincrementTests`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Are the 44 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 44 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08208020050125313 - nodes in this community are weakly interconnected._
- **Why does `SourceData` connect `SourceData` to `make_item`, `test_app.py`, `TelegramSinkTests`, `Application`, `FeedGeneratorRemixer`, `ProcessingScope`, `.select`, `Telegram Channel Parsing`, `test_db.py`, `Database`, `Markdownify Processor`, `Prensa Iberica Plain Provider`, `PluginOptions`, `.close`, `migrate_autoincrement.py`, `telegram_channel.py`, `SourceItem`, `.__init__`, `single_link_groups`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_cli.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14624505928853754 - nodes in this community are weakly interconnected._