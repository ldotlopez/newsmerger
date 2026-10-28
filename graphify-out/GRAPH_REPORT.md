# Graph Report - feedreader-fetch-article  (2026-10-28)

## Corpus Check
- 72 files · ~122,586 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1559 nodes · 4481 edges · 78 communities (52 shown, 26 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 594 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ace3a2c9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- BaseProcessor
- .close
- ApplicationTests
- .__init__
- TelegramSinkTests
- Application
- migrate_telegram_state.py
- Artifact
- StubLLM
- .session_scope
- app_from_context
- PluginTypes
- test_cli.py
- process_cmd
- Services
- BaseSink
- test_providers.py
- Catalog
- catalog.py
- 0009: Workflows and keyed entries
- Any
- SourceItem
- Database
- ProcessingScope
- SourceData
- .get_artifact
- MarkdownifyProcessor
- PrensaIbericaPlainProvider
- deliveries table (the ledger)
- Delivery
- delete_items_cmd
- inspect_items_cmd
- googlechat.py
- plugins
- RecordingItemSink
- Config
- report_user_errors
- db.py
- ADR 0007 Sinks and the delivery ledger
- grouping.py
- options
- hooks
- Services object (services.llm(name))
- GoogleChatSinkTests
- config.example.yaml
- .llm
- cli.py
- models.py
- merge_options
- TestSourceItemDataContent
- ConfigError
- LogLevelTests
- sinks.py
- Processor
- El Periódico Mediterráneo
- SourceItemData
- get_section
- cli.py Click commands
- OllamaLLM
- feedreader.py
- Item
- DigestRemixer
- config.py
- Sink
- CSJuntasGobiernoProvider
- TestFeedReader
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- Workflow
- Artifact
- Grouping notes: NLP clustering pipeline
- news-aggregator
- newsmerger CLAUDE.md agent guidelines
- workflows
- Provider
- ConsumerPluginTests
- ADR 0002 Processing state lifecycle

## God Nodes (most connected - your core abstractions)
1. `Database` - 158 edges
2. `ProcessingScope` - 138 edges
3. `SourceItem` - 119 edges
4. `SourceData` - 82 edges
5. `Services` - 75 edges
6. `Artifact` - 62 edges
7. `Application` - 60 edges
8. `SourceItemData` - 51 edges
9. `HTTPClient` - 46 edges
10. `ApplicationTests` - 42 edges

## Surprising Connections (you probably didn't know these)
- `Decision` --references--> `Application`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/app.py
- `Decision` --references--> `LLMType`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/llms.py
- `Decision` --references--> `Services`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/plugins/__init__.py
- `Decision` --references--> `ClassRegister`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/plugins/__init__.py
- `Decision` --references--> `ProviderType`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/providers.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (78 total, 26 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.06
Nodes (17): Base, DBItemAnnotation, DBProcessingState, DBSource, DBSourceItem, AnnotationTests, ArtifactTests, ConnectionTests (+9 more)

### Community 1 - "BaseProcessor"
Cohesion: 0.08
Nodes (6): EmbedProcessor, tags_text(), SummarizeProcessor, merge_tags(), BaseProcessor, MissingAnnotationError

### Community 2 - ".close"
Cohesion: 0.13
Nodes (3): ProcessorTestCase, make_item(), MigrateAutoincrementTests

### Community 4 - ".__init__"
Cohesion: 0.13
Nodes (3): Run, share_sources(), ClassRegister

### Community 5 - "TelegramSinkTests"
Cohesion: 0.23
Nodes (5): TelegramSink, item_options(), ok_response(), TelegramSinkTests, TelegramTestCase

### Community 7 - "migrate_telegram_state.py"
Cohesion: 0.08
Nodes (9): LockedError, write_lock(), main(), migrate(), needs_autoincrement(), recreate(), main(), migrate() (+1 more)

### Community 8 - "Artifact"
Cohesion: 0.14
Nodes (7): DBArtifact, Artifact, BaseArtifactSink, SelectionRequiredError, ArtifactSinkTests, RecordingArtifactSink, MigrateTelegramStateTests

### Community 9 - "StubLLM"
Cohesion: 0.15
Nodes (6): Processor, build(), EmbedTests, StubLLM, SummarizeTests, TaggerTests

### Community 11 - "app_from_context"
Cohesion: 0.15
Nodes (9): app_from_context(), cli(), deliver_cmd(), inspect_content_cmd(), inspect_deliveries_cmd(), parse_artifact_ids(), process_cmd(), resolve_cmd() (+1 more)

### Community 12 - "PluginTypes"
Cohesion: 0.12
Nodes (11): __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), Options, NoOptions, __newsmerger_plugin__(), __newsmerger_plugin__() (+3 more)

### Community 13 - "test_cli.py"
Cohesion: 0.14
Nodes (5): RunSummary, annotation(), CommandTests, InspectCommandTests, invoke()

### Community 14 - "process_cmd"
Cohesion: 0.15
Nodes (8): import_cmd(), import_sources(), print_import(), print_remix(), progress_rows(), remix_cmd(), run_cmd(), run_each()

### Community 15 - "Services"
Cohesion: 0.13
Nodes (6): DigestOptions, EmbedOptions, Services, TaggerProcessor, DigestPluginTests, factory()

### Community 17 - "test_providers.py"
Cohesion: 0.11
Nodes (13): Options, PluginOptions, is_home_page(), __newsmerger_plugin__(), Options, page_title(), parse_article(), parse_preview() (+5 more)

### Community 19 - "catalog.py"
Cohesion: 0.11
Nodes (8): ids_of(), in_default(), Kind, Use, DeliveryEntry, Entry, ProcessEntry, RemixEntry

### Community 20 - "0009: Workflows and keyed entries"
Cohesion: 0.33
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 21 - "Any"
Cohesion: 0.12
Nodes (4): _configure_sqlite_connection(), CustomJSON, _encode_value(), UTCDateTime

### Community 22 - "SourceItem"
Cohesion: 0.08
Nodes (5): ItemKey, SourceItem, FeedGeneratorRemixer, GoogleChatError, SearchTests

### Community 24 - "ProcessingScope"
Cohesion: 0.14
Nodes (4): ProcessingScope, Remixer, DeliveryTests, DigestRemixerTests

### Community 25 - "SourceData"
Cohesion: 0.13
Nodes (12): HTTPClient, SourceData, CastellonInformacionProvider, FeedReaderProvider, fetch_article(), PlazaProvider, PrensaIbericaProvider, TheGuardianProvider (+4 more)

### Community 27 - "MarkdownifyProcessor"
Cohesion: 0.23
Nodes (5): MarkdownifyProcessor, SkipItem, ClassRegisterTests, make_pdf(), MarkdownifyPdfTests

### Community 29 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 31 - "delete_items_cmd"
Cohesion: 0.21
Nodes (5): delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), require_selection(), sort_option()

### Community 32 - "inspect_items_cmd"
Cohesion: 0.15
Nodes (10): check_found(), format_value(), inspect_artifacts_cmd(), inspect_items_cmd(), json_default(), print_deliver(), print_item(), print_json() (+2 more)

### Community 33 - "googlechat.py"
Cohesion: 0.16
Nodes (5): build_card(), chat_image_url(), __newsmerger_plugin__(), BaseItemSink, ChatImageUrlTests

### Community 34 - "plugins"
Cohesion: 0.11
Nodes (18): lookback, title, url, api_base, api_key, chat_model, embed_model, plugins (+10 more)

### Community 35 - "RecordingItemSink"
Cohesion: 0.32
Nodes (3): ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 37 - "report_user_errors"
Cohesion: 0.19
Nodes (8): annotation_options(), artifact_options(), inspect_annotations_cmd(), preview(), report_user_errors(), wrapper(), scope_options(), wrapper()

### Community 38 - "db.py"
Cohesion: 0.17
Nodes (3): DeliveryStatus, ProcessingStatus, _sha256_column()

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.22
Nodes (13): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger (+5 more)

### Community 40 - "grouping.py"
Cohesion: 0.06
Nodes (26): average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer, GroupingOptions (+18 more)

### Community 41 - "options"
Cohesion: 0.17
Nodes (13): options, artifacts, chat_id, interval, item_image, item_url_preview, item_url_text, max_per_run (+5 more)

### Community 42 - "hooks"
Cohesion: 0.15
Nodes (12): exclude, args, entry, files, id, language, name, pass_filenames (+4 more)

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.18
Nodes (13): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+5 more)

### Community 45 - "config.example.yaml"
Cohesion: 0.10
Nodes (18): cache, expiration, llms, input, processors, options, processor, remixers (+10 more)

### Community 46 - ".llm"
Cohesion: 0.16
Nodes (7): 0010: Plugin classes and the configuration catalog, Consequences, Context, Rejected options, LLMUnavailableError, ServicesTests, factory()

### Community 47 - "cli.py"
Cohesion: 0.09
Nodes (7): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content(), print_process()

### Community 48 - "models.py"
Cohesion: 0.09
Nodes (14): Decision, LLM, strip_code_fence(), Annotation, __newsmerger_plugin__(), PluginTypes, UsesLLMOptions, __newsmerger_plugin__() (+6 more)

### Community 49 - "merge_options"
Cohesion: 0.16
Nodes (5): GoogleChatSink, WebhookOptions, merge_options(), OptionsTests, webhook_options()

### Community 51 - "ConfigError"
Cohesion: 0.15
Nodes (4): lookup(), check_section(), ConfigError, options_error()

### Community 53 - "sinks.py"
Cohesion: 0.09
Nodes (15): Duration, backoff_seconds(), build_caption(), DocumentDeliveryOptions, ItemDeliveryOptions, __newsmerger_plugin__(), post(), TelegramArtifactSink (+7 more)

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 57 - "get_section"
Cohesion: 0.27
Nodes (4): get_section(), __newsmerger_plugin__(), parse_datetime(), SectionNotFoundError

### Community 58 - "cli.py Click commands"
Cohesion: 0.23
Nodes (10): cli.py Click commands, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage, SQLAlchemy models never leave db.py; DTOs cross the boundary, foundation internal library, inspect items|annotations|artifacts|deliveries, Application class (single entry point), Phases: import, enrich, remix, deliver (+2 more)

### Community 59 - "OllamaLLM"
Cohesion: 0.16
Nodes (6): LLMType, __newsmerger_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 60 - "feedreader.py"
Cohesion: 0.27
Nodes (7): discover_feed_url(), entry_date(), fetch_feed(), find_image(), __newsmerger_plugin__(), parse_entry(), select_article()

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 63 - "config.py"
Cohesion: 0.12
Nodes (6): CacheConfig, DatabaseConfig, expand_variables(), LLMEntry, MissingVariableError, parse_duration()

### Community 65 - "CSJuntasGobiernoProvider"
Cohesion: 0.23
Nodes (5): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, TestCSJuntasGobierno

### Community 73 - "newsmerger CLAUDE.md agent guidelines"
Cohesion: 0.33
Nodes (5): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention

### Community 74 - "workflows"
Cohesion: 0.33
Nodes (6): sink, workflows, deliver, name, process, sources

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `PluginOptions (pydantic, unknown keys rejected)`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)`, `Annotation` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 457 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_db.py`, `BaseProcessor`, `.close`, `.__init__`, `TelegramSinkTests`, `Application`, `migrate_telegram_state.py`, `Artifact`, `StubLLM`, `.session_scope`, `PluginTypes`, `Services`, `BaseSink`, `Any`, `SourceItem`, `ProcessingScope`, `SourceData`, `.get_artifact`, `MarkdownifyProcessor`, `Delivery`, `googlechat.py`, `RecordingItemSink`, `db.py`, `grouping.py`, `GoogleChatSinkTests`, `models.py`, `merge_options`, `sinks.py`, `DigestRemixer`, `Sink`?**
  _High betweenness centrality (0.166) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 43 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `PluginOptions (pydantic, unknown keys rejected)`, `P1: plain logging and <APP>_LOG_LEVEL fix` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05798319327731093 - nodes in this community are weakly interconnected._
- **Why does `SourceItem` connect `SourceItem` to `test_db.py`, `BaseProcessor`, `.close`, `ApplicationTests`, `TelegramSinkTests`, `Application`, `migrate_telegram_state.py`, `.session_scope`, `PluginTypes`, `test_cli.py`, `Services`, `BaseSink`, `Database`, `ProcessingScope`, `.get_artifact`, `MarkdownifyProcessor`, `inspect_items_cmd`, `googlechat.py`, `RecordingItemSink`, `db.py`, `grouping.py`, `GoogleChatSinkTests`, `cli.py`, `models.py`, `merge_options`, `sinks.py`, `DigestRemixer`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Are the 38 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Should `BaseProcessor` be split into smaller, more focused modules?**
  _Cohesion score 0.08387096774193549 - nodes in this community are weakly interconnected._