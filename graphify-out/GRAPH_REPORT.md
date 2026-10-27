# Graph Report - workflows-plan  (2026-10-27)

## Corpus Check
- 67 files · ~115,444 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1429 nodes · 4220 edges · 75 communities (47 shown, 28 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 582 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `293150d5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- make_item
- Services
- db.py
- RunSummary
- ApplicationTests
- Artifact
- Application
- migrate
- FeedGeneratorRemixer
- GroupingTests
- DeleteCommandTests
- inspect_deliveries_cmd
- merge_options
- .run_delivery
- run_cmd
- EmbeddingsRemixer
- BaseSink
- TelegramChannelProvider
- DeliveryStatus
- run_cmd
- Base
- .from_text
- SourceItem
- GroupingRemixer
- SourceData
- Database
- markdownify.py
- PrensaIbericaPlainProvider
- cli.py Click commands
- single_link_groups
- SourceItemData
- CSJuntasGobiernoProvider
- feedreader.py
- Config
- DigestRemixer
- RecordingItemSink
- __newsmerger_plugin__
- app.py
- ADR 0007 Sinks and the delivery ledger
- db.py
- report_user_errors
- EmbeddingGroupingTests
- Services object (services.llm(name))
- EmbedProcessor
- config.example.yaml
- PluginOptions
- main
- OptionsTests
- .__init__
- cli.py
- __newsmerger_plugin__
- Any
- Processor
- El Periódico Mediterráneo
- expand_variables
- PlazaProvider
- newsmerger CLAUDE.md agent guidelines
- app_from_context
- deliveries table (the ledger)
- ADR 0001 Item identity and change detection
- sinks.py
- Options
- GoogleChatError
- ScoredItem
- tagged_items
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- MissingAnnotationError
- Artifact
- Grouping notes: NLP clustering pipeline
- news-aggregator
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
9. `ApplicationTests` - 47 edges
10. `PluginOptions` - 46 edges

## Surprising Connections (you probably didn't know these)
- `newsmerger README` --references--> `Phases: import, enrich, remix, deliver`  [INFERRED]
  README.md → docs/SPECIFICATION.md
- `main()` --uses--> `LockedError`  [INFERRED]
  scripts/migrate_autoincrement.py → newsmerger/app.py
- `main()` --uses--> `LockedError`  [INFERRED]
  scripts/migrate_telegram_state.py → newsmerger/app.py
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

## Communities (75 total, 28 thin omitted)

### Community 0 - "make_item"
Cohesion: 0.05
Nodes (18): Base, DBDelivery, DBItemAnnotation, DBProcessingState, DBSource, DBSourceItem, AnnotationTests, ConnectionTests (+10 more)

### Community 1 - "Services"
Cohesion: 0.08
Nodes (14): LLMUnavailableError, strip_code_fence(), __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), Services, __newsmerger_plugin__(), __newsmerger_plugin__() (+6 more)

### Community 3 - "RunSummary"
Cohesion: 0.10
Nodes (6): RunSummary, annotation(), CommandTests, InspectCommandTests, invoke(), LogLevelTests

### Community 5 - "Artifact"
Cohesion: 0.06
Nodes (15): DBArtifact, Artifact, Options, TelegramArtifactSink, TelegramClient, TelegramError, TelegramSink, ArtifactTests (+7 more)

### Community 6 - "Application"
Cohesion: 0.06
Nodes (3): Application, lookup(), import_sources()

### Community 7 - "migrate"
Cohesion: 0.16
Nodes (5): main(), migrate(), needs_autoincrement(), recreate(), MigrateAutoincrementTests

### Community 11 - "inspect_deliveries_cmd"
Cohesion: 0.18
Nodes (5): cli(), inspect_content_cmd(), inspect_deliveries_cmd(), resolve_cmd(), search_cmd()

### Community 14 - "run_cmd"
Cohesion: 0.24
Nodes (6): print_deliver(), print_import(), print_process(), print_remix(), print_table(), run_cmd()

### Community 15 - "EmbeddingsRemixer"
Cohesion: 0.28
Nodes (4): cosine_similarity(), EmbeddingsRemixer, jaccard(), time_decay()

### Community 16 - "BaseSink"
Cohesion: 0.08
Nodes (4): Delivery, BaseArtifactSink, BaseItemSink, BaseSink

### Community 17 - "TelegramChannelProvider"
Cohesion: 0.10
Nodes (12): CSJuntasGobiernoProvider, __newsmerger_plugin__(), Options, page_title(), parse_article(), parse_preview(), Post, preview_url() (+4 more)

### Community 18 - "DeliveryStatus"
Cohesion: 0.12
Nodes (4): DeliveryStatus, migrate(), GoogleChatSinkTests, MigrateTelegramStateTests

### Community 20 - "run_cmd"
Cohesion: 0.16
Nodes (7): deliver_cmd(), import_cmd(), process_cmd(), progress_rows(), remix_cmd(), run_each(), DeliveryEntry

### Community 21 - "Base"
Cohesion: 0.13
Nodes (3): CustomJSON, _encode_value(), UTCDateTime

### Community 23 - "SourceItem"
Cohesion: 0.10
Nodes (5): Database, SourceItem, FeedGeneratorRemixer, GoogleChatSink, make_item()

### Community 24 - "GroupingRemixer"
Cohesion: 0.28
Nodes (5): AverageLinkRemixer, EmbeddingsOptions, GroupingOptions, GroupingRemixer, SingleLinkRemixer

### Community 25 - "SourceData"
Cohesion: 0.10
Nodes (9): HTTPClient, SourceData, CastellonInformacionProvider, fetch_article(), PlazaProvider, is_home_page(), TheGuardianProvider, IndexSiteProvider (+1 more)

### Community 26 - "Database"
Cohesion: 0.13
Nodes (4): tags_text(), merge_tags(), TaggerProcessor, BaseProcessor

### Community 27 - "markdownify.py"
Cohesion: 0.16
Nodes (7): NoOptions, MarkdownifyProcessor, __newsmerger_plugin__(), Options, SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 29 - "cli.py Click commands"
Cohesion: 0.23
Nodes (10): cli.py Click commands, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage, SQLAlchemy models never leave db.py; DTOs cross the boundary, foundation internal library, inspect items|annotations|artifacts|deliveries, Application class (single entry point), Phases: import, enrich, remix, deliver (+2 more)

### Community 31 - "SourceItemData"
Cohesion: 0.17
Nodes (4): SourceItemData, PrensaIbericaProvider, TestPrensaIberica, TestSourceItemDataContent

### Community 32 - "CSJuntasGobiernoProvider"
Cohesion: 0.33
Nodes (3): find_parent_by_tag_name(), get_date_from_text(), PreparseData

### Community 33 - "feedreader.py"
Cohesion: 0.16
Nodes (9): discover_feed_url(), entry_date(), FeedReaderProvider, fetch_feed(), find_image(), __newsmerger_plugin__(), Options, parse_entry() (+1 more)

### Community 34 - "Config"
Cohesion: 0.13
Nodes (5): load_plugins(), objects_by_name(), referenced_plugins(), source_options(), Config

### Community 35 - "DigestRemixer"
Cohesion: 0.16
Nodes (5): ProcessingScope, DigestRemixer, Options, SearchTests, DigestRemixerTests

### Community 36 - "RecordingItemSink"
Cohesion: 0.11
Nodes (4): SelectionRequiredError, ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 38 - "app.py"
Cohesion: 0.06
Nodes (15): delivery_runs(), entry_location(), LockedError, process_runs(), remix_runs(), Run, write_lock(), CacheConfig (+7 more)

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.23
Nodes (12): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger, deliver SINK --force with explicit selection (+4 more)

### Community 40 - "db.py"
Cohesion: 0.12
Nodes (5): backoff_seconds(), _sha256_column(), Annotation, BaseRemixer, Remixer

### Community 41 - "report_user_errors"
Cohesion: 0.23
Nodes (7): annotation_options(), artifact_options(), inspect_annotations_cmd(), report_user_errors(), wrapper(), scope_options(), wrapper()

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "EmbedProcessor"
Cohesion: 0.07
Nodes (14): LLM, EmbedOptions, EmbedProcessor, Options, Options, SummarizeOptions, SummarizeProcessor, Processor (+6 more)

### Community 45 - "config.example.yaml"
Cohesion: 0.25
Nodes (5): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), ollama LLM backend, plugins configuration section

### Community 47 - "PluginOptions"
Cohesion: 0.13
Nodes (8): __newsmerger_plugin__(), __newsmerger_plugin__(), PluginOptions, __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), Provider

### Community 49 - "OptionsTests"
Cohesion: 0.17
Nodes (4): __newsmerger_plugin__(), Options, WebhookOptions, OptionsTests

### Community 51 - "cli.py"
Cohesion: 0.09
Nodes (6): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content()

### Community 52 - "__newsmerger_plugin__"
Cohesion: 0.18
Nodes (5): __newsmerger_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 53 - "Any"
Cohesion: 0.20
Nodes (6): format_value(), json_default(), preview(), print_item(), print_json(), setup_logging()

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 57 - "PlazaProvider"
Cohesion: 0.29
Nodes (3): get_section(), parse_datetime(), SectionNotFoundError

### Community 58 - "newsmerger CLAUDE.md agent guidelines"
Cohesion: 0.33
Nodes (5): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention

### Community 59 - "app_from_context"
Cohesion: 0.13
Nodes (10): app_from_context(), check_found(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), inspect_artifacts_cmd(), inspect_items_cmd(), parse_artifact_ids() (+2 more)

### Community 60 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 61 - "ADR 0001 Item identity and change detection"
Cohesion: 0.40
Nodes (4): IndexSiteProvider / URLProvider, ADR 0001 Item identity and change detection, Item, Provider

### Community 62 - "sinks.py"
Cohesion: 0.13
Nodes (10): build_text(), build_caption(), DocumentDeliveryOptions, ItemDeliveryOptions, __newsmerger_plugin__(), ArtifactDeliveryOptions, DeliveryOptions, Sink (+2 more)

### Community 65 - "ScoredItem"
Cohesion: 0.22
Nodes (8): average_between(), average_link_cluster(), build_score_matrix(), item_ref(), member_payload(), pair_payload(), score_pair(), ScoredItem

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)`, `PluginOptions (pydantic, unknown keys rejected)`, `Annotation` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 409 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `SourceItem` to `make_item`, `Services`, `db.py`, `Artifact`, `Application`, `migrate`, `GroupingTests`, `DeleteCommandTests`, `EmbeddingsRemixer`, `BaseSink`, `DeliveryStatus`, `Base`, `GroupingRemixer`, `SourceData`, `Database`, `markdownify.py`, `Config`, `DigestRemixer`, `RecordingItemSink`, `app.py`, `db.py`, `EmbedProcessor`, `.session_scope`, `main`, `.__init__`, `sinks.py`, `ScoredItem`?**
  _High betweenness centrality (0.173) - this node is a cross-community bridge._
- **Are the 44 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 44 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `make_item` be split into smaller, more focused modules?**
  _Cohesion score 0.05101807366735301 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `DigestRemixer` to `make_item`, `Services`, `db.py`, `RunSummary`, `ApplicationTests`, `Artifact`, `Application`, `FeedGeneratorRemixer`, `GroupingTests`, `DeleteCommandTests`, `inspect_deliveries_cmd`, `.run_delivery`, `BaseSink`, `DeliveryStatus`, `run_cmd`, `Base`, `SourceItem`, `GroupingRemixer`, `Database`, `RecordingItemSink`, `app.py`, `db.py`, `report_user_errors`, `EmbeddingGroupingTests`, `EmbedProcessor`, `cli.py`, `app_from_context`, `sinks.py`?**
  _High betweenness centrality (0.149) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Should `Services` be split into smaller, more focused modules?**
  _Cohesion score 0.07505285412262157 - nodes in this community are weakly interconnected._