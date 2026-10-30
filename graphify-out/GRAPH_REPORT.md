# Graph Report - prensaiberica-preflight  (2026-10-30)

## Corpus Check
- 75 files · ~146,223 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 4, .lock 1)

## Summary
- 1727 nodes · 4875 edges · 89 communities (56 shown, 33 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 628 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e62c84ed`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- make_item
- ConfigError
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
- RunSummary
- Context
- .from_file
- Delivery
- Services
- Workflow
- inspect_deliveries_cmd
- Database
- Any
- TelegramSinkTests
- test_app.py
- Any
- SourceData
- OllamaLLM
- app_from_context
- ProcessingScope
- grouping.py
- cli.py
- migrate_autoincrement.py
- ADR 0002 Processing state lifecycle
- plugins
- .close
- RecordingItemSink
- Config
- DeliveryStatus
- ADR 0007 Sinks and the delivery ledger
- report_user_errors
- options
- hooks
- Services object (services.llm(name))
- GoogleChatSinkTests
- config.example.yaml
- Application
- ProcessingTests
- MarkdownifyProcessor
- test_config.py
- DeliveryTests
- newstool
- Processor
- El Periódico Mediterráneo
- 0009: Workflows and keyed entries
- .settings_customise_sources
- deliveries table (the ledger)
- PluginFailure
- AnnotationTests
- Item
- ClassRegister
- describe
- TestFeedReader
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- .count
- Artifact
- Grouping notes: NLP clustering pipeline
- .__init__
- foundation internal library
- catalog.py
- setup_logging
- workflows
- LogFailureTests
- TestSourceItemDataContent
- SourceItem
- LogLevelTests
- .content_dir
- 0012: Delivery ids, changing their state and forced send
- expand_variables
- GetItemsTests
- test_db.py
- 0011: Environment overrides, relative paths and one storage directory
- check_section

## God Nodes (most connected - your core abstractions)
1. `Database` - 160 edges
2. `ProcessingScope` - 140 edges
3. `SourceItem` - 120 edges
4. `SourceData` - 80 edges
5. `Services` - 76 edges
6. `Application` - 64 edges
7. `PluginFailure` - 64 edges
8. `Artifact` - 62 edges
9. `SourceItemData` - 56 edges
10. `ApplicationTests` - 55 edges

## Surprising Connections (you probably didn't know these)
- `Decision` --references--> `Config`  [INFERRED]
  docs/decisions/0011-environment-overrides-and-storage-dir.md → newstool/config.py
- `Decision` --references--> `Application`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/app.py
- `Framework Usage` --references--> `PluginOptions`  [INFERRED]
  .claude/rules/python.md → newstool/plugins/__init__.py
- `Decision` --references--> `UsesLLMOptions`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/plugins/__init__.py
- `Decision` --references--> `ClassRegister`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/plugins/__init__.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (89 total, 33 thin omitted)

### Community 0 - "make_item"
Cohesion: 0.23
Nodes (6): DBSourceItem, ContentStorageTests, DatabaseTestCase, make_item(), make_source(), UpsertSourceItemsTests

### Community 1 - "ConfigError"
Cohesion: 0.12
Nodes (4): Catalog, Profile, Run, ConfigError

### Community 2 - "db.py"
Cohesion: 0.06
Nodes (19): Alias, CacheConfig, _sha256_column(), strip_code_fence(), Annotation, DigestOptions, __newstool_plugin__(), UsesLLMOptions (+11 more)

### Community 3 - "ApplicationTests"
Cohesion: 0.08
Nodes (6): ApplicationTests, retrieve(), retrieve(), same(), listed(), retrieved()

### Community 4 - "BaseProcessor"
Cohesion: 0.06
Nodes (13): 0010: Plugin classes and the configuration catalog, Consequences, Context, Rejected options, EmbedOptions, EmbedProcessor, tags_text(), SummarizeProcessor (+5 more)

### Community 5 - "Artifact"
Cohesion: 0.09
Nodes (6): DBArtifact, Artifact, SelectionRequiredError, MigrateFeedNamesTests, ArtifactSinkTests, RecordingArtifactSink

### Community 7 - "feedgenerator.py"
Cohesion: 0.18
Nodes (6): __newstool_plugin__(), Options, Options, PluginOptions, Options, RemixerType

### Community 8 - "Database (db.py, only SQLite/storage access)"
Cohesion: 0.17
Nodes (11): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention, AUTOINCREMENT integer ids, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage (+3 more)

### Community 9 - "StubLLM"
Cohesion: 0.11
Nodes (8): Processor, build(), ConsumerPluginTests, EmbedTests, ProcessorTestCase, StubLLM, SummarizeTests, TaggerTests

### Community 11 - "run_cmd"
Cohesion: 0.14
Nodes (8): import_cmd(), print_import(), print_process(), print_remix(), progress_rows(), remix_cmd(), run_cmd(), run_each()

### Community 12 - "SourceItemData"
Cohesion: 0.11
Nodes (11): PreflightSourceItemData, SourceItemData, CSJuntasGobiernoProvider, PreparseData, NoOptions, _extract_href(), _get_modified_at(), PrensaIbericaProvider (+3 more)

### Community 13 - "RunSummary"
Cohesion: 0.10
Nodes (6): RunSummary, annotation(), CommandTests, ExternalErrorTests, InspectCommandTests, invoke()

### Community 14 - "Context"
Cohesion: 0.17
Nodes (5): cli(), inspect_content_cmd(), parse_artifact_ids(), process_cmd(), search_cmd()

### Community 17 - "Services"
Cohesion: 0.06
Nodes (14): Decision, LLM, LLMType, LLMUnavailableError, __newstool_plugin__(), Services, parse_article(), parse_preview() (+6 more)

### Community 18 - "Workflow"
Cohesion: 0.17
Nodes (3): share_sources(), own_entries(), Workflow

### Community 19 - "inspect_deliveries_cmd"
Cohesion: 0.16
Nodes (10): format_value(), inspect_artifacts_cmd(), inspect_deliveries_cmd(), inspect_items_cmd(), json_default(), preview(), print_deliver(), print_item() (+2 more)

### Community 20 - "Database"
Cohesion: 0.14
Nodes (4): Database, BaseArtifactSink, BaseItemSink, Sink

### Community 21 - "Any"
Cohesion: 0.14
Nodes (3): CustomJSON, _encode_value(), UTCDateTime

### Community 22 - "TelegramSinkTests"
Cohesion: 0.10
Nodes (11): merge_options(), __newstool_plugin__(), post(), TelegramArtifactSink, TelegramSink, item_options(), ok_response(), PluginTests (+3 more)

### Community 23 - "test_app.py"
Cohesion: 0.15
Nodes (4): ProcessingStatus, build_caption(), GroupingPluginTests, BuildCaptionTests

### Community 25 - "SourceData"
Cohesion: 0.08
Nodes (13): HTTPClient, SourceData, CastellonInformacionProvider, FeedReaderProvider, fetch_article(), PlazaProvider, is_home_page(), preview_url() (+5 more)

### Community 27 - "OllamaLLM"
Cohesion: 0.21
Nodes (5): __newstool_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 28 - "app_from_context"
Cohesion: 0.15
Nodes (12): app_from_context(), check_found(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_deliveries_cmd(), delete_items_cmd(), deliveries_send_cmd(), deliveries_set_status_cmd() (+4 more)

### Community 29 - "ProcessingScope"
Cohesion: 0.16
Nodes (4): ProcessingScope, DigestRemixer, Remixer, DigestRemixerTests

### Community 30 - "grouping.py"
Cohesion: 0.05
Nodes (26): average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer, GroupingOptions (+18 more)

### Community 31 - "cli.py"
Cohesion: 0.10
Nodes (6): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content()

### Community 32 - "migrate_autoincrement.py"
Cohesion: 0.08
Nodes (9): LockedError, write_lock(), main(), migrate(), needs_autoincrement(), recreate(), main(), migrate() (+1 more)

### Community 34 - "plugins"
Cohesion: 0.12
Nodes (17): lookback, title, url, api_base, chat_model, embed_model, plugins, digest (+9 more)

### Community 36 - "RecordingItemSink"
Cohesion: 0.28
Nodes (3): ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 38 - "DeliveryStatus"
Cohesion: 0.27
Nodes (3): DeliveryStatus, migrate(), MigrateTelegramStateTests

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.21
Nodes (14): Architecture, cli.py Click commands, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger (+6 more)

### Community 40 - "report_user_errors"
Cohesion: 0.21
Nodes (8): annotation_options(), artifact_options(), delivery_options(), inspect_annotations_cmd(), report_user_errors(), wrapper(), scope_options(), wrapper()

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
Cohesion: 0.06
Nodes (3): Application, lookup(), workflow_scope()

### Community 50 - "MarkdownifyProcessor"
Cohesion: 0.23
Nodes (5): MarkdownifyProcessor, SkipItem, ClassRegisterTests, make_pdf(), MarkdownifyPdfTests

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
Cohesion: 0.15
Nodes (4): EnvAliasSource, load_context(), LoadContext, LoadEnvSettingsSource

### Community 58 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 59 - "PluginFailure"
Cohesion: 0.08
Nodes (21): PluginFailure, __newstool_plugin__(), find_parent_by_tag_name(), get_date_from_text(), __newstool_plugin__(), discover_feed_url(), entry_date(), fetch_feed() (+13 more)

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 63 - "describe"
Cohesion: 0.15
Nodes (6): import_sources(), import_one(), describe(), log_failure(), reason(), DescribeTests

### Community 73 - "foundation internal library"
Cohesion: 0.29
Nodes (7): foundation internal library, foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section, P1: plain logging and <APP>_LOG_LEVEL fix, P2: rich progress per stream (RICH_STDOUT_*/RICH_STDERR_*)

### Community 74 - "catalog.py"
Cohesion: 0.10
Nodes (9): ids_of(), in_default(), Kind, Use, DeliveryEntry, Entry, options_error(), ProcessEntry (+1 more)

### Community 75 - "setup_logging"
Cohesion: 0.33
Nodes (4): Additional Approved Packages, Framework Usage, newstool Python Specifics, setup_logging()

### Community 76 - "workflows"
Cohesion: 0.33
Nodes (6): sink, workflows, deliver, name, process, sources

### Community 79 - "SourceItem"
Cohesion: 0.15
Nodes (3): SourceItem, FeedGeneratorRemixer, SearchTests

### Community 81 - ".content_dir"
Cohesion: 0.29
Nodes (3): Database & ORM Conventions, DTO, Protocol & ORM Implementation Reference, resolve_config_path()

### Community 82 - "0012: Delivery ids, changing their state and forced send"
Cohesion: 0.33
Nodes (5): 0012: Delivery ids, changing their state and forced send, Consequences, Context, Decision, Rejected options

### Community 85 - "test_db.py"
Cohesion: 0.11
Nodes (6): Base, DBItemAnnotation, DBProcessingState, DBSource, ArtifactTests, ConnectionTests

### Community 86 - "0011: Environment overrides, relative paths and one storage directory"
Cohesion: 0.40
Nodes (4): 0011: Environment overrides, relative paths and one storage directory, Consequences, Context, Decision

## Knowledge Gaps
- **13 isolated node(s):** `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)`, `IndexSiteProvider / URLProvider` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 515 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ProcessingScope` connect `ProcessingScope` to `db.py`, `ApplicationTests`, `BaseProcessor`, `Artifact`, `feedgenerator.py`, `StubLLM`, `DeleteCommandTests`, `run_cmd`, `RunSummary`, `Context`, `Delivery`, `inspect_deliveries_cmd`, `Database`, `test_app.py`, `app_from_context`, `grouping.py`, `cli.py`, `RecordingItemSink`, `DeliveryStatus`, `report_user_errors`, `Application`, `DeliveryTests`, `AnnotationTests`, `.count`, `SourceItem`, `GetItemsTests`, `test_db.py`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ConfigError` be split into smaller, more focused modules?**
  _Cohesion score 0.11693548387096774 - nodes in this community are weakly interconnected._
- **Why does `Database` connect `Database` to `make_item`, `db.py`, `BaseProcessor`, `Artifact`, `feedgenerator.py`, `StubLLM`, `DeleteCommandTests`, `Delivery`, `Any`, `TelegramSinkTests`, `test_app.py`, `SourceData`, `.session_scope`, `ProcessingScope`, `grouping.py`, `migrate_autoincrement.py`, `.close`, `RecordingItemSink`, `DeliveryStatus`, `GoogleChatSinkTests`, `Application`, `.record_result`, `MarkdownifyProcessor`, `ClassRegister`, `.__init__`, `SourceItem`, `test_db.py`, `.get_stored_content`?**
  _High betweenness centrality (0.132) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Should `db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05640203154236835 - nodes in this community are weakly interconnected._