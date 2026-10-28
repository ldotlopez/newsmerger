# Graph Report - newsmerger  (2026-10-28)

## Corpus Check
- 70 files · ~119,790 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .lock 1)

## Summary
- 1497 nodes · 4414 edges · 70 communities (51 shown, 19 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 607 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5cc0adc1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- merge_options
- Services
- .from_text
- ApplicationTests
- Artifact
- Application
- migrate_autoincrement.py
- feedreader.py
- app.py
- DeleteCommandTests
- app_from_context
- Provider
- RunSummary
- process_cmd
- app.py
- BaseSink
- telegram_channel.py
- ConfigError
- RunSummary
- 0009: Workflows and keyed entries
- .get_annotation_values
- Database
- ItemKey
- SourceData
- SourceItem
- MarkdownifyProcessor
- PrensaIbericaPlainProvider
- cli.py Click commands
- DeliveryStatus
- DigestRemixer
- get_date_from_text
- __newsmerger_plugin__
- plugins
- ProcessingScope
- RecordingItemSink
- report_user_errors
- config.py
- ADR 0007 Sinks and the delivery ledger
- grouping.py
- options
- hooks
- Services object (services.llm(name))
- StubLLM
- config.example.yaml
- PlazaProvider
- Any
- db.py
- GoogleChatSinkTests
- SourceItemData
- cli.py
- GroupingRemixer
- print_table
- Processor
- El Periódico Mediterráneo
- merge_options
- newsmerger CLAUDE.md agent guidelines
- foundation.plugin.Register plugin loading
- Item
- sinks.py
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- Artifact
- Grouping notes: NLP clustering pipeline
- news-aggregator
- LogLevelTests
- __newsmerger_plugin__
- ADR 0002 Processing state lifecycle

## God Nodes (most connected - your core abstractions)
1. `Database` - 162 edges
2. `ProcessingScope` - 142 edges
3. `SourceItem` - 119 edges
4. `SourceData` - 81 edges
5. `Artifact` - 62 edges
6. `Application` - 61 edges
7. `Services` - 61 edges
8. `SourceItemData` - 49 edges
9. `PluginOptions` - 49 edges
10. `ApplicationTests` - 49 edges

## Surprising Connections (you probably didn't know these)
- `Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)` --implements--> `Source`  [INFERRED]
  config.example.yaml → docs/SPECIFICATION.md
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

## Communities (70 total, 19 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.06
Nodes (13): DBSourceItem, AnnotationTests, ConnectionTests, ContentStorageTests, DatabaseTestCase, DeleteTests, DeliveryTests, GetItemsTests (+5 more)

### Community 2 - "Services"
Cohesion: 0.08
Nodes (15): LLM, LLMUnavailableError, strip_code_fence(), __newsmerger_plugin__(), Options, __newsmerger_plugin__(), Options, TaggerProcessor (+7 more)

### Community 5 - "Artifact"
Cohesion: 0.06
Nodes (16): DBArtifact, Artifact, __newsmerger_plugin__(), Options, post(), TelegramArtifactSink, TelegramError, TelegramSink (+8 more)

### Community 7 - "migrate_autoincrement.py"
Cohesion: 0.12
Nodes (7): Base, DBItemAnnotation, main(), migrate(), needs_autoincrement(), recreate(), MigrateAutoincrementTests

### Community 8 - "feedreader.py"
Cohesion: 0.16
Nodes (9): discover_feed_url(), entry_date(), FeedReaderProvider, fetch_feed(), find_image(), __newsmerger_plugin__(), Options, parse_entry() (+1 more)

### Community 9 - "app.py"
Cohesion: 0.13
Nodes (5): LockedError, write_lock(), main(), migrate(), main()

### Community 11 - "app_from_context"
Cohesion: 0.15
Nodes (10): app_from_context(), cli(), deliver_cmd(), inspect_content_cmd(), inspect_deliveries_cmd(), parse_artifact_ids(), process_cmd(), remix_cmd() (+2 more)

### Community 12 - "Provider"
Cohesion: 0.14
Nodes (13): __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), PluginObjects, Services, __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__() (+5 more)

### Community 13 - "RunSummary"
Cohesion: 0.18
Nodes (4): annotation(), InspectCommandTests, invoke(), SearchTests

### Community 14 - "process_cmd"
Cohesion: 0.17
Nodes (6): import_cmd(), import_sources(), print_import(), progress_rows(), run_cmd(), run_each()

### Community 15 - "app.py"
Cohesion: 0.08
Nodes (12): delivery_runs(), entry_location(), process_runs(), referenced_plugins(), remix_runs(), Run, source_options(), CacheConfig (+4 more)

### Community 16 - "BaseSink"
Cohesion: 0.09
Nodes (3): ArtifactNames, BaseItemSink, BaseSink

### Community 17 - "telegram_channel.py"
Cohesion: 0.12
Nodes (10): is_home_page(), Options, page_title(), parse_article(), parse_preview(), Post, preview_url(), TelegramChannelProvider (+2 more)

### Community 18 - "ConfigError"
Cohesion: 0.13
Nodes (4): workflow_scope(), ConfigError, expand_variables(), MissingVariableError

### Community 20 - "0009: Workflows and keyed entries"
Cohesion: 0.33
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 21 - ".get_annotation_values"
Cohesion: 0.10
Nodes (4): _configure_sqlite_connection(), CustomJSON, _encode_value(), UTCDateTime

### Community 23 - "Database"
Cohesion: 0.09
Nodes (3): backoff_seconds(), Database, DBProcessingState

### Community 25 - "SourceData"
Cohesion: 0.12
Nodes (10): DBSource, HTTPClient, SourceData, CastellonInformacionProvider, fetch_article(), PlazaProvider, TheGuardianProvider, IndexSiteProvider (+2 more)

### Community 26 - "SourceItem"
Cohesion: 0.08
Nodes (9): ItemKey, SourceItem, tagged_items(), SummarizeOptions, merge_tags(), TaggerOptions, BaseProcessor, MissingAnnotationError (+1 more)

### Community 27 - "MarkdownifyProcessor"
Cohesion: 0.20
Nodes (5): MarkdownifyProcessor, Options, SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 29 - "cli.py Click commands"
Cohesion: 0.18
Nodes (12): cli.py Click commands, Database (db.py, only SQLite/storage access), deliveries table (the ledger), foundation.storage.DiskStorage content-addressed storage, foundation internal library, ADR 0005 Remixers with external side effects, inspect items|annotations|artifacts|deliveries, Application class (single entry point) (+4 more)

### Community 30 - "DeliveryStatus"
Cohesion: 0.12
Nodes (4): DBDelivery, DeliveryStatus, Delivery, BaseArtifactSink

### Community 31 - "DigestRemixer"
Cohesion: 0.28
Nodes (3): DigestOptions, DigestRemixer, Options

### Community 32 - "get_date_from_text"
Cohesion: 0.19
Nodes (5): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, TestCSJuntasGobierno

### Community 34 - "plugins"
Cohesion: 0.11
Nodes (19): days, title, url, api_base, api_key, chat_model, embed_model, plugins (+11 more)

### Community 35 - "ProcessingScope"
Cohesion: 0.24
Nodes (4): ProcessingScope, migrate(), DigestRemixerTests, MigrateTelegramStateTests

### Community 36 - "RecordingItemSink"
Cohesion: 0.10
Nodes (4): SelectionRequiredError, ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 37 - "report_user_errors"
Cohesion: 0.11
Nodes (15): annotation_options(), artifact_options(), check_found(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), inspect_annotations_cmd(), inspect_artifacts_cmd() (+7 more)

### Community 38 - "config.py"
Cohesion: 0.09
Nodes (4): Config, DeliveryEntry, ProcessEntry, RemixEntry

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.23
Nodes (12): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger (+4 more)

### Community 40 - "grouping.py"
Cohesion: 0.06
Nodes (23): average_between(), average_link_cluster(), build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer, GroupingOptions, item_ref() (+15 more)

### Community 41 - "options"
Cohesion: 0.13
Nodes (16): deliver, options, sink, artifacts, chat_id, interval, item_image, item_url_preview (+8 more)

### Community 42 - "hooks"
Cohesion: 0.15
Nodes (12): exclude, args, entry, files, id, language, name, pass_filenames (+4 more)

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.18
Nodes (14): BaseSink deliver cycle (queue, select, send), digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks) (+6 more)

### Community 44 - "StubLLM"
Cohesion: 0.11
Nodes (9): EmbedOptions, EmbedProcessor, Options, tags_text(), Options, SummarizeProcessor, EmbedTests, StubLLM (+1 more)

### Community 45 - "config.example.yaml"
Cohesion: 0.12
Nodes (14): cache, expiration, input, process, options, processor, remix, sources (+6 more)

### Community 46 - "PlazaProvider"
Cohesion: 0.29
Nodes (3): get_section(), parse_datetime(), SectionNotFoundError

### Community 47 - "Any"
Cohesion: 0.33
Nodes (4): json_default(), preview(), print_json(), setup_logging()

### Community 48 - "db.py"
Cohesion: 0.16
Nodes (3): ProcessingStatus, _sha256_column(), Annotation

### Community 49 - "GoogleChatSinkTests"
Cohesion: 0.10
Nodes (8): GoogleChatError, GoogleChatSink, image_card(), __newsmerger_plugin__(), Options, WebhookOptions, GoogleChatSinkTests, OptionsTests

### Community 50 - "SourceItemData"
Cohesion: 0.18
Nodes (4): SourceItemData, PrensaIbericaProvider, TestPrensaIberica, TestSourceItemDataContent

### Community 51 - "cli.py"
Cohesion: 0.10
Nodes (6): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content()

### Community 53 - "print_table"
Cohesion: 0.18
Nodes (6): format_value(), print_deliver(), print_item(), print_process(), print_remix(), print_table()

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 56 - "merge_options"
Cohesion: 0.12
Nodes (4): FeedGeneratorRemixer, Options, BaseRemixer, UnavailableRemixer

### Community 58 - "newsmerger CLAUDE.md agent guidelines"
Cohesion: 0.29
Nodes (6): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention, SQLAlchemy models never leave db.py; DTOs cross the boundary

### Community 59 - "foundation.plugin.Register plugin loading"
Cohesion: 0.50
Nodes (4): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 62 - "sinks.py"
Cohesion: 0.10
Nodes (12): build_text(), Options, NoOptions, PluginOptions, build_caption(), DocumentDeliveryOptions, ItemDeliveryOptions, ArtifactDeliveryOptions (+4 more)

### Community 76 - "__newsmerger_plugin__"
Cohesion: 0.22
Nodes (3): __newsmerger_plugin__(), __newsmerger_plugin__(), DigestPluginTests

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 436 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_db.py`, `Services`, `Artifact`, `Application`, `migrate_autoincrement.py`, `app.py`, `DeleteCommandTests`, `app.py`, `BaseSink`, `.get_annotation_values`, `.get_content`, `SourceData`, `SourceItem`, `MarkdownifyProcessor`, `DeliveryStatus`, `DigestRemixer`, `ProcessingScope`, `RecordingItemSink`, `grouping.py`, `StubLLM`, `db.py`, `GoogleChatSinkTests`, `GroupingRemixer`, `merge_options`, `sinks.py`?**
  _High betweenness centrality (0.166) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.061419753086419754 - nodes in this community are weakly interconnected._
- **Why does `SourceItem` connect `SourceItem` to `test_db.py`, `Services`, `ApplicationTests`, `Artifact`, `Application`, `DeleteCommandTests`, `RunSummary`, `app.py`, `BaseSink`, `.get_annotation_values`, `.get_content`, `Database`, `ItemKey`, `SourceData`, `MarkdownifyProcessor`, `DeliveryStatus`, `DigestRemixer`, `ProcessingScope`, `RecordingItemSink`, `grouping.py`, `StubLLM`, `db.py`, `GoogleChatSinkTests`, `cli.py`, `print_table`, `merge_options`, `sinks.py`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Should `merge_options` be split into smaller, more focused modules?**
  _Cohesion score 0.12418300653594772 - nodes in this community are weakly interconnected._