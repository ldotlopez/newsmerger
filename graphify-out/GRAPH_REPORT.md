# Graph Report - newsmerger  (2026-10-26)

## Corpus Check
- 65 files · ~108,808 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .lock 1)

## Summary
- 1300 nodes · 3777 edges · 74 communities (48 shown, 26 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 506 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f52b6732`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ORM Models & Ledger Rows
- Services
- db.py
- test_cli.py
- ApplicationTests
- ScoredItem
- Application
- sinks.py
- Remixer
- LockedError
- DeleteCommandTests
- app_from_context
- DeliveryStatus
- Artifact
- Services
- Sink Delivery Cycle
- Telegram Channel Parsing
- cli.py
- migrate_feed_names.py
- run_cmd
- db.py
- .from_text
- SourceItem
- SourceData
- IndexSiteProvider
- Markdownify Processor
- Prensa Iberica Plain Provider
- Inspect/Delete CLI Decision
- TestFeedReader
- PluginOptions
- CSJuntasGobiernoProvider
- SourceItemData
- Plugin Loading
- ProcessingScope
- .close
- Database
- migrate_autoincrement.py
- Architecture & Processing ADRs
- models.py
- Selection CLI Options
- delete_items_cmd
- Processor & Remixer Bundles
- ollama.py
- Plugin System Docs
- GroupingRemixer
- get_section
- expand_variables
- .__init__
- inspect_annotations_cmd
- single_link_groups
- OllamaLLM
- Spec Glossary Entities
- Sample Pages & Formats
- config.py
- EmbeddingGroupingTests
- Agent Conventions
- Options
- Side-Effect Remixers ADR
- Item Identity ADR
- feedreader.py
- MissingAnnotationError
- Item Data Validation Tests
- GroupingTests
- grouping.py
- Example Sources
- Artifact & Remixer
- Grouping Notes
- News Aggregator
- ADR 0002 Processing state lifecycle

## God Nodes (most connected - your core abstractions)
1. `Database` - 157 edges
2. `ProcessingScope` - 141 edges
3. `SourceItem` - 114 edges
4. `SourceData` - 80 edges
5. `Artifact` - 62 edges
6. `Services` - 55 edges
7. `Application` - 53 edges
8. `SourceItemData` - 49 edges
9. `HTTPClient` - 44 edges
10. `PluginOptions` - 39 edges

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

## Communities (74 total, 26 thin omitted)

### Community 0 - "ORM Models & Ledger Rows"
Cohesion: 0.08
Nodes (12): DBSourceItem, AnnotationTests, ConnectionTests, ContentStorageTests, DatabaseTestCase, DeleteTests, GetItemsTests, IdentityTests (+4 more)

### Community 1 - "Services"
Cohesion: 0.07
Nodes (21): LLM, LLMUnavailableError, strip_code_fence(), EmbedProcessor, __newsmerger_plugin__(), Options, tags_text(), __newsmerger_plugin__() (+13 more)

### Community 3 - "test_cli.py"
Cohesion: 0.08
Nodes (8): cli(), Annotation, RunSummary, annotation(), CommandTests, InspectCommandTests, invoke(), LogLevelTests

### Community 5 - "ScoredItem"
Cohesion: 0.22
Nodes (8): average_between(), average_link_cluster(), build_score_matrix(), item_ref(), member_payload(), pair_payload(), score_pair(), ScoredItem

### Community 7 - "sinks.py"
Cohesion: 0.13
Nodes (3): BaseArtifactSink, BaseItemSink, UnavailableSink

### Community 8 - "Remixer"
Cohesion: 0.21
Nodes (4): __newsmerger_plugin__(), __newsmerger_plugin__(), Remixer, GroupingPluginTests

### Community 9 - "LockedError"
Cohesion: 0.20
Nodes (3): LockedError, write_lock(), main()

### Community 11 - "app_from_context"
Cohesion: 0.15
Nodes (9): delete_annotations_cmd(), deliver_cmd(), enrich_cmd(), import_cmd(), inspect_content_cmd(), inspect_deliveries_cmd(), parse_artifact_ids(), resolve_cmd() (+1 more)

### Community 12 - "DeliveryStatus"
Cohesion: 0.10
Nodes (4): DBDelivery, DeliveryStatus, Delivery, migrate()

### Community 13 - "Artifact"
Cohesion: 0.05
Nodes (22): DBArtifact, Artifact, ArtifactSinkOptions, build_caption(), ItemSinkOptions, __newsmerger_plugin__(), Options, TelegramArtifactSink (+14 more)

### Community 14 - "Services"
Cohesion: 0.12
Nodes (8): __newsmerger_plugin__(), Services, __newsmerger_plugin__(), UnavailableRemixer, DigestPluginTests, ConsumerPluginTests, ServicesTests, StubLLM

### Community 17 - "Telegram Channel Parsing"
Cohesion: 0.13
Nodes (9): is_home_page(), page_title(), parse_article(), parse_preview(), Post, preview_url(), TelegramChannelProvider, read_sample() (+1 more)

### Community 18 - "cli.py"
Cohesion: 0.09
Nodes (6): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content()

### Community 19 - "migrate_feed_names.py"
Cohesion: 0.19
Nodes (3): main(), migrate(), MigrateFeedNamesTests

### Community 20 - "run_cmd"
Cohesion: 0.17
Nodes (6): import_sources(), print_remix(), progress_rows(), remix_cmd(), run_cmd(), run_each()

### Community 21 - "db.py"
Cohesion: 0.13
Nodes (4): CustomJSON, DBItemAnnotation, _sha256_column(), UTCDateTime

### Community 23 - "SourceItem"
Cohesion: 0.10
Nodes (4): SourceItem, DigestRemixer, FeedGeneratorRemixer, SearchTests

### Community 24 - "SourceData"
Cohesion: 0.13
Nodes (3): DBSource, SourceData, CastellonInformacionProvider

### Community 25 - "IndexSiteProvider"
Cohesion: 0.15
Nodes (3): TheGuardianProvider, IndexSiteProvider, TestHTTPClient

### Community 27 - "Markdownify Processor"
Cohesion: 0.16
Nodes (6): MarkdownifyProcessor, __newsmerger_plugin__(), PartialFailure, SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 29 - "Inspect/Delete CLI Decision"
Cohesion: 0.23
Nodes (10): cli.py Click commands, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage, SQLAlchemy models never leave db.py; DTOs cross the boundary, foundation internal library, inspect items|annotations|artifacts|deliveries, Application class (single entry point), Phases: import, enrich, remix, deliver (+2 more)

### Community 31 - "PluginOptions"
Cohesion: 0.10
Nodes (9): __newsmerger_plugin__(), Options, Options, PluginOptions, Options, __newsmerger_plugin__(), __newsmerger_plugin__(), Options (+1 more)

### Community 32 - "CSJuntasGobiernoProvider"
Cohesion: 0.18
Nodes (6): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), __newsmerger_plugin__(), PreparseData, TestCSJuntasGobierno

### Community 33 - "SourceItemData"
Cohesion: 0.31
Nodes (3): SourceItemData, PrensaIbericaProvider, TestPrensaIberica

### Community 34 - "Plugin Loading"
Cohesion: 0.13
Nodes (6): check_provider_options(), load_plugins(), lookup(), objects_by_name(), ConfigError, plugin_options_error()

### Community 35 - "ProcessingScope"
Cohesion: 0.14
Nodes (4): ProcessingScope, BaseRemixer, DeliveryTests, DigestRemixerTests

### Community 36 - ".close"
Cohesion: 0.10
Nodes (4): SelectionRequiredError, ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 37 - "Database"
Cohesion: 0.09
Nodes (3): Database, DBProcessingState, _encode_value()

### Community 38 - "migrate_autoincrement.py"
Cohesion: 0.13
Nodes (7): Base, main(), migrate(), needs_autoincrement(), recreate(), make_item(), MigrateAutoincrementTests

### Community 39 - "Architecture & Processing ADRs"
Cohesion: 0.23
Nodes (12): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger, deliver SINK --force with explicit selection (+4 more)

### Community 40 - "models.py"
Cohesion: 0.17
Nodes (3): HTTPClient, Options, Provider

### Community 41 - "Selection CLI Options"
Cohesion: 0.23
Nodes (7): annotation_options(), artifact_options(), inspect_annotations_cmd(), report_user_errors(), wrapper(), scope_options(), wrapper()

### Community 42 - "delete_items_cmd"
Cohesion: 0.24
Nodes (5): check_found(), delete_artifacts_cmd(), delete_items_cmd(), require_selection(), sort_option()

### Community 43 - "Processor & Remixer Bundles"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "ollama.py"
Cohesion: 0.24
Nodes (4): __newsmerger_plugin__(), ollama_client(), Options, OllamaTests

### Community 45 - "Plugin System Docs"
Cohesion: 0.25
Nodes (5): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), ollama LLM backend, plugins configuration section

### Community 46 - "GroupingRemixer"
Cohesion: 0.28
Nodes (5): AverageLinkRemixer, EmbeddingsOptions, GroupingOptions, GroupingRemixer, SingleLinkRemixer

### Community 47 - "get_section"
Cohesion: 0.17
Nodes (5): get_section(), __newsmerger_plugin__(), parse_datetime(), PlazaProvider, SectionNotFoundError

### Community 51 - "inspect_annotations_cmd"
Cohesion: 0.11
Nodes (12): format_value(), inspect_artifacts_cmd(), inspect_items_cmd(), json_default(), preview(), print_deliver(), print_enrich(), print_import() (+4 more)

### Community 54 - "Spec Glossary Entities"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "Sample Pages & Formats"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 56 - "config.py"
Cohesion: 0.18
Nodes (3): CacheConfig, Config, DatabaseConfig

### Community 58 - "Agent Conventions"
Cohesion: 0.33
Nodes (5): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention

### Community 60 - "Side-Effect Remixers ADR"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 61 - "Item Identity ADR"
Cohesion: 0.40
Nodes (4): IndexSiteProvider / URLProvider, ADR 0001 Item identity and change detection, Item, Provider

### Community 62 - "feedreader.py"
Cohesion: 0.26
Nodes (7): discover_feed_url(), entry_date(), fetch_article(), fetch_feed(), find_image(), __newsmerger_plugin__(), parse_entry()

### Community 65 - "GroupingTests"
Cohesion: 0.25
Nodes (3): FeedGeneratorTests, GroupingTests, RemixerTestCase

### Community 66 - "grouping.py"
Cohesion: 0.20
Nodes (5): cosine_similarity(), EmbeddingsRemixer, jaccard(), tagged_items(), time_decay()

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)`, `PluginOptions (pydantic, unknown keys rejected)`, `Annotation` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 374 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `ORM Models & Ledger Rows`, `Services`, `db.py`, `test_cli.py`, `ScoredItem`, `Application`, `sinks.py`, `Remixer`, `LockedError`, `DeleteCommandTests`, `DeliveryStatus`, `Artifact`, `Services`, `.select`, `Sink Delivery Cycle`, `migrate_feed_names.py`, `db.py`, `SourceItem`, `SourceData`, `.require_annotation`, `Markdownify Processor`, `PluginOptions`, `Plugin Loading`, `ProcessingScope`, `.close`, `migrate_autoincrement.py`, `models.py`, `GroupingRemixer`, `.__init__`, `config.py`, `GroupingTests`, `grouping.py`?**
  _High betweenness centrality (0.172) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 43 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ORM Models & Ledger Rows` be split into smaller, more focused modules?**
  _Cohesion score 0.07901668129938542 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `ProcessingScope` to `ORM Models & Ledger Rows`, `Services`, `db.py`, `test_cli.py`, `ApplicationTests`, `Application`, `sinks.py`, `Remixer`, `DeleteCommandTests`, `app_from_context`, `DeliveryStatus`, `Artifact`, `Services`, `Sink Delivery Cycle`, `cli.py`, `run_cmd`, `db.py`, `SourceItem`, `.require_annotation`, `Plugin Loading`, `.close`, `Database`, `models.py`, `Selection CLI Options`, `delete_items_cmd`, `GroupingRemixer`, `inspect_annotations_cmd`, `config.py`, `EmbeddingGroupingTests`, `GroupingTests`, `grouping.py`?**
  _High betweenness centrality (0.147) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Should `Services` be split into smaller, more focused modules?**
  _Cohesion score 0.06845238095238096 - nodes in this community are weakly interconnected._