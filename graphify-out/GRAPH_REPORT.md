# Graph Report - two-stage-import  (2026-10-30)

## Corpus Check
- 76 files · ~127,899 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 4, .lock 1)

## Summary
- 1726 nodes · 4876 edges · 84 communities (62 shown, 22 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 626 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `de59da2a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- Entry
- Config
- ApplicationTests
- Database
- post
- .from_text
- grouping.py
- Database (db.py, only SQLite/storage access)
- StubLLM
- ProcessingScope
- process_cmd
- CSJuntasGobiernoProvider
- RunSummary
- SourceData
- processors.py
- BaseSink
- TelegramChannelProvider
- migrate_feed_names.py
- ConfigError
- DigestRemixerTests
- .get_annotation_values
- TelegramSinkTests
- db.py
- Any
- HTTPClient
- plugins/__init__.py
- app_from_context
- Services
- ScoredItem
- cli.py
- migrate
- ADR 0002 Processing state lifecycle
- plugins
- RecordingItemSink
- DirectoryTests
- PreflightSourceItemData
- ADR 0007 Sinks and the delivery ledger
- .settings_customise_sources
- options
- hooks
- Services object (services.llm(name))
- GoogleChatSinkTests
- config.example.yaml
- Application
- cli
- PrensaIbericaPlainProvider
- MarkdownifyProcessor
- PluginFailure
- migrate_telegram_state.py
- newstool
- Processor
- El Periódico Mediterráneo
- LogLevelTests
- config.py
- deliveries table (the ledger)
- app.py
- sinks.py
- Item
- ClassRegister
- describe
- RecordingArtifactSink
- test_providers.py
- TestFeedReader
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- 0010: Plugin classes and the configuration catalog
- Artifact
- Grouping notes: NLP clustering pipeline
- .__init__
- 0011: Environment overrides, relative paths and one storage directory
- foundation internal library
- .get_artifact
- Framework Usage
- workflows
- Artifact
- SourceItemData
- SourceItem
- MigrateAutoincrementTests
- Database & ORM Conventions
- TelegramArtifactSink
- migrate_autoincrement.py

## God Nodes (most connected - your core abstractions)
1. `Database` - 159 edges
2. `ProcessingScope` - 140 edges
3. `SourceItem` - 120 edges
4. `SourceData` - 83 edges
5. `Services` - 76 edges
6. `PluginFailure` - 67 edges
7. `Application` - 64 edges
8. `Artifact` - 62 edges
9. `SourceItemData` - 58 edges
10. `ApplicationTests` - 54 edges

## Surprising Connections (you probably didn't know these)
- `Decision` --references--> `Config`  [INFERRED]
  docs/decisions/0011-environment-overrides-and-storage-dir.md → newstool/config.py
- `Decision` --references--> `Application`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/app.py
- `Framework Usage` --references--> `setup_logging()`  [INFERRED]
  .claude/rules/python.md → newstool/cli.py
- `Decision` --references--> `LLMType`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/llms.py
- `Framework Usage` --references--> `PluginOptions`  [INFERRED]
  .claude/rules/python.md → newstool/plugins/__init__.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (84 total, 22 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.05
Nodes (20): 0012: Delivery ids, changing their state and forced send, Consequences, Context, Decision, Rejected options, DBDelivery, DBProcessingState, DBSourceItem (+12 more)

### Community 1 - "Entry"
Cohesion: 0.10
Nodes (8): ids_of(), in_default(), Kind, Use, DeliveryEntry, Entry, ProcessEntry, RemixEntry

### Community 2 - "Config"
Cohesion: 0.09
Nodes (5): Catalog, Run, share_sources(), Config, Workflow

### Community 3 - "ApplicationTests"
Cohesion: 0.08
Nodes (5): ApplicationTests, retrieve(), retrieve(), listed(), retrieved()

### Community 4 - "Database"
Cohesion: 0.09
Nodes (7): Database, tags_text(), SummarizeProcessor, merge_tags(), BaseProcessor, Remixer, Sink

### Community 5 - "post"
Cohesion: 0.24
Nodes (3): build_caption(), post(), BuildCaptionTests

### Community 6 - ".from_text"
Cohesion: 0.07
Nodes (3): AliasTests, ConfigTests, EnvironmentOverrideTests

### Community 7 - "grouping.py"
Cohesion: 0.13
Nodes (8): __newstool_plugin__(), __newstool_plugin__(), EmbeddingsOptions, GroupingOptions, __newstool_plugin__(), BaseRemixer, RemixerType, GroupingPluginTests

### Community 8 - "Database (db.py, only SQLite/storage access)"
Cohesion: 0.17
Nodes (11): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention, AUTOINCREMENT integer ids, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage (+3 more)

### Community 9 - "StubLLM"
Cohesion: 0.13
Nodes (7): Processor, build(), EmbedTests, ProcessorTestCase, StubLLM, SummarizeTests, TaggerTests

### Community 10 - "ProcessingScope"
Cohesion: 0.07
Nodes (9): wrapper(), select_deliveries(), DeliveryStatus, Delivery, ProcessingScope, BaseArtifactSink, migrate(), DeleteCommandTests (+1 more)

### Community 11 - "process_cmd"
Cohesion: 0.20
Nodes (4): import_cmd(), process_cmd(), progress_rows(), run_each()

### Community 12 - "CSJuntasGobiernoProvider"
Cohesion: 0.27
Nodes (5): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, TestCSJuntasGobierno

### Community 13 - "RunSummary"
Cohesion: 0.15
Nodes (5): RunSummary, annotation(), CommandTests, InspectCommandTests, invoke()

### Community 14 - "SourceData"
Cohesion: 0.15
Nodes (4): DBSource, SourceData, CastellonInformacionProvider, IndexSiteProvider

### Community 15 - "processors.py"
Cohesion: 0.11
Nodes (11): Decision, EmbedOptions, EmbedProcessor, __newstool_plugin__(), UsesLLMOptions, __newstool_plugin__(), __newstool_plugin__(), SummarizeOptions (+3 more)

### Community 17 - "TelegramChannelProvider"
Cohesion: 0.17
Nodes (7): page_title(), parse_article(), parse_preview(), Post, TelegramChannelProvider, read_sample(), TestTelegramChannel

### Community 19 - "ConfigError"
Cohesion: 0.12
Nodes (5): lookup(), check_section(), Profile, ConfigError, options_error()

### Community 20 - "DigestRemixerTests"
Cohesion: 0.19
Nodes (6): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options, DigestRemixerTests

### Community 21 - ".get_annotation_values"
Cohesion: 0.07
Nodes (4): backoff_seconds(), CustomJSON, DBItemAnnotation, UTCDateTime

### Community 22 - "TelegramSinkTests"
Cohesion: 0.21
Nodes (5): TelegramSink, item_options(), ok_response(), TelegramSinkTests, TelegramTestCase

### Community 23 - "db.py"
Cohesion: 0.15
Nodes (4): _encode_value(), ProcessingStatus, _sha256_column(), Annotation

### Community 25 - "HTTPClient"
Cohesion: 0.12
Nodes (9): HTTPClient, discover_feed_url(), entry_date(), fetch_article(), fetch_feed(), find_image(), parse_entry(), is_home_page() (+1 more)

### Community 27 - "plugins/__init__.py"
Cohesion: 0.08
Nodes (12): LLM, LLMType, LLMUnavailableError, strip_code_fence(), __newstool_plugin__(), ollama_client(), OllamaLLM, Options (+4 more)

### Community 28 - "app_from_context"
Cohesion: 0.10
Nodes (25): annotation_options(), app_from_context(), artifact_options(), check_found(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_deliveries_cmd(), delete_items_cmd() (+17 more)

### Community 29 - "Services"
Cohesion: 0.13
Nodes (7): DigestOptions, DigestRemixer, Services, TaggerProcessor, DigestPluginTests, factory(), factory()

### Community 30 - "ScoredItem"
Cohesion: 0.06
Nodes (22): average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsRemixer, GroupingRemixer, item_ref() (+14 more)

### Community 31 - "cli.py"
Cohesion: 0.08
Nodes (15): format_value(), json_default(), lexer_for(), match_snippet(), parse_artifact_ids(), preview(), print_content(), print_deliver() (+7 more)

### Community 32 - "migrate"
Cohesion: 0.21
Nodes (4): main(), migrate(), needs_autoincrement(), recreate()

### Community 34 - "plugins"
Cohesion: 0.12
Nodes (17): lookback, title, url, api_base, chat_model, embed_model, plugins, digest (+9 more)

### Community 36 - "RecordingItemSink"
Cohesion: 0.24
Nodes (4): SelectionRequiredError, ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 38 - "PreflightSourceItemData"
Cohesion: 0.17
Nodes (3): PreflightSourceItemData, PreflightProvider, Provider

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.21
Nodes (14): Architecture, cli.py Click commands, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger (+6 more)

### Community 40 - ".settings_customise_sources"
Cohesion: 0.12
Nodes (5): EnvAliasSource, load_context(), LoadContext, LoadEnvSettingsSource, resolve_config_path()

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
Cohesion: 0.09
Nodes (10): build_card(), chat_image_url(), GoogleChatSink, __newstool_plugin__(), WebhookOptions, card_widgets(), ChatImageUrlTests, GoogleChatSinkTests (+2 more)

### Community 45 - "config.example.yaml"
Cohesion: 0.11
Nodes (15): cache, expiration, llms, input, processors, options, processor, remixers (+7 more)

### Community 46 - "Application"
Cohesion: 0.07
Nodes (3): Application, workflow_scope(), import_sources()

### Community 47 - "cli"
Cohesion: 0.17
Nodes (4): cli(), delete_group(), deliveries_group(), inspect_group()

### Community 50 - "MarkdownifyProcessor"
Cohesion: 0.23
Nodes (5): MarkdownifyProcessor, SkipItem, ClassRegisterTests, make_pdf(), MarkdownifyPdfTests

### Community 51 - "PluginFailure"
Cohesion: 0.09
Nodes (8): PluginFailure, select_article(), get_section(), parse_datetime(), PlazaProvider, TheGuardianProvider, ExternalErrorTests, LogFailureTests

### Community 52 - "migrate_telegram_state.py"
Cohesion: 0.16
Nodes (3): LockedError, write_lock(), main()

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 57 - "config.py"
Cohesion: 0.11
Nodes (6): Alias, CacheConfig, expand_variables(), MissingVariableError, ollama_url(), parse_duration()

### Community 58 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 59 - "app.py"
Cohesion: 0.12
Nodes (10): __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__() (+2 more)

### Community 60 - "sinks.py"
Cohesion: 0.20
Nodes (5): DocumentDeliveryOptions, ItemDeliveryOptions, ArtifactDeliveryOptions, DeliveryOptions, SinkType

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 63 - "describe"
Cohesion: 0.17
Nodes (5): import_one(), describe(), log_failure(), reason(), DescribeTests

### Community 65 - "test_providers.py"
Cohesion: 0.16
Nodes (7): Options, Options, merge_options(), NoOptions, PluginOptions, Options, preview_url()

### Community 68 - "0010: Plugin classes and the configuration catalog"
Cohesion: 0.40
Nodes (4): 0010: Plugin classes and the configuration catalog, Consequences, Context, Rejected options

### Community 72 - "0011: Environment overrides, relative paths and one storage directory"
Cohesion: 0.40
Nodes (4): 0011: Environment overrides, relative paths and one storage directory, Consequences, Context, Decision

### Community 73 - "foundation internal library"
Cohesion: 0.29
Nodes (7): foundation internal library, foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section, P1: plain logging and <APP>_LOG_LEVEL fix, P2: rich progress per stream (RICH_STDOUT_*/RICH_STDERR_*)

### Community 75 - "Framework Usage"
Cohesion: 0.50
Nodes (3): Additional Approved Packages, Framework Usage, newstool Python Specifics

### Community 76 - "workflows"
Cohesion: 0.33
Nodes (6): sink, workflows, deliver, name, process, sources

### Community 77 - "Artifact"
Cohesion: 0.12
Nodes (3): DBArtifact, Artifact, ArtifactTests

### Community 78 - "SourceItemData"
Cohesion: 0.22
Nodes (4): SourceItemData, PrensaIbericaProvider, TestPrensaIberica, TestSourceItemDataContent

### Community 79 - "SourceItem"
Cohesion: 0.09
Nodes (3): SourceItem, FeedGeneratorRemixer, SearchTests

### Community 82 - "TelegramArtifactSink"
Cohesion: 0.29
Nodes (4): __newstool_plugin__(), TelegramArtifactSink, PluginTests, TelegramArtifactSinkTests

## Knowledge Gaps
- **13 isolated node(s):** `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)`, `IndexSiteProvider / URLProvider` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 517 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ProcessingScope` connect `ProcessingScope` to `test_db.py`, `ApplicationTests`, `Database`, `grouping.py`, `StubLLM`, `process_cmd`, `RunSummary`, `processors.py`, `BaseSink`, `DigestRemixerTests`, `db.py`, `app_from_context`, `Services`, `ScoredItem`, `cli.py`, `RecordingItemSink`, `Application`, `migrate_telegram_state.py`, `app.py`, `sinks.py`, `Artifact`, `SourceItem`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05078929306794784 - nodes in this community are weakly interconnected._
- **Why does `Database` connect `Database` to `test_db.py`, `Config`, `post`, `grouping.py`, `StubLLM`, `ProcessingScope`, `SourceData`, `processors.py`, `BaseSink`, `DigestRemixerTests`, `.get_annotation_values`, `TelegramSinkTests`, `db.py`, `._release_contents`, `plugins/__init__.py`, `Services`, `ScoredItem`, `.close`, `RecordingItemSink`, `GoogleChatSinkTests`, `Application`, `MarkdownifyProcessor`, `migrate_telegram_state.py`, `app.py`, `sinks.py`, `RecordingArtifactSink`, `.__init__`, `.get_artifact`, `Artifact`, `SourceItem`, `MigrateAutoincrementTests`, `TelegramArtifactSink`, `migrate_autoincrement.py`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Should `Entry` be split into smaller, more focused modules?**
  _Cohesion score 0.1032258064516129 - nodes in this community are weakly interconnected._