# Graph Report - newstool  (2026-10-29)

## Corpus Check
- 77 files · ~127,447 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1660 nodes · 4717 edges · 81 communities (57 shown, 24 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 643 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1f936451`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- ConfigError
- Application
- .from_text
- SourceItem
- Artifact
- .from_text
- ProcessingScope
- TestFeedReader
- StubLLM
- .session_scope
- run_cmd
- csjuntasgobierno.py
- test_cli.py
- Sink
- DeliveryStatus
- test_providers.py
- migrate_autoincrement.py
- catalog.py
- 0009: Workflows and keyed entries
- Any
- SourceItemData
- db.py
- Any
- workflow_scope
- Database
- plugins/__init__.py
- telegram_channel.py
- Services
- ScoredItem
- delete_items_cmd
- load_context
- ADR 0002 Processing state lifecycle
- plugins
- FeedReaderProvider
- HTTPClient
- .from_file
- config.py
- ADR 0007 Sinks and the delivery ledger
- ProcessorType
- options
- hooks
- Services object (services.llm(name))
- GoogleChatSinkTests
- config.example.yaml
- Workflow
- cli.py
- .feed
- markdownify.py
- SourceData
- feedreader.py
- newstool
- Processor
- El Periódico Mediterráneo
- LogLevelTests
- config.py
- deliveries table (the ledger)
- Services
- DeliveryStatus
- Item
- LazySourceItemData
- AliasTests
- 0010: Plugin classes and the configuration catalog
- 0012: Delivery ids, changing their state and forced send
- TestFeedReader
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- parse_entry
- Artifact
- Grouping notes: NLP clustering pipeline
- app_from_context
- LLMEntry
- foundation.plugin.Register plugin loading
- .__init__
- setup_logging
- get_section
- Artifact
- TestSourceItemDataContent
- FeedGeneratorRemixer
- Database & ORM Conventions

## God Nodes (most connected - your core abstractions)
1. `Database` - 160 edges
2. `ProcessingScope` - 140 edges
3. `SourceItem` - 119 edges
4. `SourceData` - 82 edges
5. `Services` - 76 edges
6. `Application` - 64 edges
7. `Artifact` - 62 edges
8. `SourceItemData` - 54 edges
9. `HTTPClient` - 47 edges
10. `ApplicationTests` - 45 edges

## Surprising Connections (you probably didn't know these)
- `Decision` --references--> `Application`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/app.py
- `Changes` --references--> `workflow_scope()`  [INFERRED]
  PLAN-workflow-selectors.md → newstool/app.py
- `Review findings (current code)` --references--> `workflow_scope()`  [INFERRED]
  PLAN-workflow-selectors.md → newstool/app.py
- `Verification` --references--> `share_sources()`  [INFERRED]
  PLAN-workflow-selectors.md → newstool/catalog.py
- `Changes` --references--> `run_each()`  [INFERRED]
  PLAN-workflow-selectors.md → newstool/cli.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (81 total, 24 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.06
Nodes (13): DBSourceItem, AnnotationTests, ArtifactTests, ConnectionTests, ContentStorageTests, DatabaseTestCase, DeleteTests, GetItemsTests (+5 more)

### Community 1 - "ConfigError"
Cohesion: 0.10
Nodes (5): Catalog, check_section(), Profile, Run, ConfigError

### Community 3 - ".from_text"
Cohesion: 0.08
Nodes (5): ollama_client(), OllamaLLM, Options, ApplicationTests, OllamaTests

### Community 4 - "SourceItem"
Cohesion: 0.06
Nodes (14): strip_code_fence(), ItemKey, SourceItem, DigestRemixer, tags_text(), tagged_items(), SummarizeProcessor, merge_tags() (+6 more)

### Community 5 - "Artifact"
Cohesion: 0.08
Nodes (14): merge_options(), build_caption(), post(), TelegramArtifactSink, TelegramError, TelegramSink, BuildCaptionTests, item_options() (+6 more)

### Community 7 - "ProcessingScope"
Cohesion: 0.12
Nodes (4): ProcessingScope, Remixer, DeliveryTests, DigestRemixerTests

### Community 8 - "TestFeedReader"
Cohesion: 0.17
Nodes (11): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention, AUTOINCREMENT integer ids, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage (+3 more)

### Community 9 - "StubLLM"
Cohesion: 0.13
Nodes (8): Processor, build(), ConsumerPluginTests, EmbedTests, ProcessorTestCase, StubLLM, SummarizeTests, TaggerTests

### Community 11 - "run_cmd"
Cohesion: 0.13
Nodes (10): import_sources(), print_deliver(), print_import(), print_process(), print_remix(), print_table(), progress_rows(), run_cmd() (+2 more)

### Community 12 - "csjuntasgobierno.py"
Cohesion: 0.25
Nodes (5): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, TestCSJuntasGobierno

### Community 13 - "test_cli.py"
Cohesion: 0.14
Nodes (5): RunSummary, annotation(), CommandTests, InspectCommandTests, invoke()

### Community 17 - "test_providers.py"
Cohesion: 0.13
Nodes (9): is_home_page(), page_title(), parse_article(), parse_preview(), Post, preview_url(), TelegramChannelProvider, read_sample() (+1 more)

### Community 18 - "migrate_autoincrement.py"
Cohesion: 0.05
Nodes (12): LockedError, write_lock(), Base, DBItemAnnotation, main(), migrate(), needs_autoincrement(), recreate() (+4 more)

### Community 19 - "catalog.py"
Cohesion: 0.09
Nodes (10): ids_of(), in_default(), Kind, Use, DeliveryEntry, Entry, options_error(), own_entries() (+2 more)

### Community 20 - "0009: Workflows and keyed entries"
Cohesion: 0.33
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 21 - "Any"
Cohesion: 0.09
Nodes (6): backoff_seconds(), _configure_sqlite_connection(), CustomJSON, DBProcessingState, _encode_value(), UTCDateTime

### Community 22 - "SourceItemData"
Cohesion: 0.31
Nodes (3): SourceItemData, PrensaIbericaProvider, TestPrensaIberica

### Community 23 - "db.py"
Cohesion: 0.09
Nodes (10): ProcessingStatus, _sha256_column(), Annotation, __newstool_plugin__(), DocumentDeliveryOptions, ItemDeliveryOptions, __newstool_plugin__(), ArtifactDeliveryOptions (+2 more)

### Community 26 - "Database"
Cohesion: 0.07
Nodes (6): Database, GoogleChatError, AverageLinkRemixer, EmbeddingsRemixer, GroupingRemixer, SingleLinkRemixer

### Community 27 - "plugins/__init__.py"
Cohesion: 0.12
Nodes (10): Duration, DigestOptions, __newstool_plugin__(), __newstool_plugin__(), Options, __newstool_plugin__(), RemixerType, DigestPluginTests (+2 more)

### Community 28 - "telegram_channel.py"
Cohesion: 0.16
Nodes (7): cli(), import_cmd(), inspect_content_cmd(), parse_artifact_ids(), process_cmd(), remix_cmd(), search_cmd()

### Community 29 - "Services"
Cohesion: 0.07
Nodes (18): Decision, LLM, LLMType, LLMUnavailableError, EmbedOptions, EmbedProcessor, __newstool_plugin__(), Services (+10 more)

### Community 30 - "ScoredItem"
Cohesion: 0.07
Nodes (19): average_between(), average_link_cluster(), build_score_matrix(), cosine_similarity(), EmbeddingsOptions, GroupingOptions, item_ref(), jaccard() (+11 more)

### Community 31 - "delete_items_cmd"
Cohesion: 0.21
Nodes (7): check_found(), inspect_artifacts_cmd(), inspect_deliveries_cmd(), inspect_items_cmd(), json_default(), preview(), print_json()

### Community 32 - "load_context"
Cohesion: 0.17
Nodes (4): load_context(), LoadContext, LoadEnvSettingsSource, resolve_config_path()

### Community 34 - "plugins"
Cohesion: 0.12
Nodes (17): lookback, title, url, api_base, chat_model, embed_model, plugins, digest (+9 more)

### Community 35 - "FeedReaderProvider"
Cohesion: 0.22
Nodes (4): SelectionRequiredError, ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 36 - "HTTPClient"
Cohesion: 0.17
Nodes (6): HTTPClient, discover_feed_url(), fetch_article(), fetch_feed(), select_article(), TestHTTPClient

### Community 37 - ".from_file"
Cohesion: 0.14
Nodes (6): 0011: Environment overrides, relative paths and one storage directory, Consequences, Context, Decision, Config, DirectoryTests

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.21
Nodes (14): Architecture, cli.py Click commands, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger (+6 more)

### Community 40 - "ProcessorType"
Cohesion: 0.19
Nodes (9): annotation_options(), artifact_options(), delete_annotations_cmd(), delivery_options(), inspect_annotations_cmd(), report_user_errors(), wrapper(), scope_options() (+1 more)

### Community 41 - "options"
Cohesion: 0.15
Nodes (14): options, artifacts, chat_id, interval, item_image, item_url_preview, item_url_text, markdown (+6 more)

### Community 42 - "hooks"
Cohesion: 0.15
Nodes (12): exclude, args, entry, files, id, language, name, pass_filenames (+4 more)

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "GoogleChatSinkTests"
Cohesion: 0.10
Nodes (9): build_card(), chat_image_url(), GoogleChatSink, WebhookOptions, card_widgets(), ChatImageUrlTests, GoogleChatSinkTests, OptionsTests (+1 more)

### Community 45 - "config.example.yaml"
Cohesion: 0.11
Nodes (15): cache, expiration, llms, input, processors, options, processor, remixers (+7 more)

### Community 46 - "Workflow"
Cohesion: 0.17
Nodes (6): share_sources(), Workflow, Changes, Design, Verification, Workflow selectors: read from the DB without importing

### Community 47 - "cli.py"
Cohesion: 0.09
Nodes (8): delete_group(), deliveries_group(), format_value(), inspect_group(), lexer_for(), match_snippet(), print_content(), print_item()

### Community 50 - "markdownify.py"
Cohesion: 0.17
Nodes (6): MarkdownifyProcessor, __newstool_plugin__(), SkipItem, ClassRegisterTests, make_pdf(), MarkdownifyPdfTests

### Community 51 - "SourceData"
Cohesion: 0.15
Nodes (6): DBSource, SourceData, CastellonInformacionProvider, TheGuardianProvider, IndexSiteProvider, URI

### Community 52 - "feedreader.py"
Cohesion: 0.19
Nodes (4): LazySourceItemData, BaseProvider, Provider, lazy()

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 57 - "config.py"
Cohesion: 0.11
Nodes (7): Alias, CacheConfig, ConfigPath, expand_variables(), MissingVariableError, ollama_url(), parse_duration()

### Community 58 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 59 - "Services"
Cohesion: 0.17
Nodes (14): __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), Options, NoOptions, PluginOptions, PluginTypes, __newstool_plugin__() (+6 more)

### Community 60 - "DeliveryStatus"
Cohesion: 0.11
Nodes (5): DBDelivery, DeliveryStatus, Delivery, BaseItemSink, migrate()

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 64 - "0010: Plugin classes and the configuration catalog"
Cohesion: 0.40
Nodes (4): 0010: Plugin classes and the configuration catalog, Consequences, Context, Rejected options

### Community 65 - "0012: Delivery ids, changing their state and forced send"
Cohesion: 0.33
Nodes (5): 0012: Delivery ids, changing their state and forced send, Consequences, Context, Decision, Rejected options

### Community 68 - "parse_entry"
Cohesion: 0.60
Nodes (3): entry_date(), find_image(), parse_entry()

### Community 71 - "app_from_context"
Cohesion: 0.16
Nodes (10): app_from_context(), delete_artifacts_cmd(), delete_deliveries_cmd(), delete_items_cmd(), deliveries_send_cmd(), deliveries_set_status_cmd(), delivery_filters(), require_selection() (+2 more)

### Community 73 - "foundation.plugin.Register plugin loading"
Cohesion: 0.29
Nodes (7): foundation internal library, foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section, P1: plain logging and <APP>_LOG_LEVEL fix, P2: rich progress per stream (RICH_STDOUT_*/RICH_STDERR_*)

### Community 74 - ".__init__"
Cohesion: 0.25
Nodes (4): get_section(), parse_datetime(), PlazaProvider, SectionNotFoundError

### Community 75 - "setup_logging"
Cohesion: 0.33
Nodes (4): Additional Approved Packages, Framework Usage, newstool Python Specifics, setup_logging()

### Community 76 - "get_section"
Cohesion: 0.33
Nodes (6): sink, workflows, deliver, name, process, sources

### Community 77 - "Artifact"
Cohesion: 0.09
Nodes (6): DBArtifact, Artifact, BaseArtifactSink, MigrateFeedNamesTests, ArtifactSinkTests, RecordingArtifactSink

## Knowledge Gaps
- **13 isolated node(s):** `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)`, `IndexSiteProvider / URLProvider` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 488 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_db.py`, `Application`, `SourceItem`, `Artifact`, `ProcessingScope`, `StubLLM`, `.session_scope`, `Sink`, `.get_content`, `DeliveryStatus`, `migrate_autoincrement.py`, `Any`, `db.py`, `plugins/__init__.py`, `Services`, `ScoredItem`, `FeedReaderProvider`, `GoogleChatSinkTests`, `markdownify.py`, `SourceData`, `DeliveryStatus`, `LazySourceItemData`, `Artifact`, `FeedGeneratorRemixer`?**
  _High betweenness centrality (0.149) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 43 INFERRED edges - model-reasoned connections that need verification._
- **What connects `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06350877192982456 - nodes in this community are weakly interconnected._
- **Why does `SourceItem` connect `SourceItem` to `test_db.py`, `Application`, `.from_text`, `Artifact`, `ProcessingScope`, `StubLLM`, `.session_scope`, `test_cli.py`, `.get_content`, `DeliveryStatus`, `db.py`, `workflow_scope`, `Database`, `plugins/__init__.py`, `Services`, `ScoredItem`, `FeedReaderProvider`, `GoogleChatSinkTests`, `cli.py`, `markdownify.py`, `SourceData`, `DeliveryStatus`, `FeedGeneratorRemixer`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Should `ConfigError` be split into smaller, more focused modules?**
  _Cohesion score 0.10158730158730159 - nodes in this community are weakly interconnected._