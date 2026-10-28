# Graph Report - googlechat-blogger-image-proxy  (2026-10-28)

## Corpus Check
- 72 files · ~122,137 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1546 nodes · 4450 edges · 77 communities (54 shown, 23 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 591 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `24d63244`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- make_item
- merge_options
- ProcessorType
- .from_text
- ApplicationTests
- TelegramSinkTests
- Application
- LockedError
- TestFeedReader
- StubLLM
- DeleteCommandTests
- app_from_context
- models.py
- Artifact
- process_cmd
- digest.py
- BaseSink
- test_providers.py
- ConfigError
- GoogleChatSinkTests
- 0009: Workflows and keyed entries
- Any
- SourceItem
- DigestRemixerTests
- SourceData
- test_db.py
- MarkdownifyProcessor
- newsmerger README
- migrate_autoincrement.py
- delete_items_cmd
- .feed
- catalog.py
- plugins
- RecordingItemSink
- Config
- report_user_errors
- Config
- ADR 0007 Sinks and the delivery ledger
- ScoredItem
- options
- hooks
- Services object (services.llm(name))
- EmbedProcessor
- config.example.yaml
- .record_result
- json
- db.py
- GoogleChatSinkTests
- TestSourceItemDataContent
- cli.py
- LogLevelTests
- .get_annotation_values
- Processor
- El Periódico Mediterráneo
- get_section
- parse_entry
- cli.py Click commands
- OllamaLLM
- .process_item
- Item
- DigestRemixer
- Entry
- Sink
- .__init__
- MigrateAutoincrementTests
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- newsmerger CLAUDE.md agent guidelines
- Artifact
- Grouping notes: NLP clustering pipeline
- news-aggregator
- workflows
- Remixer
- TelegramError
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
- `Decision` --references--> `UsesLLMOptions`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/plugins/__init__.py
- `Decision` --references--> `Services`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/plugins/__init__.py
- `Decision` --references--> `ProcessorType`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/processors.py
- `Decision` --references--> `ProviderType`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/providers.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (77 total, 23 thin omitted)

### Community 0 - "make_item"
Cohesion: 0.06
Nodes (16): Base, DBItemAnnotation, DBProcessingState, DBSource, AnnotationTests, ArtifactTests, ConnectionTests, ContentStorageTests (+8 more)

### Community 1 - "merge_options"
Cohesion: 0.10
Nodes (5): SummarizeProcessor, merge_tags(), TaggerProcessor, BaseProcessor, MissingAnnotationError

### Community 2 - "ProcessorType"
Cohesion: 0.20
Nodes (8): __newsmerger_plugin__(), UsesLLMOptions, __newsmerger_plugin__(), SummarizeOptions, __newsmerger_plugin__(), TaggerOptions, ProcessorOptions, ProcessorType

### Community 4 - "ApplicationTests"
Cohesion: 0.10
Nodes (5): Decision, LLM, LLMType, ClassRegister, __newsmerger_plugin__()

### Community 5 - "TelegramSinkTests"
Cohesion: 0.10
Nodes (5): TelegramSink, item_options(), ok_response(), TelegramSinkTests, TelegramTestCase

### Community 6 - "Application"
Cohesion: 0.06
Nodes (4): Application, lookup(), workflow_scope(), Workflow

### Community 7 - "LockedError"
Cohesion: 0.08
Nodes (9): LockedError, write_lock(), main(), migrate(), needs_autoincrement(), recreate(), main(), migrate() (+1 more)

### Community 9 - "StubLLM"
Cohesion: 0.12
Nodes (8): Processor, build(), ConsumerPluginTests, EmbedTests, ProcessorTestCase, StubLLM, SummarizeTests, TaggerTests

### Community 11 - "app_from_context"
Cohesion: 0.15
Nodes (8): app_from_context(), cli(), deliver_cmd(), inspect_content_cmd(), inspect_deliveries_cmd(), parse_artifact_ids(), resolve_cmd(), search_cmd()

### Community 12 - "models.py"
Cohesion: 0.13
Nodes (16): __newsmerger_plugin__(), find_parent_by_tag_name(), get_date_from_text(), __newsmerger_plugin__(), entry_date(), find_image(), __newsmerger_plugin__(), parse_entry() (+8 more)

### Community 13 - "Artifact"
Cohesion: 0.14
Nodes (5): RunSummary, annotation(), CommandTests, InspectCommandTests, invoke()

### Community 14 - "process_cmd"
Cohesion: 0.14
Nodes (9): import_cmd(), import_sources(), print_process(), print_remix(), process_cmd(), progress_rows(), remix_cmd(), run_cmd() (+1 more)

### Community 15 - "digest.py"
Cohesion: 0.16
Nodes (7): strip_code_fence(), __newsmerger_plugin__(), __newsmerger_plugin__(), Options, __newsmerger_plugin__(), RemixerType, GroupingPluginTests

### Community 16 - "BaseSink"
Cohesion: 0.10
Nodes (4): backoff_seconds(), Database, ArtifactNames, BaseSink

### Community 17 - "test_providers.py"
Cohesion: 0.09
Nodes (14): Options, NoOptions, PluginOptions, Services, Options, page_title(), parse_article(), parse_preview() (+6 more)

### Community 18 - "ConfigError"
Cohesion: 0.12
Nodes (4): Catalog, Profile, Run, ConfigError

### Community 19 - "GoogleChatSinkTests"
Cohesion: 0.15
Nodes (6): in_default(), Kind, Use, DeliveryEntry, ProcessEntry, RemixEntry

### Community 20 - "0009: Workflows and keyed entries"
Cohesion: 0.33
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 21 - "Any"
Cohesion: 0.19
Nodes (3): CustomJSON, _encode_value(), UTCDateTime

### Community 25 - "SourceData"
Cohesion: 0.08
Nodes (22): HTTPClient, SourceData, SourceItemData, CastellonInformacionProvider, CSJuntasGobiernoProvider, PreparseData, discover_feed_url(), FeedReaderProvider (+14 more)

### Community 26 - "test_db.py"
Cohesion: 0.12
Nodes (11): __newsmerger_plugin__(), merge_options(), DocumentDeliveryOptions, ItemDeliveryOptions, __newsmerger_plugin__(), TelegramArtifactSink, ArtifactDeliveryOptions, DeliveryOptions (+3 more)

### Community 27 - "MarkdownifyProcessor"
Cohesion: 0.17
Nodes (6): MarkdownifyProcessor, __newsmerger_plugin__(), SkipItem, ClassRegisterTests, make_pdf(), MarkdownifyPdfTests

### Community 29 - "newsmerger README"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 30 - "migrate_autoincrement.py"
Cohesion: 0.08
Nodes (10): DBDelivery, DeliveryStatus, Delivery, ProcessingScope, BaseArtifactSink, BaseItemSink, migrate(), SearchTests (+2 more)

### Community 31 - "delete_items_cmd"
Cohesion: 0.21
Nodes (5): delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), require_selection(), sort_option()

### Community 32 - ".feed"
Cohesion: 0.17
Nodes (5): GroupingOptions, EmbeddingGroupingTests, FeedGeneratorTests, GroupingTests, RemixerTestCase

### Community 33 - "catalog.py"
Cohesion: 0.15
Nodes (4): check_section(), ids_of(), share_sources(), options_error()

### Community 34 - "plugins"
Cohesion: 0.11
Nodes (18): days, title, url, api_base, api_key, chat_model, embed_model, plugins (+10 more)

### Community 35 - "RecordingItemSink"
Cohesion: 0.22
Nodes (4): SelectionRequiredError, ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 37 - "report_user_errors"
Cohesion: 0.16
Nodes (10): annotation_options(), artifact_options(), check_found(), inspect_annotations_cmd(), inspect_artifacts_cmd(), inspect_items_cmd(), report_user_errors(), wrapper() (+2 more)

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.22
Nodes (13): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger (+5 more)

### Community 40 - "ScoredItem"
Cohesion: 0.10
Nodes (19): average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer, GroupingRemixer (+11 more)

### Community 41 - "options"
Cohesion: 0.17
Nodes (13): options, artifacts, chat_id, interval, item_image, item_url_preview, item_url_text, max_per_run (+5 more)

### Community 42 - "hooks"
Cohesion: 0.15
Nodes (12): exclude, args, entry, files, id, language, name, pass_filenames (+4 more)

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.18
Nodes (13): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+5 more)

### Community 44 - "EmbedProcessor"
Cohesion: 0.28
Nodes (3): EmbedOptions, EmbedProcessor, tags_text()

### Community 45 - "config.example.yaml"
Cohesion: 0.10
Nodes (18): cache, expiration, llms, input, processors, options, processor, remixers (+10 more)

### Community 47 - "json"
Cohesion: 0.15
Nodes (9): format_value(), json_default(), preview(), print_deliver(), print_import(), print_item(), print_json(), print_table() (+1 more)

### Community 48 - "db.py"
Cohesion: 0.10
Nodes (6): CacheConfig, DatabaseConfig, ProcessingStatus, _sha256_column(), LLMUnavailableError, Annotation

### Community 49 - "GoogleChatSinkTests"
Cohesion: 0.08
Nodes (11): build_card(), chat_image_url(), GoogleChatSink, WebhookOptions, build_caption(), card_widgets(), ChatImageUrlTests, GoogleChatSinkTests (+3 more)

### Community 51 - "cli.py"
Cohesion: 0.10
Nodes (6): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content()

### Community 53 - ".get_annotation_values"
Cohesion: 0.15
Nodes (3): ItemKey, GoogleChatError, post()

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 56 - "get_section"
Cohesion: 0.10
Nodes (6): DBArtifact, Artifact, BaseRemixer, MigrateFeedNamesTests, ArtifactSinkTests, RecordingArtifactSink

### Community 57 - "parse_entry"
Cohesion: 0.29
Nodes (3): get_section(), parse_datetime(), SectionNotFoundError

### Community 58 - "cli.py Click commands"
Cohesion: 0.23
Nodes (10): cli.py Click commands, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage, SQLAlchemy models never leave db.py; DTOs cross the boundary, foundation internal library, inspect items|annotations|artifacts|deliveries, Application class (single entry point), Phases: import, enrich, remix, deliver (+2 more)

### Community 59 - "OllamaLLM"
Cohesion: 0.26
Nodes (4): ollama_client(), OllamaLLM, Options, OllamaTests

### Community 60 - ".process_item"
Cohesion: 0.40
Nodes (4): 0010: Plugin classes and the configuration catalog, Consequences, Context, Rejected options

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 62 - "DigestRemixer"
Cohesion: 0.17
Nodes (5): DigestOptions, DigestRemixer, DigestPluginTests, factory(), factory()

### Community 63 - "Entry"
Cohesion: 0.17
Nodes (3): Entry, LLMEntry, own_entries()

### Community 68 - "newsmerger CLAUDE.md agent guidelines"
Cohesion: 0.33
Nodes (5): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention

### Community 73 - "workflows"
Cohesion: 0.33
Nodes (6): sink, workflows, deliver, name, process, sources

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)`, `pre-commit config` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 454 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `BaseSink` to `make_item`, `merge_options`, `ProcessorType`, `TelegramSinkTests`, `Application`, `LockedError`, `StubLLM`, `DeleteCommandTests`, `digest.py`, `Any`, `SourceItem`, `.session_scope`, `DigestRemixerTests`, `SourceData`, `test_db.py`, `MarkdownifyProcessor`, `migrate_autoincrement.py`, `.feed`, `RecordingItemSink`, `Config`, `ScoredItem`, `EmbedProcessor`, `.record_result`, `db.py`, `GoogleChatSinkTests`, `.get_annotation_values`, `get_section`, `DigestRemixer`, `Sink`, `.__init__`, `MigrateAutoincrementTests`, `Remixer`?**
  _High betweenness centrality (0.176) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 43 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `External pipelines (scripts/pipeline_url.py)`, `Annotation` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `make_item` be split into smaller, more focused modules?**
  _Cohesion score 0.05737234652897304 - nodes in this community are weakly interconnected._
- **Why does `SourceItem` connect `SourceItem` to `make_item`, `merge_options`, `ProcessorType`, `.from_text`, `TelegramSinkTests`, `Application`, `StubLLM`, `DeleteCommandTests`, `Artifact`, `digest.py`, `BaseSink`, `.session_scope`, `DigestRemixerTests`, `test_db.py`, `MarkdownifyProcessor`, `migrate_autoincrement.py`, `.feed`, `RecordingItemSink`, `ScoredItem`, `EmbedProcessor`, `.record_result`, `json`, `db.py`, `GoogleChatSinkTests`, `cli.py`, `.get_annotation_values`, `DigestRemixer`, `MigrateAutoincrementTests`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Are the 38 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Should `merge_options` be split into smaller, more focused modules?**
  _Cohesion score 0.10052910052910052 - nodes in this community are weakly interconnected._