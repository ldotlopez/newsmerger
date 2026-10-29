# Graph Report - newstool  (2026-10-29)

## Corpus Check
- 76 files · ~125,951 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1636 nodes · 4635 edges · 81 communities (55 shown, 26 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 631 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `88dec063`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- ConfigError
- Application
- .from_text
- BaseProcessor
- Artifact
- .from_text
- app.py
- TestFeedReader
- StubLLM
- .session_scope
- cli
- csjuntasgobierno.py
- test_cli.py
- telegram.py
- SourceItem
- DeliveryStatus
- test_providers.py
- test_migrate_autoincrement.py
- catalog.py
- 0009: Workflows and keyed entries
- Any
- SourceItemData
- db.py
- Any
- tagger.py
- Database
- plugins/__init__.py
- app_from_context
- Services
- ScoredItem
- inspect_annotations_cmd
- .feed
- ADR 0002 Processing state lifecycle
- plugins
- FeedReaderProvider
- feedreader.py
- Config
- .from_file
- ADR 0007 Sinks and the delivery ledger
- report_user_errors
- options
- hooks
- Services object (services.llm(name))
- GoogleChatSinkTests
- config.example.yaml
- run_cmd
- cli.py
- PrensaIbericaPlainProvider
- markdownify.py
- SourceData
- LazySourceItemData
- newstool
- Processor
- El Periódico Mediterráneo
- LockedError
- config.py
- deliveries table (the ledger)
- plugins/__init__.py
- ProcessingScope
- Item
- ClassRegister
- test_config.py
- ProcessorType
- migrate_autoincrement.py
- TestFeedReader
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- Artifact
- Grouping notes: NLP clustering pipeline
- delete_items_cmd
- migrate_feed_names.py
- foundation.plugin.Register plugin loading
- get_section
- setup_logging
- workflows
- .get_artifact
- .__init__
- 0011: Environment overrides, relative paths and one storage directory
- Database & ORM Conventions

## God Nodes (most connected - your core abstractions)
1. `Database` - 160 edges
2. `ProcessingScope` - 134 edges
3. `SourceItem` - 119 edges
4. `SourceData` - 82 edges
5. `Services` - 76 edges
6. `Artifact` - 62 edges
7. `Application` - 61 edges
8. `SourceItemData` - 54 edges
9. `HTTPClient` - 47 edges
10. `ApplicationTests` - 43 edges

## Surprising Connections (you probably didn't know these)
- `Decision` --references--> `Config`  [INFERRED]
  docs/decisions/0011-environment-overrides-and-storage-dir.md → newstool/config.py
- `Decision` --references--> `Application`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/app.py
- `Verification` --references--> `share_sources()`  [INFERRED]
  PLAN-workflow-selectors.md → newstool/catalog.py
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

## Communities (81 total, 26 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.06
Nodes (15): DBDelivery, DBProcessingState, DBSourceItem, AnnotationTests, ConnectionTests, ContentStorageTests, DatabaseTestCase, DeleteTests (+7 more)

### Community 1 - "ConfigError"
Cohesion: 0.09
Nodes (7): Catalog, Kind, Profile, Run, Use, ConfigError, DeliveryEntry

### Community 4 - "BaseProcessor"
Cohesion: 0.13
Nodes (4): tags_text(), SummarizeProcessor, BaseProcessor, MissingAnnotationError

### Community 5 - "Artifact"
Cohesion: 0.06
Nodes (21): DBArtifact, Artifact, merge_options(), build_caption(), DocumentDeliveryOptions, ItemDeliveryOptions, post(), TelegramArtifactSink (+13 more)

### Community 7 - "app.py"
Cohesion: 0.18
Nodes (3): ItemKey, main(), migrate()

### Community 8 - "TestFeedReader"
Cohesion: 0.17
Nodes (11): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention, AUTOINCREMENT integer ids, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage (+3 more)

### Community 9 - "StubLLM"
Cohesion: 0.13
Nodes (8): Processor, build(), ConsumerPluginTests, EmbedTests, ProcessorTestCase, StubLLM, SummarizeTests, TaggerTests

### Community 12 - "csjuntasgobierno.py"
Cohesion: 0.20
Nodes (6): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, NoOptions, TestCSJuntasGobierno

### Community 13 - "test_cli.py"
Cohesion: 0.09
Nodes (7): Annotation, RunSummary, annotation(), CommandTests, InspectCommandTests, invoke(), LogLevelTests

### Community 14 - "telegram.py"
Cohesion: 0.09
Nodes (10): build_card(), chat_image_url(), GoogleChatError, __newstool_plugin__(), __newstool_plugin__(), ArtifactDeliveryOptions, DeliveryOptions, Sink (+2 more)

### Community 15 - "SourceItem"
Cohesion: 0.12
Nodes (4): SourceItem, DigestRemixer, FeedGeneratorRemixer, SearchTests

### Community 17 - "test_providers.py"
Cohesion: 0.12
Nodes (11): Options, is_home_page(), Options, page_title(), parse_article(), parse_preview(), Post, preview_url() (+3 more)

### Community 18 - "test_migrate_autoincrement.py"
Cohesion: 0.23
Nodes (5): Base, DBItemAnnotation, migrate(), make_item(), MigrateAutoincrementTests

### Community 19 - "catalog.py"
Cohesion: 0.12
Nodes (6): check_section(), ids_of(), in_default(), Entry, ProcessEntry, RemixEntry

### Community 20 - "0009: Workflows and keyed entries"
Cohesion: 0.33
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 21 - "Any"
Cohesion: 0.11
Nodes (4): backoff_seconds(), CustomJSON, _encode_value(), UTCDateTime

### Community 22 - "SourceItemData"
Cohesion: 0.18
Nodes (4): SourceItemData, PrensaIbericaProvider, TestPrensaIberica, TestSourceItemDataContent

### Community 25 - "tagger.py"
Cohesion: 0.12
Nodes (9): LLMType, strip_code_fence(), __newstool_plugin__(), ollama_client(), OllamaLLM, Options, merge_tags(), TaggerProcessor (+1 more)

### Community 26 - "Database"
Cohesion: 0.07
Nodes (5): Database, AverageLinkRemixer, GroupingRemixer, SingleLinkRemixer, BaseRemixer

### Community 27 - "plugins/__init__.py"
Cohesion: 0.12
Nodes (14): Duration, DigestOptions, __newstool_plugin__(), __newstool_plugin__(), Options, EmbeddingsOptions, GroupingOptions, __newstool_plugin__() (+6 more)

### Community 28 - "app_from_context"
Cohesion: 0.15
Nodes (8): app_from_context(), cli(), import_cmd(), inspect_content_cmd(), parse_artifact_ids(), process_cmd(), remix_cmd(), search_cmd()

### Community 29 - "Services"
Cohesion: 0.09
Nodes (9): LLM, LLMUnavailableError, Services, SummarizeOptions, TaggerOptions, DigestPluginTests, factory(), ServicesTests (+1 more)

### Community 30 - "ScoredItem"
Cohesion: 0.11
Nodes (15): average_between(), average_link_cluster(), build_score_matrix(), cosine_similarity(), EmbeddingsRemixer, item_ref(), jaccard(), member_payload() (+7 more)

### Community 31 - "inspect_annotations_cmd"
Cohesion: 0.16
Nodes (10): check_found(), format_value(), inspect_annotations_cmd(), inspect_artifacts_cmd(), inspect_deliveries_cmd(), inspect_items_cmd(), json_default(), preview() (+2 more)

### Community 32 - ".feed"
Cohesion: 0.18
Nodes (4): EmbeddingGroupingTests, FeedGeneratorTests, GroupingTests, RemixerTestCase

### Community 34 - "plugins"
Cohesion: 0.12
Nodes (17): lookback, title, url, api_base, chat_model, embed_model, plugins, digest (+9 more)

### Community 35 - "FeedReaderProvider"
Cohesion: 0.22
Nodes (4): SelectionRequiredError, ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 36 - "feedreader.py"
Cohesion: 0.25
Nodes (8): discover_feed_url(), entry_date(), fetch_article(), fetch_feed(), find_image(), __newstool_plugin__(), parse_entry(), select_article()

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.21
Nodes (14): Architecture, cli.py Click commands, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger (+6 more)

### Community 40 - "report_user_errors"
Cohesion: 0.18
Nodes (9): annotation_options(), artifact_options(), delete_annotations_cmd(), delete_deliveries_cmd(), delivery_options(), report_user_errors(), wrapper(), scope_options() (+1 more)

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
Cohesion: 0.13
Nodes (6): GoogleChatSink, WebhookOptions, card_widgets(), GoogleChatSinkTests, OptionsTests, webhook_options()

### Community 45 - "config.example.yaml"
Cohesion: 0.11
Nodes (15): cache, expiration, llms, input, processors, options, processor, remixers (+7 more)

### Community 46 - "run_cmd"
Cohesion: 0.10
Nodes (13): workflow_scope(), share_sources(), import_sources(), progress_rows(), run_cmd(), run_each(), Workflow, Changes (+5 more)

### Community 47 - "cli.py"
Cohesion: 0.10
Nodes (8): lexer_for(), match_snippet(), print_content(), print_deliver(), print_import(), print_process(), print_remix(), print_table()

### Community 50 - "markdownify.py"
Cohesion: 0.16
Nodes (7): MarkdownifyProcessor, __newstool_plugin__(), ProcessorOptions, SkipItem, ClassRegisterTests, make_pdf(), MarkdownifyPdfTests

### Community 51 - "SourceData"
Cohesion: 0.12
Nodes (9): DBSource, HTTPClient, SourceData, CastellonInformacionProvider, PlazaProvider, TheGuardianProvider, IndexSiteProvider, URI (+1 more)

### Community 52 - "LazySourceItemData"
Cohesion: 0.19
Nodes (4): LazySourceItemData, BaseProvider, Provider, lazy()

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 56 - "LockedError"
Cohesion: 0.20
Nodes (3): LockedError, write_lock(), main()

### Community 57 - "config.py"
Cohesion: 0.06
Nodes (12): Alias, CacheConfig, ConfigPath, EnvAliasSource, expand_variables(), load_context(), LoadContext, LoadEnvSettingsSource (+4 more)

### Community 58 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 59 - "plugins/__init__.py"
Cohesion: 0.22
Nodes (8): __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), ProviderType

### Community 60 - "ProcessingScope"
Cohesion: 0.10
Nodes (6): DeliveryStatus, ProcessingScope, ArtifactNames, BaseArtifactSink, BaseItemSink, DigestRemixerTests

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 64 - "ProcessorType"
Cohesion: 0.10
Nodes (11): 0010: Plugin classes and the configuration catalog, Consequences, Context, Decision, Rejected options, EmbedOptions, EmbedProcessor, __newstool_plugin__() (+3 more)

### Community 71 - "delete_items_cmd"
Cohesion: 0.28
Nodes (4): delete_artifacts_cmd(), delete_items_cmd(), require_selection(), sort_option()

### Community 73 - "foundation.plugin.Register plugin loading"
Cohesion: 0.29
Nodes (7): foundation internal library, foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section, P1: plain logging and <APP>_LOG_LEVEL fix, P2: rich progress per stream (RICH_STDOUT_*/RICH_STDERR_*)

### Community 74 - "get_section"
Cohesion: 0.29
Nodes (3): get_section(), parse_datetime(), SectionNotFoundError

### Community 75 - "setup_logging"
Cohesion: 0.33
Nodes (4): Additional Approved Packages, Framework Usage, newstool Python Specifics, setup_logging()

### Community 76 - "workflows"
Cohesion: 0.33
Nodes (6): sink, workflows, deliver, name, process, sources

### Community 79 - "0011: Environment overrides, relative paths and one storage directory"
Cohesion: 0.40
Nodes (4): 0011: Environment overrides, relative paths and one storage directory, Consequences, Context, Decision

## Knowledge Gaps
- **13 isolated node(s):** `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)`, `IndexSiteProvider / URLProvider` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 477 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `test_db.py`, `Application`, `BaseProcessor`, `Artifact`, `app.py`, `StubLLM`, `.session_scope`, `test_cli.py`, `telegram.py`, `SourceItem`, `DeliveryStatus`, `test_migrate_autoincrement.py`, `Any`, `db.py`, `tagger.py`, `plugins/__init__.py`, `ScoredItem`, `.feed`, `FeedReaderProvider`, `GoogleChatSinkTests`, `markdownify.py`, `SourceData`, `ProcessingScope`, `ProcessorType`, `.close`, `.get_artifact`, `.__init__`?**
  _High betweenness centrality (0.160) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 43 INFERRED edges - model-reasoned connections that need verification._
- **What connects `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05693664795509222 - nodes in this community are weakly interconnected._
- **Why does `SourceItem` connect `SourceItem` to `test_db.py`, `Application`, `.from_text`, `BaseProcessor`, `Artifact`, `app.py`, `StubLLM`, `.session_scope`, `test_cli.py`, `telegram.py`, `DeliveryStatus`, `test_migrate_autoincrement.py`, `Any`, `db.py`, `tagger.py`, `Database`, `plugins/__init__.py`, `ScoredItem`, `inspect_annotations_cmd`, `.feed`, `FeedReaderProvider`, `GoogleChatSinkTests`, `cli.py`, `markdownify.py`, `SourceData`, `ProcessingScope`, `ProcessorType`?**
  _High betweenness centrality (0.137) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Should `ConfigError` be split into smaller, more focused modules?**
  _Cohesion score 0.08880666049953746 - nodes in this community are weakly interconnected._