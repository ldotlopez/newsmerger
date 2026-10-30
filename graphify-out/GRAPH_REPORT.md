# Graph Report - provider-order  (2026-10-30)

## Corpus Check
- 75 files · ~146,493 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 4, .lock 1)

## Summary
- 1731 nodes · 4889 edges · 97 communities (62 shown, 35 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 631 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `37cdb16c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- make_item
- catalog.py
- db.py
- ApplicationTests
- plaza.py
- Artifact
- .from_text
- test_db.py
- Database (db.py, only SQLite/storage access)
- StubLLM
- DeleteCommandTests
- run_cmd
- SourceItemData
- invoke
- app_from_context
- sinks.py
- Delivery
- TelegramChannelProvider
- Services
- cli.py
- Any
- TelegramSinkTests
- migrate_autoincrement.py
- Any
- HTTPClient
- Database
- ollama.py
- report_user_errors
- ProcessingScope
- grouping.py
- group
- migrate_telegram_state.py
- ADR 0002 Processing state lifecycle
- plugins
- .close
- RecordingItemSink
- Config
- AnnotationTests
- ADR 0007 Sinks and the delivery ledger
- CSJuntasGobiernoProvider
- options
- hooks
- Services object (services.llm(name))
- GoogleChatSinkTests
- config.example.yaml
- ._object
- SourceItem
- PreflightSourceItemData
- MarkdownifyProcessor
- app.py
- DeliveryTests
- newstool
- Processor
- El Periódico Mediterráneo
- 0009: Workflows and keyed entries
- .settings_customise_sources
- deliveries table (the ledger)
- models.py
- .feed
- Item
- PluginFailure
- describe
- .from_file
- PrensaIbericaProvider
- TestFeedReader
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- GroupingTests
- Artifact
- Grouping notes: NLP clustering pipeline
- Application
- ProcessingTests
- foundation internal library
- LogFailureTests
- Framework Usage
- workflows
- DigestRemixer
- AliasTests
- post
- LogLevelTests
- .content_dir
- 0012: Delivery ids, changing their state and forced send
- SourceData
- expand_variables
- EmbedProcessor
- GetItemsTests
- search_cmd
- 0011: Environment overrides, relative paths and one storage directory
- parse_entry
- TestSourceItemDataContent
- Workflow
- SelectionRequiredError

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
10. `ApplicationTests` - 56 edges

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

## Communities (97 total, 35 thin omitted)

### Community 0 - "make_item"
Cohesion: 0.23
Nodes (4): ContentStorageTests, make_item(), make_source(), UpsertSourceItemsTests

### Community 1 - "catalog.py"
Cohesion: 0.06
Nodes (15): Catalog, check_section(), ids_of(), in_default(), Kind, Profile, Run, share_sources() (+7 more)

### Community 2 - "db.py"
Cohesion: 0.10
Nodes (5): Base, _configure_sqlite_connection(), DBItemAnnotation, _sha256_column(), Annotation

### Community 3 - "ApplicationTests"
Cohesion: 0.08
Nodes (7): ApplicationTests, retrieve(), retrieve_published(), retrieve(), same(), listed(), retrieved()

### Community 4 - "plaza.py"
Cohesion: 0.09
Nodes (11): __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), get_section(), __newstool_plugin__(), parse_datetime(), PlazaProvider, __newstool_plugin__() (+3 more)

### Community 5 - "Artifact"
Cohesion: 0.10
Nodes (6): DBArtifact, Artifact, BaseRemixer, MigrateFeedNamesTests, ArtifactSinkTests, RecordingArtifactSink

### Community 7 - "test_db.py"
Cohesion: 0.13
Nodes (6): DBProcessingState, DBSourceItem, ArtifactTests, ConnectionTests, DatabaseTestCase, IdentityTests

### Community 8 - "Database (db.py, only SQLite/storage access)"
Cohesion: 0.17
Nodes (11): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention, AUTOINCREMENT integer ids, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage (+3 more)

### Community 9 - "StubLLM"
Cohesion: 0.10
Nodes (7): Processor, build(), EmbedTests, ProcessorTestCase, StubLLM, SummarizeTests, TaggerTests

### Community 11 - "run_cmd"
Cohesion: 0.14
Nodes (9): import_cmd(), print_import(), print_process(), print_remix(), process_cmd(), progress_rows(), remix_cmd(), run_cmd() (+1 more)

### Community 12 - "SourceItemData"
Cohesion: 0.25
Nodes (3): SourceItemData, TheGuardianProvider, TestPrensaIberica

### Community 13 - "invoke"
Cohesion: 0.10
Nodes (5): annotation(), CommandTests, ExternalErrorTests, InspectCommandTests, invoke()

### Community 14 - "app_from_context"
Cohesion: 0.12
Nodes (14): app_from_context(), cli(), delete_artifacts_cmd(), delete_deliveries_cmd(), delete_items_cmd(), deliveries_send_cmd(), deliveries_set_status_cmd(), delivery_filters() (+6 more)

### Community 15 - "sinks.py"
Cohesion: 0.13
Nodes (10): merge_options(), DocumentDeliveryOptions, ItemDeliveryOptions, __newstool_plugin__(), TelegramArtifactSink, ArtifactDeliveryOptions, DeliveryOptions, SinkType (+2 more)

### Community 16 - "Delivery"
Cohesion: 0.08
Nodes (3): Delivery, BaseArtifactSink, BaseSink

### Community 17 - "TelegramChannelProvider"
Cohesion: 0.20
Nodes (6): parse_article(), parse_preview(), Post, TelegramChannelProvider, read_sample(), TestTelegramChannel

### Community 18 - "Services"
Cohesion: 0.07
Nodes (17): Decision, LLMUnavailableError, DigestOptions, __newstool_plugin__(), __newstool_plugin__(), Options, __newstool_plugin__(), NoOptions (+9 more)

### Community 19 - "cli.py"
Cohesion: 0.11
Nodes (12): format_value(), inspect_artifacts_cmd(), inspect_items_cmd(), json_default(), lexer_for(), preview(), print_content(), print_deliver() (+4 more)

### Community 21 - "Any"
Cohesion: 0.19
Nodes (3): CustomJSON, _encode_value(), UTCDateTime

### Community 22 - "TelegramSinkTests"
Cohesion: 0.16
Nodes (5): TelegramSink, item_options(), ok_response(), TelegramSinkTests, TelegramTestCase

### Community 23 - "migrate_autoincrement.py"
Cohesion: 0.17
Nodes (4): main(), migrate(), needs_autoincrement(), recreate()

### Community 24 - "Any"
Cohesion: 0.10
Nodes (3): LLMEntry, own_entries(), parse_duration()

### Community 25 - "HTTPClient"
Cohesion: 0.16
Nodes (6): HTTPClient, discover_feed_url(), fetch_article(), fetch_feed(), is_home_page(), TestHTTPClient

### Community 27 - "ollama.py"
Cohesion: 0.11
Nodes (7): LLM, LLMType, __newstool_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 28 - "report_user_errors"
Cohesion: 0.17
Nodes (10): annotation_options(), artifact_options(), check_found(), delete_annotations_cmd(), delivery_options(), inspect_annotations_cmd(), report_user_errors(), wrapper() (+2 more)

### Community 29 - "ProcessingScope"
Cohesion: 0.07
Nodes (8): DeliveryStatus, ProcessingScope, RunSummary, Remixer, BaseItemSink, Sink, migrate(), MigrateTelegramStateTests

### Community 30 - "grouping.py"
Cohesion: 0.10
Nodes (19): average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer, GroupingRemixer (+11 more)

### Community 31 - "group"
Cohesion: 0.29
Nodes (3): delete_group(), deliveries_group(), inspect_group()

### Community 32 - "migrate_telegram_state.py"
Cohesion: 0.12
Nodes (5): LockedError, write_lock(), main(), migrate(), main()

### Community 34 - "plugins"
Cohesion: 0.12
Nodes (17): lookback, title, url, api_base, chat_model, embed_model, plugins, digest (+9 more)

### Community 36 - "RecordingItemSink"
Cohesion: 0.31
Nodes (3): ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.21
Nodes (14): Architecture, cli.py Click commands, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger (+6 more)

### Community 40 - "CSJuntasGobiernoProvider"
Cohesion: 0.27
Nodes (5): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, TestCSJuntasGobierno

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
Cohesion: 0.07
Nodes (12): build_card(), chat_image_url(), GoogleChatSink, __newstool_plugin__(), WebhookOptions, build_caption(), card_widgets(), ChatImageUrlTests (+4 more)

### Community 45 - "config.example.yaml"
Cohesion: 0.11
Nodes (15): cache, expiration, llms, input, processors, options, processor, remixers (+7 more)

### Community 47 - "SourceItem"
Cohesion: 0.09
Nodes (3): SourceItem, tags_text(), SearchTests

### Community 48 - "PreflightSourceItemData"
Cohesion: 0.16
Nodes (3): PreflightSourceItemData, PreflightProvider, Provider

### Community 50 - "MarkdownifyProcessor"
Cohesion: 0.16
Nodes (5): MarkdownifyProcessor, SkipItem, ClassRegisterTests, make_pdf(), MarkdownifyPdfTests

### Community 51 - "app.py"
Cohesion: 0.10
Nodes (4): lookup(), Alias, CacheConfig, ClassRegister

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

### Community 59 - "models.py"
Cohesion: 0.16
Nodes (8): Options, select_article(), PluginOptions, Options, Options, page_title(), preview_url(), BaseProvider

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 62 - "PluginFailure"
Cohesion: 0.08
Nodes (15): ProcessingStatus, PluginFailure, strip_code_fence(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), SummarizeOptions, SummarizeProcessor (+7 more)

### Community 63 - "describe"
Cohesion: 0.15
Nodes (6): import_sources(), import_one(), describe(), log_failure(), reason(), DescribeTests

### Community 65 - "PrensaIbericaProvider"
Cohesion: 0.18
Nodes (3): _extract_href(), _get_modified_at(), PrensaIbericaProvider

### Community 68 - "GroupingTests"
Cohesion: 0.23
Nodes (4): GroupingOptions, EmbeddingGroupingTests, GroupingTests, RemixerTestCase

### Community 73 - "foundation internal library"
Cohesion: 0.29
Nodes (7): foundation internal library, foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section, P1: plain logging and <APP>_LOG_LEVEL fix, P2: rich progress per stream (RICH_STDOUT_*/RICH_STDERR_*)

### Community 75 - "Framework Usage"
Cohesion: 0.50
Nodes (3): Additional Approved Packages, Framework Usage, newstool Python Specifics

### Community 76 - "workflows"
Cohesion: 0.33
Nodes (6): sink, workflows, deliver, name, process, sources

### Community 79 - "post"
Cohesion: 0.20
Nodes (5): 0010: Plugin classes and the configuration catalog, Consequences, Context, Rejected options, post()

### Community 81 - ".content_dir"
Cohesion: 0.29
Nodes (3): Database & ORM Conventions, DTO, Protocol & ORM Implementation Reference, resolve_config_path()

### Community 83 - "0012: Delivery ids, changing their state and forced send"
Cohesion: 0.33
Nodes (5): 0012: Delivery ids, changing their state and forced send, Consequences, Context, Decision, Rejected options

### Community 85 - "SourceData"
Cohesion: 0.13
Nodes (4): DBSource, SourceData, CastellonInformacionProvider, IndexSiteProvider

### Community 90 - "0011: Environment overrides, relative paths and one storage directory"
Cohesion: 0.40
Nodes (4): 0011: Environment overrides, relative paths and one storage directory, Consequences, Context, Decision

### Community 91 - "parse_entry"
Cohesion: 0.60
Nodes (3): entry_date(), find_image(), parse_entry()

## Knowledge Gaps
- **13 isolated node(s):** `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)`, `IndexSiteProvider / URLProvider` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 515 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `make_item`, `db.py`, `Artifact`, `test_db.py`, `StubLLM`, `DeleteCommandTests`, `sinks.py`, `Delivery`, `Services`, `Any`, `TelegramSinkTests`, `migrate_autoincrement.py`, `ProcessingScope`, `grouping.py`, `migrate_telegram_state.py`, `.close`, `RecordingItemSink`, `Config`, `GoogleChatSinkTests`, `SourceItem`, `MarkdownifyProcessor`, `app.py`, `.feed`, `PluginFailure`, `GroupingTests`, `Application`, `DigestRemixer`, `post`, `SourceData`, `EmbedProcessor`, `.get_stored_content`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `catalog.py` be split into smaller, more focused modules?**
  _Cohesion score 0.059237319511292116 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `ProcessingScope` to `make_item`, `db.py`, `ApplicationTests`, `Artifact`, `test_db.py`, `StubLLM`, `DeleteCommandTests`, `run_cmd`, `invoke`, `app_from_context`, `sinks.py`, `Delivery`, `Services`, `cli.py`, `Database`, `report_user_errors`, `grouping.py`, `migrate_telegram_state.py`, `RecordingItemSink`, `AnnotationTests`, `._object`, `SourceItem`, `app.py`, `DeliveryTests`, `models.py`, `.feed`, `PluginFailure`, `GroupingTests`, `Application`, `DigestRemixer`, `GetItemsTests`, `search_cmd`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Should `db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._