# Graph Report - telegram-markdown-option  (2026-10-28)

## Corpus Check
- 72 files · ~122,491 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1556 nodes · 4477 edges · 83 communities (59 shown, 24 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 594 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ace3a2c9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- BaseProcessor
- plugins/__init__.py
- ApplicationTests
- LLM
- TelegramSinkTests
- Application
- migrate_telegram_state.py
- TestFeedReader
- StubLLM
- DeleteCommandTests
- app_from_context
- models.py
- ProcessingScope
- process_cmd
- test_remixers.py
- Delivery
- test_providers.py
- catalog.py
- Services
- 0009: Workflows and keyed entries
- Any
- Database
- HTTPClient
- SourceData
- sinks.py
- markdownify.py
- PrensaIbericaPlainProvider
- deliveries table (the ledger)
- DeliveryStatus
- delete_items_cmd
- .close
- config.py
- plugins
- RecordingItemSink
- test_telegram.py
- report_user_errors
- Config
- ADR 0007 Sinks and the delivery ledger
- grouping.py
- options
- hooks
- Services object (services.llm(name))
- CSJuntasGobiernoProvider
- config.example.yaml
- SourceItem
- print_table
- db.py
- WebhookOptions
- SourceItemData
- cli.py
- LogLevelTests
- .get_annotation_values
- Processor
- El Periódico Mediterráneo
- Artifact
- get_section
- cli.py Click commands
- OllamaLLM
- GoogleChatSinkTests
- Item
- digest.py
- SinkType
- ClassRegister
- MigrateAutoincrementTests
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- newsmerger CLAUDE.md agent guidelines
- Artifact
- Grouping notes: NLP clustering pipeline
- news-aggregator
- workflows
- BaseProvider
- post
- recreate
- EmbeddingGroupingTests
- parse_entry
- foundation.plugin.Register plugin loading
- GoogleChatError
- MissingAnnotationError

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
- `Decision` --references--> `UsesLLMOptions`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/plugins/__init__.py
- `Decision` --references--> `Services`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/plugins/__init__.py
- `Decision` --references--> `ClassRegister`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/plugins/__init__.py
- `Decision` --references--> `ProcessorType`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/processors.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (83 total, 24 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.06
Nodes (14): DBDelivery, DBProcessingState, AnnotationTests, ConnectionTests, ContentStorageTests, DatabaseTestCase, DeleteTests, DeliveryTests (+6 more)

### Community 1 - "BaseProcessor"
Cohesion: 0.18
Nodes (3): SummarizeProcessor, TaggerProcessor, BaseProcessor

### Community 2 - "plugins/__init__.py"
Cohesion: 0.10
Nodes (10): strip_code_fence(), __newsmerger_plugin__(), tags_text(), PluginOptions, __newsmerger_plugin__(), SummarizeOptions, merge_tags(), __newsmerger_plugin__() (+2 more)

### Community 4 - "LLM"
Cohesion: 0.12
Nodes (7): 0010: Plugin classes and the configuration catalog, Consequences, Context, Decision, Rejected options, LLM, LLMType

### Community 5 - "TelegramSinkTests"
Cohesion: 0.26
Nodes (4): TelegramSink, item_options(), ok_response(), TelegramSinkTests

### Community 6 - "Application"
Cohesion: 0.05
Nodes (5): Application, lookup(), workflow_scope(), Workflow, Annotation

### Community 7 - "migrate_telegram_state.py"
Cohesion: 0.13
Nodes (3): LockedError, write_lock(), main()

### Community 9 - "StubLLM"
Cohesion: 0.12
Nodes (9): EmbedOptions, EmbedProcessor, Processor, build(), EmbedTests, ProcessorTestCase, StubLLM, SummarizeTests (+1 more)

### Community 11 - "app_from_context"
Cohesion: 0.15
Nodes (8): app_from_context(), cli(), deliver_cmd(), inspect_content_cmd(), inspect_deliveries_cmd(), parse_artifact_ids(), resolve_cmd(), search_cmd()

### Community 12 - "models.py"
Cohesion: 0.24
Nodes (10): __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), PluginTypes, __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__() (+2 more)

### Community 13 - "ProcessingScope"
Cohesion: 0.12
Nodes (8): ProcessingScope, RunSummary, Sink, annotation(), CommandTests, InspectCommandTests, invoke(), SearchTests

### Community 14 - "process_cmd"
Cohesion: 0.14
Nodes (9): import_cmd(), import_sources(), print_process(), print_remix(), process_cmd(), progress_rows(), remix_cmd(), run_cmd() (+1 more)

### Community 15 - "test_remixers.py"
Cohesion: 0.15
Nodes (6): __newsmerger_plugin__(), __newsmerger_plugin__(), BaseRemixer, Remixer, RemixerType, GroupingPluginTests

### Community 16 - "Delivery"
Cohesion: 0.08
Nodes (4): Delivery, ArtifactNames, BaseArtifactSink, BaseSink

### Community 17 - "test_providers.py"
Cohesion: 0.14
Nodes (10): Options, Options, page_title(), parse_article(), parse_preview(), Post, preview_url(), TelegramChannelProvider (+2 more)

### Community 18 - "catalog.py"
Cohesion: 0.07
Nodes (14): Catalog, check_section(), ids_of(), in_default(), Kind, Profile, Run, share_sources() (+6 more)

### Community 19 - "Services"
Cohesion: 0.14
Nodes (6): LLMUnavailableError, Services, TaggerOptions, ConsumerPluginTests, ServicesTests, factory()

### Community 20 - "0009: Workflows and keyed entries"
Cohesion: 0.33
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 21 - "Any"
Cohesion: 0.10
Nodes (5): backoff_seconds(), _configure_sqlite_connection(), CustomJSON, _encode_value(), UTCDateTime

### Community 24 - "HTTPClient"
Cohesion: 0.17
Nodes (6): HTTPClient, discover_feed_url(), fetch_article(), fetch_feed(), is_home_page(), TestHTTPClient

### Community 25 - "SourceData"
Cohesion: 0.14
Nodes (7): DBSource, SourceData, CastellonInformacionProvider, PlazaProvider, TheGuardianProvider, IndexSiteProvider, URI

### Community 26 - "sinks.py"
Cohesion: 0.12
Nodes (9): build_card(), chat_image_url(), GoogleChatSink, DocumentDeliveryOptions, ItemDeliveryOptions, ArtifactDeliveryOptions, BaseItemSink, DeliveryOptions (+1 more)

### Community 27 - "markdownify.py"
Cohesion: 0.20
Nodes (5): MarkdownifyProcessor, __newsmerger_plugin__(), SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 29 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 30 - "DeliveryStatus"
Cohesion: 0.23
Nodes (4): DeliveryStatus, migrate(), MigrateTelegramStateTests, TelegramTestCase

### Community 31 - "delete_items_cmd"
Cohesion: 0.21
Nodes (5): delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), require_selection(), sort_option()

### Community 32 - ".close"
Cohesion: 0.08
Nodes (5): Options, DigestRemixerTests, FeedGeneratorTests, GroupingTests, RemixerTestCase

### Community 33 - "config.py"
Cohesion: 0.12
Nodes (6): CacheConfig, DatabaseConfig, expand_variables(), MissingVariableError, options_error(), parse_duration()

### Community 34 - "plugins"
Cohesion: 0.11
Nodes (18): lookback, title, url, api_base, api_key, chat_model, embed_model, plugins (+10 more)

### Community 35 - "RecordingItemSink"
Cohesion: 0.24
Nodes (4): SelectionRequiredError, ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 36 - "test_telegram.py"
Cohesion: 0.20
Nodes (5): merge_options(), build_caption(), TelegramArtifactSink, BuildCaptionTests, TelegramArtifactSinkTests

### Community 37 - "report_user_errors"
Cohesion: 0.16
Nodes (10): annotation_options(), artifact_options(), check_found(), inspect_annotations_cmd(), inspect_artifacts_cmd(), inspect_items_cmd(), report_user_errors(), wrapper() (+2 more)

### Community 38 - "Config"
Cohesion: 0.09
Nodes (3): Config, LLMEntry, own_entries()

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.18
Nodes (14): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0002 Processing state lifecycle, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins (+6 more)

### Community 40 - "grouping.py"
Cohesion: 0.12
Nodes (17): average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsRemixer, GroupingRemixer, item_ref() (+9 more)

### Community 41 - "options"
Cohesion: 0.15
Nodes (14): options, artifacts, chat_id, interval, item_image, item_url_preview, item_url_text, markdown (+6 more)

### Community 42 - "hooks"
Cohesion: 0.15
Nodes (12): exclude, args, entry, files, id, language, name, pass_filenames (+4 more)

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "CSJuntasGobiernoProvider"
Cohesion: 0.21
Nodes (6): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, NoOptions, TestCSJuntasGobierno

### Community 45 - "config.example.yaml"
Cohesion: 0.11
Nodes (15): cache, expiration, llms, input, processors, options, processor, remixers (+7 more)

### Community 46 - "SourceItem"
Cohesion: 0.12
Nodes (4): DBSourceItem, SourceItem, FeedGeneratorRemixer, make_item()

### Community 47 - "print_table"
Cohesion: 0.15
Nodes (9): format_value(), json_default(), preview(), print_deliver(), print_import(), print_item(), print_json(), print_table() (+1 more)

### Community 48 - "db.py"
Cohesion: 0.08
Nodes (9): Base, DBItemAnnotation, ProcessingStatus, _sha256_column(), main(), migrate(), main(), migrate() (+1 more)

### Community 49 - "WebhookOptions"
Cohesion: 0.18
Nodes (4): __newsmerger_plugin__(), WebhookOptions, OptionsTests, webhook_options()

### Community 50 - "SourceItemData"
Cohesion: 0.22
Nodes (4): SourceItemData, PrensaIbericaProvider, TestPrensaIberica, TestSourceItemDataContent

### Community 51 - "cli.py"
Cohesion: 0.10
Nodes (6): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content()

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 56 - "Artifact"
Cohesion: 0.11
Nodes (6): DBArtifact, Artifact, ArtifactTests, MigrateFeedNamesTests, ArtifactSinkTests, RecordingArtifactSink

### Community 57 - "get_section"
Cohesion: 0.29
Nodes (3): get_section(), parse_datetime(), SectionNotFoundError

### Community 58 - "cli.py Click commands"
Cohesion: 0.23
Nodes (10): cli.py Click commands, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage, SQLAlchemy models never leave db.py; DTOs cross the boundary, foundation internal library, inspect items|annotations|artifacts|deliveries, Application class (single entry point), Phases: import, enrich, remix, deliver (+2 more)

### Community 59 - "OllamaLLM"
Cohesion: 0.23
Nodes (5): __newsmerger_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 62 - "digest.py"
Cohesion: 0.16
Nodes (7): Duration, DigestOptions, DigestRemixer, __newsmerger_plugin__(), GroupingOptions, UsesLLMOptions, factory()

### Community 64 - "SinkType"
Cohesion: 0.20
Nodes (3): __newsmerger_plugin__(), SinkType, PluginTests

### Community 68 - "newsmerger CLAUDE.md agent guidelines"
Cohesion: 0.33
Nodes (5): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention

### Community 73 - "workflows"
Cohesion: 0.33
Nodes (6): sink, workflows, deliver, name, process, sources

### Community 78 - "parse_entry"
Cohesion: 0.60
Nodes (3): entry_date(), find_image(), parse_entry()

### Community 79 - "foundation.plugin.Register plugin loading"
Cohesion: 0.50
Nodes (4): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `External pipelines (scripts/pipeline_url.py)`, `PluginOptions (pydantic, unknown keys rejected)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 457 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_db.py`, `BaseProcessor`, `plugins/__init__.py`, `TelegramSinkTests`, `Application`, `migrate_telegram_state.py`, `StubLLM`, `DeleteCommandTests`, `ProcessingScope`, `test_remixers.py`, `Delivery`, `Any`, `.get_stored_content`, `SourceData`, `sinks.py`, `markdownify.py`, `DeliveryStatus`, `.close`, `RecordingItemSink`, `test_telegram.py`, `Config`, `grouping.py`, `SourceItem`, `db.py`, `.get_annotation_values`, `Artifact`, `GoogleChatSinkTests`, `digest.py`, `MigrateAutoincrementTests`, `post`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 43 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `External pipelines (scripts/pipeline_url.py)`, `PluginOptions (pydantic, unknown keys rejected)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05823293172690763 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `ProcessingScope` to `test_db.py`, `BaseProcessor`, `plugins/__init__.py`, `ApplicationTests`, `Application`, `migrate_telegram_state.py`, `StubLLM`, `DeleteCommandTests`, `app_from_context`, `models.py`, `process_cmd`, `test_remixers.py`, `Delivery`, `Database`, `sinks.py`, `DeliveryStatus`, `delete_items_cmd`, `.close`, `RecordingItemSink`, `test_telegram.py`, `report_user_errors`, `grouping.py`, `SourceItem`, `db.py`, `cli.py`, `.get_annotation_values`, `Artifact`, `digest.py`, `EmbeddingGroupingTests`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Are the 38 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Should `plugins/__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10384068278805121 - nodes in this community are weakly interconnected._