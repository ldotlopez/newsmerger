# Graph Report - inspect-delete-no-processor  (2026-10-28)

## Corpus Check
- 72 files · ~122,526 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1554 nodes · 4459 edges · 81 communities (59 shown, 22 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 595 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7baeba2b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- Database
- .close
- ApplicationTests
- ConfigError
- test_telegram.py
- Application
- migrate_telegram_state.py
- Artifact
- StubLLM
- .session_scope
- app_from_context
- plugins/__init__.py
- Artifact
- run_cmd
- Services
- DeliveryStatus
- TelegramChannelProvider
- migrate_autoincrement.py
- catalog.py
- 0009: Workflows and keyed entries
- Any
- .get_annotation_values
- SourceItem
- ProcessingScope
- HTTPClient
- Database
- MarkdownifyProcessor
- PrensaIbericaPlainProvider
- deliveries table (the ledger)
- Delivery
- report_user_errors
- .workflow
- plugins/__init__.py
- plugins
- RecordingItemSink
- Workflow
- scope_options
- Config
- ADR 0007 Sinks and the delivery ledger
- ScoredItem
- options
- hooks
- Services object (services.llm(name))
- GoogleChatSinkTests
- config.example.yaml
- SinkType
- inspect_annotations_cmd
- digest.py
- RemixerType
- Entry
- catalog.py
- LogLevelTests
- GoogleChatError
- Processor
- El Periódico Mediterráneo
- migrate_autoincrement.py
- URI
- Database (db.py, only SQLite/storage access)
- ollama.py
- 0010: Plugin classes and the configuration catalog
- Item
- ClassRegister
- Entry
- Any
- .__init__
- migrate
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- newsmerger CLAUDE.md agent guidelines
- Artifact
- Grouping notes: NLP clustering pipeline
- news-aggregator
- foundation internal library
- .__init__
- SourceData
- FeedGeneratorRemixer
- Sink
- DBSource
- _sha256_column
- ADR 0002 Processing state lifecycle

## God Nodes (most connected - your core abstractions)
1. `Database` - 159 edges
2. `ProcessingScope` - 134 edges
3. `SourceItem` - 119 edges
4. `SourceData` - 82 edges
5. `Services` - 75 edges
6. `Artifact` - 62 edges
7. `Application` - 60 edges
8. `SourceItemData` - 51 edges
9. `HTTPClient` - 46 edges
10. `ApplicationTests` - 40 edges

## Surprising Connections (you probably didn't know these)
- `Decision` --references--> `Application`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/app.py
- `Decision` --references--> `LLMType`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/llms.py
- `Decision` --references--> `UsesLLMOptions`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/plugins/__init__.py
- `Decision` --references--> `Services`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/plugins/__init__.py
- `Decision` --references--> `ClassRegister`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/plugins/__init__.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (81 total, 22 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.08
Nodes (11): AnnotationTests, ConnectionTests, ContentStorageTests, DatabaseTestCase, DeleteTests, GetItemsTests, IdentityTests, make_item() (+3 more)

### Community 1 - "Database"
Cohesion: 0.10
Nodes (5): tags_text(), merge_tags(), TaggerProcessor, BaseProcessor, MissingAnnotationError

### Community 2 - ".close"
Cohesion: 0.08
Nodes (4): EmbeddingGroupingTests, FeedGeneratorTests, GroupingTests, RemixerTestCase

### Community 4 - "ConfigError"
Cohesion: 0.12
Nodes (4): Catalog, Run, share_sources(), ConfigError

### Community 5 - "test_telegram.py"
Cohesion: 0.23
Nodes (5): ItemDeliveryOptions, TelegramSink, item_options(), ok_response(), TelegramSinkTests

### Community 6 - "Application"
Cohesion: 0.05
Nodes (3): Application, lookup(), workflow_scope()

### Community 7 - "migrate_telegram_state.py"
Cohesion: 0.12
Nodes (5): LockedError, write_lock(), main(), migrate(), main()

### Community 8 - "Artifact"
Cohesion: 0.13
Nodes (5): DBArtifact, Artifact, ArtifactTests, MigrateFeedNamesTests, MigrateTelegramStateTests

### Community 9 - "StubLLM"
Cohesion: 0.11
Nodes (11): __newsmerger_plugin__(), SummarizeOptions, Processor, ProcessorType, build(), ConsumerPluginTests, EmbedTests, ProcessorTestCase (+3 more)

### Community 11 - "app_from_context"
Cohesion: 0.16
Nodes (8): app_from_context(), cli(), import_cmd(), inspect_content_cmd(), parse_artifact_ids(), process_cmd(), remix_cmd(), search_cmd()

### Community 12 - "plugins/__init__.py"
Cohesion: 0.24
Nodes (10): __newsmerger_plugin__(), __newsmerger_plugin__(), PluginTypes, __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__() (+2 more)

### Community 13 - "Artifact"
Cohesion: 0.14
Nodes (5): RunSummary, annotation(), CommandTests, InspectCommandTests, invoke()

### Community 14 - "run_cmd"
Cohesion: 0.13
Nodes (9): import_sources(), print_deliver(), print_import(), print_process(), print_remix(), print_table(), progress_rows(), run_cmd() (+1 more)

### Community 15 - "Services"
Cohesion: 0.09
Nodes (8): LLM, LLMUnavailableError, EmbedOptions, EmbedProcessor, __newsmerger_plugin__(), Services, ServicesTests, factory()

### Community 17 - "TelegramChannelProvider"
Cohesion: 0.14
Nodes (10): Options, Options, page_title(), parse_article(), parse_preview(), Post, preview_url(), TelegramChannelProvider (+2 more)

### Community 18 - "migrate_autoincrement.py"
Cohesion: 0.10
Nodes (9): Base, DBItemAnnotation, DBProcessingState, main(), migrate(), needs_autoincrement(), recreate(), make_item() (+1 more)

### Community 19 - "catalog.py"
Cohesion: 0.12
Nodes (7): in_default(), Kind, Profile, Use, DeliveryEntry, ProcessEntry, RemixEntry

### Community 20 - "0009: Workflows and keyed entries"
Cohesion: 0.33
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 21 - "Any"
Cohesion: 0.14
Nodes (3): CustomJSON, _encode_value(), UTCDateTime

### Community 22 - ".get_annotation_values"
Cohesion: 0.12
Nodes (3): ItemKey, GoogleChatError, GoogleChatSink

### Community 24 - "ProcessingScope"
Cohesion: 0.15
Nodes (5): wrapper(), ProcessingScope, SearchTests, DeliveryTests, DigestRemixerTests

### Community 25 - "HTTPClient"
Cohesion: 0.13
Nodes (5): HTTPClient, fetch_article(), is_home_page(), IndexSiteProvider, TestHTTPClient

### Community 26 - "Database"
Cohesion: 0.10
Nodes (3): backoff_seconds(), Database, SummarizeProcessor

### Community 27 - "MarkdownifyProcessor"
Cohesion: 0.16
Nodes (7): MarkdownifyProcessor, __newsmerger_plugin__(), ProcessorOptions, SkipItem, ClassRegisterTests, make_pdf(), MarkdownifyPdfTests

### Community 29 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 30 - "Delivery"
Cohesion: 0.14
Nodes (4): DBDelivery, Delivery, ArtifactNames, BaseArtifactSink

### Community 31 - "report_user_errors"
Cohesion: 0.18
Nodes (9): check_found(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_deliveries_cmd(), delete_items_cmd(), inspect_artifacts_cmd(), report_user_errors(), require_selection() (+1 more)

### Community 32 - ".workflow"
Cohesion: 0.16
Nodes (9): format_value(), inspect_annotations_cmd(), inspect_deliveries_cmd(), inspect_items_cmd(), json_default(), preview(), print_item(), print_json() (+1 more)

### Community 33 - "plugins/__init__.py"
Cohesion: 0.12
Nodes (10): Duration, Options, cosine_similarity(), EmbeddingsOptions, GroupingOptions, time_decay(), NoOptions, PluginOptions (+2 more)

### Community 34 - "plugins"
Cohesion: 0.11
Nodes (18): lookback, title, url, api_base, api_key, chat_model, embed_model, plugins (+10 more)

### Community 35 - "RecordingItemSink"
Cohesion: 0.16
Nodes (6): SelectionRequiredError, ArtifactSinkTests, ItemSinkTests, RecordingArtifactSink, RecordingItemSink, SinkTestCase

### Community 37 - "scope_options"
Cohesion: 0.25
Nodes (5): annotation_options(), artifact_options(), delivery_options(), wrapper(), scope_options()

### Community 38 - "Config"
Cohesion: 0.17
Nodes (4): DeliveryStatus, ProcessingStatus, Annotation, TelegramTestCase

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.21
Nodes (14): Architecture, cli.py Click commands, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger (+6 more)

### Community 40 - "ScoredItem"
Cohesion: 0.11
Nodes (16): average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), EmbeddingsRemixer, GroupingRemixer, item_ref(), jaccard() (+8 more)

### Community 41 - "options"
Cohesion: 0.11
Nodes (19): options, sink, artifacts, chat_id, interval, item_image, item_url_preview, item_url_text (+11 more)

### Community 42 - "hooks"
Cohesion: 0.15
Nodes (12): exclude, args, entry, files, id, language, name, pass_filenames (+4 more)

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "GoogleChatSinkTests"
Cohesion: 0.09
Nodes (8): build_card(), chat_image_url(), WebhookOptions, card_widgets(), ChatImageUrlTests, GoogleChatSinkTests, OptionsTests, webhook_options()

### Community 45 - "config.example.yaml"
Cohesion: 0.11
Nodes (15): cache, expiration, llms, input, processors, options, processor, remixers (+7 more)

### Community 46 - "SinkType"
Cohesion: 0.20
Nodes (7): 0010: Plugin classes and the configuration catalog, Consequences, Context, Decision, Rejected options, __newsmerger_plugin__(), SinkType

### Community 47 - "inspect_annotations_cmd"
Cohesion: 0.10
Nodes (5): delete_group(), inspect_group(), lexer_for(), match_snippet(), print_content()

### Community 48 - "digest.py"
Cohesion: 0.14
Nodes (9): strip_code_fence(), DigestOptions, DigestRemixer, __newsmerger_plugin__(), UsesLLMOptions, __newsmerger_plugin__(), TaggerOptions, DigestPluginTests (+1 more)

### Community 49 - "RemixerType"
Cohesion: 0.20
Nodes (5): __newsmerger_plugin__(), __newsmerger_plugin__(), Remixer, RemixerType, GroupingPluginTests

### Community 50 - "Entry"
Cohesion: 0.18
Nodes (3): ids_of(), Entry, LLMEntry

### Community 51 - "catalog.py"
Cohesion: 0.17
Nodes (3): check_section(), options_error(), merge_options()

### Community 53 - "GoogleChatError"
Cohesion: 0.11
Nodes (10): build_caption(), DocumentDeliveryOptions, __newsmerger_plugin__(), post(), TelegramArtifactSink, TelegramError, ArtifactDeliveryOptions, BuildCaptionTests (+2 more)

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 56 - "migrate_autoincrement.py"
Cohesion: 0.20
Nodes (5): SourceItemData, PrensaIbericaProvider, TheGuardianProvider, TestPrensaIberica, TestSourceItemDataContent

### Community 57 - "URI"
Cohesion: 0.25
Nodes (4): get_section(), parse_datetime(), PlazaProvider, SectionNotFoundError

### Community 58 - "Database (db.py, only SQLite/storage access)"
Cohesion: 0.17
Nodes (11): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention, AUTOINCREMENT integer ids, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage (+3 more)

### Community 59 - "ollama.py"
Cohesion: 0.18
Nodes (6): LLMType, __newsmerger_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 60 - "0010: Plugin classes and the configuration catalog"
Cohesion: 0.29
Nodes (7): discover_feed_url(), entry_date(), fetch_feed(), find_image(), __newsmerger_plugin__(), parse_entry(), select_article()

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 63 - "Entry"
Cohesion: 0.15
Nodes (5): CacheConfig, DatabaseConfig, expand_variables(), MissingVariableError, parse_duration()

### Community 65 - ".__init__"
Cohesion: 0.25
Nodes (5): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, TestCSJuntasGobierno

### Community 73 - "foundation internal library"
Cohesion: 0.29
Nodes (7): foundation internal library, foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section, P1: plain logging and <APP>_LOG_LEVEL fix, P2: rich progress per stream (RICH_STDOUT_*/RICH_STDERR_*)

### Community 75 - "SourceData"
Cohesion: 0.13
Nodes (4): SourceData, CastellonInformacionProvider, BaseProvider, Provider

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `External pipelines (scripts/pipeline_url.py)`, `PluginOptions (pydantic, unknown keys rejected)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 455 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_db.py`, `Database`, `.close`, `test_telegram.py`, `Application`, `migrate_telegram_state.py`, `Artifact`, `StubLLM`, `.session_scope`, `Services`, `DeliveryStatus`, `migrate_autoincrement.py`, `Any`, `.get_annotation_values`, `SourceItem`, `ProcessingScope`, `MarkdownifyProcessor`, `Delivery`, `plugins/__init__.py`, `RecordingItemSink`, `Config`, `ScoredItem`, `GoogleChatSinkTests`, `digest.py`, `RemixerType`, `GoogleChatError`, `ClassRegister`, `Any`, `.__init__`, `SourceData`, `FeedGeneratorRemixer`, `Sink`?**
  _High betweenness centrality (0.152) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 43 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `External pipelines (scripts/pipeline_url.py)`, `PluginOptions (pydantic, unknown keys rejected)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0773892773892774 - nodes in this community are weakly interconnected._
- **Why does `SourceItem` connect `SourceItem` to `test_db.py`, `Database`, `.close`, `ApplicationTests`, `test_telegram.py`, `Application`, `migrate_telegram_state.py`, `StubLLM`, `.session_scope`, `Artifact`, `Services`, `DeliveryStatus`, `migrate_autoincrement.py`, `Any`, `.get_annotation_values`, `ProcessingScope`, `Database`, `MarkdownifyProcessor`, `.workflow`, `plugins/__init__.py`, `RecordingItemSink`, `Config`, `ScoredItem`, `GoogleChatSinkTests`, `inspect_annotations_cmd`, `digest.py`, `GoogleChatError`, `Any`, `SourceData`, `FeedGeneratorRemixer`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Should `Database` be split into smaller, more focused modules?**
  _Cohesion score 0.10153846153846154 - nodes in this community are weakly interconnected._