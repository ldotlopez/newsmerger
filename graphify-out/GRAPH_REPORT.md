# Graph Report - enrich-entries  (2026-10-26)

## Corpus Check
- 65 files · ~111,195 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1325 nodes · 3832 edges · 70 communities (41 shown, 29 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 509 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `22dabcf2`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- Services
- db.py
- invoke
- ApplicationTests
- Artifact
- Application
- ProcessingScope
- FeedGeneratorRemixer
- .close
- .session_scope
- app_from_context
- DeliveryStatus
- test_telegram.py
- StubLLM
- TelegramTestCase
- BaseSink
- test_providers.py
- cli.py
- migrate
- run_cmd
- .get_annotation_values
- Config
- SourceItem
- TelegramClient
- SourceData
- BaseProcessor
- markdownify.py
- .parse_index
- cli.py Click commands
- TestFeedReader
- __newsmerger_plugin__
- get_date_from_text
- RunSummary
- app.py
- DigestRemixerTests
- RecordingItemSink
- DBProcessingState
- migrate_autoincrement.py
- ADR 0007 Sinks and the delivery ledger
- models.py
- report_user_errors
- Processor
- Services object (services.llm(name))
- EmbedProcessor
- config.example.yaml
- Database
- get_section
- LogLevelTests
- .__init__
- inspect_deliveries_cmd
- DigestRemixer
- __newsmerger_plugin__
- Processor
- El Periódico Mediterráneo
- config.py
- newsmerger CLAUDE.md agent guidelines
- deliveries table (the ledger)
- ADR 0001 Item identity and change detection
- parse_entry
- .require_annotation
- TestSourceItemDataContent
- grouping.py
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- Artifact
- Grouping notes: NLP clustering pipeline
- news-aggregator
- ADR 0002 Processing state lifecycle

## God Nodes (most connected - your core abstractions)
1. `Database` - 157 edges
2. `ProcessingScope` - 141 edges
3. `SourceItem` - 114 edges
4. `SourceData` - 80 edges
5. `Artifact` - 62 edges
6. `Services` - 55 edges
7. `Application` - 54 edges
8. `SourceItemData` - 49 edges
9. `HTTPClient` - 44 edges
10. `PluginOptions` - 39 edges

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

## Communities (70 total, 29 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.06
Nodes (15): DBDelivery, DBSource, DBSourceItem, AnnotationTests, ConnectionTests, ContentStorageTests, DatabaseTestCase, DeleteTests (+7 more)

### Community 1 - "Services"
Cohesion: 0.06
Nodes (20): LLM, LLMUnavailableError, strip_code_fence(), __newsmerger_plugin__(), Options, __newsmerger_plugin__(), Options, Services (+12 more)

### Community 2 - "db.py"
Cohesion: 0.12
Nodes (4): Base, DBItemAnnotation, ProcessingStatus, _sha256_column()

### Community 3 - "invoke"
Cohesion: 0.22
Nodes (3): annotation(), InspectCommandTests, invoke()

### Community 5 - "Artifact"
Cohesion: 0.12
Nodes (5): DBArtifact, Artifact, ArtifactTests, ArtifactSinkTests, RecordingArtifactSink

### Community 6 - "Application"
Cohesion: 0.06
Nodes (3): Application, lookup(), Annotation

### Community 7 - "ProcessingScope"
Cohesion: 0.15
Nodes (3): ProcessingScope, UnavailableRemixer, UnavailableSink

### Community 11 - "app_from_context"
Cohesion: 0.13
Nodes (10): app_from_context(), cli(), deliver_cmd(), enrich_cmd(), import_cmd(), inspect_content_cmd(), parse_artifact_ids(), remix_cmd() (+2 more)

### Community 12 - "DeliveryStatus"
Cohesion: 0.18
Nodes (6): backoff_seconds(), DeliveryStatus, Delivery, BaseArtifactSink, BaseItemSink, SelectionRequiredError

### Community 13 - "test_telegram.py"
Cohesion: 0.12
Nodes (9): ArtifactSinkOptions, build_caption(), __newsmerger_plugin__(), TelegramArtifactSink, TelegramSink, Sink, BuildCaptionTests, PluginTests (+1 more)

### Community 14 - "StubLLM"
Cohesion: 0.20
Nodes (4): SummarizeProcessor, ConsumerPluginTests, StubLLM, SummarizeTests

### Community 15 - "TelegramTestCase"
Cohesion: 0.30
Nodes (5): ItemSinkOptions, MigrateTelegramStateTests, ok_response(), TelegramSinkTests, TelegramTestCase

### Community 17 - "test_providers.py"
Cohesion: 0.10
Nodes (12): CSJuntasGobiernoProvider, __newsmerger_plugin__(), __newsmerger_plugin__(), page_title(), parse_article(), parse_preview(), Post, preview_url() (+4 more)

### Community 18 - "cli.py"
Cohesion: 0.09
Nodes (8): delete_group(), deliveries_group(), format_value(), inspect_group(), lexer_for(), match_snippet(), print_content(), print_item()

### Community 20 - "run_cmd"
Cohesion: 0.12
Nodes (9): import_sources(), print_deliver(), print_enrich(), print_import(), print_remix(), print_table(), progress_rows(), run_cmd() (+1 more)

### Community 24 - "TelegramClient"
Cohesion: 0.13
Nodes (3): Options, TelegramClient, TelegramError

### Community 25 - "SourceData"
Cohesion: 0.07
Nodes (16): HTTPClient, SourceData, SourceItemData, CastellonInformacionProvider, discover_feed_url(), FeedReaderProvider, fetch_article(), fetch_feed() (+8 more)

### Community 27 - "markdownify.py"
Cohesion: 0.16
Nodes (6): MarkdownifyProcessor, __newsmerger_plugin__(), Options, SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 29 - "cli.py Click commands"
Cohesion: 0.23
Nodes (10): cli.py Click commands, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage, SQLAlchemy models never leave db.py; DTOs cross the boundary, foundation internal library, inspect items|annotations|artifacts|deliveries, Application class (single entry point), Phases: import, enrich, remix, deliver (+2 more)

### Community 32 - "get_date_from_text"
Cohesion: 0.33
Nodes (3): find_parent_by_tag_name(), get_date_from_text(), PreparseData

### Community 34 - "app.py"
Cohesion: 0.14
Nodes (7): check_provider_options(), enrich_runs(), load_plugins(), objects_by_name(), ConfigError, EnrichEntry, plugin_options_error()

### Community 36 - "RecordingItemSink"
Cohesion: 0.33
Nodes (3): ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 38 - "migrate_autoincrement.py"
Cohesion: 0.09
Nodes (9): LockedError, write_lock(), main(), migrate(), needs_autoincrement(), recreate(), main(), migrate() (+1 more)

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.23
Nodes (12): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger, deliver SINK --force with explicit selection (+4 more)

### Community 40 - "models.py"
Cohesion: 0.14
Nodes (9): __newsmerger_plugin__(), Options, Options, PluginOptions, __newsmerger_plugin__(), __newsmerger_plugin__(), Options, __newsmerger_plugin__() (+1 more)

### Community 41 - "report_user_errors"
Cohesion: 0.11
Nodes (15): annotation_options(), artifact_options(), check_found(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), inspect_annotations_cmd(), inspect_artifacts_cmd() (+7 more)

### Community 42 - "Processor"
Cohesion: 0.24
Nodes (3): Processor, ProcessorTestCase, TaggerTests

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 45 - "config.example.yaml"
Cohesion: 0.25
Nodes (5): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), ollama LLM backend, plugins configuration section

### Community 46 - "Database"
Cohesion: 0.09
Nodes (5): Database, AverageLinkRemixer, GroupingRemixer, SingleLinkRemixer, BaseRemixer

### Community 47 - "get_section"
Cohesion: 0.29
Nodes (3): get_section(), parse_datetime(), SectionNotFoundError

### Community 51 - "inspect_deliveries_cmd"
Cohesion: 0.28
Nodes (5): inspect_deliveries_cmd(), json_default(), preview(), print_json(), setup_logging()

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 56 - "config.py"
Cohesion: 0.14
Nodes (4): CacheConfig, DatabaseConfig, expand_variables(), MissingVariableError

### Community 58 - "newsmerger CLAUDE.md agent guidelines"
Cohesion: 0.33
Nodes (5): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention

### Community 60 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 61 - "ADR 0001 Item identity and change detection"
Cohesion: 0.40
Nodes (4): IndexSiteProvider / URLProvider, ADR 0001 Item identity and change detection, Item, Provider

### Community 62 - "parse_entry"
Cohesion: 0.60
Nodes (3): entry_date(), find_image(), parse_entry()

### Community 63 - ".require_annotation"
Cohesion: 0.17
Nodes (3): tags_text(), merge_tags(), MissingAnnotationError

### Community 65 - "grouping.py"
Cohesion: 0.05
Nodes (25): average_between(), average_link_cluster(), build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer, GroupingOptions, item_ref() (+17 more)

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)`, `PluginOptions (pydantic, unknown keys rejected)`, `Annotation` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 385 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_db.py`, `Services`, `db.py`, `Artifact`, `Application`, `ProcessingScope`, `FeedGeneratorRemixer`, `.close`, `.session_scope`, `DeliveryStatus`, `test_telegram.py`, `StubLLM`, `TelegramTestCase`, `BaseSink`, `migrate`, `.get_annotation_values`, `SourceItem`, `TelegramClient`, `SourceData`, `BaseProcessor`, `markdownify.py`, `RunSummary`, `app.py`, `DigestRemixerTests`, `RecordingItemSink`, `DBProcessingState`, `migrate_autoincrement.py`, `models.py`, `Processor`, `EmbedProcessor`, `.__init__`, `DigestRemixer`, `config.py`, `.require_annotation`, `grouping.py`?**
  _High betweenness centrality (0.179) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 43 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05512016718913271 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `ProcessingScope` to `test_db.py`, `Services`, `db.py`, `invoke`, `ApplicationTests`, `Application`, `FeedGeneratorRemixer`, `.session_scope`, `app_from_context`, `DeliveryStatus`, `test_telegram.py`, `TelegramTestCase`, `BaseSink`, `cli.py`, `migrate`, `SourceItem`, `BaseProcessor`, `RunSummary`, `app.py`, `DigestRemixerTests`, `RecordingItemSink`, `models.py`, `report_user_errors`, `Processor`, `Database`, `inspect_deliveries_cmd`, `DigestRemixer`, `config.py`, `grouping.py`?**
  _High betweenness centrality (0.152) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Should `Services` be split into smaller, more focused modules?**
  _Cohesion score 0.058126619770455384 - nodes in this community are weakly interconnected._