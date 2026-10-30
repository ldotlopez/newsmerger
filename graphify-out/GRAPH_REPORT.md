# Graph Report - deliveries-queue  (2026-10-30)

## Corpus Check
- 75 files · ~147,023 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 4, .lock 1)

## Summary
- 1739 nodes · 4925 edges · 74 communities (53 shown, 21 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 634 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e5ae09f5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- make_item
- catalog.py
- db.py
- ApplicationTests
- BaseProcessor
- Artifact
- .from_text
- feedreader.py
- Database (db.py, only SQLite/storage access)
- StubLLM
- Any
- run_cmd
- CSJuntasGobiernoProvider
- invoke
- app_from_context
- telegram.py
- DeliveryStatus
- test_providers.py
- Services
- tagger.py
- LLM
- .get_annotation_values
- ClassRegister
- DBSource
- Workflow
- HTTPClient
- Database
- OllamaLLM
- ConsumerPluginTests
- _sha256_column
- grouping.py
- cli.py
- migrate_telegram_state.py
- ADR 0002 Processing state lifecycle
- plugins
- RecordingItemSink
- Config
- ADR 0007 Sinks and the delivery ledger
- options
- hooks
- Services object (services.llm(name))
- GoogleChatSinkTests
- config.example.yaml
- Application
- Database
- SourceItemData
- MarkdownifyProcessor
- config.py
- newstool
- Processor
- El Periódico Mediterráneo
- .settings_customise_sources
- deliveries table (the ledger)
- PluginFailure
- feedgenerator.py
- Item
- Remixer
- describe
- PreflightSourceItemData
- TestFeedReader
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- Artifact
- Grouping notes: NLP clustering pipeline
- ExternalErrorTests
- foundation internal library
- workflows
- DigestRemixer
- LogLevelTests
- ConfigError

## God Nodes (most connected - your core abstractions)
1. `Database` - 160 edges
2. `ProcessingScope` - 145 edges
3. `SourceItem` - 120 edges
4. `SourceData` - 80 edges
5. `Services` - 77 edges
6. `Application` - 66 edges
7. `Artifact` - 65 edges
8. `PluginFailure` - 64 edges
9. `ApplicationTests` - 58 edges
10. `SourceItemData` - 56 edges

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

## Communities (74 total, 21 thin omitted)

### Community 0 - "make_item"
Cohesion: 0.05
Nodes (18): 0012: Delivery ids, changing their state and forced send, Consequences, Context, Decision, Rejected options, DBDelivery, AnnotationTests, ConnectionTests (+10 more)

### Community 1 - "catalog.py"
Cohesion: 0.07
Nodes (12): Catalog, ids_of(), in_default(), Kind, Profile, Run, share_sources(), Use (+4 more)

### Community 2 - "db.py"
Cohesion: 0.11
Nodes (7): backoff_seconds(), DeliveryStatus, ProcessingStatus, Annotation, SourceData, GoogleChatSink, SinkTestCase

### Community 3 - "ApplicationTests"
Cohesion: 0.08
Nodes (7): ApplicationTests, retrieve(), retrieve_published(), retrieve(), same(), listed(), retrieved()

### Community 4 - "BaseProcessor"
Cohesion: 0.08
Nodes (9): EmbedOptions, EmbedProcessor, __newstool_plugin__(), tags_text(), __newstool_plugin__(), SummarizeProcessor, BaseProcessor, Processor (+1 more)

### Community 5 - "Artifact"
Cohesion: 0.05
Nodes (7): DBArtifact, Artifact, ArtifactTests, DeleteCommandTests, MigrateFeedNamesTests, ArtifactSinkTests, RecordingArtifactSink

### Community 6 - ".from_text"
Cohesion: 0.08
Nodes (3): AliasTests, ConfigTests, EnvironmentOverrideTests

### Community 7 - "feedreader.py"
Cohesion: 0.18
Nodes (10): discover_feed_url(), entry_date(), FeedReaderProvider, fetch_article(), fetch_feed(), find_image(), __newstool_plugin__(), parse_entry() (+2 more)

### Community 8 - "Database (db.py, only SQLite/storage access)"
Cohesion: 0.17
Nodes (11): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention, AUTOINCREMENT integer ids, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage (+3 more)

### Community 9 - "StubLLM"
Cohesion: 0.23
Nodes (4): build(), EmbedTests, StubLLM, SummarizeTests

### Community 11 - "run_cmd"
Cohesion: 0.15
Nodes (6): print_deliver(), print_process(), print_remix(), progress_rows(), run_cmd(), run_each()

### Community 12 - "CSJuntasGobiernoProvider"
Cohesion: 0.23
Nodes (6): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, NoOptions, TestCSJuntasGobierno

### Community 13 - "invoke"
Cohesion: 0.11
Nodes (9): wrapper(), ProcessingScope, RunSummary, Sink, annotation(), CommandTests, InspectCommandTests, invoke() (+1 more)

### Community 14 - "app_from_context"
Cohesion: 0.09
Nodes (29): annotation_options(), app_from_context(), artifact_options(), check_found(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_deliveries_cmd(), delete_items_cmd() (+21 more)

### Community 15 - "telegram.py"
Cohesion: 0.06
Nodes (19): merge_options(), build_caption(), DocumentDeliveryOptions, ItemDeliveryOptions, __newstool_plugin__(), post(), TelegramArtifactSink, TelegramSink (+11 more)

### Community 16 - "DeliveryStatus"
Cohesion: 0.09
Nodes (3): Delivery, BaseArtifactSink, BaseSink

### Community 17 - "test_providers.py"
Cohesion: 0.12
Nodes (11): Options, PluginOptions, Options, is_home_page(), Options, parse_preview(), Post, preview_url() (+3 more)

### Community 18 - "Services"
Cohesion: 0.13
Nodes (6): LLMUnavailableError, Services, SummarizeOptions, factory(), ServicesTests, factory()

### Community 19 - "tagger.py"
Cohesion: 0.24
Nodes (4): strip_code_fence(), merge_tags(), __newstool_plugin__(), TaggerProcessor

### Community 21 - ".get_annotation_values"
Cohesion: 0.12
Nodes (4): _configure_sqlite_connection(), CustomJSON, _encode_value(), UTCDateTime

### Community 25 - "HTTPClient"
Cohesion: 0.11
Nodes (6): HTTPClient, CastellonInformacionProvider, PlazaProvider, TheGuardianProvider, IndexSiteProvider, TestHTTPClient

### Community 26 - "Database"
Cohesion: 0.06
Nodes (3): Database, BaseItemSink, migrate()

### Community 27 - "OllamaLLM"
Cohesion: 0.20
Nodes (5): __newstool_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 30 - "grouping.py"
Cohesion: 0.05
Nodes (27): FeedGeneratorRemixer, average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer (+19 more)

### Community 31 - "cli.py"
Cohesion: 0.05
Nodes (18): Additional Approved Packages, Framework Usage, newstool Python Specifics, cli(), delete_group(), deliveries_group(), format_value(), inspect_group() (+10 more)

### Community 32 - "migrate_telegram_state.py"
Cohesion: 0.09
Nodes (9): LockedError, write_lock(), main(), migrate(), needs_autoincrement(), recreate(), main(), migrate() (+1 more)

### Community 34 - "plugins"
Cohesion: 0.12
Nodes (17): lookback, title, url, api_base, chat_model, embed_model, plugins, digest (+9 more)

### Community 36 - "RecordingItemSink"
Cohesion: 0.29
Nodes (3): SelectionRequiredError, ItemSinkTests, RecordingItemSink

### Community 37 - "Config"
Cohesion: 0.10
Nodes (7): 0011: Environment overrides, relative paths and one storage directory, Consequences, Context, Decision, Config, EnvAliasSource, DirectoryTests

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.21
Nodes (14): Architecture, cli.py Click commands, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger (+6 more)

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
Nodes (9): build_card(), chat_image_url(), __newstool_plugin__(), WebhookOptions, card_widgets(), ChatImageUrlTests, GoogleChatSinkTests, OptionsTests (+1 more)

### Community 45 - "config.example.yaml"
Cohesion: 0.11
Nodes (15): cache, expiration, llms, input, processors, options, processor, remixers (+7 more)

### Community 46 - "Application"
Cohesion: 0.05
Nodes (3): Application, workflow_scope(), import_sources()

### Community 47 - "Database"
Cohesion: 0.10
Nodes (9): Base, DBItemAnnotation, DBProcessingState, DBSourceItem, SourceItem, ProcessorTestCase, TaggerTests, make_item() (+1 more)

### Community 48 - "SourceItemData"
Cohesion: 0.10
Nodes (5): SourceItemData, PreflightProvider, Provider, TestPrensaIberica, TestSourceItemDataContent

### Community 50 - "MarkdownifyProcessor"
Cohesion: 0.14
Nodes (8): MarkdownifyProcessor, __newstool_plugin__(), TaggerOptions, ProcessorOptions, SkipItem, ClassRegisterTests, make_pdf(), MarkdownifyPdfTests

### Community 51 - "config.py"
Cohesion: 0.11
Nodes (6): Alias, CacheConfig, expand_variables(), MissingVariableError, ollama_url(), parse_duration()

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 57 - ".settings_customise_sources"
Cohesion: 0.12
Nodes (6): Database & ORM Conventions, DTO, Protocol & ORM Implementation Reference, load_context(), LoadContext, LoadEnvSettingsSource, resolve_config_path()

### Community 58 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 59 - "PluginFailure"
Cohesion: 0.10
Nodes (12): PluginFailure, __newstool_plugin__(), __newstool_plugin__(), get_section(), __newstool_plugin__(), parse_datetime(), __newstool_plugin__(), __newstool_plugin__() (+4 more)

### Community 60 - "feedgenerator.py"
Cohesion: 0.13
Nodes (9): Decision, DigestOptions, __newstool_plugin__(), __newstool_plugin__(), Options, UsesLLMOptions, BaseRemixer, RemixerType (+1 more)

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 63 - "describe"
Cohesion: 0.11
Nodes (6): import_one(), describe(), log_failure(), reason(), DescribeTests, LogFailureTests

### Community 65 - "PreflightSourceItemData"
Cohesion: 0.15
Nodes (4): PreflightSourceItemData, _extract_href(), _get_modified_at(), PrensaIbericaProvider

### Community 73 - "foundation internal library"
Cohesion: 0.29
Nodes (7): foundation internal library, foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section, P1: plain logging and <APP>_LOG_LEVEL fix, P2: rich progress per stream (RICH_STDOUT_*/RICH_STDERR_*)

### Community 76 - "workflows"
Cohesion: 0.33
Nodes (6): sink, workflows, deliver, name, process, sources

### Community 77 - "DigestRemixer"
Cohesion: 0.09
Nodes (11): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options, 0010: Plugin classes and the configuration catalog, Consequences, Context (+3 more)

### Community 84 - "ConfigError"
Cohesion: 0.15
Nodes (4): lookup(), check_section(), ConfigError, options_error()

## Knowledge Gaps
- **13 isolated node(s):** `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)`, `IndexSiteProvider / URLProvider` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 518 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `make_item`, `db.py`, `BaseProcessor`, `Artifact`, `invoke`, `telegram.py`, `DeliveryStatus`, `tagger.py`, `.get_annotation_values`, `ClassRegister`, `DBSource`, `grouping.py`, `migrate_telegram_state.py`, `RecordingItemSink`, `GoogleChatSinkTests`, `Application`, `Database`, `MarkdownifyProcessor`, `PluginFailure`, `feedgenerator.py`, `Remixer`, `DigestRemixer`, `.get_content`?**
  _High betweenness centrality (0.179) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `make_item` be split into smaller, more focused modules?**
  _Cohesion score 0.05132317562149158 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `invoke` to `make_item`, `db.py`, `ApplicationTests`, `BaseProcessor`, `Artifact`, `RecordingItemSink`, `DigestRemixer`, `app_from_context`, `Application`, `DeliveryStatus`, `telegram.py`, `Remixer`, `Database`, `PluginFailure`, `feedgenerator.py`, `grouping.py`, `cli.py`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Should `catalog.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07401129943502825 - nodes in this community are weakly interconnected._