# Graph Report - telegram-item-image  (2026-10-27)

## Corpus Check
- 68 files · ~119,201 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1449 nodes · 4279 edges · 70 communities (41 shown, 29 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 584 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1b532842`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- .close
- db.py
- .from_text
- ApplicationTests
- test_telegram.py
- Application
- migrate_autoincrement.py
- feedreader.py
- GroupingTests
- DeleteCommandTests
- app_from_context
- FeedGeneratorRemixer
- ProcessingScope
- run_cmd
- app.py
- BaseSink
- telegram_channel.py
- DeliveryStatus
- TestFeedReader
- .key
- Any
- SourceItem
- Database
- SourceData
- Any
- MarkdownifyProcessor
- PrensaIbericaPlainProvider
- cli.py Click commands
- migrate
- Provider
- csjuntasgobierno.py
- __newsmerger_plugin__
- backoff_seconds
- DigestRemixer
- Artifact
- delete_items_cmd
- Config
- ADR 0007 Sinks and the delivery ledger
- grouping.py
- report_user_errors
- PluginOptions
- Services object (services.llm(name))
- StubLLM
- config.example.yaml
- inspect_items_cmd
- config.py
- GoogleChatSink
- expand_variables
- cli.py
- _sha256_column
- json
- Processor
- El Periódico Mediterráneo
- plaza.py
- newsmerger CLAUDE.md agent guidelines
- deliveries table (the ledger)
- ADR 0001 Item identity and change detection
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- Artifact
- Grouping notes: NLP clustering pipeline
- news-aggregator
- LogLevelTests
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
Cohesion: 0.07
Nodes (14): DBProcessingState, DBSource, DBSourceItem, AnnotationTests, ConnectionTests, ContentStorageTests, DatabaseTestCase, DeleteTests (+6 more)

### Community 2 - "db.py"
Cohesion: 0.09
Nodes (9): LLM, LLMUnavailableError, strip_code_fence(), __newsmerger_plugin__(), Services, __newsmerger_plugin__(), __newsmerger_plugin__(), UnavailableProcessor (+1 more)

### Community 5 - "test_telegram.py"
Cohesion: 0.08
Nodes (18): ProcessingStatus, build_caption(), DocumentDeliveryOptions, ItemDeliveryOptions, __newsmerger_plugin__(), Options, post(), TelegramArtifactSink (+10 more)

### Community 7 - "migrate_autoincrement.py"
Cohesion: 0.07
Nodes (11): LockedError, write_lock(), Base, DBItemAnnotation, main(), migrate(), needs_autoincrement(), recreate() (+3 more)

### Community 8 - "feedreader.py"
Cohesion: 0.13
Nodes (8): discover_feed_url(), entry_date(), fetch_feed(), find_image(), __newsmerger_plugin__(), Options, parse_entry(), merge_options()

### Community 11 - "app_from_context"
Cohesion: 0.14
Nodes (10): app_from_context(), cli(), delete_annotations_cmd(), deliver_cmd(), inspect_content_cmd(), inspect_deliveries_cmd(), parse_artifact_ids(), process_cmd() (+2 more)

### Community 12 - "FeedGeneratorRemixer"
Cohesion: 0.29
Nodes (3): FeedGeneratorRemixer, Options, FeedGeneratorTests

### Community 13 - "ProcessingScope"
Cohesion: 0.07
Nodes (11): workflow_scope(), wrapper(), ProcessingScope, RunSummary, annotation(), CommandTests, InspectCommandTests, invoke() (+3 more)

### Community 14 - "run_cmd"
Cohesion: 0.15
Nodes (8): import_cmd(), import_sources(), print_import(), print_remix(), progress_rows(), remix_cmd(), run_cmd(), run_each()

### Community 15 - "app.py"
Cohesion: 0.08
Nodes (14): delivery_runs(), entry_location(), load_plugins(), lookup(), objects_by_name(), process_runs(), referenced_plugins(), remix_runs() (+6 more)

### Community 17 - "telegram_channel.py"
Cohesion: 0.10
Nodes (11): is_home_page(), __newsmerger_plugin__(), Options, page_title(), parse_article(), parse_preview(), Post, preview_url() (+3 more)

### Community 18 - "DeliveryStatus"
Cohesion: 0.10
Nodes (5): DBDelivery, DeliveryStatus, Delivery, BaseItemSink, GoogleChatSinkTests

### Community 20 - ".key"
Cohesion: 0.20
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 21 - "Any"
Cohesion: 0.12
Nodes (4): _configure_sqlite_connection(), CustomJSON, _encode_value(), UTCDateTime

### Community 25 - "SourceData"
Cohesion: 0.08
Nodes (12): HTTPClient, SourceData, SourceItemData, CastellonInformacionProvider, FeedReaderProvider, fetch_article(), PlazaProvider, PrensaIbericaProvider (+4 more)

### Community 27 - "MarkdownifyProcessor"
Cohesion: 0.22
Nodes (5): MarkdownifyProcessor, __newsmerger_plugin__(), SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 28 - "PrensaIbericaPlainProvider"
Cohesion: 0.15
Nodes (3): _extract_href(), __newsmerger_plugin__(), PrensaIbericaPlainProvider

### Community 29 - "cli.py Click commands"
Cohesion: 0.23
Nodes (10): cli.py Click commands, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage, SQLAlchemy models never leave db.py; DTOs cross the boundary, foundation internal library, inspect items|annotations|artifacts|deliveries, Application class (single entry point), Phases: import, enrich, remix, deliver (+2 more)

### Community 31 - "Provider"
Cohesion: 0.12
Nodes (4): __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), Provider

### Community 32 - "csjuntasgobierno.py"
Cohesion: 0.18
Nodes (6): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), __newsmerger_plugin__(), PreparseData, TestCSJuntasGobierno

### Community 33 - "__newsmerger_plugin__"
Cohesion: 0.25
Nodes (4): __newsmerger_plugin__(), ollama_client(), Options, OllamaTests

### Community 36 - "Artifact"
Cohesion: 0.05
Nodes (15): DBArtifact, Artifact, __newsmerger_plugin__(), BaseRemixer, UnavailableRemixer, ArtifactDeliveryOptions, DeliveryOptions, SelectionRequiredError (+7 more)

### Community 37 - "delete_items_cmd"
Cohesion: 0.24
Nodes (5): check_found(), delete_artifacts_cmd(), delete_items_cmd(), require_selection(), sort_option()

### Community 38 - "Config"
Cohesion: 0.10
Nodes (4): Config, DeliveryEntry, ProcessEntry, RemixEntry

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.23
Nodes (12): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger, deliver SINK --force with explicit selection (+4 more)

### Community 40 - "grouping.py"
Cohesion: 0.06
Nodes (26): __newsmerger_plugin__(), average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer (+18 more)

### Community 41 - "report_user_errors"
Cohesion: 0.21
Nodes (7): annotation_options(), artifact_options(), inspect_annotations_cmd(), inspect_artifacts_cmd(), report_user_errors(), wrapper(), scope_options()

### Community 42 - "PluginOptions"
Cohesion: 0.10
Nodes (9): Options, NoOptions, PluginOptions, Options, merge_tags(), Options, TaggerOptions, TaggerProcessor (+1 more)

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "StubLLM"
Cohesion: 0.08
Nodes (13): EmbedOptions, EmbedProcessor, Options, tags_text(), Options, SummarizeOptions, SummarizeProcessor, ConsumerPluginTests (+5 more)

### Community 45 - "config.example.yaml"
Cohesion: 0.25
Nodes (5): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), ollama LLM backend, plugins configuration section

### Community 47 - "inspect_items_cmd"
Cohesion: 0.25
Nodes (5): inspect_items_cmd(), print_deliver(), print_item(), print_process(), print_table()

### Community 49 - "GoogleChatSink"
Cohesion: 0.13
Nodes (7): build_text(), GoogleChatError, GoogleChatSink, __newsmerger_plugin__(), Options, WebhookOptions, OptionsTests

### Community 51 - "cli.py"
Cohesion: 0.10
Nodes (6): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content()

### Community 53 - "json"
Cohesion: 0.27
Nodes (5): format_value(), json_default(), preview(), print_json(), setup_logging()

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 57 - "plaza.py"
Cohesion: 0.19
Nodes (4): get_section(), __newsmerger_plugin__(), parse_datetime(), SectionNotFoundError

### Community 58 - "newsmerger CLAUDE.md agent guidelines"
Cohesion: 0.33
Nodes (5): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention

### Community 60 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 61 - "ADR 0001 Item identity and change detection"
Cohesion: 0.40
Nodes (4): IndexSiteProvider / URLProvider, ADR 0001 Item identity and change detection, Item, Provider

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)`, `PluginOptions (pydantic, unknown keys rejected)`, `Annotation` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 418 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_db.py`, `.close`, `db.py`, `test_telegram.py`, `Application`, `migrate_autoincrement.py`, `GroupingTests`, `DeleteCommandTests`, `FeedGeneratorRemixer`, `ProcessingScope`, `app.py`, `BaseSink`, `DeliveryStatus`, `Any`, `SourceItem`, `.get_annotation_values`, `SourceData`, `Any`, `MarkdownifyProcessor`, `migrate`, `backoff_seconds`, `DigestRemixer`, `Artifact`, `grouping.py`, `PluginOptions`, `StubLLM`, `.get_content`, `config.py`, `GoogleChatSink`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Are the 44 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 44 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06807017543859649 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `ProcessingScope` to `test_db.py`, `db.py`, `ApplicationTests`, `test_telegram.py`, `Application`, `GroupingTests`, `DeleteCommandTests`, `app_from_context`, `FeedGeneratorRemixer`, `run_cmd`, `app.py`, `BaseSink`, `DeliveryStatus`, `SourceItem`, `Database`, `Any`, `migrate`, `DigestRemixer`, `Artifact`, `delete_items_cmd`, `grouping.py`, `report_user_errors`, `PluginOptions`, `inspect_items_cmd`, `config.py`, `cli.py`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Should `.close` be split into smaller, more focused modules?**
  _Cohesion score 0.14166666666666666 - nodes in this community are weakly interconnected._