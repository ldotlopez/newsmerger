# Graph Report - inspect-delete-no-processor  (2026-10-28)

## Corpus Check
- 72 files · ~122,246 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1547 nodes · 4447 edges · 83 communities (54 shown, 29 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 595 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ace3a2c9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- Database
- tagger.py
- ApplicationTests
- .__init__
- test_telegram.py
- Application
- migrate_telegram_state.py
- test_llm.py
- StubLLM
- .session_scope
- app_from_context
- plugins/__init__.py
- Artifact
- run_cmd
- test_remixers.py
- DeliveryStatus
- TelegramChannelProvider
- Catalog
- catalog.py
- 0009: Workflows and keyed entries
- Any
- SourceData
- ProcessingScope
- HTTPClient
- config.py
- MarkdownifyProcessor
- PrensaIbericaPlainProvider
- deliveries table (the ledger)
- SourceItemData
- inspect_artifacts_cmd
- .workflow
- ConfigError
- plugins
- RecordingItemSink
- Workflow
- report_user_errors
- Config
- ADR 0007 Sinks and the delivery ledger
- grouping.py
- options
- hooks
- Services object (services.llm(name))
- NoOptions
- config.example.yaml
- SourceItem
- inspect_annotations_cmd
- db.py
- GoogleChatSinkTests
- TestSourceItemDataContent
- cli.py
- LogLevelTests
- GoogleChatError
- Processor
- El Periódico Mediterráneo
- migrate_autoincrement.py
- URI
- cli.py Click commands
- ollama.py
- 0010: Plugin classes and the configuration catalog
- Item
- Services
- Entry
- .__init__
- migrate
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- newsmerger CLAUDE.md agent guidelines
- Artifact
- Grouping notes: NLP clustering pipeline
- news-aggregator
- workflows
- inspect_items_cmd
- migrate_feed_names.py
- Processor
- IndexSiteProvider
- parse_entry
- MissingAnnotationError
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

## Communities (83 total, 29 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.05
Nodes (17): Base, DBDelivery, DBItemAnnotation, DBProcessingState, DBSourceItem, AnnotationTests, ConnectionTests, ContentStorageTests (+9 more)

### Community 1 - "Database"
Cohesion: 0.11
Nodes (7): Database, EmbedProcessor, tags_text(), SummarizeProcessor, merge_tags(), TaggerProcessor, BaseProcessor

### Community 2 - "tagger.py"
Cohesion: 0.19
Nodes (10): Decision, EmbedOptions, __newsmerger_plugin__(), UsesLLMOptions, __newsmerger_plugin__(), SummarizeOptions, __newsmerger_plugin__(), TaggerOptions (+2 more)

### Community 5 - "test_telegram.py"
Cohesion: 0.09
Nodes (14): merge_options(), DocumentDeliveryOptions, ItemDeliveryOptions, TelegramArtifactSink, TelegramSink, TestFeedReader, BuildCaptionTests, item_options() (+6 more)

### Community 6 - "Application"
Cohesion: 0.06
Nodes (4): Application, workflow_scope(), ItemKey, tagged_items()

### Community 7 - "migrate_telegram_state.py"
Cohesion: 0.14
Nodes (3): LockedError, write_lock(), main()

### Community 9 - "StubLLM"
Cohesion: 0.20
Nodes (5): build(), EmbedTests, StubLLM, SummarizeTests, TaggerTests

### Community 11 - "app_from_context"
Cohesion: 0.15
Nodes (7): app_from_context(), cli(), inspect_content_cmd(), parse_artifact_ids(), process_cmd(), remix_cmd(), search_cmd()

### Community 12 - "plugins/__init__.py"
Cohesion: 0.20
Nodes (12): __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), Options, PluginTypes, __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__() (+4 more)

### Community 13 - "Artifact"
Cohesion: 0.05
Nodes (14): DBArtifact, Artifact, post(), TelegramError, RunSummary, Sink, annotation(), CommandTests (+6 more)

### Community 14 - "run_cmd"
Cohesion: 0.17
Nodes (6): import_cmd(), import_sources(), print_import(), progress_rows(), run_cmd(), run_each()

### Community 15 - "test_remixers.py"
Cohesion: 0.13
Nodes (7): __newsmerger_plugin__(), Options, __newsmerger_plugin__(), PluginOptions, Remixer, RemixerType, GroupingPluginTests

### Community 16 - "DeliveryStatus"
Cohesion: 0.06
Nodes (7): DeliveryStatus, Delivery, ArtifactNames, BaseArtifactSink, BaseItemSink, BaseSink, migrate()

### Community 17 - "TelegramChannelProvider"
Cohesion: 0.13
Nodes (9): is_home_page(), page_title(), parse_article(), parse_preview(), Post, preview_url(), TelegramChannelProvider, read_sample() (+1 more)

### Community 19 - "catalog.py"
Cohesion: 0.14
Nodes (7): ids_of(), in_default(), Kind, Use, DeliveryEntry, ProcessEntry, RemixEntry

### Community 20 - "0009: Workflows and keyed entries"
Cohesion: 0.33
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 21 - "Any"
Cohesion: 0.13
Nodes (3): CustomJSON, _encode_value(), UTCDateTime

### Community 22 - "SourceData"
Cohesion: 0.21
Nodes (3): DBSource, SourceData, Provider

### Community 24 - "ProcessingScope"
Cohesion: 0.15
Nodes (5): ProcessingScope, DigestRemixer, FeedGeneratorRemixer, BaseRemixer, DigestRemixerTests

### Community 25 - "HTTPClient"
Cohesion: 0.17
Nodes (8): HTTPClient, CSJuntasGobiernoProvider, discover_feed_url(), FeedReaderProvider, fetch_article(), fetch_feed(), BaseProvider, TestHTTPClient

### Community 26 - "config.py"
Cohesion: 0.13
Nodes (6): CacheConfig, DatabaseConfig, Duration, expand_variables(), MissingVariableError, options_error()

### Community 27 - "MarkdownifyProcessor"
Cohesion: 0.23
Nodes (5): MarkdownifyProcessor, SkipItem, ClassRegisterTests, make_pdf(), MarkdownifyPdfTests

### Community 29 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 30 - "SourceItemData"
Cohesion: 0.27
Nodes (4): SourceItemData, PrensaIbericaProvider, TheGuardianProvider, TestPrensaIberica

### Community 31 - "inspect_artifacts_cmd"
Cohesion: 0.19
Nodes (7): check_found(), delete_artifacts_cmd(), delete_deliveries_cmd(), delete_items_cmd(), inspect_artifacts_cmd(), require_selection(), sort_option()

### Community 33 - "ConfigError"
Cohesion: 0.14
Nodes (3): check_section(), share_sources(), ConfigError

### Community 34 - "plugins"
Cohesion: 0.11
Nodes (18): lookback, title, url, api_base, api_key, chat_model, embed_model, plugins (+10 more)

### Community 35 - "RecordingItemSink"
Cohesion: 0.24
Nodes (4): SelectionRequiredError, ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 37 - "report_user_errors"
Cohesion: 0.21
Nodes (8): annotation_options(), artifact_options(), delete_annotations_cmd(), delivery_options(), report_user_errors(), wrapper(), scope_options(), wrapper()

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.22
Nodes (13): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger (+5 more)

### Community 40 - "grouping.py"
Cohesion: 0.07
Nodes (23): average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer, GroupingOptions (+15 more)

### Community 41 - "options"
Cohesion: 0.17
Nodes (13): options, artifacts, chat_id, interval, item_image, item_url_preview, item_url_text, max_per_run (+5 more)

### Community 42 - "hooks"
Cohesion: 0.15
Nodes (12): exclude, args, entry, files, id, language, name, pass_filenames (+4 more)

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.18
Nodes (13): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+5 more)

### Community 44 - "NoOptions"
Cohesion: 0.18
Nodes (5): find_parent_by_tag_name(), get_date_from_text(), PreparseData, NoOptions, TestCSJuntasGobierno

### Community 45 - "config.example.yaml"
Cohesion: 0.10
Nodes (18): cache, expiration, llms, input, processors, options, processor, remixers (+10 more)

### Community 46 - "SourceItem"
Cohesion: 0.10
Nodes (4): SourceItem, GoogleChatSink, SearchTests, make_item()

### Community 47 - "inspect_annotations_cmd"
Cohesion: 0.20
Nodes (7): format_value(), inspect_annotations_cmd(), inspect_deliveries_cmd(), json_default(), preview(), print_json(), setup_logging()

### Community 48 - "db.py"
Cohesion: 0.12
Nodes (8): backoff_seconds(), _sha256_column(), __newsmerger_plugin__(), build_caption(), __newsmerger_plugin__(), ArtifactDeliveryOptions, DeliveryOptions, SinkType

### Community 49 - "GoogleChatSinkTests"
Cohesion: 0.09
Nodes (8): build_card(), chat_image_url(), WebhookOptions, card_widgets(), ChatImageUrlTests, GoogleChatSinkTests, OptionsTests, webhook_options()

### Community 51 - "cli.py"
Cohesion: 0.10
Nodes (5): delete_group(), inspect_group(), lexer_for(), match_snippet(), print_content()

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 57 - "URI"
Cohesion: 0.18
Nodes (6): CastellonInformacionProvider, get_section(), parse_datetime(), PlazaProvider, SectionNotFoundError, URI

### Community 58 - "cli.py Click commands"
Cohesion: 0.23
Nodes (10): cli.py Click commands, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage, SQLAlchemy models never leave db.py; DTOs cross the boundary, foundation internal library, inspect items|annotations|artifacts|deliveries, Application class (single entry point), Phases: import, enrich, remix, deliver (+2 more)

### Community 59 - "ollama.py"
Cohesion: 0.18
Nodes (6): LLMType, __newsmerger_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 60 - "0010: Plugin classes and the configuration catalog"
Cohesion: 0.40
Nodes (4): 0010: Plugin classes and the configuration catalog, Consequences, Context, Rejected options

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 62 - "Services"
Cohesion: 0.08
Nodes (11): LLM, LLMUnavailableError, strip_code_fence(), DigestOptions, __newsmerger_plugin__(), Services, DigestPluginTests, factory() (+3 more)

### Community 66 - "migrate"
Cohesion: 0.25
Nodes (3): main(), migrate(), MigrateAutoincrementTests

### Community 68 - "newsmerger CLAUDE.md agent guidelines"
Cohesion: 0.33
Nodes (5): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention

### Community 73 - "workflows"
Cohesion: 0.33
Nodes (6): sink, workflows, deliver, name, process, sources

### Community 74 - "inspect_items_cmd"
Cohesion: 0.20
Nodes (6): inspect_items_cmd(), print_deliver(), print_item(), print_process(), print_remix(), print_table()

### Community 80 - "parse_entry"
Cohesion: 0.60
Nodes (3): entry_date(), find_image(), parse_entry()

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `External pipelines (scripts/pipeline_url.py)`, `PluginOptions (pydantic, unknown keys rejected)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 453 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_db.py`, `tagger.py`, `.__init__`, `test_telegram.py`, `Application`, `migrate_telegram_state.py`, `test_llm.py`, `.session_scope`, `Artifact`, `test_remixers.py`, `DeliveryStatus`, `Any`, `SourceData`, `._release_contents`, `ProcessingScope`, `MarkdownifyProcessor`, `RecordingItemSink`, `grouping.py`, `SourceItem`, `db.py`, `GoogleChatSinkTests`, `Services`, `.__init__`, `migrate`, `.close`, `Processor`?**
  _High betweenness centrality (0.178) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 43 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `External pipelines (scripts/pipeline_url.py)`, `PluginOptions (pydantic, unknown keys rejected)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05468164794007491 - nodes in this community are weakly interconnected._
- **Why does `SourceItem` connect `SourceItem` to `test_db.py`, `Database`, `tagger.py`, `ApplicationTests`, `test_telegram.py`, `Application`, `migrate_telegram_state.py`, `test_llm.py`, `.session_scope`, `Artifact`, `test_remixers.py`, `DeliveryStatus`, `Any`, `SourceData`, `ProcessingScope`, `MarkdownifyProcessor`, `RecordingItemSink`, `grouping.py`, `db.py`, `GoogleChatSinkTests`, `cli.py`, `Services`, `inspect_items_cmd`, `Processor`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Should `Database` be split into smaller, more focused modules?**
  _Cohesion score 0.10752688172043011 - nodes in this community are weakly interconnected._