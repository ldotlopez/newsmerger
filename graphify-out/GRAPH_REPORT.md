# Graph Report - workflows-plan  (2026-10-27)

## Corpus Check
- 67 files · ~115,248 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1428 nodes · 4217 edges · 69 communities (48 shown, 21 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 582 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8f7a00fd`
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
- MigrateAutoincrementTests
- FeedGeneratorRemixer
- GroupingTests
- DeleteCommandTests
- app_from_context
- Delivery
- Config
- ProcessingScope
- RunSummary
- BaseSink
- TelegramChannelProvider
- .get_item_deliveries
- run_cmd
- Base
- .from_text
- SourceItem
- SourceData
- Database
- markdownify.py
- PrensaIbericaPlainProvider
- cli.py Click commands
- SourceItemData
- CSJuntasGobiernoProvider
- feedreader.py
- ConfigError
- DigestRemixer
- RecordingItemSink
- app.py
- ADR 0007 Sinks and the delivery ledger
- digest.py
- report_user_errors
- Services object (services.llm(name))
- EmbedProcessor
- config.example.yaml
- .session_scope
- PluginOptions
- LogLevelTests
- OptionsTests
- .__init__
- cli.py
- __newsmerger_plugin__
- inspect_items_cmd
- Processor
- El Periódico Mediterráneo
- expand_variables
- PlazaProvider
- newsmerger CLAUDE.md agent guidelines
- delete_items_cmd
- deliveries table (the ledger)
- ADR 0001 Item identity and change detection
- sinks.py
- grouping.py
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
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
9. `PluginOptions` - 46 edges
10. `ApplicationTests` - 46 edges

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

## Communities (69 total, 21 thin omitted)

### Community 0 - "make_item"
Cohesion: 0.08
Nodes (11): DBSourceItem, AnnotationTests, ConnectionTests, ContentStorageTests, DatabaseTestCase, DeleteTests, IdentityTests, make_item() (+3 more)

### Community 1 - "Services"
Cohesion: 0.09
Nodes (12): LLM, LLMUnavailableError, strip_code_fence(), __newsmerger_plugin__(), Services, __newsmerger_plugin__(), __newsmerger_plugin__(), Processor (+4 more)

### Community 2 - "db.py"
Cohesion: 0.15
Nodes (5): DeliveryStatus, ProcessingStatus, _sha256_column(), Annotation, migrate()

### Community 3 - "invoke"
Cohesion: 0.22
Nodes (3): annotation(), InspectCommandTests, invoke()

### Community 5 - "Artifact"
Cohesion: 0.05
Nodes (18): DBArtifact, Artifact, __newsmerger_plugin__(), Options, TelegramArtifactSink, TelegramClient, TelegramError, TelegramSink (+10 more)

### Community 8 - "FeedGeneratorRemixer"
Cohesion: 0.27
Nodes (3): FeedGeneratorRemixer, Options, FeedGeneratorTests

### Community 9 - "GroupingTests"
Cohesion: 0.25
Nodes (3): EmbeddingGroupingTests, GroupingTests, RemixerTestCase

### Community 11 - "app_from_context"
Cohesion: 0.15
Nodes (9): app_from_context(), cli(), deliver_cmd(), inspect_content_cmd(), inspect_deliveries_cmd(), parse_artifact_ids(), process_cmd(), resolve_cmd() (+1 more)

### Community 12 - "Delivery"
Cohesion: 0.11
Nodes (4): DBDelivery, Delivery, BaseArtifactSink, BaseItemSink

### Community 13 - "Config"
Cohesion: 0.16
Nodes (8): delivery_runs(), entry_location(), process_runs(), referenced_plugins(), remix_runs(), Run, Config, Workflow

### Community 14 - "ProcessingScope"
Cohesion: 0.19
Nodes (3): ProcessingScope, DeliveryTests, GetItemsTests

### Community 17 - "TelegramChannelProvider"
Cohesion: 0.13
Nodes (9): __newsmerger_plugin__(), Options, page_title(), parse_article(), parse_preview(), Post, TelegramChannelProvider, read_sample() (+1 more)

### Community 20 - "run_cmd"
Cohesion: 0.12
Nodes (9): import_cmd(), import_sources(), print_process(), print_remix(), progress_rows(), remix_cmd(), run_cmd(), run_each() (+1 more)

### Community 21 - "Base"
Cohesion: 0.12
Nodes (5): Base, CustomJSON, DBItemAnnotation, _encode_value(), UTCDateTime

### Community 23 - "SourceItem"
Cohesion: 0.09
Nodes (4): SourceItem, GoogleChatError, GoogleChatSink, SearchTests

### Community 25 - "SourceData"
Cohesion: 0.08
Nodes (10): DBSource, HTTPClient, SourceData, CastellonInformacionProvider, fetch_article(), is_home_page(), preview_url(), TheGuardianProvider (+2 more)

### Community 26 - "Database"
Cohesion: 0.09
Nodes (7): Database, tags_text(), SummarizeProcessor, merge_tags(), TaggerProcessor, BaseProcessor, MissingAnnotationError

### Community 27 - "markdownify.py"
Cohesion: 0.16
Nodes (7): NoOptions, MarkdownifyProcessor, __newsmerger_plugin__(), Options, SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 28 - "PrensaIbericaPlainProvider"
Cohesion: 0.15
Nodes (3): _extract_href(), __newsmerger_plugin__(), PrensaIbericaPlainProvider

### Community 29 - "cli.py Click commands"
Cohesion: 0.23
Nodes (10): cli.py Click commands, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage, SQLAlchemy models never leave db.py; DTOs cross the boundary, foundation internal library, inspect items|annotations|artifacts|deliveries, Application class (single entry point), Phases: import, enrich, remix, deliver (+2 more)

### Community 31 - "SourceItemData"
Cohesion: 0.20
Nodes (4): SourceItemData, PrensaIbericaProvider, TestPrensaIberica, TestSourceItemDataContent

### Community 32 - "CSJuntasGobiernoProvider"
Cohesion: 0.19
Nodes (5): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, TestCSJuntasGobierno

### Community 33 - "feedreader.py"
Cohesion: 0.12
Nodes (10): discover_feed_url(), entry_date(), FeedReaderProvider, fetch_feed(), find_image(), __newsmerger_plugin__(), Options, parse_entry() (+2 more)

### Community 34 - "ConfigError"
Cohesion: 0.11
Nodes (6): load_plugins(), objects_by_name(), source_options(), workflow_scope(), ConfigError, options_error()

### Community 35 - "DigestRemixer"
Cohesion: 0.23
Nodes (3): DigestRemixer, Options, DigestRemixerTests

### Community 36 - "RecordingItemSink"
Cohesion: 0.11
Nodes (4): SelectionRequiredError, ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 38 - "app.py"
Cohesion: 0.06
Nodes (11): LockedError, write_lock(), CacheConfig, DatabaseConfig, main(), migrate(), needs_autoincrement(), recreate() (+3 more)

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.23
Nodes (12): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger, deliver SINK --force with explicit selection (+4 more)

### Community 40 - "digest.py"
Cohesion: 0.13
Nodes (5): __newsmerger_plugin__(), __newsmerger_plugin__(), Remixer, UnavailableRemixer, DigestPluginTests

### Community 41 - "report_user_errors"
Cohesion: 0.19
Nodes (8): annotation_options(), artifact_options(), inspect_annotations_cmd(), preview(), report_user_errors(), wrapper(), scope_options(), wrapper()

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "EmbedProcessor"
Cohesion: 0.08
Nodes (11): EmbedOptions, EmbedProcessor, Options, Options, SummarizeOptions, Options, TaggerOptions, EmbedTests (+3 more)

### Community 45 - "config.example.yaml"
Cohesion: 0.25
Nodes (5): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), ollama LLM backend, plugins configuration section

### Community 47 - "PluginOptions"
Cohesion: 0.17
Nodes (6): __newsmerger_plugin__(), __newsmerger_plugin__(), PluginOptions, __newsmerger_plugin__(), __newsmerger_plugin__(), Provider

### Community 49 - "OptionsTests"
Cohesion: 0.24
Nodes (3): Options, WebhookOptions, OptionsTests

### Community 51 - "cli.py"
Cohesion: 0.09
Nodes (7): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content(), setup_logging()

### Community 52 - "__newsmerger_plugin__"
Cohesion: 0.18
Nodes (5): __newsmerger_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 53 - "inspect_items_cmd"
Cohesion: 0.16
Nodes (10): check_found(), format_value(), inspect_artifacts_cmd(), inspect_items_cmd(), json_default(), print_deliver(), print_import(), print_item() (+2 more)

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 56 - "expand_variables"
Cohesion: 0.12
Nodes (3): expand_variables(), MissingVariableError, ProcessEntry

### Community 57 - "PlazaProvider"
Cohesion: 0.17
Nodes (5): get_section(), __newsmerger_plugin__(), parse_datetime(), PlazaProvider, SectionNotFoundError

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

### Community 62 - "sinks.py"
Cohesion: 0.09
Nodes (11): backoff_seconds(), build_text(), __newsmerger_plugin__(), build_caption(), DocumentDeliveryOptions, ItemDeliveryOptions, ArtifactDeliveryOptions, DeliveryOptions (+3 more)

### Community 65 - "grouping.py"
Cohesion: 0.08
Nodes (23): average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer, GroupingOptions (+15 more)

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)`, `PluginOptions (pydantic, unknown keys rejected)`, `Annotation` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 409 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `make_item`, `Services`, `db.py`, `Artifact`, `Application`, `MigrateAutoincrementTests`, `FeedGeneratorRemixer`, `GroupingTests`, `DeleteCommandTests`, `Delivery`, `Config`, `ProcessingScope`, `BaseSink`, `.get_item_deliveries`, `Base`, `SourceItem`, `SourceData`, `markdownify.py`, `DigestRemixer`, `RecordingItemSink`, `app.py`, `digest.py`, `EmbedProcessor`, `.session_scope`, `.__init__`, `sinks.py`, `grouping.py`?**
  _High betweenness centrality (0.177) - this node is a cross-community bridge._
- **Are the 44 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 44 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `make_item` be split into smaller, more focused modules?**
  _Cohesion score 0.08302485457429931 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `ProcessingScope` to `make_item`, `Services`, `db.py`, `invoke`, `ApplicationTests`, `Artifact`, `Application`, `FeedGeneratorRemixer`, `GroupingTests`, `DeleteCommandTests`, `app_from_context`, `Delivery`, `RunSummary`, `BaseSink`, `.get_item_deliveries`, `run_cmd`, `SourceItem`, `.find_deliveries`, `Database`, `ConfigError`, `DigestRemixer`, `RecordingItemSink`, `app.py`, `digest.py`, `report_user_errors`, `EmbedProcessor`, `cli.py`, `inspect_items_cmd`, `delete_items_cmd`, `sinks.py`, `grouping.py`?**
  _High betweenness centrality (0.152) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Should `Services` be split into smaller, more focused modules?**
  _Cohesion score 0.08831168831168831 - nodes in this community are weakly interconnected._