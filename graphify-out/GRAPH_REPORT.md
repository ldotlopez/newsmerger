# Graph Report - telegram-upload-photo  (2026-10-27)

## Corpus Check
- 68 files · ~119,696 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1458 nodes · 4307 edges · 75 communities (50 shown, 25 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 584 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f1fe2a03`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- app.py
- .from_text
- ApplicationTests
- TelegramSinkTests
- Application
- migrate_autoincrement.py
- feedreader.py
- migrate_telegram_state.py
- .session_scope
- app_from_context
- grouping.py
- RunSummary
- run_cmd
- Sink
- BaseSink
- test_providers.py
- DeliveryStatus
- ProcessingScope
- 0009: Workflows and keyed entries
- Any
- SourceItem
- Database
- SourceData
- BaseProcessor
- MarkdownifyProcessor
- .parse_index
- cli.py Click commands
- Artifact
- PluginOptions
- get_date_from_text
- __newsmerger_plugin__
- GroupingRemixer
- DigestRemixer
- RecordingItemSink
- report_user_errors
- config.py
- ADR 0007 Sinks and the delivery ledger
- ScoredItem
- EmbeddingGroupingTests
- TestFeedReader
- Services object (services.llm(name))
- StubLLM
- config.example.yaml
- GroupingTests
- __newsmerger_plugin__
- db.py
- GoogleChatSinkTests
- PrensaIbericaProvider
- cli.py
- Config
- inspect_annotations_cmd
- Processor
- El Periódico Mediterráneo
- merge_options
- TelegramTestCase
- newsmerger CLAUDE.md agent guidelines
- TestSourceItemDataContent
- deliveries table (the ledger)
- ADR 0001 Item identity and change detection
- TelegramArtifactSink
- .get_artifact
- .__init__
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- Artifact
- Grouping notes: NLP clustering pipeline
- news-aggregator
- LogLevelTests
- MigrateAutoincrementTests
- FeedGeneratorRemixer
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
- `ApplicationTests` --uses--> `LockedError`  [INFERRED]
  tests/test_app.py → newsmerger/app.py
- `ApplicationTests` --uses--> `Application`  [INFERRED]
  tests/test_app.py → newsmerger/app.py
- `invoke()` --indirect_call--> `cli()`  [INFERRED]
  tests/test_cli.py → newsmerger/cli.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (75 total, 25 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.05
Nodes (18): Base, DBDelivery, DBItemAnnotation, DBProcessingState, DBSource, DBSourceItem, AnnotationTests, ConnectionTests (+10 more)

### Community 2 - "app.py"
Cohesion: 0.08
Nodes (12): LLM, LLMUnavailableError, strip_code_fence(), __newsmerger_plugin__(), Services, __newsmerger_plugin__(), __newsmerger_plugin__(), Processor (+4 more)

### Community 5 - "TelegramSinkTests"
Cohesion: 0.31
Nodes (3): TelegramSink, ok_response(), TelegramSinkTests

### Community 6 - "Application"
Cohesion: 0.07
Nodes (4): Application, lookup(), workflow_scope(), ConfigError

### Community 7 - "migrate_autoincrement.py"
Cohesion: 0.17
Nodes (4): main(), migrate(), needs_autoincrement(), recreate()

### Community 8 - "feedreader.py"
Cohesion: 0.13
Nodes (10): discover_feed_url(), entry_date(), FeedReaderProvider, fetch_article(), fetch_feed(), find_image(), __newsmerger_plugin__(), Options (+2 more)

### Community 9 - "migrate_telegram_state.py"
Cohesion: 0.11
Nodes (5): LockedError, write_lock(), main(), migrate(), main()

### Community 10 - ".session_scope"
Cohesion: 0.10
Nodes (3): Annotation, migrate(), DeleteCommandTests

### Community 11 - "app_from_context"
Cohesion: 0.15
Nodes (10): app_from_context(), cli(), deliver_cmd(), import_cmd(), inspect_content_cmd(), parse_artifact_ids(), process_cmd(), remix_cmd() (+2 more)

### Community 12 - "grouping.py"
Cohesion: 0.19
Nodes (5): average_between(), average_link_cluster(), cosine_similarity(), Options, time_decay()

### Community 13 - "RunSummary"
Cohesion: 0.12
Nodes (5): RunSummary, annotation(), CommandTests, InspectCommandTests, invoke()

### Community 14 - "run_cmd"
Cohesion: 0.13
Nodes (9): import_sources(), print_deliver(), print_import(), print_process(), print_remix(), print_table(), progress_rows(), run_cmd() (+1 more)

### Community 15 - "Sink"
Cohesion: 0.08
Nodes (12): delivery_runs(), entry_location(), load_plugins(), objects_by_name(), process_runs(), referenced_plugins(), remix_runs(), Run (+4 more)

### Community 17 - "test_providers.py"
Cohesion: 0.11
Nodes (13): CSJuntasGobiernoProvider, is_home_page(), __newsmerger_plugin__(), Options, page_title(), parse_article(), parse_preview(), Post (+5 more)

### Community 18 - "DeliveryStatus"
Cohesion: 0.13
Nodes (5): backoff_seconds(), DeliveryStatus, Delivery, BaseArtifactSink, BaseItemSink

### Community 19 - "ProcessingScope"
Cohesion: 0.33
Nodes (4): wrapper(), ProcessingScope, SearchTests, DigestRemixerTests

### Community 20 - "0009: Workflows and keyed entries"
Cohesion: 0.25
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 21 - "Any"
Cohesion: 0.16
Nodes (3): CustomJSON, _encode_value(), UTCDateTime

### Community 25 - "SourceData"
Cohesion: 0.08
Nodes (14): HTTPClient, SourceData, SourceItemData, CastellonInformacionProvider, __newsmerger_plugin__(), get_section(), __newsmerger_plugin__(), parse_datetime() (+6 more)

### Community 26 - "BaseProcessor"
Cohesion: 0.11
Nodes (5): tags_text(), merge_tags(), TaggerProcessor, BaseProcessor, MissingAnnotationError

### Community 27 - "MarkdownifyProcessor"
Cohesion: 0.22
Nodes (5): MarkdownifyProcessor, __newsmerger_plugin__(), SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 29 - "cli.py Click commands"
Cohesion: 0.23
Nodes (10): cli.py Click commands, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage, SQLAlchemy models never leave db.py; DTOs cross the boundary, foundation internal library, inspect items|annotations|artifacts|deliveries, Application class (single entry point), Phases: import, enrich, remix, deliver (+2 more)

### Community 30 - "Artifact"
Cohesion: 0.15
Nodes (4): DBArtifact, Artifact, ArtifactTests, MigrateTelegramStateTests

### Community 31 - "PluginOptions"
Cohesion: 0.08
Nodes (7): __newsmerger_plugin__(), NoOptions, PluginOptions, Options, __newsmerger_plugin__(), __newsmerger_plugin__(), BaseRemixer

### Community 32 - "get_date_from_text"
Cohesion: 0.33
Nodes (3): find_parent_by_tag_name(), get_date_from_text(), PreparseData

### Community 33 - "__newsmerger_plugin__"
Cohesion: 0.18
Nodes (5): __newsmerger_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 34 - "GroupingRemixer"
Cohesion: 0.21
Nodes (5): AverageLinkRemixer, GroupingOptions, GroupingRemixer, SingleLinkRemixer, tagged_items()

### Community 35 - "DigestRemixer"
Cohesion: 0.29
Nodes (3): DigestOptions, DigestRemixer, Options

### Community 36 - "RecordingItemSink"
Cohesion: 0.16
Nodes (6): SelectionRequiredError, ArtifactSinkTests, ItemSinkTests, RecordingArtifactSink, RecordingItemSink, SinkTestCase

### Community 37 - "report_user_errors"
Cohesion: 0.15
Nodes (9): annotation_options(), artifact_options(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), report_user_errors(), wrapper(), require_selection() (+1 more)

### Community 38 - "config.py"
Cohesion: 0.08
Nodes (7): CacheConfig, DatabaseConfig, DeliveryEntry, expand_variables(), MissingVariableError, ProcessEntry, RemixEntry

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.23
Nodes (12): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger, deliver SINK --force with explicit selection (+4 more)

### Community 40 - "ScoredItem"
Cohesion: 0.22
Nodes (8): build_score_matrix(), item_ref(), member_payload(), pair_payload(), score_pair(), ScoredItem, single_link_groups(), UnionFind

### Community 41 - "EmbeddingGroupingTests"
Cohesion: 0.33
Nodes (4): EmbeddingsOptions, EmbeddingsRemixer, jaccard(), EmbeddingGroupingTests

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "StubLLM"
Cohesion: 0.08
Nodes (13): EmbedOptions, EmbedProcessor, Options, Options, SummarizeOptions, SummarizeProcessor, Options, TaggerOptions (+5 more)

### Community 45 - "config.example.yaml"
Cohesion: 0.25
Nodes (5): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), ollama LLM backend, plugins configuration section

### Community 48 - "db.py"
Cohesion: 0.11
Nodes (9): ProcessingStatus, _sha256_column(), build_text(), build_caption(), DocumentDeliveryOptions, ItemDeliveryOptions, ArtifactDeliveryOptions, DeliveryOptions (+1 more)

### Community 49 - "GoogleChatSinkTests"
Cohesion: 0.09
Nodes (8): GoogleChatError, GoogleChatSink, image_card(), __newsmerger_plugin__(), Options, WebhookOptions, GoogleChatSinkTests, OptionsTests

### Community 50 - "PrensaIbericaProvider"
Cohesion: 0.24
Nodes (3): __newsmerger_plugin__(), PrensaIbericaProvider, TestPrensaIberica

### Community 51 - "cli.py"
Cohesion: 0.10
Nodes (7): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content(), setup_logging()

### Community 53 - "inspect_annotations_cmd"
Cohesion: 0.15
Nodes (11): check_found(), format_value(), inspect_annotations_cmd(), inspect_artifacts_cmd(), inspect_deliveries_cmd(), inspect_items_cmd(), json_default(), preview() (+3 more)

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 56 - "merge_options"
Cohesion: 0.09
Nodes (4): __newsmerger_plugin__(), merge_options(), UnavailableRemixer, DigestPluginTests

### Community 58 - "newsmerger CLAUDE.md agent guidelines"
Cohesion: 0.33
Nodes (5): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention

### Community 60 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 61 - "ADR 0001 Item identity and change detection"
Cohesion: 0.40
Nodes (4): IndexSiteProvider / URLProvider, ADR 0001 Item identity and change detection, Item, Provider

### Community 62 - "TelegramArtifactSink"
Cohesion: 0.15
Nodes (6): __newsmerger_plugin__(), post(), TelegramArtifactSink, TelegramError, PluginTests, TelegramArtifactSinkTests

### Community 76 - "FeedGeneratorRemixer"
Cohesion: 0.21
Nodes (4): FeedGeneratorRemixer, __newsmerger_plugin__(), Options, FeedGeneratorTests

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)`, `PluginOptions (pydantic, unknown keys rejected)`, `Annotation` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 418 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_db.py`, `.close`, `app.py`, `TelegramSinkTests`, `Application`, `migrate_telegram_state.py`, `.session_scope`, `grouping.py`, `RunSummary`, `Sink`, `BaseSink`, `DeliveryStatus`, `ProcessingScope`, `Any`, `SourceItem`, `.get_annotation_values`, `SourceData`, `BaseProcessor`, `MarkdownifyProcessor`, `Artifact`, `PluginOptions`, `GroupingRemixer`, `DigestRemixer`, `RecordingItemSink`, `ScoredItem`, `EmbeddingGroupingTests`, `StubLLM`, `GroupingTests`, `db.py`, `GoogleChatSinkTests`, `merge_options`, `TelegramTestCase`, `TelegramArtifactSink`, `.get_artifact`, `.get_stored_content`, `.__init__`, `MigrateAutoincrementTests`, `FeedGeneratorRemixer`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Are the 44 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 44 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05255613951266125 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `ProcessingScope` to `test_db.py`, `app.py`, `ApplicationTests`, `Application`, `migrate_telegram_state.py`, `.session_scope`, `app_from_context`, `grouping.py`, `RunSummary`, `Sink`, `BaseSink`, `DeliveryStatus`, `Database`, `BaseProcessor`, `Artifact`, `PluginOptions`, `GroupingRemixer`, `DigestRemixer`, `RecordingItemSink`, `report_user_errors`, `EmbeddingGroupingTests`, `StubLLM`, `GroupingTests`, `db.py`, `GoogleChatSinkTests`, `cli.py`, `inspect_annotations_cmd`, `merge_options`, `FeedGeneratorRemixer`?**
  _High betweenness centrality (0.128) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Should `.close` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._