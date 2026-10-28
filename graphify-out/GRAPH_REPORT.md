# Graph Report - newsmerger  (2026-10-28)

## Corpus Check
- 70 files · ~119,855 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .lock 1)

## Summary
- 1499 nodes · 4420 edges · 69 communities (42 shown, 27 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 607 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a78cdf5e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- merge_options
- Services
- .from_text
- ApplicationTests
- DeliveryStatus
- Application
- migrate_autoincrement.py
- TestFeedReader
- config.py
- DeleteCommandTests
- app_from_context
- Provider
- ProcessingScope
- process_cmd
- app.py
- BaseSink
- telegram_channel.py
- ConfigError
- GoogleChatSinkTests
- 0009: Workflows and keyed entries
- .get_annotation_values
- SourceItem
- Database
- .get_annotation_values
- SourceData
- .require_annotation
- MarkdownifyProcessor
- cli.py Click commands
- BaseArtifactSink
- delete_items_cmd
- get_date_from_text
- .get_artifact
- plugins
- FeedReaderProvider
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
- DBDelivery
- inspect_items_cmd
- db.py
- GoogleChatSink
- TestSourceItemDataContent
- cli.py
- Annotation
- GoogleChatError
- Processor
- El Periódico Mediterráneo
- Artifact
- newsmerger CLAUDE.md agent guidelines
- foundation.plugin.Register plugin loading
- image_card
- Item
- backoff_seconds
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- Artifact
- Grouping notes: NLP clustering pipeline
- news-aggregator
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
- `ApplicationTests` --uses--> `LockedError`  [INFERRED]
  tests/test_app.py → newsmerger/app.py
- `ApplicationTests` --uses--> `Application`  [INFERRED]
  tests/test_app.py → newsmerger/app.py
- `ApplicationTests` --uses--> `ConfigError`  [INFERRED]
  tests/test_app.py → newsmerger/config.py
- `CommandTests` --uses--> `ConfigError`  [INFERRED]
  tests/test_cli.py → newsmerger/config.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (69 total, 27 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.07
Nodes (14): DBProcessingState, DBSource, DBSourceItem, AnnotationTests, ConnectionTests, ContentStorageTests, DatabaseTestCase, DeleteTests (+6 more)

### Community 2 - "Services"
Cohesion: 0.06
Nodes (30): LLM, LLMUnavailableError, strip_code_fence(), __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), NoOptions (+22 more)

### Community 5 - "DeliveryStatus"
Cohesion: 0.09
Nodes (17): DeliveryStatus, build_caption(), ItemDeliveryOptions, __newsmerger_plugin__(), Options, post(), TelegramArtifactSink, TelegramError (+9 more)

### Community 7 - "migrate_autoincrement.py"
Cohesion: 0.05
Nodes (13): LockedError, write_lock(), Base, DBItemAnnotation, main(), migrate(), needs_autoincrement(), recreate() (+5 more)

### Community 9 - "config.py"
Cohesion: 0.16
Nodes (4): CacheConfig, DatabaseConfig, expand_variables(), MissingVariableError

### Community 11 - "app_from_context"
Cohesion: 0.16
Nodes (10): app_from_context(), deliver_cmd(), import_cmd(), inspect_content_cmd(), inspect_deliveries_cmd(), parse_artifact_ids(), process_cmd(), remix_cmd() (+2 more)

### Community 12 - "Provider"
Cohesion: 0.14
Nodes (10): entry_date(), find_image(), parse_entry(), get_section(), __newsmerger_plugin__(), parse_datetime(), SectionNotFoundError, __newsmerger_plugin__() (+2 more)

### Community 13 - "ProcessingScope"
Cohesion: 0.05
Nodes (14): cli(), ProcessingScope, DigestOptions, DigestRemixer, Options, RunSummary, annotation(), CommandTests (+6 more)

### Community 14 - "process_cmd"
Cohesion: 0.13
Nodes (9): import_sources(), print_deliver(), print_import(), print_process(), print_remix(), print_table(), progress_rows(), run_cmd() (+1 more)

### Community 15 - "app.py"
Cohesion: 0.11
Nodes (10): delivery_runs(), entry_location(), process_runs(), referenced_plugins(), remix_runs(), Run, source_options(), options_error() (+2 more)

### Community 16 - "BaseSink"
Cohesion: 0.09
Nodes (4): Delivery, ArtifactNames, BaseItemSink, BaseSink

### Community 17 - "telegram_channel.py"
Cohesion: 0.15
Nodes (8): Options, page_title(), parse_article(), parse_preview(), Post, TelegramChannelProvider, read_sample(), TestTelegramChannel

### Community 18 - "ConfigError"
Cohesion: 0.18
Nodes (4): load_plugins(), objects_by_name(), workflow_scope(), ConfigError

### Community 20 - "0009: Workflows and keyed entries"
Cohesion: 0.33
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 21 - ".get_annotation_values"
Cohesion: 0.12
Nodes (4): _configure_sqlite_connection(), CustomJSON, _encode_value(), UTCDateTime

### Community 25 - "SourceData"
Cohesion: 0.08
Nodes (18): HTTPClient, SourceData, SourceItemData, CastellonInformacionProvider, discover_feed_url(), fetch_article(), fetch_feed(), PlazaProvider (+10 more)

### Community 27 - "MarkdownifyProcessor"
Cohesion: 0.26
Nodes (4): MarkdownifyProcessor, SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 29 - "cli.py Click commands"
Cohesion: 0.18
Nodes (12): cli.py Click commands, Database (db.py, only SQLite/storage access), deliveries table (the ledger), foundation.storage.DiskStorage content-addressed storage, foundation internal library, ADR 0005 Remixers with external side effects, inspect items|annotations|artifacts|deliveries, Application class (single entry point) (+4 more)

### Community 31 - "delete_items_cmd"
Cohesion: 0.21
Nodes (5): delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), require_selection(), sort_option()

### Community 32 - "get_date_from_text"
Cohesion: 0.19
Nodes (6): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), __newsmerger_plugin__(), PreparseData, TestCSJuntasGobierno

### Community 34 - "plugins"
Cohesion: 0.11
Nodes (19): days, title, url, api_base, api_key, chat_model, embed_model, plugins (+11 more)

### Community 35 - "FeedReaderProvider"
Cohesion: 0.47
Nodes (3): FeedReaderProvider, __newsmerger_plugin__(), Options

### Community 36 - "RecordingItemSink"
Cohesion: 0.22
Nodes (4): SelectionRequiredError, ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 37 - "report_user_errors"
Cohesion: 0.23
Nodes (7): annotation_options(), artifact_options(), inspect_annotations_cmd(), report_user_errors(), wrapper(), scope_options(), wrapper()

### Community 38 - "config.py"
Cohesion: 0.12
Nodes (3): DeliveryEntry, ProcessEntry, RemixEntry

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.23
Nodes (12): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger (+4 more)

### Community 40 - "grouping.py"
Cohesion: 0.05
Nodes (28): FeedGeneratorRemixer, Options, average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions (+20 more)

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
Cohesion: 0.10
Nodes (13): EmbedOptions, EmbedProcessor, Options, tags_text(), Options, SummarizeOptions, SummarizeProcessor, ConsumerPluginTests (+5 more)

### Community 45 - "config.example.yaml"
Cohesion: 0.12
Nodes (14): cache, expiration, input, process, options, processor, remix, sources (+6 more)

### Community 47 - "inspect_items_cmd"
Cohesion: 0.14
Nodes (9): check_found(), format_value(), inspect_artifacts_cmd(), inspect_items_cmd(), json_default(), preview(), print_item(), print_json() (+1 more)

### Community 48 - "db.py"
Cohesion: 0.09
Nodes (9): ProcessingStatus, _sha256_column(), __newsmerger_plugin__(), build_text(), Options, DocumentDeliveryOptions, Remixer, ArtifactDeliveryOptions (+1 more)

### Community 49 - "GoogleChatSink"
Cohesion: 0.21
Nodes (4): GoogleChatSink, Options, WebhookOptions, OptionsTests

### Community 51 - "cli.py"
Cohesion: 0.09
Nodes (6): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content()

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 56 - "Artifact"
Cohesion: 0.09
Nodes (6): DBArtifact, Artifact, BaseRemixer, ArtifactTests, ArtifactSinkTests, RecordingArtifactSink

### Community 58 - "newsmerger CLAUDE.md agent guidelines"
Cohesion: 0.29
Nodes (6): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention, SQLAlchemy models never leave db.py; DTOs cross the boundary

### Community 59 - "foundation.plugin.Register plugin loading"
Cohesion: 0.50
Nodes (4): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 436 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_db.py`, `merge_options`, `Services`, `DeliveryStatus`, `Application`, `migrate_autoincrement.py`, `DeleteCommandTests`, `ProcessingScope`, `app.py`, `BaseSink`, `GoogleChatSinkTests`, `.get_annotation_values`, `SourceItem`, `.get_annotation_values`, `SourceData`, `.require_annotation`, `MarkdownifyProcessor`, `BaseArtifactSink`, `.get_artifact`, `RecordingItemSink`, `grouping.py`, `StubLLM`, `db.py`, `GoogleChatSink`, `Annotation`, `Artifact`?**
  _High betweenness centrality (0.163) - this node is a cross-community bridge._
- **Are the 45 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 45 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06526806526806526 - nodes in this community are weakly interconnected._
- **Why does `SourceItem` connect `SourceItem` to `test_db.py`, `merge_options`, `Services`, `ApplicationTests`, `DeliveryStatus`, `Application`, `migrate_autoincrement.py`, `DeleteCommandTests`, `ProcessingScope`, `app.py`, `BaseSink`, `GoogleChatSinkTests`, `Database`, `.get_annotation_values`, `.require_annotation`, `MarkdownifyProcessor`, `RecordingItemSink`, `grouping.py`, `StubLLM`, `inspect_items_cmd`, `db.py`, `GoogleChatSink`, `cli.py`?**
  _High betweenness centrality (0.138) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Should `merge_options` be split into smaller, more focused modules?**
  _Cohesion score 0.06507936507936508 - nodes in this community are weakly interconnected._