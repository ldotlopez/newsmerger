# Graph Report - delete-deliveries-all  (2026-10-30)

## Corpus Check
- 75 files · ~147,089 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 4, .lock 1)

## Summary
- 1740 nodes · 4930 edges · 82 communities (54 shown, 28 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 635 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6a5196e7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- make_item
- catalog.py
- db.py
- ApplicationTests
- Database
- Artifact
- .from_text
- HTTPClient
- Database (db.py, only SQLite/storage access)
- StubLLM
- Any
- run_cmd
- test_providers.py
- DeleteCommandTests
- app_from_context
- TelegramSinkTests
- DeliveryStatus
- TelegramChannelProvider
- Services
- plugins/__init__.py
- .close
- .record_result
- ClassRegister
- Base
- test_llm.py
- SourceData
- LLM
- test_db.py
- grouping.py
- cli.py
- migrate_autoincrement.py
- ADR 0002 Processing state lifecycle
- plugins
- .get_artifact
- RecordingItemSink
- Config
- DeliveryTests
- ADR 0007 Sinks and the delivery ledger
- ProcessingTests
- options
- hooks
- Services object (services.llm(name))
- GoogleChatSinkTests
- config.example.yaml
- ProcessingScope
- SourceItem
- PreflightProvider
- markdownify.py
- config.py
- AnnotationTests
- newstool
- Processor
- El Periódico Mediterráneo
- SinkType
- chat_image_url
- deliveries table (the ledger)
- telegram_channel.py
- feedgenerator.py
- Item
- .__init__
- describe
- 0012: Delivery ids, changing their state and forced send
- SourceItemData
- TestFeedReader
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- migrate
- Artifact
- Grouping notes: NLP clustering pipeline
- GetItemsTests
- foundation internal library
- build_caption
- workflows
- DigestRemixerTests
- TestSourceItemDataContent
- LogLevelTests

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
- `Framework Usage` --references--> `setup_logging()`  [INFERRED]
  .claude/rules/python.md → newstool/cli.py
- `Decision` --references--> `Config`  [INFERRED]
  docs/decisions/0011-environment-overrides-and-storage-dir.md → newstool/config.py
- `Decision` --references--> `LLMType`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/llms.py
- `Decision` --references--> `UsesLLMOptions`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newstool/plugins/__init__.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (82 total, 28 thin omitted)

### Community 0 - "make_item"
Cohesion: 0.24
Nodes (4): ContentStorageTests, make_item(), make_source(), UpsertSourceItemsTests

### Community 1 - "catalog.py"
Cohesion: 0.07
Nodes (14): Catalog, check_section(), ids_of(), in_default(), Kind, Profile, Run, share_sources() (+6 more)

### Community 2 - "db.py"
Cohesion: 0.14
Nodes (3): ProcessingStatus, _sha256_column(), Annotation

### Community 3 - "ApplicationTests"
Cohesion: 0.08
Nodes (7): ApplicationTests, retrieve(), retrieve_published(), retrieve(), same(), listed(), retrieved()

### Community 4 - "Database"
Cohesion: 0.11
Nodes (7): Database, EmbedProcessor, tags_text(), SummarizeProcessor, merge_tags(), TaggerProcessor, BaseProcessor

### Community 5 - "Artifact"
Cohesion: 0.06
Nodes (9): DBArtifact, Artifact, annotation(), ExternalErrorTests, InspectCommandTests, invoke(), ArtifactTests, ArtifactSinkTests (+1 more)

### Community 6 - ".from_text"
Cohesion: 0.08
Nodes (3): AliasTests, ConfigTests, EnvironmentOverrideTests

### Community 7 - "HTTPClient"
Cohesion: 0.13
Nodes (10): HTTPClient, discover_feed_url(), entry_date(), FeedReaderProvider, fetch_article(), fetch_feed(), find_image(), parse_entry() (+2 more)

### Community 8 - "Database (db.py, only SQLite/storage access)"
Cohesion: 0.17
Nodes (11): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention, AUTOINCREMENT integer ids, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage (+3 more)

### Community 9 - "StubLLM"
Cohesion: 0.14
Nodes (6): build(), ConsumerPluginTests, EmbedTests, StubLLM, SummarizeTests, TaggerTests

### Community 11 - "run_cmd"
Cohesion: 0.15
Nodes (7): import_sources(), print_deliver(), print_process(), print_remix(), progress_rows(), run_cmd(), run_each()

### Community 12 - "test_providers.py"
Cohesion: 0.12
Nodes (13): Additional Approved Packages, Framework Usage, newstool Python Specifics, CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, Options (+5 more)

### Community 14 - "app_from_context"
Cohesion: 0.09
Nodes (28): annotation_options(), app_from_context(), artifact_options(), check_found(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_deliveries_cmd(), delete_items_cmd() (+20 more)

### Community 15 - "TelegramSinkTests"
Cohesion: 0.13
Nodes (10): merge_options(), __newstool_plugin__(), TelegramArtifactSink, TelegramSink, item_options(), ok_response(), PluginTests, TelegramArtifactSinkTests (+2 more)

### Community 16 - "DeliveryStatus"
Cohesion: 0.07
Nodes (5): DeliveryStatus, Delivery, BaseArtifactSink, BaseItemSink, BaseSink

### Community 17 - "TelegramChannelProvider"
Cohesion: 0.16
Nodes (7): is_home_page(), parse_article(), parse_preview(), Post, preview_url(), TelegramChannelProvider, TestTelegramChannel

### Community 18 - "Services"
Cohesion: 0.12
Nodes (12): DigestOptions, DigestRemixer, EmbedOptions, Services, UsesLLMOptions, SummarizeOptions, TaggerOptions, ProcessorOptions (+4 more)

### Community 19 - "plugins/__init__.py"
Cohesion: 0.13
Nodes (6): backoff_seconds(), strip_code_fence(), DocumentDeliveryOptions, ItemDeliveryOptions, ArtifactDeliveryOptions, DeliveryOptions

### Community 21 - ".record_result"
Cohesion: 0.11
Nodes (3): CustomJSON, _encode_value(), UTCDateTime

### Community 23 - "Base"
Cohesion: 0.20
Nodes (4): Base, DBItemAnnotation, DBProcessingState, DBSource

### Community 24 - "test_llm.py"
Cohesion: 0.12
Nodes (7): LLMUnavailableError, __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), Processor, ProcessorType, ServicesTests

### Community 25 - "SourceData"
Cohesion: 0.10
Nodes (9): PluginFailure, SourceData, CastellonInformacionProvider, get_section(), parse_datetime(), PlazaProvider, page_title(), TheGuardianProvider (+1 more)

### Community 27 - "LLM"
Cohesion: 0.11
Nodes (7): LLM, LLMType, __newstool_plugin__(), ollama_client(), OllamaLLM, Options, OllamaTests

### Community 28 - "test_db.py"
Cohesion: 0.17
Nodes (5): DBSourceItem, ConnectionTests, DatabaseTestCase, DeleteTests, IdentityTests

### Community 30 - "grouping.py"
Cohesion: 0.06
Nodes (26): Options, average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer (+18 more)

### Community 31 - "cli.py"
Cohesion: 0.06
Nodes (16): cli(), delete_group(), deliveries_group(), format_value(), inspect_group(), json_default(), lexer_for(), match_snippet() (+8 more)

### Community 32 - "migrate_autoincrement.py"
Cohesion: 0.09
Nodes (9): LockedError, write_lock(), main(), migrate(), needs_autoincrement(), recreate(), main(), migrate() (+1 more)

### Community 34 - "plugins"
Cohesion: 0.12
Nodes (17): lookback, title, url, api_base, chat_model, embed_model, plugins, digest (+9 more)

### Community 36 - "RecordingItemSink"
Cohesion: 0.31
Nodes (3): ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 37 - "Config"
Cohesion: 0.08
Nodes (9): Database & ORM Conventions, DTO, Protocol & ORM Implementation Reference, 0011: Environment overrides, relative paths and one storage directory, Consequences, Context, Decision, Config, Workflow (+1 more)

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
Cohesion: 0.12
Nodes (7): GoogleChatSink, __newstool_plugin__(), WebhookOptions, card_widgets(), GoogleChatSinkTests, OptionsTests, webhook_options()

### Community 45 - "config.example.yaml"
Cohesion: 0.11
Nodes (15): cache, expiration, llms, input, processors, options, processor, remixers (+7 more)

### Community 46 - "ProcessingScope"
Cohesion: 0.06
Nodes (10): Application, lookup(), workflow_scope(), wrapper(), select_deliveries(), ProcessingScope, RunSummary, Sink (+2 more)

### Community 47 - "SourceItem"
Cohesion: 0.11
Nodes (4): SourceItem, FeedGeneratorRemixer, SearchTests, ProcessorTestCase

### Community 50 - "markdownify.py"
Cohesion: 0.16
Nodes (6): MarkdownifyProcessor, __newstool_plugin__(), SkipItem, ClassRegisterTests, make_pdf(), MarkdownifyPdfTests

### Community 51 - "config.py"
Cohesion: 0.06
Nodes (12): Alias, CacheConfig, EnvAliasSource, expand_variables(), load_context(), LoadContext, LoadEnvSettingsSource, MissingVariableError (+4 more)

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 56 - "SinkType"
Cohesion: 0.22
Nodes (6): 0010: Plugin classes and the configuration catalog, Consequences, Context, Decision, Rejected options, SinkType

### Community 57 - "chat_image_url"
Cohesion: 0.29
Nodes (3): build_card(), chat_image_url(), ChatImageUrlTests

### Community 58 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 59 - "telegram_channel.py"
Cohesion: 0.15
Nodes (9): __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), __newstool_plugin__(), BaseProvider (+1 more)

### Community 60 - "feedgenerator.py"
Cohesion: 0.15
Nodes (5): __newstool_plugin__(), __newstool_plugin__(), Remixer, RemixerType, GroupingPluginTests

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 63 - "describe"
Cohesion: 0.11
Nodes (6): import_one(), describe(), log_failure(), reason(), DescribeTests, LogFailureTests

### Community 64 - "0012: Delivery ids, changing their state and forced send"
Cohesion: 0.33
Nodes (5): 0012: Delivery ids, changing their state and forced send, Consequences, Context, Decision, Rejected options

### Community 65 - "SourceItemData"
Cohesion: 0.10
Nodes (7): PreflightSourceItemData, SourceItemData, _extract_href(), _get_modified_at(), PrensaIbericaProvider, read_sample(), TestPrensaIberica

### Community 73 - "foundation internal library"
Cohesion: 0.29
Nodes (7): foundation internal library, foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section, P1: plain logging and <APP>_LOG_LEVEL fix, P2: rich progress per stream (RICH_STDOUT_*/RICH_STDERR_*)

### Community 76 - "workflows"
Cohesion: 0.33
Nodes (6): sink, workflows, deliver, name, process, sources

### Community 77 - "DigestRemixerTests"
Cohesion: 0.19
Nodes (6): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options, DigestRemixerTests

## Knowledge Gaps
- **13 isolated node(s):** `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)`, `IndexSiteProvider / URLProvider` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 518 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `make_item`, `db.py`, `Artifact`, `DeleteCommandTests`, `TelegramSinkTests`, `DeliveryStatus`, `Services`, `plugins/__init__.py`, `.close`, `.record_result`, `test_llm.py`, `SourceData`, `.session_scope`, `test_db.py`, `.get_annotation_values`, `grouping.py`, `migrate_autoincrement.py`, `.get_artifact`, `RecordingItemSink`, `Config`, `GoogleChatSinkTests`, `ProcessingScope`, `SourceItem`, `markdownify.py`, `feedgenerator.py`, `.__init__`, `migrate`, `DigestRemixerTests`?**
  _High betweenness centrality (0.179) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 42 INFERRED edges - model-reasoned connections that need verification._
- **What connects `newstool`, `External pipelines (scripts/pipeline_url.py)`, `Annotation` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `catalog.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06829488919041157 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `ProcessingScope` to `make_item`, `db.py`, `ApplicationTests`, `Database`, `Artifact`, `StubLLM`, `DeleteCommandTests`, `app_from_context`, `DeliveryStatus`, `Services`, `plugins/__init__.py`, `.close`, `test_llm.py`, `test_db.py`, `.get_annotation_values`, `grouping.py`, `cli.py`, `RecordingItemSink`, `DeliveryTests`, `SourceItem`, `AnnotationTests`, `feedgenerator.py`, `migrate`, `GetItemsTests`, `DigestRemixerTests`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Are the 42 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Should `db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13636363636363635 - nodes in this community are weakly interconnected._