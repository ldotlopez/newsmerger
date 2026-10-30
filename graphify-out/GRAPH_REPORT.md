# Graph Report - two-stage-import  (2026-10-30)

## Corpus Check
- 76 files · ~128,311 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 4, .lock 1)

## Summary
- 1731 nodes · 4888 edges · 82 communities (58 shown, 24 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 628 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4a0dd197`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- catalog.py
- app.py
- ApplicationTests
- Database
- .feed
- .from_text
- grouping.py
- Database (db.py, only SQLite/storage access)
- StubLLM
- DeleteCommandTests
- process_cmd
- CSJuntasGobiernoProvider
- RunSummary
- SourceData
- processors.py
- BaseSink
- TelegramChannelProvider
- migrate_feed_names.py
- inspect_annotations_cmd
- ProcessingScope
- datetime
- Artifact
- db.py
- Any
- HTTPClient
- Database
- plugins/__init__.py
- app_from_context
- DigestRemixer
- ScoredItem
- cli.py
- migrate
- ADR 0002 Processing state lifecycle
- plugins
- RecordingItemSink
- Config
- GoogleChatSinkTests
- ADR 0007 Sinks and the delivery ledger
- report_user_errors
- options
- hooks
- Services object (services.llm(name))
- WebhookOptions
- config.example.yaml
- Application
- feedreader.py
- PrensaIbericaPlainProvider
- MarkdownifyProcessor
- PluginFailure
- migrate_telegram_state.py
- newstool
- Processor
- El Periódico Mediterráneo
- 0009: Workflows and keyed entries
- config.py
- deliveries table (the ledger)
- app.py
- telegram.py
- Item
- ClassRegister
- describe
- merge_options
- TestFeedReader
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- 0010: Plugin classes and the configuration catalog
- Artifact
- Grouping notes: NLP clustering pipeline
- .__init__
- foundation internal library
- Framework Usage
- workflows
- SourceItemData
- SourceItem
- MigrateAutoincrementTests
- Base

## God Nodes (most connected - your core abstractions)
1. `Database` - 160 edges
2. `ProcessingScope` - 140 edges
3. `SourceItem` - 120 edges
4. `SourceData` - 83 edges
5. `Services` - 76 edges
6. `PluginFailure` - 67 edges
7. `Application` - 64 edges
8. `Artifact` - 62 edges
9. `SourceItemData` - 58 edges
10. `ApplicationTests` - 55 edges

## Surprising Connections (you probably didn't know these)
- `Decision` --references--> `Application`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/app.py
- `Decision` --references--> `Config`  [INFERRED]
  docs/decisions/0011-environment-overrides-and-storage-dir.md → newstool/config.py
- `Decision` --references--> `LLMType`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/llms.py
- `Framework Usage` --references--> `PluginOptions`  [INFERRED]
  .claude/rules/python.md → newstool/plugins/__init__.py
- `Decision` --references--> `ClassRegister`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/plugins/__init__.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (82 total, 24 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.06
Nodes (17): 0012: Delivery ids, changing their state and forced send, Consequences, Context, Decision, Rejected options, DBSourceItem, AnnotationTests, ConnectionTests (+9 more)

### Community 1 - "catalog.py"
Cohesion: 0.07
Nodes (14): Catalog, check_section(), ids_of(), in_default(), Kind, Profile, Run, share_sources() (+6 more)

### Community 3 - "ApplicationTests"
Cohesion: 0.08
Nodes (6): ApplicationTests, retrieve(), retrieve(), same(), listed(), retrieved()

### Community 4 - "Database"
Cohesion: 0.11
Nodes (4): tags_text(), SummarizeProcessor, merge_tags(), BaseProcessor

### Community 5 - ".feed"
Cohesion: 0.15
Nodes (5): FeedGeneratorRemixer, EmbeddingGroupingTests, FeedGeneratorTests, GroupingTests, RemixerTestCase

### Community 6 - ".from_text"
Cohesion: 0.09
Nodes (3): AliasTests, ConfigTests, EnvironmentOverrideTests

### Community 7 - "grouping.py"
Cohesion: 0.10
Nodes (11): __newstool_plugin__(), Options, cosine_similarity(), EmbeddingsOptions, GroupingOptions, __newstool_plugin__(), time_decay(), PluginOptions (+3 more)

### Community 8 - "Database (db.py, only SQLite/storage access)"
Cohesion: 0.17
Nodes (11): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention, AUTOINCREMENT integer ids, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage (+3 more)

### Community 9 - "StubLLM"
Cohesion: 0.08
Nodes (10): DBDelivery, Processor, DeliveryTests, build(), ConsumerPluginTests, EmbedTests, ProcessorTestCase, StubLLM (+2 more)

### Community 11 - "process_cmd"
Cohesion: 0.17
Nodes (7): print_process(), print_remix(), process_cmd(), progress_rows(), remix_cmd(), run_cmd(), run_each()

### Community 12 - "CSJuntasGobiernoProvider"
Cohesion: 0.19
Nodes (7): PreflightSourceItemData, CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, NoOptions, TestCSJuntasGobierno

### Community 13 - "RunSummary"
Cohesion: 0.08
Nodes (7): RunSummary, annotation(), CommandTests, ExternalErrorTests, InspectCommandTests, invoke(), LogLevelTests

### Community 14 - "SourceData"
Cohesion: 0.09
Nodes (6): DBSource, SourceData, CastellonInformacionProvider, BaseProvider, PreflightProvider, Provider

### Community 15 - "processors.py"
Cohesion: 0.09
Nodes (16): Decision, LLMUnavailableError, EmbedOptions, EmbedProcessor, __newstool_plugin__(), Services, UsesLLMOptions, __newstool_plugin__() (+8 more)

### Community 17 - "TelegramChannelProvider"
Cohesion: 0.15
Nodes (9): Options, Options, parse_article(), parse_preview(), Post, preview_url(), TelegramChannelProvider, read_sample() (+1 more)

### Community 19 - "inspect_annotations_cmd"
Cohesion: 0.14
Nodes (12): check_found(), format_value(), inspect_annotations_cmd(), inspect_artifacts_cmd(), inspect_items_cmd(), json_default(), preview(), print_deliver() (+4 more)

### Community 20 - "ProcessingScope"
Cohesion: 0.12
Nodes (6): ProcessingScope, Remixer, BaseArtifactSink, BaseItemSink, Sink, DigestRemixerTests

### Community 21 - "datetime"
Cohesion: 0.09
Nodes (4): backoff_seconds(), CustomJSON, DBProcessingState, UTCDateTime

### Community 22 - "Artifact"
Cohesion: 0.06
Nodes (17): DBArtifact, Artifact, __newstool_plugin__(), post(), TelegramArtifactSink, TelegramSink, ArtifactTests, MigrateFeedNamesTests (+9 more)

### Community 23 - "db.py"
Cohesion: 0.16
Nodes (4): DeliveryStatus, ProcessingStatus, _sha256_column(), Annotation

### Community 25 - "HTTPClient"
Cohesion: 0.11
Nodes (5): HTTPClient, fetch_article(), is_home_page(), IndexSiteProvider, TestHTTPClient

### Community 27 - "plugins/__init__.py"
Cohesion: 0.11
Nodes (7): LLM, LLMType, __newstool_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 28 - "app_from_context"
Cohesion: 0.13
Nodes (14): app_from_context(), delete_annotations_cmd(), delete_deliveries_cmd(), delete_items_cmd(), deliveries_send_cmd(), deliveries_set_status_cmd(), delivery_filters(), import_cmd() (+6 more)

### Community 29 - "DigestRemixer"
Cohesion: 0.19
Nodes (5): DigestOptions, DigestRemixer, __newstool_plugin__(), DigestPluginTests, factory()

### Community 30 - "ScoredItem"
Cohesion: 0.10
Nodes (16): average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), EmbeddingsRemixer, GroupingRemixer, item_ref(), jaccard() (+8 more)

### Community 31 - "cli.py"
Cohesion: 0.08
Nodes (8): cli(), delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content(), search_cmd()

### Community 32 - "migrate"
Cohesion: 0.17
Nodes (4): main(), migrate(), needs_autoincrement(), recreate()

### Community 34 - "plugins"
Cohesion: 0.12
Nodes (17): lookback, title, url, api_base, chat_model, embed_model, plugins, digest (+9 more)

### Community 36 - "RecordingItemSink"
Cohesion: 0.22
Nodes (4): SelectionRequiredError, ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 37 - "Config"
Cohesion: 0.09
Nodes (8): Database & ORM Conventions, DTO, Protocol & ORM Implementation Reference, 0011: Environment overrides, relative paths and one storage directory, Consequences, Context, Decision, Config, DirectoryTests

### Community 38 - "GoogleChatSinkTests"
Cohesion: 0.24
Nodes (3): migrate(), card_widgets(), GoogleChatSinkTests

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.21
Nodes (14): Architecture, cli.py Click commands, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger (+6 more)

### Community 40 - "report_user_errors"
Cohesion: 0.20
Nodes (8): annotation_options(), artifact_options(), delete_artifacts_cmd(), delivery_options(), report_user_errors(), wrapper(), scope_options(), wrapper()

### Community 41 - "options"
Cohesion: 0.15
Nodes (14): options, artifacts, chat_id, interval, item_image, item_url_preview, item_url_text, markdown (+6 more)

### Community 42 - "hooks"
Cohesion: 0.15
Nodes (12): exclude, args, entry, files, id, language, name, pass_filenames (+4 more)

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "WebhookOptions"
Cohesion: 0.18
Nodes (4): __newstool_plugin__(), WebhookOptions, OptionsTests, webhook_options()

### Community 45 - "config.example.yaml"
Cohesion: 0.11
Nodes (15): cache, expiration, llms, input, processors, options, processor, remixers (+7 more)

### Community 46 - "Application"
Cohesion: 0.05
Nodes (4): Application, lookup(), workflow_scope(), Workflow

### Community 47 - "feedreader.py"
Cohesion: 0.27
Nodes (7): discover_feed_url(), entry_date(), fetch_feed(), find_image(), __newstool_plugin__(), parse_entry(), select_article()

### Community 50 - "MarkdownifyProcessor"
Cohesion: 0.19
Nodes (5): MarkdownifyProcessor, __newstool_plugin__(), SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 51 - "PluginFailure"
Cohesion: 0.18
Nodes (6): PluginFailure, get_section(), parse_datetime(), PlazaProvider, page_title(), TheGuardianProvider

### Community 52 - "migrate_telegram_state.py"
Cohesion: 0.17
Nodes (3): LockedError, write_lock(), main()

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 56 - "0009: Workflows and keyed entries"
Cohesion: 0.25
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 57 - "config.py"
Cohesion: 0.06
Nodes (12): Alias, CacheConfig, EnvAliasSource, expand_variables(), load_context(), LoadContext, LoadEnvSettingsSource, MissingVariableError (+4 more)

### Community 58 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 59 - "app.py"
Cohesion: 0.15
Nodes (8): __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), ProviderType

### Community 60 - "telegram.py"
Cohesion: 0.10
Nodes (10): build_card(), chat_image_url(), build_caption(), DocumentDeliveryOptions, ItemDeliveryOptions, ArtifactDeliveryOptions, DeliveryOptions, SinkType (+2 more)

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 63 - "describe"
Cohesion: 0.11
Nodes (7): import_sources(), import_one(), describe(), log_failure(), reason(), DescribeTests, LogFailureTests

### Community 68 - "0010: Plugin classes and the configuration catalog"
Cohesion: 0.40
Nodes (4): 0010: Plugin classes and the configuration catalog, Consequences, Context, Rejected options

### Community 73 - "foundation internal library"
Cohesion: 0.29
Nodes (7): foundation internal library, foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section, P1: plain logging and <APP>_LOG_LEVEL fix, P2: rich progress per stream (RICH_STDOUT_*/RICH_STDERR_*)

### Community 75 - "Framework Usage"
Cohesion: 0.33
Nodes (4): Additional Approved Packages, Framework Usage, newstool Python Specifics, setup_logging()

### Community 76 - "workflows"
Cohesion: 0.33
Nodes (6): sink, workflows, deliver, name, process, sources

### Community 78 - "SourceItemData"
Cohesion: 0.22
Nodes (4): SourceItemData, PrensaIbericaProvider, TestPrensaIberica, TestSourceItemDataContent

### Community 79 - "SourceItem"
Cohesion: 0.13
Nodes (3): SourceItem, GoogleChatSink, SearchTests

## Knowledge Gaps
- **13 isolated node(s):** `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)`, `IndexSiteProvider / URLProvider` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 518 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_db.py`, `app.py`, `Database`, `.feed`, `grouping.py`, `StubLLM`, `DeleteCommandTests`, `SourceData`, `processors.py`, `BaseSink`, `ProcessingScope`, `datetime`, `Artifact`, `db.py`, `DigestRemixer`, `ScoredItem`, `.close`, `RecordingItemSink`, `Config`, `GoogleChatSinkTests`, `Application`, `MarkdownifyProcessor`, `migrate_telegram_state.py`, `telegram.py`, `.__init__`, `SourceItem`, `MigrateAutoincrementTests`?**
  _High betweenness centrality (0.154) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06460206460206461 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `ProcessingScope` to `test_db.py`, `app.py`, `ApplicationTests`, `Database`, `.feed`, `grouping.py`, `StubLLM`, `DeleteCommandTests`, `process_cmd`, `RunSummary`, `BaseSink`, `inspect_annotations_cmd`, `Artifact`, `db.py`, `Database`, `app_from_context`, `DigestRemixer`, `ScoredItem`, `cli.py`, `RecordingItemSink`, `GoogleChatSinkTests`, `report_user_errors`, `Application`, `SourceItem`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Should `catalog.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06829488919041157 - nodes in this community are weakly interconnected._