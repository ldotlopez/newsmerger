# Graph Report - newsmerger  (2026-10-27)

## Corpus Check
- 67 files · ~112,365 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 2, .bak-before-enrich 1, .lock 1)

## Summary
- 1362 nodes · 3966 edges · 74 communities (49 shown, 25 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 539 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3c43c289`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ORM Models & Ledger Rows
- Services
- test_app.py
- test_cli.py
- ApplicationTests
- ScoredItem
- Application
- .close
- FeedGeneratorRemixer
- GroupingTests
- DeleteCommandTests
- app_from_context
- ProcessingScope
- Artifact
- Services
- .select
- Sink Delivery Cycle
- Telegram Channel Parsing
- group
- Database
- run_cmd
- db.py
- .from_text
- SourceItem
- SourceData
- SourceData
- .require_annotation
- Markdownify Processor
- Prensa Iberica Plain Provider
- Inspect/Delete CLI Decision
- TestFeedReader
- PluginOptions
- CSJuntasGobiernoProvider
- feedreader.py
- ConfigError
- DigestRemixerTests
- .close
- .queue_item_deliveries
- migrate_autoincrement.py
- Architecture & Processing ADRs
- db.py
- Selection CLI Options
- delete_items_cmd
- Processor & Remixer Bundles
- ollama.py
- Plugin System Docs
- Provider
- .get_annotation_values
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
- Options
- Side-Effect Remixers ADR
- Item Identity ADR
- test_telegram.py
- LLM
- Item Data Validation Tests
- GroupingTests
- Example Sources
- Artifact & Remixer
- Grouping Notes
- News Aggregator
- SelectionRequiredError
- ADR 0002 Processing state lifecycle

## God Nodes (most connected - your core abstractions)
1. `Database` - 163 edges
2. `ProcessingScope` - 141 edges
3. `SourceItem` - 120 edges
4. `SourceData` - 81 edges
5. `Artifact` - 62 edges
6. `Services` - 61 edges
7. `Application` - 56 edges
8. `SourceItemData` - 49 edges
9. `HTTPClient` - 44 edges
10. `ApplicationTests` - 42 edges

## Surprising Connections (you probably didn't know these)
- `newsmerger README` --references--> `Phases: import, enrich, remix, deliver`  [INFERRED]
  README.md → docs/SPECIFICATION.md
- `ApplicationTests` --uses--> `LockedError`  [INFERRED]
  tests/test_app.py → newsmerger/app.py
- `ApplicationTests` --uses--> `Application`  [INFERRED]
  tests/test_app.py → newsmerger/app.py
- `invoke()` --indirect_call--> `cli()`  [INFERRED]
  tests/test_cli.py → newsmerger/cli.py
- `ApplicationTests` --uses--> `ConfigError`  [INFERRED]
  tests/test_app.py → newsmerger/config.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (74 total, 25 thin omitted)

### Community 0 - "ORM Models & Ledger Rows"
Cohesion: 0.06
Nodes (15): DBDelivery, DBProcessingState, DBSourceItem, AnnotationTests, ConnectionTests, ContentStorageTests, DatabaseTestCase, DeleteTests (+7 more)

### Community 1 - "Services"
Cohesion: 0.11
Nodes (9): LLMUnavailableError, __newsmerger_plugin__(), __newsmerger_plugin__(), Services, __newsmerger_plugin__(), __newsmerger_plugin__(), UnavailableProcessor, DigestPluginTests (+1 more)

### Community 3 - "test_cli.py"
Cohesion: 0.13
Nodes (5): RunSummary, annotation(), CommandTests, InspectCommandTests, invoke()

### Community 5 - "ScoredItem"
Cohesion: 0.12
Nodes (6): DBArtifact, Artifact, ArtifactTests, MigrateFeedNamesTests, ArtifactSinkTests, RecordingArtifactSink

### Community 8 - "FeedGeneratorRemixer"
Cohesion: 0.21
Nodes (3): FeedGeneratorRemixer, __newsmerger_plugin__(), FeedGeneratorTests

### Community 9 - "GroupingTests"
Cohesion: 0.19
Nodes (5): EmbeddingsOptions, GroupingOptions, EmbeddingGroupingTests, GroupingTests, RemixerTestCase

### Community 11 - "app_from_context"
Cohesion: 0.14
Nodes (11): app_from_context(), cli(), deliver_cmd(), import_cmd(), inspect_content_cmd(), inspect_deliveries_cmd(), parse_artifact_ids(), process_cmd() (+3 more)

### Community 12 - "ProcessingScope"
Cohesion: 0.11
Nodes (7): DeliveryStatus, ProcessingScope, BaseArtifactSink, BaseItemSink, UnavailableSink, migrate(), MigrateTelegramStateTests

### Community 13 - "Artifact"
Cohesion: 0.31
Nodes (3): ArtifactSinkOptions, TelegramArtifactSink, TelegramArtifactSinkTests

### Community 15 - ".select"
Cohesion: 0.37
Nodes (4): ItemSinkOptions, ok_response(), TelegramSinkTests, TelegramTestCase

### Community 17 - "Telegram Channel Parsing"
Cohesion: 0.11
Nodes (10): is_home_page(), __newsmerger_plugin__(), page_title(), parse_article(), parse_preview(), Post, preview_url(), TelegramChannelProvider (+2 more)

### Community 18 - "group"
Cohesion: 0.29
Nodes (3): delete_group(), deliveries_group(), inspect_group()

### Community 19 - "Database"
Cohesion: 0.09
Nodes (5): Database, AverageLinkRemixer, GroupingRemixer, BaseRemixer, UnavailableRemixer

### Community 20 - "run_cmd"
Cohesion: 0.21
Nodes (4): import_sources(), progress_rows(), run_cmd(), run_each()

### Community 21 - "db.py"
Cohesion: 0.11
Nodes (3): CustomJSON, _encode_value(), UTCDateTime

### Community 23 - "SourceItem"
Cohesion: 0.11
Nodes (3): SourceItem, GoogleChatError, SearchTests

### Community 25 - "SourceData"
Cohesion: 0.09
Nodes (8): DBSource, HTTPClient, SourceData, CastellonInformacionProvider, PlazaProvider, TheGuardianProvider, IndexSiteProvider, TestHTTPClient

### Community 27 - "Markdownify Processor"
Cohesion: 0.20
Nodes (5): MarkdownifyProcessor, __newsmerger_plugin__(), SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 28 - "Prensa Iberica Plain Provider"
Cohesion: 0.15
Nodes (3): _extract_href(), __newsmerger_plugin__(), PrensaIbericaPlainProvider

### Community 29 - "Inspect/Delete CLI Decision"
Cohesion: 0.23
Nodes (10): cli.py Click commands, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage, SQLAlchemy models never leave db.py; DTOs cross the boundary, foundation internal library, inspect items|annotations|artifacts|deliveries, Application class (single entry point), Phases: import, enrich, remix, deliver (+2 more)

### Community 31 - "PluginOptions"
Cohesion: 0.18
Nodes (6): SourceItemData, CSJuntasGobiernoProvider, FeedReaderProvider, PrensaIbericaProvider, TestCSJuntasGobierno, TestPrensaIberica

### Community 32 - "CSJuntasGobiernoProvider"
Cohesion: 0.33
Nodes (3): find_parent_by_tag_name(), get_date_from_text(), PreparseData

### Community 33 - "feedreader.py"
Cohesion: 0.27
Nodes (7): discover_feed_url(), entry_date(), fetch_article(), fetch_feed(), find_image(), __newsmerger_plugin__(), parse_entry()

### Community 34 - "ConfigError"
Cohesion: 0.14
Nodes (6): load_plugins(), lookup(), objects_by_name(), process_runs(), ConfigError, plugin_options_error()

### Community 36 - ".close"
Cohesion: 0.30
Nodes (3): ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 38 - "migrate_autoincrement.py"
Cohesion: 0.07
Nodes (11): LockedError, write_lock(), Base, DBItemAnnotation, main(), migrate(), needs_autoincrement(), recreate() (+3 more)

### Community 39 - "Architecture & Processing ADRs"
Cohesion: 0.23
Nodes (12): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger, deliver SINK --force with explicit selection (+4 more)

### Community 40 - "db.py"
Cohesion: 0.10
Nodes (4): check_provider_options(), referenced_plugins(), _sha256_column(), Remixer

### Community 41 - "Selection CLI Options"
Cohesion: 0.23
Nodes (7): annotation_options(), artifact_options(), inspect_annotations_cmd(), report_user_errors(), wrapper(), scope_options(), wrapper()

### Community 42 - "delete_items_cmd"
Cohesion: 0.19
Nodes (6): Options, SummarizeProcessor, Processor, ProcessorTestCase, SummarizeTests, TaggerTests

### Community 43 - "Processor & Remixer Bundles"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "ollama.py"
Cohesion: 0.17
Nodes (4): EmbedProcessor, Options, tags_text(), EmbedTests

### Community 45 - "Plugin System Docs"
Cohesion: 0.25
Nodes (5): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), ollama LLM backend, plugins configuration section

### Community 47 - "Provider"
Cohesion: 0.19
Nodes (4): get_section(), parse_datetime(), SectionNotFoundError, Provider

### Community 49 - "expand_variables"
Cohesion: 0.12
Nodes (5): GoogleChatSink, __newsmerger_plugin__(), Options, GoogleChatSinkTests, OptionsTests

### Community 51 - "inspect_annotations_cmd"
Cohesion: 0.08
Nodes (13): format_value(), inspect_items_cmd(), json_default(), match_snippet(), preview(), print_deliver(), print_import(), print_item() (+5 more)

### Community 52 - "single_link_groups"
Cohesion: 0.18
Nodes (5): __newsmerger_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 53 - "inspect_artifacts_cmd"
Cohesion: 0.33
Nodes (3): inspect_artifacts_cmd(), lexer_for(), print_content()

### Community 54 - "Spec Glossary Entities"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "Sample Pages & Formats"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 56 - "config.py"
Cohesion: 0.12
Nodes (5): CacheConfig, DatabaseConfig, expand_variables(), MissingVariableError, ProcessEntry

### Community 57 - "PluginOptions"
Cohesion: 0.09
Nodes (12): __newsmerger_plugin__(), __newsmerger_plugin__(), Options, Options, Options, Options, PluginOptions, Options (+4 more)

### Community 58 - "Agent Conventions"
Cohesion: 0.33
Nodes (5): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention

### Community 59 - "Options"
Cohesion: 0.19
Nodes (6): check_found(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), require_selection(), sort_option()

### Community 60 - "Side-Effect Remixers ADR"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 61 - "Item Identity ADR"
Cohesion: 0.40
Nodes (4): IndexSiteProvider / URLProvider, ADR 0001 Item identity and change detection, Item, Provider

### Community 62 - "test_telegram.py"
Cohesion: 0.11
Nodes (8): build_text(), build_caption(), __newsmerger_plugin__(), TelegramClient, TelegramSink, Sink, BuildCaptionTests, PluginTests

### Community 63 - "LLM"
Cohesion: 0.12
Nodes (6): LLM, strip_code_fence(), DigestRemixer, merge_tags(), Options, TaggerProcessor

### Community 65 - "GroupingTests"
Cohesion: 0.08
Nodes (18): average_between(), average_link_cluster(), build_score_matrix(), cosine_similarity(), EmbeddingsRemixer, item_ref(), jaccard(), member_payload() (+10 more)

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)`, `PluginOptions (pydantic, unknown keys rejected)`, `Annotation` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 395 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `ORM Models & Ledger Rows`, `Services`, `test_app.py`, `ScoredItem`, `Application`, `.close`, `FeedGeneratorRemixer`, `GroupingTests`, `DeleteCommandTests`, `ProcessingScope`, `Artifact`, `.select`, `Sink Delivery Cycle`, `db.py`, `SourceItem`, `SourceData`, `.require_annotation`, `Markdownify Processor`, `ConfigError`, `DigestRemixerTests`, `.close`, `.queue_item_deliveries`, `migrate_autoincrement.py`, `db.py`, `delete_items_cmd`, `ollama.py`, `GroupingRemixer`, `expand_variables`, `.__init__`, `test_telegram.py`, `LLM`, `GroupingTests`?**
  _High betweenness centrality (0.201) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ORM Models & Ledger Rows` be split into smaller, more focused modules?**
  _Cohesion score 0.05854341736694678 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `ProcessingScope` to `ORM Models & Ledger Rows`, `Services`, `test_app.py`, `test_cli.py`, `ApplicationTests`, `Application`, `FeedGeneratorRemixer`, `GroupingTests`, `DeleteCommandTests`, `app_from_context`, `Sink Delivery Cycle`, `Database`, `SourceItem`, `.require_annotation`, `ConfigError`, `DigestRemixerTests`, `.close`, `.queue_item_deliveries`, `migrate_autoincrement.py`, `db.py`, `Selection CLI Options`, `delete_items_cmd`, `inspect_annotations_cmd`, `Options`, `test_telegram.py`, `LLM`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Should `Services` be split into smaller, more focused modules?**
  _Cohesion score 0.11264367816091954 - nodes in this community are weakly interconnected._