# Graph Report - telegram-token-per-entry  (2026-10-27)

## Corpus Check
- 68 files · ~118,840 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1447 nodes · 4271 edges · 84 communities (56 shown, 28 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 584 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e7c11324`
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
- GroupingTests
- .session_scope
- app_from_context
- Remixer
- ProcessingScope
- run_cmd
- app.py
- DeliveryStatus
- test_providers.py
- .get_item_deliveries
- RemixEntry
- .get_annotation_values
- SourceItem
- Database
- __newsmerger_plugin__
- SourceData
- BaseProcessor
- MarkdownifyProcessor
- PrensaIbericaPlainProvider
- cli.py Click commands
- .close
- SourceItemData
- PluginOptions
- merge_options
- load_plugins
- DigestRemixer
- RecordingItemSink
- delete_items_cmd
- config.py
- ADR 0007 Sinks and the delivery ledger
- grouping.py
- report_user_errors
- tagger.py
- Services object (services.llm(name))
- EmbedProcessor
- config.example.yaml
- LLM
- inspect_items_cmd
- migrate_telegram_state.py
- GoogleChatSink
- TelegramSinkTests
- cli.py
- SummarizeProcessor
- json
- Processor
- El Periódico Mediterráneo
- model_validator
- get_section
- newsmerger CLAUDE.md agent guidelines
- StubLLM
- deliveries table (the ledger)
- ADR 0001 Item identity and change detection
- telegram.py
- BaseRemixer
- TelegramArtifactSink
- ScoredItem
- migrate_feed_names.py
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- EmbeddingGroupingTests
- Artifact
- Grouping notes: NLP clustering pipeline
- news-aggregator
- LogLevelTests
- RecordingArtifactSink
- .get_artifact
- .__init__
- __newsmerger_plugin__
- Annotation
- _sha256_column
- Processor
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

## Communities (84 total, 28 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.05
Nodes (18): Base, DBDelivery, DBItemAnnotation, DBProcessingState, DBSource, DBSourceItem, AnnotationTests, ConnectionTests (+10 more)

### Community 1 - "LLMUnavailableError"
Cohesion: 0.14
Nodes (5): LLMUnavailableError, __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), UnavailableProcessor

### Community 3 - "invoke"
Cohesion: 0.18
Nodes (3): annotation(), InspectCommandTests, invoke()

### Community 5 - "Artifact"
Cohesion: 0.15
Nodes (4): DBArtifact, Artifact, ArtifactTests, MigrateTelegramStateTests

### Community 7 - "migrate_autoincrement.py"
Cohesion: 0.16
Nodes (4): main(), migrate(), needs_autoincrement(), recreate()

### Community 8 - "FeedGeneratorRemixer"
Cohesion: 0.21
Nodes (4): FeedGeneratorRemixer, __newsmerger_plugin__(), Options, FeedGeneratorTests

### Community 9 - "GroupingTests"
Cohesion: 0.33
Nodes (3): SingleLinkRemixer, GroupingTests, RemixerTestCase

### Community 11 - "app_from_context"
Cohesion: 0.15
Nodes (10): app_from_context(), cli(), deliver_cmd(), inspect_content_cmd(), inspect_deliveries_cmd(), parse_artifact_ids(), process_cmd(), remix_cmd() (+2 more)

### Community 13 - "ProcessingScope"
Cohesion: 0.15
Nodes (6): workflow_scope(), ProcessingScope, RunSummary, Sink, CommandTests, SearchTests

### Community 14 - "run_cmd"
Cohesion: 0.17
Nodes (6): import_cmd(), import_sources(), print_import(), progress_rows(), run_cmd(), run_each()

### Community 15 - "app.py"
Cohesion: 0.11
Nodes (11): delivery_runs(), entry_location(), process_runs(), referenced_plugins(), remix_runs(), Run, source_options(), Config (+3 more)

### Community 16 - "DeliveryStatus"
Cohesion: 0.07
Nodes (6): backoff_seconds(), DeliveryStatus, Delivery, BaseArtifactSink, BaseItemSink, BaseSink

### Community 17 - "test_providers.py"
Cohesion: 0.11
Nodes (12): CSJuntasGobiernoProvider, __newsmerger_plugin__(), Options, page_title(), parse_article(), parse_preview(), Post, preview_url() (+4 more)

### Community 21 - ".get_annotation_values"
Cohesion: 0.14
Nodes (3): CustomJSON, _encode_value(), UTCDateTime

### Community 22 - "SourceItem"
Cohesion: 0.08
Nodes (6): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options, SourceItem

### Community 24 - "__newsmerger_plugin__"
Cohesion: 0.19
Nodes (4): __newsmerger_plugin__(), ollama_client(), OllamaLLM, OllamaTests

### Community 25 - "SourceData"
Cohesion: 0.09
Nodes (14): HTTPClient, SourceData, discover_feed_url(), entry_date(), fetch_article(), fetch_feed(), find_image(), parse_entry() (+6 more)

### Community 26 - "BaseProcessor"
Cohesion: 0.13
Nodes (3): tags_text(), BaseProcessor, MissingAnnotationError

### Community 27 - "MarkdownifyProcessor"
Cohesion: 0.22
Nodes (5): MarkdownifyProcessor, __newsmerger_plugin__(), SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 28 - "PrensaIbericaPlainProvider"
Cohesion: 0.15
Nodes (3): _extract_href(), __newsmerger_plugin__(), PrensaIbericaPlainProvider

### Community 29 - "cli.py Click commands"
Cohesion: 0.23
Nodes (10): cli.py Click commands, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage, SQLAlchemy models never leave db.py; DTOs cross the boundary, foundation internal library, inspect items|annotations|artifacts|deliveries, Application class (single entry point), Phases: import, enrich, remix, deliver (+2 more)

### Community 31 - "SourceItemData"
Cohesion: 0.12
Nodes (6): SourceItemData, CastellonInformacionProvider, __newsmerger_plugin__(), __newsmerger_plugin__(), PrensaIbericaProvider, TestPrensaIberica

### Community 32 - "PluginOptions"
Cohesion: 0.10
Nodes (10): find_parent_by_tag_name(), get_date_from_text(), __newsmerger_plugin__(), PreparseData, NoOptions, PluginOptions, Options, Options (+2 more)

### Community 33 - "merge_options"
Cohesion: 0.09
Nodes (8): __newsmerger_plugin__(), FeedReaderProvider, __newsmerger_plugin__(), Options, merge_options(), UnavailableRemixer, DigestPluginTests, TestFeedReader

### Community 35 - "DigestRemixer"
Cohesion: 0.20
Nodes (4): DigestOptions, DigestRemixer, Options, DigestRemixerTests

### Community 36 - "RecordingItemSink"
Cohesion: 0.24
Nodes (4): SelectionRequiredError, ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 37 - "delete_items_cmd"
Cohesion: 0.19
Nodes (6): check_found(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), require_selection(), sort_option()

### Community 38 - "config.py"
Cohesion: 0.18
Nodes (4): CacheConfig, DatabaseConfig, expand_variables(), MissingVariableError

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.23
Nodes (12): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger, deliver SINK --force with explicit selection (+4 more)

### Community 40 - "grouping.py"
Cohesion: 0.19
Nodes (5): average_between(), average_link_cluster(), cosine_similarity(), Options, time_decay()

### Community 41 - "report_user_errors"
Cohesion: 0.19
Nodes (8): annotation_options(), artifact_options(), inspect_annotations_cmd(), inspect_artifacts_cmd(), report_user_errors(), wrapper(), scope_options(), wrapper()

### Community 42 - "tagger.py"
Cohesion: 0.27
Nodes (4): strip_code_fence(), merge_tags(), Options, TaggerOptions

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "EmbedProcessor"
Cohesion: 0.33
Nodes (4): EmbedOptions, EmbedProcessor, Options, EmbedTests

### Community 45 - "config.example.yaml"
Cohesion: 0.25
Nodes (5): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), ollama LLM backend, plugins configuration section

### Community 47 - "inspect_items_cmd"
Cohesion: 0.20
Nodes (6): inspect_items_cmd(), print_deliver(), print_item(), print_process(), print_remix(), print_table()

### Community 48 - "migrate_telegram_state.py"
Cohesion: 0.14
Nodes (3): LockedError, write_lock(), main()

### Community 49 - "GoogleChatSink"
Cohesion: 0.14
Nodes (6): GoogleChatError, GoogleChatSink, __newsmerger_plugin__(), Options, WebhookOptions, OptionsTests

### Community 50 - "TelegramSinkTests"
Cohesion: 0.28
Nodes (5): Options, TelegramSink, ok_response(), TelegramSinkTests, TelegramTestCase

### Community 51 - "cli.py"
Cohesion: 0.10
Nodes (6): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content()

### Community 52 - "SummarizeProcessor"
Cohesion: 0.24
Nodes (6): Options, SummarizeOptions, SummarizeProcessor, ProcessorTestCase, SummarizeTests, TaggerTests

### Community 53 - "json"
Cohesion: 0.27
Nodes (5): format_value(), json_default(), preview(), print_json(), setup_logging()

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 57 - "get_section"
Cohesion: 0.29
Nodes (3): get_section(), parse_datetime(), SectionNotFoundError

### Community 58 - "newsmerger CLAUDE.md agent guidelines"
Cohesion: 0.33
Nodes (5): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention

### Community 59 - "StubLLM"
Cohesion: 0.29
Nodes (3): ConsumerPluginTests, ServicesTests, StubLLM

### Community 60 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 61 - "ADR 0001 Item identity and change detection"
Cohesion: 0.40
Nodes (4): IndexSiteProvider / URLProvider, ADR 0001 Item identity and change detection, Item, Provider

### Community 62 - "telegram.py"
Cohesion: 0.14
Nodes (7): build_text(), build_caption(), ItemDeliveryOptions, post(), TelegramError, DeliveryOptions, BuildCaptionTests

### Community 63 - "BaseRemixer"
Cohesion: 0.22
Nodes (4): GroupingOptions, GroupingRemixer, tagged_items(), BaseRemixer

### Community 64 - "TelegramArtifactSink"
Cohesion: 0.20
Nodes (5): DocumentDeliveryOptions, __newsmerger_plugin__(), TelegramArtifactSink, PluginTests, TelegramArtifactSinkTests

### Community 65 - "ScoredItem"
Cohesion: 0.22
Nodes (8): build_score_matrix(), item_ref(), member_payload(), pair_payload(), score_pair(), ScoredItem, single_link_groups(), UnionFind

### Community 68 - "EmbeddingGroupingTests"
Cohesion: 0.33
Nodes (4): EmbeddingsOptions, EmbeddingsRemixer, jaccard(), EmbeddingGroupingTests

### Community 74 - "RecordingArtifactSink"
Cohesion: 0.39
Nodes (3): ArtifactDeliveryOptions, ArtifactSinkTests, RecordingArtifactSink

### Community 77 - "__newsmerger_plugin__"
Cohesion: 0.43
Nodes (3): AverageLinkRemixer, __newsmerger_plugin__(), GroupingPluginTests

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)`, `PluginOptions (pydantic, unknown keys rejected)`, `Annotation` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 418 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_db.py`, `LLMUnavailableError`, `db.py`, `Artifact`, `Application`, `FeedGeneratorRemixer`, `GroupingTests`, `.session_scope`, `Remixer`, `ProcessingScope`, `app.py`, `DeliveryStatus`, `.get_item_deliveries`, `.get_annotation_values`, `SourceItem`, `SourceData`, `BaseProcessor`, `MarkdownifyProcessor`, `.close`, `merge_options`, `DigestRemixer`, `RecordingItemSink`, `grouping.py`, `tagger.py`, `EmbedProcessor`, `LLM`, `migrate_telegram_state.py`, `GoogleChatSink`, `TelegramSinkTests`, `SummarizeProcessor`, `telegram.py`, `BaseRemixer`, `TelegramArtifactSink`, `ScoredItem`, `EmbeddingGroupingTests`, `RecordingArtifactSink`, `.get_artifact`, `.__init__`, `__newsmerger_plugin__`, `Annotation`, `Processor`, `.save_artifact`?**
  _High betweenness centrality (0.159) - this node is a cross-community bridge._
- **Are the 44 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 44 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05101807366735301 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `ProcessingScope` to `test_db.py`, `LLMUnavailableError`, `db.py`, `invoke`, `ApplicationTests`, `Artifact`, `Application`, `FeedGeneratorRemixer`, `GroupingTests`, `.session_scope`, `app_from_context`, `Remixer`, `app.py`, `DeliveryStatus`, `.get_item_deliveries`, `SourceItem`, `Database`, `BaseProcessor`, `merge_options`, `DigestRemixer`, `RecordingItemSink`, `delete_items_cmd`, `grouping.py`, `report_user_errors`, `inspect_items_cmd`, `migrate_telegram_state.py`, `cli.py`, `BaseRemixer`, `EmbeddingGroupingTests`, `Annotation`, `Processor`, `.save_artifact`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Should `LLMUnavailableError` be split into smaller, more focused modules?**
  _Cohesion score 0.1437908496732026 - nodes in this community are weakly interconnected._