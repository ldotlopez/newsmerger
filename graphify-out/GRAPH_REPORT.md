# Graph Report - newstool  (2026-10-29)

## Corpus Check
- 79 files · ~128,151 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1689 nodes · 4872 edges · 87 communities (60 shown, 27 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 659 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6a6a75b1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- ConfigError
- .from_text
- telegram.py
- .from_text
- grouping.py
- TestFeedReader
- StubLLM
- .session_scope
- run_cmd
- LazySourceItemData
- ProcessingScope
- BaseItemSink
- plugins/__init__.py
- Delivery
- test_providers.py
- LockedError
- 0009: Workflows and keyed entries
- .get_annotation_values
- TelegramSinkTests
- db.py
- Any
- HTTPClient
- ollama.py
- deliveries_send_cmd
- Services
- ScoredItem
- inspect_annotations_cmd
- migrate_autoincrement.py
- ADR 0002 Processing state lifecycle
- plugins
- Context
- Config
- LazySourceItemData
- ADR 0007 Sinks and the delivery ledger
- scope_options
- options
- hooks
- Services object (services.llm(name))
- GoogleChatSink
- config.example.yaml
- Application
- cli.py
- .feed
- markdownify.py
- SourceData
- GoogleChatSinkTests
- newstool
- Processor
- El Periódico Mediterráneo
- LogLevelTests
- config.py
- deliveries table (the ledger)
- Services
- googlechat.py
- Item
- LazySourceItemData
- describe
- RecordingArtifactSink
- 0012: Delivery ids, changing their state and forced send
- TestFeedReader
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- feedreader.py
- Artifact
- Grouping notes: NLP clustering pipeline
- .__init__
- ExternalErrorTests
- foundation.plugin.Register plugin loading
- .get_artifact
- app_from_context
- get_section
- Artifact
- SourceItemData
- Database
- MigrateAutoincrementTests
- Database & ORM Conventions
- merge_options
- Base
- _sha256_column

## God Nodes (most connected - your core abstractions)
1. `Database` - 160 edges
2. `ProcessingScope` - 140 edges
3. `SourceItem` - 119 edges
4. `SourceData` - 82 edges
5. `Services` - 76 edges
6. `Application` - 64 edges
7. `PluginFailure` - 64 edges
8. `Artifact` - 62 edges
9. `SourceItemData` - 54 edges
10. `HTTPClient` - 47 edges

## Surprising Connections (you probably didn't know these)
- `Verification` --references--> `share_sources()`  [INFERRED]
  PLAN-workflow-selectors.md → newstool/catalog.py
- `Decision` --references--> `Application`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/app.py
- `Review findings (current code)` --references--> `workflow_scope()`  [INFERRED]
  PLAN-workflow-selectors.md → newstool/app.py
- `Changes` --references--> `share_sources()`  [INFERRED]
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

## Communities (87 total, 27 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.07
Nodes (13): DBProcessingState, DBSource, AnnotationTests, ConnectionTests, ContentStorageTests, DatabaseTestCase, DeleteTests, GetItemsTests (+5 more)

### Community 1 - "ConfigError"
Cohesion: 0.07
Nodes (14): Catalog, check_section(), ids_of(), in_default(), Kind, Profile, Run, share_sources() (+6 more)

### Community 5 - "telegram.py"
Cohesion: 0.13
Nodes (8): build_caption(), DocumentDeliveryOptions, ItemDeliveryOptions, post(), TelegramSink, ArtifactDeliveryOptions, DeliveryOptions, BuildCaptionTests

### Community 6 - ".from_text"
Cohesion: 0.08
Nodes (3): AliasTests, ConfigTests, EnvironmentOverrideTests

### Community 7 - "grouping.py"
Cohesion: 0.13
Nodes (11): __newstool_plugin__(), Options, AverageLinkRemixer, EmbeddingsRemixer, GroupingRemixer, __newstool_plugin__(), SingleLinkRemixer, PluginOptions (+3 more)

### Community 8 - "TestFeedReader"
Cohesion: 0.17
Nodes (11): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention, AUTOINCREMENT integer ids, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage (+3 more)

### Community 9 - "StubLLM"
Cohesion: 0.14
Nodes (7): Processor, build(), EmbedTests, ProcessorTestCase, StubLLM, SummarizeTests, TaggerTests

### Community 11 - "run_cmd"
Cohesion: 0.14
Nodes (10): import_cmd(), import_sources(), print_process(), print_remix(), process_cmd(), progress_rows(), remix_cmd(), run_cmd() (+2 more)

### Community 12 - "LazySourceItemData"
Cohesion: 0.20
Nodes (6): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, NoOptions, TestCSJuntasGobierno

### Community 13 - "ProcessingScope"
Cohesion: 0.06
Nodes (13): wrapper(), ProcessingScope, RunSummary, Remixer, annotation(), CommandTests, InspectCommandTests, invoke() (+5 more)

### Community 14 - "BaseItemSink"
Cohesion: 0.14
Nodes (5): __newstool_plugin__(), BaseItemSink, Sink, SinkType, PluginTests

### Community 15 - "plugins/__init__.py"
Cohesion: 0.13
Nodes (10): Duration, LLMUnavailableError, strip_code_fence(), DigestOptions, __newstool_plugin__(), UsesLLMOptions, __newstool_plugin__(), TaggerOptions (+2 more)

### Community 16 - "Delivery"
Cohesion: 0.06
Nodes (6): DBDelivery, DeliveryStatus, Delivery, ArtifactNames, BaseArtifactSink, BaseSink

### Community 17 - "test_providers.py"
Cohesion: 0.14
Nodes (10): Options, Options, page_title(), parse_article(), parse_preview(), Post, preview_url(), TelegramChannelProvider (+2 more)

### Community 18 - "LockedError"
Cohesion: 0.14
Nodes (5): LockedError, write_lock(), main(), migrate(), main()

### Community 20 - "0009: Workflows and keyed entries"
Cohesion: 0.33
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 21 - ".get_annotation_values"
Cohesion: 0.11
Nodes (4): backoff_seconds(), CustomJSON, _encode_value(), UTCDateTime

### Community 22 - "TelegramSinkTests"
Cohesion: 0.21
Nodes (5): item_options(), MigrateTelegramStateTests, ok_response(), TelegramSinkTests, TelegramTestCase

### Community 23 - "db.py"
Cohesion: 0.13
Nodes (4): ProcessingStatus, Annotation, ItemKey, migrate()

### Community 25 - "HTTPClient"
Cohesion: 0.18
Nodes (4): HTTPClient, fetch_article(), is_home_page(), TestHTTPClient

### Community 27 - "ollama.py"
Cohesion: 0.11
Nodes (7): LLM, LLMType, __newstool_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 28 - "deliveries_send_cmd"
Cohesion: 0.15
Nodes (9): check_found(), delete_artifacts_cmd(), delete_deliveries_cmd(), delete_items_cmd(), deliveries_send_cmd(), delivery_filters(), require_selection(), select_deliveries() (+1 more)

### Community 29 - "Services"
Cohesion: 0.10
Nodes (13): EmbedOptions, EmbedProcessor, __newstool_plugin__(), Services, __newstool_plugin__(), SummarizeOptions, SummarizeProcessor, TaggerProcessor (+5 more)

### Community 30 - "ScoredItem"
Cohesion: 0.07
Nodes (19): average_between(), average_link_cluster(), build_score_matrix(), cosine_similarity(), EmbeddingsOptions, GroupingOptions, item_ref(), jaccard() (+11 more)

### Community 31 - "inspect_annotations_cmd"
Cohesion: 0.14
Nodes (11): format_value(), inspect_artifacts_cmd(), inspect_deliveries_cmd(), inspect_items_cmd(), json_default(), preview(), print_deliver(), print_import() (+3 more)

### Community 32 - "migrate_autoincrement.py"
Cohesion: 0.17
Nodes (4): main(), migrate(), needs_autoincrement(), recreate()

### Community 34 - "plugins"
Cohesion: 0.12
Nodes (17): lookback, title, url, api_base, chat_model, embed_model, plugins, digest (+9 more)

### Community 36 - "Context"
Cohesion: 0.21
Nodes (4): cli(), deliveries_set_status_cmd(), inspect_content_cmd(), parse_artifact_ids()

### Community 37 - "Config"
Cohesion: 0.07
Nodes (8): 0011: Environment overrides, relative paths and one storage directory, Consequences, Context, Decision, Config, EnvAliasSource, resolve_config_path(), DirectoryTests

### Community 38 - "LazySourceItemData"
Cohesion: 0.19
Nodes (4): LazySourceItemData, BaseProvider, Provider, lazy()

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.21
Nodes (14): Architecture, cli.py Click commands, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger (+6 more)

### Community 40 - "scope_options"
Cohesion: 0.21
Nodes (8): annotation_options(), artifact_options(), delete_annotations_cmd(), delivery_options(), inspect_annotations_cmd(), report_user_errors(), wrapper(), scope_options()

### Community 41 - "options"
Cohesion: 0.15
Nodes (14): options, artifacts, chat_id, interval, item_image, item_url_preview, item_url_text, markdown (+6 more)

### Community 42 - "hooks"
Cohesion: 0.15
Nodes (12): exclude, args, entry, files, id, language, name, pass_filenames (+4 more)

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "GoogleChatSink"
Cohesion: 0.21
Nodes (4): GoogleChatSink, WebhookOptions, OptionsTests, webhook_options()

### Community 45 - "config.example.yaml"
Cohesion: 0.11
Nodes (15): cache, expiration, llms, input, processors, options, processor, remixers (+7 more)

### Community 46 - "Application"
Cohesion: 0.05
Nodes (9): Application, lookup(), workflow_scope(), Workflow, Changes, Context, Design, Verification (+1 more)

### Community 47 - "cli.py"
Cohesion: 0.12
Nodes (5): delete_group(), deliveries_group(), inspect_group(), lexer_for(), print_content()

### Community 50 - "markdownify.py"
Cohesion: 0.16
Nodes (7): MarkdownifyProcessor, __newstool_plugin__(), ProcessorOptions, SkipItem, ClassRegisterTests, make_pdf(), MarkdownifyPdfTests

### Community 51 - "SourceData"
Cohesion: 0.13
Nodes (9): PluginFailure, SourceData, CastellonInformacionProvider, get_section(), parse_datetime(), PlazaProvider, TheGuardianProvider, IndexSiteProvider (+1 more)

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 57 - "config.py"
Cohesion: 0.07
Nodes (11): Alias, CacheConfig, ConfigPath, expand_variables(), load_context(), LoadContext, LoadEnvSettingsSource, MissingVariableError (+3 more)

### Community 58 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 59 - "Services"
Cohesion: 0.25
Nodes (9): __newstool_plugin__(), __newstool_plugin__(), PluginTypes, __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__() (+1 more)

### Community 60 - "googlechat.py"
Cohesion: 0.19
Nodes (4): build_card(), chat_image_url(), __newstool_plugin__(), ChatImageUrlTests

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 62 - "LazySourceItemData"
Cohesion: 0.16
Nodes (6): 0010: Plugin classes and the configuration catalog, Consequences, Context, Decision, Rejected options, ClassRegister

### Community 63 - "describe"
Cohesion: 0.11
Nodes (6): import_one(), describe(), log_failure(), reason(), DescribeTests, LogFailureTests

### Community 64 - "RecordingArtifactSink"
Cohesion: 0.31
Nodes (3): SelectionRequiredError, ArtifactSinkTests, RecordingArtifactSink

### Community 65 - "0012: Delivery ids, changing their state and forced send"
Cohesion: 0.33
Nodes (5): 0012: Delivery ids, changing their state and forced send, Consequences, Context, Decision, Rejected options

### Community 68 - "feedreader.py"
Cohesion: 0.26
Nodes (8): discover_feed_url(), entry_date(), FeedReaderProvider, fetch_feed(), find_image(), __newstool_plugin__(), parse_entry(), select_article()

### Community 73 - "foundation.plugin.Register plugin loading"
Cohesion: 0.29
Nodes (7): foundation internal library, foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section, P1: plain logging and <APP>_LOG_LEVEL fix, P2: rich progress per stream (RICH_STDOUT_*/RICH_STDERR_*)

### Community 75 - "app_from_context"
Cohesion: 0.17
Nodes (7): Additional Approved Packages, Framework Usage, newstool Python Specifics, app_from_context(), match_snippet(), search_cmd(), setup_logging()

### Community 76 - "get_section"
Cohesion: 0.33
Nodes (6): sink, workflows, deliver, name, process, sources

### Community 77 - "Artifact"
Cohesion: 0.13
Nodes (3): DBArtifact, Artifact, ArtifactTests

### Community 78 - "SourceItemData"
Cohesion: 0.22
Nodes (4): SourceItemData, PrensaIbericaProvider, TestPrensaIberica, TestSourceItemDataContent

### Community 79 - "Database"
Cohesion: 0.07
Nodes (9): Database, DBSourceItem, SourceItem, DigestRemixer, tags_text(), FeedGeneratorRemixer, tagged_items(), merge_tags() (+1 more)

### Community 82 - "merge_options"
Cohesion: 0.33
Nodes (3): merge_options(), TelegramArtifactSink, TelegramArtifactSinkTests

## Knowledge Gaps
- **13 isolated node(s):** `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)`, `IndexSiteProvider / URLProvider` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 492 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_db.py`, `.delete_deliveries`, `._run_item`, `telegram.py`, `grouping.py`, `StubLLM`, `.session_scope`, `ProcessingScope`, `BaseItemSink`, `plugins/__init__.py`, `Delivery`, `LockedError`, `.get_annotation_values`, `TelegramSinkTests`, `db.py`, `._release_contents`, `Services`, `ScoredItem`, `.close`, `Config`, `GoogleChatSink`, `Application`, `markdownify.py`, `SourceData`, `GoogleChatSinkTests`, `googlechat.py`, `RecordingArtifactSink`, `.__init__`, `.get_artifact`, `Artifact`, `MigrateAutoincrementTests`, `merge_options`, `.get_annotation_keys`?**
  _High betweenness centrality (0.186) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 43 INFERRED edges - model-reasoned connections that need verification._
- **What connects `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06997408367271381 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `ProcessingScope` to `test_db.py`, `.from_text`, `._run_item`, `grouping.py`, `StubLLM`, `.session_scope`, `run_cmd`, `BaseItemSink`, `plugins/__init__.py`, `Delivery`, `TelegramSinkTests`, `db.py`, `deliveries_send_cmd`, `Services`, `ScoredItem`, `inspect_annotations_cmd`, `Context`, `scope_options`, `Application`, `cli.py`, `app_from_context`, `Artifact`, `Database`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Should `ConfigError` be split into smaller, more focused modules?**
  _Cohesion score 0.06829488919041157 - nodes in this community are weakly interconnected._