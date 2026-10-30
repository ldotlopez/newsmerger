# Graph Report - newstool  (2026-10-30)

## Corpus Check
- 75 files · ~177,913 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1745 nodes · 4802 edges · 83 communities (54 shown, 29 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 580 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1c2fba72`
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
- migrate_autoincrement.py
- cli.py Click commands
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
- plugins/__init__.py
- run_cmd
- db.py
- Artifact
- report_user_errors
- ._profile
- PluginFailure
- BaseProcessor
- Markdownify Processor
- migrate_autoincrement.py
- .from_file
- ScoredItem
- cli.py
- CSJuntasGobiernoProvider
- SourceItemData
- AnnotationTests
- migrate
- .close
- .queue_item_deliveries
- ProcessingScope
- Architecture & Processing ADRs
- IndexSiteProvider
- Selection CLI Options
- telegram_channel.py
- Processor & Remixer Bundles
- ollama.py
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
- Workflow
- PrensaIbericaProvider
- test_markdownify.py
- Example Sources
- newsmerger CLAUDE.md agent guidelines
- Artifact & Remixer
- Grouping Notes
- setup_logging
- LogLevelTests
- Entry
- expand_variables
- __newsmerger_plugin__
- DigestRemixerTests
- 0009: Workflows and keyed entries
- 0011: Environment overrides, relative paths and one storage directory
- LogLevelTests
- ConfigError

## God Nodes (most connected - your core abstractions)
1. `ProcessingScope` - 145 edges
2. `SourceItem` - 122 edges
3. `Database` - 93 edges
4. `SourceData` - 80 edges
5. `Services` - 80 edges
6. `Application` - 66 edges
7. `Artifact` - 65 edges
8. `PluginFailure` - 63 edges
9. `ApplicationTests` - 58 edges
10. `SourceItemData` - 56 edges

## Surprising Connections (you probably didn't know these)
- `Decision` --references--> `Config`  [INFERRED]
  docs/decisions/0011-environment-overrides-and-storage-dir.md → newstool/config.py
- `Decision` --references--> `Application`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/app.py
- `Decision` --references--> `LLMType`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/llms.py
- `Framework Usage` --references--> `PluginOptions`  [INFERRED]
  .claude/rules/python.md → newstool/plugins/__init__.py
- `Decision` --references--> `UsesLLMOptions`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/plugins/__init__.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (83 total, 29 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.06
Nodes (17): 0012: Delivery ids, changing their state and forced send, Consequences, Context, Decision, Rejected options, DBSource, AnnotationTests, ConnectionTests (+9 more)

### Community 1 - "catalog.py"
Cohesion: 0.14
Nodes (7): ids_of(), in_default(), Kind, Use, DeliveryEntry, ProcessEntry, RemixEntry

### Community 2 - "test_app.py"
Cohesion: 0.10
Nodes (7): Alias, CacheConfig, backoff_seconds(), ProcessingStatus, _sha256_column(), Annotation, SourceData

### Community 3 - "test_cli.py"
Cohesion: 0.08
Nodes (7): ApplicationTests, retrieve(), retrieve_published(), retrieve(), same(), listed(), retrieved()

### Community 5 - "invoke"
Cohesion: 0.12
Nodes (5): RunSummary, annotation(), CommandTests, InspectCommandTests, invoke()

### Community 7 - "migrate_autoincrement.py"
Cohesion: 0.11
Nodes (10): HTTPClient, discover_feed_url(), entry_date(), FeedReaderProvider, fetch_article(), fetch_feed(), find_image(), parse_entry() (+2 more)

### Community 8 - "cli.py Click commands"
Cohesion: 0.23
Nodes (10): cli.py Click commands, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage, SQLAlchemy models never leave db.py; DTOs cross the boundary, foundation internal library, inspect items|annotations|artifacts|deliveries, Application class (single entry point), Phases: import, enrich, remix, deliver (+2 more)

### Community 9 - "LockedError"
Cohesion: 0.17
Nodes (6): Processor, EmbedTests, ProcessorTestCase, StubLLM, SummarizeTests, TaggerTests

### Community 10 - "DeleteCommandTests"
Cohesion: 0.09
Nodes (3): EnvAliasSource, LLMEntry, parse_duration()

### Community 11 - "inspect_deliveries_cmd"
Cohesion: 0.12
Nodes (13): format_value(), inspect_artifacts_cmd(), inspect_deliveries_cmd(), inspect_items_cmd(), json_default(), preview(), print_deliver(), print_item() (+5 more)

### Community 12 - "CSJuntasGobiernoProvider"
Cohesion: 0.27
Nodes (5): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, TestCSJuntasGobierno

### Community 14 - "app_from_context"
Cohesion: 0.12
Nodes (13): app_from_context(), cli(), delete_deliveries_cmd(), deliveries_queue_cmd(), deliveries_send_cmd(), deliveries_set_status_cmd(), delivery_filters(), inspect_content_cmd() (+5 more)

### Community 15 - "Artifact"
Cohesion: 0.09
Nodes (13): merge_options(), build_caption(), __newstool_plugin__(), post(), TelegramArtifactSink, TelegramSink, BuildCaptionTests, item_options() (+5 more)

### Community 16 - "BaseSink"
Cohesion: 0.07
Nodes (5): DeliveryStatus, Delivery, BaseArtifactSink, BaseItemSink, BaseSink

### Community 17 - "Telegram Channel Parsing"
Cohesion: 0.18
Nodes (6): is_home_page(), parse_article(), parse_preview(), Post, TelegramChannelProvider, TestTelegramChannel

### Community 18 - "Services"
Cohesion: 0.07
Nodes (21): DigestOptions, EmbedOptions, EmbedProcessor, __newstool_plugin__(), tags_text(), Services, UsesLLMOptions, __newstool_plugin__() (+13 more)

### Community 19 - "plugins/__init__.py"
Cohesion: 0.14
Nodes (3): LLM, LLMType, LLMUnavailableError

### Community 21 - "db.py"
Cohesion: 0.10
Nodes (6): Base, CustomJSON, DBItemAnnotation, DBProcessingState, _encode_value(), UTCDateTime

### Community 22 - "Artifact"
Cohesion: 0.10
Nodes (7): DBArtifact, Artifact, SelectionRequiredError, ArtifactTests, ArtifactSinkTests, RecordingArtifactSink, MigrateTelegramStateTests

### Community 23 - "report_user_errors"
Cohesion: 0.14
Nodes (12): annotation_options(), artifact_options(), check_found(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), delivery_options(), inspect_annotations_cmd() (+4 more)

### Community 24 - "._profile"
Cohesion: 0.12
Nodes (3): check_section(), Profile, options_error()

### Community 25 - "PluginFailure"
Cohesion: 0.07
Nodes (13): PluginFailure, select_article(), get_section(), parse_datetime(), PlazaProvider, merge_tags(), page_title(), DocumentDeliveryOptions (+5 more)

### Community 27 - "Markdownify Processor"
Cohesion: 0.21
Nodes (5): __newstool_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 28 - "migrate_autoincrement.py"
Cohesion: 0.17
Nodes (4): main(), migrate(), needs_autoincrement(), recreate()

### Community 30 - "ScoredItem"
Cohesion: 0.06
Nodes (25): FeedGeneratorRemixer, average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer (+17 more)

### Community 31 - "cli.py"
Cohesion: 0.10
Nodes (6): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content()

### Community 32 - "CSJuntasGobiernoProvider"
Cohesion: 0.13
Nodes (5): LockedError, write_lock(), main(), migrate(), main()

### Community 33 - "SourceItemData"
Cohesion: 0.22
Nodes (3): SourceItemData, Provider, TestPrensaIberica

### Community 34 - "AnnotationTests"
Cohesion: 0.12
Nodes (17): lookback, title, url, api_base, chat_model, embed_model, plugins, digest (+9 more)

### Community 36 - ".close"
Cohesion: 0.28
Nodes (3): ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 37 - ".queue_item_deliveries"
Cohesion: 0.15
Nodes (4): Database & ORM Conventions, DTO, Protocol & ORM Implementation Reference, Config, DirectoryTests

### Community 38 - "ProcessingScope"
Cohesion: 0.08
Nodes (7): wrapper(), DBDelivery, ProcessingScope, Remixer, Sink, SearchTests, DeliveryTests

### Community 39 - "Architecture & Processing ADRs"
Cohesion: 0.18
Nodes (14): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0002 Processing state lifecycle, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins (+6 more)

### Community 41 - "Selection CLI Options"
Cohesion: 0.15
Nodes (14): options, artifacts, chat_id, interval, item_image, item_url_preview, item_url_text, markdown (+6 more)

### Community 42 - "telegram_channel.py"
Cohesion: 0.15
Nodes (12): exclude, args, entry, files, id, language, name, pass_filenames (+4 more)

### Community 43 - "Processor & Remixer Bundles"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "ollama.py"
Cohesion: 0.05
Nodes (19): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options, 0010: Plugin classes and the configuration catalog, Consequences, Context (+11 more)

### Community 45 - "Plugin System Docs"
Cohesion: 0.11
Nodes (15): cache, expiration, llms, input, processors, options, processor, remixers (+7 more)

### Community 50 - ".__init__"
Cohesion: 0.16
Nodes (5): MarkdownifyProcessor, SkipItem, ClassRegisterTests, make_pdf(), MarkdownifyPdfTests

### Community 51 - "load_context"
Cohesion: 0.18
Nodes (4): load_context(), LoadContext, LoadEnvSettingsSource, resolve_config_path()

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
Cohesion: 0.11
Nodes (15): __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), Options, NoOptions, PluginOptions, __newstool_plugin__(), __newstool_plugin__() (+7 more)

### Community 60 - "digest.py"
Cohesion: 0.08
Nodes (11): Decision, strip_code_fence(), DigestRemixer, __newstool_plugin__(), __newstool_plugin__(), Options, __newstool_plugin__(), ClassRegister (+3 more)

### Community 61 - "Item Identity ADR"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 63 - "run_cmd"
Cohesion: 0.11
Nodes (10): import_cmd(), import_sources(), import_one(), print_import(), progress_rows(), run_cmd(), run_each(), describe() (+2 more)

### Community 65 - "PrensaIbericaProvider"
Cohesion: 0.14
Nodes (4): _extract_href(), _get_modified_at(), PrensaIbericaProvider, read_sample()

### Community 68 - "newsmerger CLAUDE.md agent guidelines"
Cohesion: 0.33
Nodes (5): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention

### Community 71 - "setup_logging"
Cohesion: 0.33
Nodes (4): Additional Approved Packages, Framework Usage, newstool Python Specifics, setup_logging()

### Community 73 - "LogLevelTests"
Cohesion: 0.50
Nodes (4): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section

### Community 76 - "__newsmerger_plugin__"
Cohesion: 0.33
Nodes (6): sink, workflows, deliver, name, process, sources

### Community 79 - "0011: Environment overrides, relative paths and one storage directory"
Cohesion: 0.40
Nodes (4): 0011: Environment overrides, relative paths and one storage directory, Consequences, Context, Decision

### Community 85 - "ConfigError"
Cohesion: 0.12
Nodes (5): lookup(), Catalog, Run, share_sources(), ConfigError

## Knowledge Gaps
- **13 isolated node(s):** `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)`, `IndexSiteProvider / URLProvider` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 520 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ProcessingScope` connect `ProcessingScope` to `test_db.py`, `test_app.py`, `test_cli.py`, `invoke`, `LockedError`, `inspect_deliveries_cmd`, `ProcessingScope`, `app_from_context`, `BaseSink`, `Services`, `Artifact`, `report_user_errors`, `BaseProcessor`, `ScoredItem`, `cli.py`, `migrate`, `.close`, `Application`, `SourceItem`, `digest.py`, `DigestRemixerTests`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06199285946121389 - nodes in this community are weakly interconnected._
- **Why does `Database` connect `BaseProcessor` to `test_db.py`, `test_app.py`, `LockedError`, `ProcessingScope`, `Artifact`, `BaseSink`, `Services`, `plugins/__init__.py`, `run_cmd`, `db.py`, `Artifact`, `ScoredItem`, `CSJuntasGobiernoProvider`, `migrate`, `.close`, `.queue_item_deliveries`, `ProcessingScope`, `ollama.py`, `Application`, `SourceItem`, `.send`, `.get_content`, `DigestRemixerTests`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `SourceItem` (e.g. with `Application` and `print_item()`) actually correct?**
  _`SourceItem` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Should `catalog.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13675213675213677 - nodes in this community are weakly interconnected._