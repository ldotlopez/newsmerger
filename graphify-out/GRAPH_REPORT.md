# Graph Report - workflows-plan  (2026-10-27)

## Corpus Check
- 67 files · ~115,874 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1443 nodes · 4264 edges · 87 communities (52 shown, 35 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 580 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1da74c21`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- make_item
- Services
- db.py
- invoke
- ApplicationTests
- Artifact
- Application
- migrate
- FeedGeneratorRemixer
- GroupingTests
- DeleteCommandTests
- app_from_context
- merge_options
- ProcessingScope
- run_cmd
- Config
- BaseSink
- TelegramChannelProvider
- .get_item_deliveries
- RemixEntry
- Base
- SourceItem
- Database
- app.py
- SourceData
- Database
- markdownify.py
- PrensaIbericaPlainProvider
- cli.py Click commands
- .close
- SourceItemData
- CSJuntasGobiernoProvider
- feedreader.py
- ConfigError
- DigestRemixerTests
- RecordingItemSink
- SourceData
- config.py
- ADR 0007 Sinks and the delivery ledger
- PluginOptions
- report_user_errors
- ProcessorTestCase
- Services object (services.llm(name))
- EmbedProcessor
- config.example.yaml
- PluginOptions
- migrate_telegram_state.py
- OptionsTests
- TelegramSinkTests
- cli.py
- SummarizeProcessor
- inspect_annotations_cmd
- Processor
- El Periódico Mediterráneo
- expand_variables
- PlazaProvider
- newsmerger CLAUDE.md agent guidelines
- StubLLM
- deliveries table (the ledger)
- ADR 0001 Item identity and change detection
- sinks.py
- test_telegram.py
- TelegramArtifactSink
- .get_annotation_values
- migrate_feed_names.py
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- MissingAnnotationError
- Artifact
- Grouping notes: NLP clustering pipeline
- news-aggregator
- LogLevelTests
- .get_artifact
- DeliveryStatus
- DigestRemixer
- TelegramTestCase
- parse_entry
- .post
- ADR 0002 Processing state lifecycle
- TestSourceItemDataContent

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
10. `ApplicationTests` - 48 edges

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

## Communities (87 total, 35 thin omitted)

### Community 0 - "make_item"
Cohesion: 0.06
Nodes (16): Base, DBDelivery, DBProcessingState, DBSourceItem, AnnotationTests, ConnectionTests, ContentStorageTests, DatabaseTestCase (+8 more)

### Community 1 - "Services"
Cohesion: 0.07
Nodes (15): LLM, LLMUnavailableError, strip_code_fence(), __newsmerger_plugin__(), Options, __newsmerger_plugin__(), Services, __newsmerger_plugin__() (+7 more)

### Community 2 - "db.py"
Cohesion: 0.13
Nodes (5): DBItemAnnotation, _encode_value(), ProcessingStatus, _sha256_column(), Annotation

### Community 3 - "invoke"
Cohesion: 0.22
Nodes (3): annotation(), InspectCommandTests, invoke()

### Community 4 - "ApplicationTests"
Cohesion: 0.06
Nodes (3): OllamaLLM, ApplicationTests, ConfigTests

### Community 5 - "Artifact"
Cohesion: 0.16
Nodes (5): DBArtifact, Artifact, ArtifactTests, ArtifactSinkTests, RecordingArtifactSink

### Community 7 - "migrate"
Cohesion: 0.17
Nodes (4): main(), migrate(), needs_autoincrement(), recreate()

### Community 8 - "FeedGeneratorRemixer"
Cohesion: 0.29
Nodes (3): FeedGeneratorRemixer, Options, FeedGeneratorTests

### Community 11 - "app_from_context"
Cohesion: 0.15
Nodes (10): app_from_context(), cli(), deliver_cmd(), import_cmd(), inspect_content_cmd(), parse_artifact_ids(), process_cmd(), remix_cmd() (+2 more)

### Community 13 - "ProcessingScope"
Cohesion: 0.14
Nodes (5): workflow_scope(), wrapper(), ProcessingScope, RunSummary, CommandTests

### Community 14 - "run_cmd"
Cohesion: 0.13
Nodes (9): import_sources(), print_deliver(), print_import(), print_process(), print_remix(), print_table(), progress_rows(), run_cmd() (+1 more)

### Community 15 - "Config"
Cohesion: 0.11
Nodes (9): delivery_runs(), entry_location(), process_runs(), referenced_plugins(), remix_runs(), Run, Config, Workflow (+1 more)

### Community 16 - "BaseSink"
Cohesion: 0.09
Nodes (3): Delivery, BaseItemSink, BaseSink

### Community 17 - "TelegramChannelProvider"
Cohesion: 0.13
Nodes (9): is_home_page(), Options, page_title(), parse_article(), parse_preview(), Post, TelegramChannelProvider, read_sample() (+1 more)

### Community 21 - "Base"
Cohesion: 0.12
Nodes (3): _configure_sqlite_connection(), CustomJSON, UTCDateTime

### Community 25 - "SourceData"
Cohesion: 0.13
Nodes (7): HTTPClient, discover_feed_url(), fetch_article(), fetch_feed(), TheGuardianProvider, IndexSiteProvider, TestHTTPClient

### Community 27 - "markdownify.py"
Cohesion: 0.22
Nodes (5): MarkdownifyProcessor, __newsmerger_plugin__(), SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 29 - "cli.py Click commands"
Cohesion: 0.23
Nodes (10): cli.py Click commands, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage, SQLAlchemy models never leave db.py; DTOs cross the boundary, foundation internal library, inspect items|annotations|artifacts|deliveries, Application class (single entry point), Phases: import, enrich, remix, deliver (+2 more)

### Community 31 - "SourceItemData"
Cohesion: 0.31
Nodes (3): SourceItemData, PrensaIbericaProvider, TestPrensaIberica

### Community 32 - "CSJuntasGobiernoProvider"
Cohesion: 0.18
Nodes (6): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), __newsmerger_plugin__(), PreparseData, TestCSJuntasGobierno

### Community 33 - "feedreader.py"
Cohesion: 0.26
Nodes (3): FeedReaderProvider, Options, TestFeedReader

### Community 34 - "ConfigError"
Cohesion: 0.14
Nodes (5): load_plugins(), objects_by_name(), source_options(), ConfigError, options_error()

### Community 36 - "RecordingItemSink"
Cohesion: 0.29
Nodes (3): ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 37 - "SourceData"
Cohesion: 0.22
Nodes (3): DBSource, SourceData, CastellonInformacionProvider

### Community 38 - "config.py"
Cohesion: 0.18
Nodes (4): CacheConfig, DatabaseConfig, expand_variables(), MissingVariableError

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.23
Nodes (12): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger, deliver SINK --force with explicit selection (+4 more)

### Community 40 - "PluginOptions"
Cohesion: 0.12
Nodes (6): __newsmerger_plugin__(), Options, NoOptions, PluginOptions, Options, BaseRemixer

### Community 41 - "report_user_errors"
Cohesion: 0.15
Nodes (9): annotation_options(), artifact_options(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), report_user_errors(), wrapper(), require_selection() (+1 more)

### Community 42 - "ProcessorTestCase"
Cohesion: 0.19
Nodes (6): merge_tags(), Options, TaggerOptions, TaggerProcessor, ProcessorTestCase, TaggerTests

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "EmbedProcessor"
Cohesion: 0.24
Nodes (5): EmbedOptions, EmbedProcessor, Options, tags_text(), EmbedTests

### Community 45 - "config.example.yaml"
Cohesion: 0.25
Nodes (5): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), ollama LLM backend, plugins configuration section

### Community 47 - "PluginOptions"
Cohesion: 0.12
Nodes (8): __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), preview_url(), __newsmerger_plugin__(), Provider

### Community 48 - "migrate_telegram_state.py"
Cohesion: 0.14
Nodes (3): LockedError, write_lock(), main()

### Community 49 - "OptionsTests"
Cohesion: 0.14
Nodes (6): GoogleChatError, GoogleChatSink, __newsmerger_plugin__(), Options, WebhookOptions, OptionsTests

### Community 50 - "TelegramSinkTests"
Cohesion: 0.37
Nodes (3): TelegramSink, ok_response(), TelegramSinkTests

### Community 51 - "cli.py"
Cohesion: 0.10
Nodes (7): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content(), setup_logging()

### Community 52 - "SummarizeProcessor"
Cohesion: 0.26
Nodes (4): Options, SummarizeOptions, SummarizeProcessor, SummarizeTests

### Community 53 - "inspect_annotations_cmd"
Cohesion: 0.15
Nodes (11): check_found(), format_value(), inspect_annotations_cmd(), inspect_artifacts_cmd(), inspect_deliveries_cmd(), inspect_items_cmd(), json_default(), preview() (+3 more)

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 57 - "PlazaProvider"
Cohesion: 0.22
Nodes (4): get_section(), parse_datetime(), PlazaProvider, SectionNotFoundError

### Community 58 - "newsmerger CLAUDE.md agent guidelines"
Cohesion: 0.33
Nodes (5): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention

### Community 59 - "StubLLM"
Cohesion: 0.24
Nodes (3): ConsumerPluginTests, ServicesTests, StubLLM

### Community 60 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 61 - "ADR 0001 Item identity and change detection"
Cohesion: 0.40
Nodes (4): IndexSiteProvider / URLProvider, ADR 0001 Item identity and change detection, Item, Provider

### Community 62 - "sinks.py"
Cohesion: 0.16
Nodes (6): build_text(), DocumentDeliveryOptions, ItemDeliveryOptions, ArtifactDeliveryOptions, DeliveryOptions, SelectionRequiredError

### Community 63 - "test_telegram.py"
Cohesion: 0.24
Nodes (5): build_caption(), migrate(), BuildCaptionTests, MigrateTelegramStateTests, PluginTests

### Community 64 - "TelegramArtifactSink"
Cohesion: 0.24
Nodes (3): __newsmerger_plugin__(), TelegramArtifactSink, TelegramArtifactSinkTests

### Community 65 - ".get_annotation_values"
Cohesion: 0.06
Nodes (23): average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer, GroupingOptions (+15 more)

### Community 78 - "TelegramTestCase"
Cohesion: 0.39
Nodes (3): Options, TelegramClient, TelegramTestCase

### Community 79 - "parse_entry"
Cohesion: 0.60
Nodes (3): entry_date(), find_image(), parse_entry()

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)`, `PluginOptions (pydantic, unknown keys rejected)`, `Annotation` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 415 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `make_item`, `Services`, `db.py`, `Artifact`, `Application`, `FeedGeneratorRemixer`, `GroupingTests`, `DeleteCommandTests`, `merge_options`, `ProcessingScope`, `Config`, `BaseSink`, `.get_item_deliveries`, `Base`, `SourceItem`, `app.py`, `Database`, `markdownify.py`, `.close`, `DigestRemixerTests`, `RecordingItemSink`, `SourceData`, `PluginOptions`, `ProcessorTestCase`, `EmbedProcessor`, `.session_scope`, `migrate_telegram_state.py`, `OptionsTests`, `TelegramSinkTests`, `SummarizeProcessor`, `sinks.py`, `test_telegram.py`, `TelegramArtifactSink`, `.get_annotation_values`, `MissingAnnotationError`, `.get_artifact`, `DeliveryStatus`, `DigestRemixer`, `TelegramTestCase`, `.remix`, `.get_stored_content`?**
  _High betweenness centrality (0.160) - this node is a cross-community bridge._
- **Are the 44 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 44 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `make_item` be split into smaller, more focused modules?**
  _Cohesion score 0.05693664795509222 - nodes in this community are weakly interconnected._
- **Why does `SourceItem` connect `SourceItem` to `make_item`, `Services`, `db.py`, `invoke`, `ApplicationTests`, `Application`, `FeedGeneratorRemixer`, `GroupingTests`, `DeleteCommandTests`, `BaseSink`, `.get_item_deliveries`, `Base`, `Database`, `app.py`, `Database`, `markdownify.py`, `.close`, `DigestRemixerTests`, `RecordingItemSink`, `PluginOptions`, `ProcessorTestCase`, `EmbedProcessor`, `migrate_telegram_state.py`, `OptionsTests`, `TelegramSinkTests`, `cli.py`, `SummarizeProcessor`, `inspect_annotations_cmd`, `StubLLM`, `sinks.py`, `test_telegram.py`, `TelegramArtifactSink`, `.get_annotation_values`, `MissingAnnotationError`, `.get_annotation_values`, `DigestRemixer`, `TelegramTestCase`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Should `Services` be split into smaller, more focused modules?**
  _Cohesion score 0.07322068612391193 - nodes in this community are weakly interconnected._