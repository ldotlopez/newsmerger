# Graph Report - enrich-entries  (2026-10-26)

## Corpus Check
- 67 files · ~111,829 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1355 nodes · 3935 edges · 80 communities (54 shown, 26 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 530 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `96a512a4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- LLMUnavailableError
- db.py
- invoke
- ApplicationTests
- Artifact
- Application
- migrate_autoincrement.py
- FeedGeneratorRemixer
- .close
- .session_scope
- app_from_context
- Delivery
- TelegramArtifactSink
- StubLLM
- TelegramTestCase
- BaseSink
- test_providers.py
- cli.py
- .get_artifact
- run_cmd
- .get_annotation_values
- Config
- SourceItem
- TelegramClient
- HTTPClient
- BaseProcessor
- markdownify.py
- .parse_index
- cli.py Click commands
- TestFeedReader
- SourceItemData
- get_date_from_text
- SourceData
- app.py
- ProcessingScope
- RecordingItemSink
- DBProcessingState
- migrate_autoincrement.py
- ADR 0007 Sinks and the delivery ledger
- models.py
- report_user_errors
- Processor
- Services object (services.llm(name))
- embed.py
- config.example.yaml
- Database
- get_section
- LogLevelTests
- Sink
- .__init__
- inspect_items_cmd
- __newsmerger_plugin__
- LLM
- Processor
- El Periódico Mediterráneo
- config.py
- Provider
- newsmerger CLAUDE.md agent guidelines
- delete_items_cmd
- deliveries table (the ledger)
- ADR 0001 Item identity and change detection
- TelegramTestCase
- tagger.py
- TestSourceItemDataContent
- grouping.py
- .run_sink
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- DeliveryStatus
- Artifact
- Grouping notes: NLP clustering pipeline
- news-aggregator
- .get_item_deliveries
- Annotation
- GoogleChatError
- SelectionRequiredError
- ADR 0002 Processing state lifecycle

## God Nodes (most connected - your core abstractions)
1. `Database` - 163 edges
2. `ProcessingScope` - 141 edges
3. `SourceItem` - 120 edges
4. `SourceData` - 81 edges
5. `Artifact` - 62 edges
6. `Services` - 59 edges
7. `Application` - 54 edges
8. `SourceItemData` - 49 edges
9. `HTTPClient` - 44 edges
10. `PluginOptions` - 41 edges

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

## Communities (80 total, 26 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.06
Nodes (14): DBDelivery, DBSourceItem, AnnotationTests, ConnectionTests, ContentStorageTests, DatabaseTestCase, DeleteTests, DeliveryTests (+6 more)

### Community 1 - "LLMUnavailableError"
Cohesion: 0.16
Nodes (4): LLMUnavailableError, __newsmerger_plugin__(), __newsmerger_plugin__(), UnavailableProcessor

### Community 2 - "db.py"
Cohesion: 0.14
Nodes (4): _sha256_column(), build_text(), build_caption(), BuildCaptionTests

### Community 3 - "invoke"
Cohesion: 0.13
Nodes (6): RunSummary, annotation(), CommandTests, InspectCommandTests, invoke(), SearchTests

### Community 5 - "Artifact"
Cohesion: 0.16
Nodes (5): DBArtifact, Artifact, ArtifactTests, ArtifactSinkTests, RecordingArtifactSink

### Community 7 - "migrate_autoincrement.py"
Cohesion: 0.13
Nodes (7): Base, DBItemAnnotation, migrate(), needs_autoincrement(), recreate(), make_item(), MigrateAutoincrementTests

### Community 9 - ".close"
Cohesion: 0.08
Nodes (4): EmbeddingGroupingTests, FeedGeneratorTests, GroupingTests, RemixerTestCase

### Community 11 - "app_from_context"
Cohesion: 0.14
Nodes (10): app_from_context(), cli(), deliver_cmd(), enrich_cmd(), import_cmd(), inspect_content_cmd(), inspect_deliveries_cmd(), parse_artifact_ids() (+2 more)

### Community 12 - "Delivery"
Cohesion: 0.14
Nodes (3): Delivery, BaseArtifactSink, BaseItemSink

### Community 13 - "TelegramArtifactSink"
Cohesion: 0.31
Nodes (3): ArtifactSinkOptions, TelegramArtifactSink, TelegramArtifactSinkTests

### Community 14 - "StubLLM"
Cohesion: 0.24
Nodes (3): ConsumerPluginTests, ServicesTests, StubLLM

### Community 15 - "TelegramTestCase"
Cohesion: 0.39
Nodes (3): ItemSinkOptions, ok_response(), TelegramSinkTests

### Community 17 - "test_providers.py"
Cohesion: 0.14
Nodes (8): page_title(), parse_article(), parse_preview(), Post, preview_url(), TelegramChannelProvider, read_sample(), TestTelegramChannel

### Community 18 - "cli.py"
Cohesion: 0.10
Nodes (6): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content()

### Community 20 - "run_cmd"
Cohesion: 0.17
Nodes (6): import_sources(), print_remix(), progress_rows(), remix_cmd(), run_cmd(), run_each()

### Community 21 - ".get_annotation_values"
Cohesion: 0.14
Nodes (3): CustomJSON, _encode_value(), UTCDateTime

### Community 23 - "SourceItem"
Cohesion: 0.11
Nodes (3): SourceItem, GoogleChatSink, TelegramSink

### Community 24 - "TelegramClient"
Cohesion: 0.17
Nodes (3): __newsmerger_plugin__(), TelegramError, PluginTests

### Community 25 - "HTTPClient"
Cohesion: 0.10
Nodes (11): HTTPClient, discover_feed_url(), entry_date(), FeedReaderProvider, fetch_article(), fetch_feed(), find_image(), __newsmerger_plugin__() (+3 more)

### Community 26 - "BaseProcessor"
Cohesion: 0.17
Nodes (3): ProcessingStatus, BaseProcessor, MissingAnnotationError

### Community 27 - "markdownify.py"
Cohesion: 0.16
Nodes (6): MarkdownifyProcessor, __newsmerger_plugin__(), Options, SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 28 - ".parse_index"
Cohesion: 0.15
Nodes (3): _extract_href(), __newsmerger_plugin__(), PrensaIbericaPlainProvider

### Community 29 - "cli.py Click commands"
Cohesion: 0.23
Nodes (10): cli.py Click commands, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage, SQLAlchemy models never leave db.py; DTOs cross the boundary, foundation internal library, inspect items|annotations|artifacts|deliveries, Application class (single entry point), Phases: import, enrich, remix, deliver (+2 more)

### Community 31 - "SourceItemData"
Cohesion: 0.19
Nodes (5): SourceItemData, PrensaIbericaProvider, TheGuardianProvider, IndexSiteProvider, TestPrensaIberica

### Community 32 - "get_date_from_text"
Cohesion: 0.18
Nodes (6): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), __newsmerger_plugin__(), PreparseData, TestCSJuntasGobierno

### Community 33 - "SourceData"
Cohesion: 0.15
Nodes (4): DBSource, SourceData, CastellonInformacionProvider, __newsmerger_plugin__()

### Community 34 - "app.py"
Cohesion: 0.12
Nodes (6): check_provider_options(), enrich_runs(), load_plugins(), objects_by_name(), ConfigError, plugin_options_error()

### Community 35 - "ProcessingScope"
Cohesion: 0.14
Nodes (4): ProcessingScope, DigestRemixer, UnavailableSink, DigestRemixerTests

### Community 36 - "RecordingItemSink"
Cohesion: 0.30
Nodes (3): ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 38 - "migrate_autoincrement.py"
Cohesion: 0.11
Nodes (7): LockedError, write_lock(), main(), main(), migrate(), main(), migrate()

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.23
Nodes (12): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger, deliver SINK --force with explicit selection (+4 more)

### Community 40 - "models.py"
Cohesion: 0.13
Nodes (8): Options, Options, Options, PluginOptions, Services, Options, Options, Options

### Community 41 - "report_user_errors"
Cohesion: 0.23
Nodes (7): annotation_options(), artifact_options(), inspect_annotations_cmd(), report_user_errors(), wrapper(), scope_options(), wrapper()

### Community 42 - "Processor"
Cohesion: 0.17
Nodes (5): Processor, EmbedTests, ProcessorTestCase, SummarizeTests, TaggerTests

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "embed.py"
Cohesion: 0.17
Nodes (4): EmbedProcessor, __newsmerger_plugin__(), Options, tags_text()

### Community 45 - "config.example.yaml"
Cohesion: 0.25
Nodes (5): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), ollama LLM backend, plugins configuration section

### Community 46 - "Database"
Cohesion: 0.10
Nodes (5): Database, AverageLinkRemixer, GroupingRemixer, SingleLinkRemixer, BaseRemixer

### Community 47 - "get_section"
Cohesion: 0.17
Nodes (5): get_section(), __newsmerger_plugin__(), parse_datetime(), PlazaProvider, SectionNotFoundError

### Community 49 - "Sink"
Cohesion: 0.14
Nodes (4): __newsmerger_plugin__(), Options, Sink, OptionsTests

### Community 51 - "inspect_items_cmd"
Cohesion: 0.11
Nodes (13): check_found(), format_value(), inspect_artifacts_cmd(), inspect_items_cmd(), json_default(), preview(), print_deliver(), print_enrich() (+5 more)

### Community 52 - "__newsmerger_plugin__"
Cohesion: 0.19
Nodes (4): __newsmerger_plugin__(), ollama_client(), OllamaLLM, OllamaTests

### Community 53 - "LLM"
Cohesion: 0.20
Nodes (3): LLM, Options, SummarizeProcessor

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 56 - "config.py"
Cohesion: 0.12
Nodes (5): CacheConfig, DatabaseConfig, EnrichEntry, expand_variables(), MissingVariableError

### Community 57 - "Provider"
Cohesion: 0.14
Nodes (4): __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), Provider

### Community 58 - "newsmerger CLAUDE.md agent guidelines"
Cohesion: 0.33
Nodes (5): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention

### Community 59 - "delete_items_cmd"
Cohesion: 0.21
Nodes (5): delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), require_selection(), sort_option()

### Community 60 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 61 - "ADR 0001 Item identity and change detection"
Cohesion: 0.40
Nodes (4): IndexSiteProvider / URLProvider, ADR 0001 Item identity and change detection, Item, Provider

### Community 62 - "TelegramTestCase"
Cohesion: 0.25
Nodes (3): TelegramClient, MigrateTelegramStateTests, TelegramTestCase

### Community 63 - "tagger.py"
Cohesion: 0.24
Nodes (4): strip_code_fence(), merge_tags(), Options, TaggerProcessor

### Community 65 - "grouping.py"
Cohesion: 0.06
Nodes (25): __newsmerger_plugin__(), __newsmerger_plugin__(), average_between(), average_link_cluster(), build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer (+17 more)

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)`, `PluginOptions (pydantic, unknown keys rejected)`, `Annotation` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 394 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_db.py`, `LLMUnavailableError`, `db.py`, `Artifact`, `Application`, `migrate_autoincrement.py`, `FeedGeneratorRemixer`, `.close`, `.session_scope`, `Delivery`, `TelegramArtifactSink`, `BaseSink`, `.get_artifact`, `.get_annotation_values`, `SourceItem`, `BaseProcessor`, `markdownify.py`, `SourceData`, `app.py`, `ProcessingScope`, `RecordingItemSink`, `DBProcessingState`, `migrate_autoincrement.py`, `models.py`, `Processor`, `embed.py`, `Sink`, `.__init__`, `LLM`, `TelegramTestCase`, `tagger.py`, `grouping.py`, `DeliveryStatus`, `.get_item_deliveries`, `Annotation`?**
  _High betweenness centrality (0.176) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06112616681722373 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `ProcessingScope` to `test_db.py`, `LLMUnavailableError`, `db.py`, `invoke`, `ApplicationTests`, `Artifact`, `Application`, `FeedGeneratorRemixer`, `.close`, `.session_scope`, `app_from_context`, `Delivery`, `StubLLM`, `BaseSink`, `cli.py`, `run_cmd`, `BaseProcessor`, `app.py`, `RecordingItemSink`, `migrate_autoincrement.py`, `models.py`, `report_user_errors`, `Processor`, `Database`, `Sink`, `inspect_items_cmd`, `delete_items_cmd`, `TelegramTestCase`, `grouping.py`, `.run_sink`, `DeliveryStatus`, `.get_item_deliveries`, `Annotation`?**
  _High betweenness centrality (0.159) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Should `db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1354723707664884 - nodes in this community are weakly interconnected._