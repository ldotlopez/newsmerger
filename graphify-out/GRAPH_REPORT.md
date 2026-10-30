# Graph Report - prensaiberica-preflight  (2026-10-30)

## Corpus Check
- 75 files · ~146,322 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 4, .lock 1)

## Summary
- 1729 nodes · 4884 edges · 84 communities (60 shown, 24 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 630 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a18cf1e0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- catalog.py
- db.py
- ApplicationTests
- BaseProcessor
- Artifact
- .from_text
- feedgenerator.py
- Database (db.py, only SQLite/storage access)
- StubLLM
- DeleteCommandTests
- run_cmd
- SourceItemData
- invoke
- Context
- test_telegram.py
- Delivery
- test_providers.py
- Services
- inspect_deliveries_cmd
- BaseItemSink
- Any
- TelegramSinkTests
- test_app.py
- Any
- HTTPClient
- plugins/__init__.py
- report_user_errors
- ProcessingScope
- grouping.py
- cli.py
- migrate_autoincrement.py
- ADR 0002 Processing state lifecycle
- plugins
- .close
- RecordingItemSink
- Config
- GoogleChatSinkTests
- ADR 0007 Sinks and the delivery ledger
- CSJuntasGobiernoProvider
- options
- hooks
- Services object (services.llm(name))
- WebhookOptions
- config.example.yaml
- Application
- .record_result
- PreflightProvider
- MarkdownifyProcessor
- config.py
- Delivery
- newstool
- Processor
- El Periódico Mediterráneo
- 0009: Workflows and keyed entries
- .settings_customise_sources
- deliveries table (the ledger)
- PluginFailure
- .feed
- Item
- PluginOptions
- PluginFailure
- RunSummary
- PreflightSourceItemData
- TestFeedReader
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- .save_artifact
- Artifact
- Grouping notes: NLP clustering pipeline
- .__init__
- ExternalErrorTests
- foundation internal library
- setup_logging
- workflows
- DigestRemixerTests
- deliveries_send_cmd
- SourceItem
- LogLevelTests
- 0010: Plugin classes and the configuration catalog
- SourceData

## God Nodes (most connected - your core abstractions)
1. `Database` - 160 edges
2. `ProcessingScope` - 140 edges
3. `SourceItem` - 120 edges
4. `SourceData` - 80 edges
5. `Services` - 77 edges
6. `Application` - 64 edges
7. `PluginFailure` - 64 edges
8. `Artifact` - 62 edges
9. `SourceItemData` - 56 edges
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
- `Decision` --references--> `Services`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/plugins/__init__.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (84 total, 24 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.06
Nodes (19): 0012: Delivery ids, changing their state and forced send, Consequences, Context, Decision, Rejected options, DBProcessingState, DBSourceItem, AnnotationTests (+11 more)

### Community 1 - "catalog.py"
Cohesion: 0.07
Nodes (14): Catalog, check_section(), ids_of(), in_default(), Kind, Profile, Run, share_sources() (+6 more)

### Community 2 - "db.py"
Cohesion: 0.11
Nodes (4): backoff_seconds(), _sha256_column(), Annotation, BaseRemixer

### Community 3 - "ApplicationTests"
Cohesion: 0.08
Nodes (7): Options, ApplicationTests, retrieve(), retrieve(), same(), listed(), retrieved()

### Community 4 - "BaseProcessor"
Cohesion: 0.13
Nodes (6): Database, tags_text(), SummarizeProcessor, merge_tags(), TaggerProcessor, BaseProcessor

### Community 5 - "Artifact"
Cohesion: 0.14
Nodes (8): DBArtifact, DeliveryStatus, Artifact, BaseArtifactSink, SelectionRequiredError, ArtifactSinkTests, RecordingArtifactSink, MigrateTelegramStateTests

### Community 6 - ".from_text"
Cohesion: 0.09
Nodes (3): AliasTests, ConfigTests, EnvironmentOverrideTests

### Community 7 - "feedgenerator.py"
Cohesion: 0.21
Nodes (4): __newstool_plugin__(), __newstool_plugin__(), RemixerType, GroupingPluginTests

### Community 8 - "Database (db.py, only SQLite/storage access)"
Cohesion: 0.17
Nodes (11): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention, AUTOINCREMENT integer ids, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage (+3 more)

### Community 9 - "StubLLM"
Cohesion: 0.16
Nodes (7): Processor, build(), EmbedTests, ProcessorTestCase, StubLLM, SummarizeTests, TaggerTests

### Community 11 - "run_cmd"
Cohesion: 0.13
Nodes (8): import_sources(), import_one(), print_process(), print_remix(), progress_rows(), run_cmd(), run_each(), log_failure()

### Community 12 - "SourceItemData"
Cohesion: 0.21
Nodes (3): SourceItemData, TestPrensaIberica, TestSourceItemDataContent

### Community 13 - "invoke"
Cohesion: 0.22
Nodes (3): annotation(), InspectCommandTests, invoke()

### Community 14 - "Context"
Cohesion: 0.17
Nodes (8): app_from_context(), deliveries_set_status_cmd(), import_cmd(), inspect_content_cmd(), parse_artifact_ids(), process_cmd(), remix_cmd(), search_cmd()

### Community 15 - "test_telegram.py"
Cohesion: 0.09
Nodes (15): build_card(), chat_image_url(), merge_options(), build_caption(), DocumentDeliveryOptions, ItemDeliveryOptions, __newstool_plugin__(), TelegramArtifactSink (+7 more)

### Community 17 - "test_providers.py"
Cohesion: 0.15
Nodes (9): Options, Options, parse_article(), parse_preview(), Post, preview_url(), TelegramChannelProvider, read_sample() (+1 more)

### Community 18 - "Services"
Cohesion: 0.11
Nodes (10): LLMUnavailableError, DigestOptions, EmbedOptions, EmbedProcessor, Services, DigestPluginTests, factory(), ConsumerPluginTests (+2 more)

### Community 19 - "inspect_deliveries_cmd"
Cohesion: 0.14
Nodes (13): check_found(), format_value(), inspect_annotations_cmd(), inspect_artifacts_cmd(), inspect_deliveries_cmd(), inspect_items_cmd(), json_default(), preview() (+5 more)

### Community 22 - "TelegramSinkTests"
Cohesion: 0.21
Nodes (5): TelegramSink, item_options(), ok_response(), TelegramSinkTests, TelegramTestCase

### Community 23 - "test_app.py"
Cohesion: 0.11
Nodes (5): LockedError, cli(), Base, DBItemAnnotation, ProcessingStatus

### Community 25 - "HTTPClient"
Cohesion: 0.15
Nodes (6): HTTPClient, discover_feed_url(), fetch_article(), fetch_feed(), is_home_page(), TestHTTPClient

### Community 27 - "plugins/__init__.py"
Cohesion: 0.09
Nodes (8): LLM, LLMType, strip_code_fence(), __newstool_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 28 - "report_user_errors"
Cohesion: 0.13
Nodes (13): annotation_options(), artifact_options(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_deliveries_cmd(), delete_items_cmd(), delivery_options(), report_user_errors() (+5 more)

### Community 29 - "ProcessingScope"
Cohesion: 0.15
Nodes (3): ProcessingScope, Remixer, DeliveryTests

### Community 30 - "grouping.py"
Cohesion: 0.07
Nodes (23): average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer, GroupingOptions (+15 more)

### Community 31 - "cli.py"
Cohesion: 0.10
Nodes (6): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content()

### Community 32 - "migrate_autoincrement.py"
Cohesion: 0.09
Nodes (8): write_lock(), main(), migrate(), needs_autoincrement(), recreate(), main(), migrate(), main()

### Community 34 - "plugins"
Cohesion: 0.12
Nodes (17): lookback, title, url, api_base, chat_model, embed_model, plugins, digest (+9 more)

### Community 36 - "RecordingItemSink"
Cohesion: 0.31
Nodes (3): ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 37 - "Config"
Cohesion: 0.09
Nodes (8): Database & ORM Conventions, DTO, Protocol & ORM Implementation Reference, 0011: Environment overrides, relative paths and one storage directory, Consequences, Context, Decision, Config, DirectoryTests

### Community 38 - "GoogleChatSinkTests"
Cohesion: 0.28
Nodes (3): GoogleChatSink, card_widgets(), GoogleChatSinkTests

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.21
Nodes (14): Architecture, cli.py Click commands, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger (+6 more)

### Community 40 - "CSJuntasGobiernoProvider"
Cohesion: 0.23
Nodes (6): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, NoOptions, TestCSJuntasGobierno

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
Cohesion: 0.17
Nodes (4): __newstool_plugin__(), WebhookOptions, OptionsTests, webhook_options()

### Community 45 - "config.example.yaml"
Cohesion: 0.11
Nodes (15): cache, expiration, llms, input, processors, options, processor, remixers (+7 more)

### Community 46 - "Application"
Cohesion: 0.05
Nodes (4): Application, lookup(), workflow_scope(), Workflow

### Community 50 - "MarkdownifyProcessor"
Cohesion: 0.19
Nodes (5): MarkdownifyProcessor, __newstool_plugin__(), SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 51 - "config.py"
Cohesion: 0.10
Nodes (7): Alias, CacheConfig, expand_variables(), MissingVariableError, ollama_url(), options_error(), parse_duration()

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 56 - "0009: Workflows and keyed entries"
Cohesion: 0.25
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 57 - ".settings_customise_sources"
Cohesion: 0.12
Nodes (5): EnvAliasSource, load_context(), LoadContext, LoadEnvSettingsSource, resolve_config_path()

### Community 58 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 59 - "PluginFailure"
Cohesion: 0.13
Nodes (12): __newstool_plugin__(), __newstool_plugin__(), entry_date(), find_image(), __newstool_plugin__(), parse_entry(), __newstool_plugin__(), __newstool_plugin__() (+4 more)

### Community 60 - ".feed"
Cohesion: 0.24
Nodes (3): FeedGeneratorRemixer, FeedGeneratorTests, RemixerTestCase

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 62 - "PluginOptions"
Cohesion: 0.09
Nodes (13): Decision, __newstool_plugin__(), Options, ClassRegister, PluginOptions, UsesLLMOptions, __newstool_plugin__(), SummarizeOptions (+5 more)

### Community 63 - "PluginFailure"
Cohesion: 0.08
Nodes (11): describe(), PluginFailure, reason(), select_article(), get_section(), parse_datetime(), PlazaProvider, page_title() (+3 more)

### Community 64 - "RunSummary"
Cohesion: 0.19
Nodes (3): RunSummary, Sink, CommandTests

### Community 65 - "PreflightSourceItemData"
Cohesion: 0.15
Nodes (4): PreflightSourceItemData, _extract_href(), _get_modified_at(), PrensaIbericaProvider

### Community 73 - "foundation internal library"
Cohesion: 0.29
Nodes (7): foundation internal library, foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section, P1: plain logging and <APP>_LOG_LEVEL fix, P2: rich progress per stream (RICH_STDOUT_*/RICH_STDERR_*)

### Community 75 - "setup_logging"
Cohesion: 0.33
Nodes (4): Additional Approved Packages, Framework Usage, newstool Python Specifics, setup_logging()

### Community 76 - "workflows"
Cohesion: 0.33
Nodes (6): sink, workflows, deliver, name, process, sources

### Community 78 - "deliveries_send_cmd"
Cohesion: 0.33
Nodes (3): deliveries_send_cmd(), delivery_filters(), select_deliveries()

### Community 79 - "SourceItem"
Cohesion: 0.08
Nodes (4): SourceItem, DigestRemixer, post(), SearchTests

### Community 81 - "0010: Plugin classes and the configuration catalog"
Cohesion: 0.40
Nodes (4): 0010: Plugin classes and the configuration catalog, Consequences, Context, Rejected options

### Community 85 - "SourceData"
Cohesion: 0.15
Nodes (4): DBSource, SourceData, CastellonInformacionProvider, IndexSiteProvider

## Knowledge Gaps
- **13 isolated node(s):** `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)`, `IndexSiteProvider / URLProvider` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 515 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `BaseProcessor` to `test_db.py`, `db.py`, `Artifact`, `feedgenerator.py`, `StubLLM`, `DeleteCommandTests`, `test_telegram.py`, `Delivery`, `Services`, `BaseItemSink`, `Any`, `TelegramSinkTests`, `test_app.py`, `.session_scope`, `plugins/__init__.py`, `ProcessingScope`, `grouping.py`, `migrate_autoincrement.py`, `.close`, `RecordingItemSink`, `Config`, `GoogleChatSinkTests`, `Application`, `.record_result`, `MarkdownifyProcessor`, `Delivery`, `.feed`, `PluginOptions`, `RunSummary`, `.save_artifact`, `.__init__`, `DigestRemixerTests`, `SourceItem`, `SourceData`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05880665519219736 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `ProcessingScope` to `test_db.py`, `db.py`, `ApplicationTests`, `BaseProcessor`, `Artifact`, `feedgenerator.py`, `StubLLM`, `DeleteCommandTests`, `invoke`, `Context`, `test_telegram.py`, `Delivery`, `inspect_deliveries_cmd`, `BaseItemSink`, `Any`, `test_app.py`, `report_user_errors`, `grouping.py`, `cli.py`, `RecordingItemSink`, `GoogleChatSinkTests`, `Application`, `Delivery`, `.feed`, `RunSummary`, `.save_artifact`, `DigestRemixerTests`, `deliveries_send_cmd`, `SourceItem`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Should `catalog.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06829488919041157 - nodes in this community are weakly interconnected._