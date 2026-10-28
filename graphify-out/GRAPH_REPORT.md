# Graph Report - newsmerger  (2026-10-28)

## Corpus Check
- 75 files · ~124,230 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .lock 1)

## Summary
- 1580 nodes · 4529 edges · 69 communities (48 shown, 21 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 620 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8524ae37`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- ConfigError
- Application
- .from_text
- Database
- telegram.py
- .from_text
- migrate_telegram_state.py
- TestFeedReader
- .llm
- .session_scope
- app_from_context
- csjuntasgobierno.py
- Artifact
- run_cmd
- .get_annotation_values
- DeliveryStatus
- test_providers.py
- migrate_autoincrement.py
- catalog.py
- 0009: Workflows and keyed entries
- Any
- PrensaIbericaPlainProvider
- db.py
- model_validator
- migrate_feed_names.py
- SourceItem
- Base
- LLM
- check_section
- grouping.py
- report_user_errors
- inspect_annotations_cmd
- ADR 0002 Processing state lifecycle
- plugins
- FeedReaderProvider
- GoogleChatError
- Config
- config.py
- ADR 0007 Sinks and the delivery ledger
- MissingAnnotationError
- options
- hooks
- Services object (services.llm(name))
- GoogleChatSinkTests
- config.example.yaml
- Workflow
- cli.py
- _sha256_column
- MarkdownifyProcessor
- SourceData
- Annotation
- newstool
- Processor
- El Periódico Mediterráneo
- Artifact
- newsmerger CLAUDE.md agent guidelines
- Services
- ProcessingScope
- Item
- scope_options
- TestFeedReader
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- Artifact
- Grouping notes: NLP clustering pipeline
- foundation.plugin.Register plugin loading
- setup_logging
- Database & ORM Conventions

## God Nodes (most connected - your core abstractions)
1. `Database` - 160 edges
2. `ProcessingScope` - 134 edges
3. `SourceItem` - 119 edges
4. `SourceData` - 82 edges
5. `Services` - 76 edges
6. `Artifact` - 62 edges
7. `Application` - 61 edges
8. `SourceItemData` - 54 edges
9. `HTTPClient` - 47 edges
10. `ApplicationTests` - 43 edges

## Surprising Connections (you probably didn't know these)
- `Decision` --references--> `Application`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/app.py
- `Changes` --references--> `workflow_scope()`  [INFERRED]
  PLAN-workflow-selectors.md → newstool/app.py
- `Context` --references--> `workflow_scope()`  [INFERRED]
  PLAN-workflow-selectors.md → newstool/app.py
- `Review findings (current code)` --references--> `workflow_scope()`  [INFERRED]
  PLAN-workflow-selectors.md → newstool/app.py
- `Verification` --references--> `share_sources()`  [INFERRED]
  PLAN-workflow-selectors.md → newstool/catalog.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (69 total, 21 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.06
Nodes (13): DBDelivery, AnnotationTests, ConnectionTests, ContentStorageTests, DatabaseTestCase, DeleteTests, DeliveryTests, GetItemsTests (+5 more)

### Community 1 - "ConfigError"
Cohesion: 0.09
Nodes (6): Catalog, Kind, Profile, Run, ConfigError, DeliveryEntry

### Community 2 - "Application"
Cohesion: 0.07
Nodes (3): Application, lookup(), workflow_scope()

### Community 3 - ".from_text"
Cohesion: 0.08
Nodes (6): ollama_client(), OllamaLLM, Options, ApplicationTests, lazy(), OllamaTests

### Community 4 - "Database"
Cohesion: 0.10
Nodes (6): Database, tags_text(), SummarizeProcessor, merge_tags(), TaggerProcessor, BaseProcessor

### Community 5 - "telegram.py"
Cohesion: 0.05
Nodes (22): build_card(), chat_image_url(), build_caption(), DocumentDeliveryOptions, ItemDeliveryOptions, __newstool_plugin__(), post(), TelegramArtifactSink (+14 more)

### Community 7 - "migrate_telegram_state.py"
Cohesion: 0.14
Nodes (3): LockedError, write_lock(), main()

### Community 8 - "TestFeedReader"
Cohesion: 0.29
Nodes (6): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention, SQLAlchemy models never leave db.py; DTOs cross the boundary

### Community 9 - ".llm"
Cohesion: 0.07
Nodes (17): 0010: Plugin classes and the configuration catalog, Consequences, Context, Rejected options, EmbedOptions, EmbedProcessor, SummarizeOptions, Processor (+9 more)

### Community 11 - "app_from_context"
Cohesion: 0.16
Nodes (8): app_from_context(), cli(), import_cmd(), inspect_content_cmd(), parse_artifact_ids(), process_cmd(), remix_cmd(), search_cmd()

### Community 12 - "csjuntasgobierno.py"
Cohesion: 0.18
Nodes (6): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, NoOptions, TestCSJuntasGobierno

### Community 13 - "Artifact"
Cohesion: 0.06
Nodes (11): DBArtifact, Artifact, RunSummary, annotation(), CommandTests, InspectCommandTests, invoke(), ArtifactTests (+3 more)

### Community 14 - "run_cmd"
Cohesion: 0.18
Nodes (5): print_import(), print_process(), progress_rows(), run_cmd(), run_each()

### Community 16 - "DeliveryStatus"
Cohesion: 0.07
Nodes (6): DeliveryStatus, Delivery, ArtifactNames, BaseArtifactSink, BaseItemSink, BaseSink

### Community 17 - "test_providers.py"
Cohesion: 0.08
Nodes (20): _encode_value(), Options, discover_feed_url(), entry_date(), fetch_feed(), find_image(), Options, parse_entry() (+12 more)

### Community 18 - "migrate_autoincrement.py"
Cohesion: 0.17
Nodes (4): main(), migrate(), needs_autoincrement(), recreate()

### Community 19 - "catalog.py"
Cohesion: 0.14
Nodes (6): ids_of(), in_default(), Use, Entry, ProcessEntry, RemixEntry

### Community 20 - "0009: Workflows and keyed entries"
Cohesion: 0.33
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 21 - "Any"
Cohesion: 0.10
Nodes (3): _configure_sqlite_connection(), CustomJSON, UTCDateTime

### Community 23 - "db.py"
Cohesion: 0.08
Nodes (10): Duration, ProcessingStatus, strip_code_fence(), DigestOptions, __newstool_plugin__(), UsesLLMOptions, TaggerOptions, ProcessorOptions (+2 more)

### Community 26 - "SourceItem"
Cohesion: 0.10
Nodes (5): backoff_seconds(), DBProcessingState, DBSourceItem, SourceItem, make_item()

### Community 27 - "Base"
Cohesion: 0.28
Nodes (3): Base, DBItemAnnotation, MigrateAutoincrementTests

### Community 30 - "grouping.py"
Cohesion: 0.07
Nodes (24): average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer, GroupingOptions (+16 more)

### Community 31 - "report_user_errors"
Cohesion: 0.18
Nodes (9): check_found(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_deliveries_cmd(), delete_items_cmd(), inspect_artifacts_cmd(), report_user_errors(), require_selection() (+1 more)

### Community 32 - "inspect_annotations_cmd"
Cohesion: 0.15
Nodes (11): format_value(), inspect_annotations_cmd(), inspect_deliveries_cmd(), inspect_items_cmd(), json_default(), preview(), print_deliver(), print_item() (+3 more)

### Community 34 - "plugins"
Cohesion: 0.11
Nodes (18): lookback, title, url, api_base, api_key, chat_model, embed_model, plugins (+10 more)

### Community 35 - "FeedReaderProvider"
Cohesion: 0.10
Nodes (4): SelectionRequiredError, ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 38 - "config.py"
Cohesion: 0.12
Nodes (6): CacheConfig, DatabaseConfig, expand_variables(), MissingVariableError, options_error(), parse_duration()

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.18
Nodes (14): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0005 Remixers with external side effects, ADR 0006 LLM plugins (+6 more)

### Community 41 - "options"
Cohesion: 0.11
Nodes (20): options, sink, artifacts, chat_id, interval, item_image, item_url_preview, item_url_text (+12 more)

### Community 42 - "hooks"
Cohesion: 0.15
Nodes (12): exclude, args, entry, files, id, language, name, pass_filenames (+4 more)

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "GoogleChatSinkTests"
Cohesion: 0.13
Nodes (6): __newstool_plugin__(), WebhookOptions, card_widgets(), GoogleChatSinkTests, OptionsTests, webhook_options()

### Community 45 - "config.example.yaml"
Cohesion: 0.11
Nodes (15): cache, expiration, llms, input, processors, options, processor, remixers (+7 more)

### Community 46 - "Workflow"
Cohesion: 0.10
Nodes (10): share_sources(), import_sources(), own_entries(), Workflow, Changes, Context, Design, Review findings (current code) (+2 more)

### Community 47 - "cli.py"
Cohesion: 0.12
Nodes (5): delete_group(), inspect_group(), lexer_for(), match_snippet(), print_content()

### Community 50 - "MarkdownifyProcessor"
Cohesion: 0.14
Nodes (6): ClassRegister, MarkdownifyProcessor, SkipItem, ClassRegisterTests, make_pdf(), MarkdownifyPdfTests

### Community 51 - "SourceData"
Cohesion: 0.07
Nodes (19): DBSource, HTTPClient, LazySourceItemData, SourceData, SourceItemData, CastellonInformacionProvider, fetch_article(), get_section() (+11 more)

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 58 - "newsmerger CLAUDE.md agent guidelines"
Cohesion: 0.20
Nodes (12): BaseSink deliver cycle (queue, select, send), cli.py Click commands, Database (db.py, only SQLite/storage access), deliveries table (the ledger), foundation.storage.DiskStorage content-addressed storage, foundation internal library, Strict FIFO per source, inspect items|annotations|artifacts|deliveries (+4 more)

### Community 59 - "Services"
Cohesion: 0.07
Nodes (24): Decision, LLMType, LLMUnavailableError, __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__() (+16 more)

### Community 60 - "ProcessingScope"
Cohesion: 0.10
Nodes (9): ProcessingScope, DigestRemixer, FeedGeneratorRemixer, BaseRemixer, Remixer, migrate(), SearchTests, DigestRemixerTests (+1 more)

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 64 - "scope_options"
Cohesion: 0.23
Nodes (6): annotation_options(), artifact_options(), delivery_options(), wrapper(), scope_options(), wrapper()

### Community 66 - "TestFeedReader"
Cohesion: 0.21
Nodes (3): FeedReaderProvider, select_article(), TestFeedReader

### Community 73 - "foundation.plugin.Register plugin loading"
Cohesion: 0.50
Nodes (4): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section

### Community 75 - "setup_logging"
Cohesion: 0.33
Nodes (4): Additional Approved Packages, Framework Usage, newstool Python Specifics, setup_logging()

## Knowledge Gaps
- **13 isolated node(s):** `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)`, `P1: plain logging and <APP>_LOG_LEVEL fix` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 464 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_db.py`, `Application`, `telegram.py`, `migrate_telegram_state.py`, `.llm`, `.session_scope`, `Artifact`, `.get_annotation_values`, `DeliveryStatus`, `Any`, `db.py`, `SourceItem`, `Base`, `grouping.py`, `FeedReaderProvider`, `GoogleChatSinkTests`, `Workflow`, `MarkdownifyProcessor`, `SourceData`, `ProcessingScope`?**
  _High betweenness centrality (0.175) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 43 INFERRED edges - model-reasoned connections that need verification._
- **What connects `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.057946069994262765 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `ProcessingScope` to `test_db.py`, `Application`, `.from_text`, `Database`, `telegram.py`, `migrate_telegram_state.py`, `.llm`, `.session_scope`, `app_from_context`, `Artifact`, `.get_annotation_values`, `DeliveryStatus`, `db.py`, `grouping.py`, `report_user_errors`, `inspect_annotations_cmd`, `FeedReaderProvider`, `cli.py`, `scope_options`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Should `ConfigError` be split into smaller, more focused modules?**
  _Cohesion score 0.09292929292929293 - nodes in this community are weakly interconnected._