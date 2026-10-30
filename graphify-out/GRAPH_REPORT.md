# Graph Report - newstool  (2026-10-30)

## Corpus Check
- 77 files · ~180,563 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1783 nodes · 4906 edges · 95 communities (60 shown, 35 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 601 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9eb6a083`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- catalog.py
- test_app.py
- test_cli.py
- reason
- invoke
- Application
- TestFeedReader
- Database (db.py, only SQLite/storage access)
- LockedError
- DeleteCommandTests
- inspect_deliveries_cmd
- CSJuntasGobiernoProvider
- ProcessingScope
- app_from_context
- Artifact
- BaseSink
- Telegram Channel Parsing
- Services
- Services
- Any
- Artifact
- report_user_errors
- PluginFailure
- Markdownify Processor
- app.py
- .from_file
- ScoredItem
- cli.py
- migrate_autoincrement.py
- BaseItemSink
- AnnotationTests
- migrate
- .close
- .queue_item_deliveries
- ProcessingScope
- Architecture & Processing ADRs
- SourceData
- Selection CLI Options
- telegram_channel.py
- Processor & Remixer Bundles
- GoogleChatSink
- Plugin System Docs
- Application
- SourceItem
- PreflightSourceItemData
- .__init__
- load_context
- test_config.py
- inspect_artifacts_cmd
- Spec Glossary Entities
- Sample Pages & Formats
- LogFailureTests
- ExternalErrorTests
- Agent Conventions
- migrate_feed_names.py
- digest.py
- Item Identity ADR
- .send
- run_cmd
- test_providers.py
- SourceItemData
- HTTPClient
- Example Sources
- .key
- Artifact & Remixer
- Grouping Notes
- setup_logging
- LogLevelTests
- Entry
- expand_variables
- __newsmerger_plugin__
- deliveries_set_status_cmd
- 0009: Workflows and keyed entries
- 0011: Environment overrides, relative paths and one storage directory
- LogLevelTests
- Delivery
- GoogleChatSinkTests
- command
- RunSummary
- ConfigError
- ClassRegister
- ._find_excluded_containers
- .content_dir
- 0010: Plugin classes and the configuration catalog
- parse_entry
- ADR 0002 Processing state lifecycle

## God Nodes (most connected - your core abstractions)
1. `ProcessingScope` - 149 edges
2. `SourceItem` - 125 edges
3. `Database` - 95 edges
4. `Services` - 82 edges
5. `SourceData` - 80 edges
6. `PluginFailure` - 67 edges
7. `Artifact` - 67 edges
8. `Application` - 66 edges
9. `ApplicationTests` - 60 edges
10. `SourceItemData` - 56 edges

## Surprising Connections (you probably didn't know these)
- `Decision` --references--> `Config`  [INFERRED]
  docs/decisions/0011-environment-overrides-and-storage-dir.md → newstool/config.py
- `Rejected options` --references--> `Services`  [INFERRED]
  docs/decisions/0013-plugin-services-at-init.md → newstool/plugins/__init__.py
- `Decision` --references--> `Application`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/app.py
- `Decision` --references--> `Application`  [INFERRED]
  docs/decisions/0013-plugin-services-at-init.md → newstool/app.py
- `Context` --references--> `Database`  [INFERRED]
  docs/decisions/0013-plugin-services-at-init.md → newstool/db.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (95 total, 35 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.07
Nodes (17): 0012: Delivery ids, changing their state and forced send, Consequences, Context, Decision, Rejected options, DBProcessingState, AnnotationTests, ConnectionTests (+9 more)

### Community 1 - "catalog.py"
Cohesion: 0.12
Nodes (8): Catalog, in_default(), Kind, Profile, Use, DeliveryEntry, ProcessEntry, RemixEntry

### Community 2 - "test_app.py"
Cohesion: 0.14
Nodes (3): ProcessingStatus, _sha256_column(), Annotation

### Community 3 - "test_cli.py"
Cohesion: 0.08
Nodes (7): ApplicationTests, retrieve(), retrieve_published(), retrieve(), same(), listed(), retrieved()

### Community 5 - "invoke"
Cohesion: 0.16
Nodes (4): MarkSummary, annotation(), InspectCommandTests, invoke()

### Community 8 - "Database (db.py, only SQLite/storage access)"
Cohesion: 0.17
Nodes (11): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention, AUTOINCREMENT integer ids, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage (+3 more)

### Community 9 - "LockedError"
Cohesion: 0.13
Nodes (5): Processor, ConsumerPluginTests, EmbedTests, StubLLM, TaggerTests

### Community 11 - "inspect_deliveries_cmd"
Cohesion: 0.16
Nodes (10): format_value(), inspect_artifacts_cmd(), inspect_deliveries_cmd(), inspect_items_cmd(), json_default(), preview(), print_deliver(), print_item() (+2 more)

### Community 12 - "CSJuntasGobiernoProvider"
Cohesion: 0.28
Nodes (3): find_parent_by_tag_name(), get_date_from_text(), PreparseData

### Community 14 - "app_from_context"
Cohesion: 0.13
Nodes (9): app_from_context(), cli(), inspect_content_cmd(), match_snippet(), parse_artifact_ids(), print_process(), process_cmd(), remix_cmd() (+1 more)

### Community 15 - "Artifact"
Cohesion: 0.10
Nodes (11): build_caption(), post(), TelegramArtifactSink, TelegramSink, BuildCaptionTests, item_options(), ok_response(), PluginTests (+3 more)

### Community 17 - "Telegram Channel Parsing"
Cohesion: 0.18
Nodes (6): is_home_page(), parse_article(), parse_preview(), Post, TelegramChannelProvider, TestTelegramChannel

### Community 18 - "Services"
Cohesion: 0.07
Nodes (15): Decision, EmbedOptions, EmbedProcessor, __newstool_plugin__(), tags_text(), UsesLLMOptions, __newstool_plugin__(), __newstool_plugin__() (+7 more)

### Community 19 - "Services"
Cohesion: 0.09
Nodes (11): Decision, LLM, LLMType, LLMUnavailableError, DigestOptions, Services, SummarizeProcessor, DigestPluginTests (+3 more)

### Community 22 - "Artifact"
Cohesion: 0.09
Nodes (8): DBArtifact, DeliveryStatus, Artifact, BaseArtifactSink, ArtifactTests, ArtifactSinkTests, RecordingArtifactSink, MigrateTelegramStateTests

### Community 23 - "report_user_errors"
Cohesion: 0.23
Nodes (7): annotation_options(), artifact_options(), delivery_options(), inspect_annotations_cmd(), report_user_errors(), wrapper(), scope_options()

### Community 25 - "PluginFailure"
Cohesion: 0.10
Nodes (9): PluginFailure, strip_code_fence(), DigestRemixer, __newstool_plugin__(), select_article(), get_section(), parse_datetime(), TaggerProcessor (+1 more)

### Community 27 - "Markdownify Processor"
Cohesion: 0.21
Nodes (5): __newstool_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 28 - "app.py"
Cohesion: 0.10
Nodes (8): Alias, CacheConfig, DocumentDeliveryOptions, ItemDeliveryOptions, __newstool_plugin__(), ArtifactDeliveryOptions, DeliveryOptions, SinkType

### Community 30 - "ScoredItem"
Cohesion: 0.05
Nodes (25): FeedGeneratorRemixer, average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer (+17 more)

### Community 31 - "cli.py"
Cohesion: 0.10
Nodes (6): delete_group(), deliveries_group(), inspect_group(), lexer_for(), print_content(), print_remix()

### Community 32 - "migrate_autoincrement.py"
Cohesion: 0.07
Nodes (12): LockedError, write_lock(), Base, DBItemAnnotation, main(), migrate(), needs_autoincrement(), recreate() (+4 more)

### Community 33 - "BaseItemSink"
Cohesion: 0.10
Nodes (3): BaseItemSink, SelectionRequiredError, SubjectKindError

### Community 34 - "AnnotationTests"
Cohesion: 0.12
Nodes (17): lookback, title, url, api_base, chat_model, embed_model, plugins, digest (+9 more)

### Community 36 - ".close"
Cohesion: 0.28
Nodes (3): ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 38 - "ProcessingScope"
Cohesion: 0.17
Nodes (5): wrapper(), ProcessingScope, Remixer, SearchTests, DigestRemixerTests

### Community 39 - "Architecture & Processing ADRs"
Cohesion: 0.21
Nodes (14): Architecture, cli.py Click commands, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger (+6 more)

### Community 40 - "SourceData"
Cohesion: 0.10
Nodes (7): DBSource, SourceData, CastellonInformacionProvider, PlazaProvider, TheGuardianProvider, IndexSiteProvider, Provider

### Community 41 - "Selection CLI Options"
Cohesion: 0.15
Nodes (14): options, artifacts, chat_id, interval, item_image, item_url_preview, item_url_text, markdown (+6 more)

### Community 42 - "telegram_channel.py"
Cohesion: 0.15
Nodes (12): exclude, args, entry, files, id, language, name, pass_filenames (+4 more)

### Community 43 - "Processor & Remixer Bundles"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "GoogleChatSink"
Cohesion: 0.10
Nodes (8): build_card(), chat_image_url(), GoogleChatSink, __newstool_plugin__(), WebhookOptions, ChatImageUrlTests, OptionsTests, webhook_options()

### Community 45 - "Plugin System Docs"
Cohesion: 0.11
Nodes (15): cache, expiration, llms, input, processors, options, processor, remixers (+7 more)

### Community 46 - "Application"
Cohesion: 0.06
Nodes (3): Application, workflow_scope(), Workflow

### Community 47 - "SourceItem"
Cohesion: 0.13
Nodes (6): Database, DBSourceItem, SourceItem, ProcessorTestCase, SummarizeTests, make_item()

### Community 50 - ".__init__"
Cohesion: 0.32
Nodes (4): MarkdownifyProcessor, SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 51 - "load_context"
Cohesion: 0.15
Nodes (4): EnvAliasSource, load_context(), LoadContext, LoadEnvSettingsSource

### Community 54 - "Spec Glossary Entities"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "Sample Pages & Formats"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 58 - "Agent Conventions"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 59 - "migrate_feed_names.py"
Cohesion: 0.13
Nodes (10): _encode_value(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__() (+2 more)

### Community 60 - "digest.py"
Cohesion: 0.13
Nodes (5): __newstool_plugin__(), __newstool_plugin__(), BaseRemixer, RemixerType, GroupingPluginTests

### Community 61 - "Item Identity ADR"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 63 - "run_cmd"
Cohesion: 0.11
Nodes (10): import_cmd(), import_sources(), import_one(), print_import(), progress_rows(), run_cmd(), run_each(), describe() (+2 more)

### Community 64 - "test_providers.py"
Cohesion: 0.15
Nodes (10): CSJuntasGobiernoProvider, Options, Options, merge_options(), NoOptions, PluginOptions, Options, Options (+2 more)

### Community 65 - "SourceItemData"
Cohesion: 0.20
Nodes (4): SourceItemData, PrensaIbericaProvider, read_sample(), TestPrensaIberica

### Community 66 - "HTTPClient"
Cohesion: 0.15
Nodes (9): 0013: Plugin services at init, Consequences, Context, Rejected options, HTTPClient, discover_feed_url(), fetch_article(), fetch_feed() (+1 more)

### Community 68 - ".key"
Cohesion: 0.12
Nodes (10): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options, 0014: Ledger rows by subject and the workflow in delivery commands, Consequences, Context (+2 more)

### Community 71 - "setup_logging"
Cohesion: 0.33
Nodes (4): Additional Approved Packages, Framework Usage, newstool Python Specifics, setup_logging()

### Community 73 - "LogLevelTests"
Cohesion: 0.29
Nodes (7): foundation internal library, foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section, P1: plain logging and <APP>_LOG_LEVEL fix, P2: rich progress per stream (RICH_STDOUT_*/RICH_STDERR_*)

### Community 76 - "__newsmerger_plugin__"
Cohesion: 0.33
Nodes (6): sink, workflows, deliver, name, process, sources

### Community 77 - "deliveries_set_status_cmd"
Cohesion: 0.18
Nodes (8): check_all_rows(), delete_deliveries_cmd(), deliveries_send_cmd(), deliveries_set_status_cmd(), delivery_filters(), require_workflow(), select_deliveries(), subject_filters()

### Community 79 - "0011: Environment overrides, relative paths and one storage directory"
Cohesion: 0.40
Nodes (4): 0011: Environment overrides, relative paths and one storage directory, Consequences, Context, Decision

### Community 81 - "Delivery"
Cohesion: 0.17
Nodes (3): DBDelivery, Delivery, DeliveryTests

### Community 83 - "command"
Cohesion: 0.22
Nodes (6): check_found(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), require_selection(), sort_option()

### Community 84 - "RunSummary"
Cohesion: 0.19
Nodes (3): RunSummary, Sink, CommandTests

### Community 85 - "ConfigError"
Cohesion: 0.09
Nodes (7): lookup(), check_section(), ids_of(), Run, share_sources(), ConfigError, options_error()

### Community 88 - ".content_dir"
Cohesion: 0.29
Nodes (3): Database & ORM Conventions, DTO, Protocol & ORM Implementation Reference, resolve_config_path()

### Community 89 - "0010: Plugin classes and the configuration catalog"
Cohesion: 0.29
Nodes (5): 0010: Plugin classes and the configuration catalog, Consequences, Context, Rejected options, sinks()

### Community 91 - "parse_entry"
Cohesion: 0.60
Nodes (3): entry_date(), find_image(), parse_entry()

## Knowledge Gaps
- **13 isolated node(s):** `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)`, `IndexSiteProvider / URLProvider` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 532 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ProcessingScope` connect `ProcessingScope` to `test_db.py`, `test_app.py`, `test_cli.py`, `reason`, `invoke`, `LockedError`, `inspect_deliveries_cmd`, `ProcessingScope`, `app_from_context`, `BaseSink`, `Services`, `Artifact`, `report_user_errors`, `PluginFailure`, `app.py`, `ScoredItem`, `cli.py`, `BaseItemSink`, `migrate`, `.close`, `Application`, `SourceItem`, `digest.py`, `deliveries_set_status_cmd`, `Delivery`, `GoogleChatSinkTests`, `command`, `RunSummary`, `0010: Plugin classes and the configuration catalog`?**
  _High betweenness centrality (0.158) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `check_all_rows()`) actually correct?**
  _`ProcessingScope` has 43 INFERRED edges - model-reasoned connections that need verification._
- **What connects `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06527682843472317 - nodes in this community are weakly interconnected._
- **Why does `SourceItem` connect `SourceItem` to `test_db.py`, `test_app.py`, `test_cli.py`, `reason`, `invoke`, `LockedError`, `inspect_deliveries_cmd`, `ProcessingScope`, `Artifact`, `BaseSink`, `Services`, `Services`, `Any`, `Artifact`, `PluginFailure`, `app.py`, `ScoredItem`, `cli.py`, `migrate_autoincrement.py`, `BaseItemSink`, `migrate`, `.close`, `ProcessingScope`, `GoogleChatSink`, `Application`, `.__init__`, `digest.py`, `.key`, `.get_content`, `Delivery`, `GoogleChatSinkTests`, `.get_annotation_values`, `.import_source`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `SourceItem` (e.g. with `Application` and `print_item()`) actually correct?**
  _`SourceItem` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Should `catalog.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11596638655462185 - nodes in this community are weakly interconnected._