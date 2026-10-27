# Graph Report - telegram-original-url-options  (2026-10-27)

## Corpus Check
- 68 files · ~119,125 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1448 nodes · 4275 edges · 72 communities (49 shown, 23 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 584 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9a0ff5c1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- make_item
- embed.py
- test_db.py
- .from_text
- ApplicationTests
- Artifact
- Application
- migrate_autoincrement.py
- merge_options
- ollama.py
- .session_scope
- Context
- __newsmerger_plugin__
- ProcessingScope
- process_cmd
- Sink
- BaseSink
- TelegramChannelProvider
- DeliveryStatus
- TestFeedReader
- single_link_groups
- .get_annotation_values
- SourceItem
- .record_result
- .require_annotation
- SourceData
- BaseProcessor
- markdownify.py
- PrensaIbericaPlainProvider
- cli.py Click commands
- Options
- telegram_channel.py
- csjuntasgobierno.py
- __newsmerger_plugin__
- backoff_seconds
- BaseRemixer
- test_sinks.py
- 0009: Workflows and keyed entries
- config.py
- ADR 0007 Sinks and the delivery ledger
- .__init__
- command
- ProcessorTestCase
- Services object (services.llm(name))
- test_llm.py
- config.example.yaml
- app.py
- test_app.py
- OptionsTests
- cli.py
- summarize.py
- inspect_items_cmd
- Processor
- El Periódico Mediterráneo
- Config
- plaza.py
- newsmerger CLAUDE.md agent guidelines
- StubLLM
- deliveries table (the ledger)
- ADR 0001 Item identity and change detection
- ScoredItem
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- EmbeddingGroupingTests
- Artifact
- Grouping notes: NLP clustering pipeline
- news-aggregator
- LogLevelTests
- GroupingRemixer
- ADR 0002 Processing state lifecycle
- TestSourceItemDataContent

## God Nodes (most connected - your core abstractions)
1. `Database` - 161 edges
2. `ProcessingScope` - 142 edges
3. `SourceItem` - 119 edges
4. `SourceData` - 81 edges
5. `Artifact` - 62 edges
6. `Services` - 61 edges
7. `Application` - 59 edges
8. `SourceItemData` - 49 edges
9. `PluginOptions` - 49 edges
10. `ApplicationTests` - 48 edges

## Surprising Connections (you probably didn't know these)
- `newsmerger README` --references--> `Phases: import, enrich, remix, deliver`  [INFERRED]
  README.md → docs/SPECIFICATION.md
- `main()` --uses--> `LockedError`  [INFERRED]
  scripts/migrate_autoincrement.py → newsmerger/app.py
- `ApplicationTests` --uses--> `LockedError`  [INFERRED]
  tests/test_app.py → newsmerger/app.py
- `ApplicationTests` --uses--> `Application`  [INFERRED]
  tests/test_app.py → newsmerger/app.py
- `invoke()` --indirect_call--> `cli()`  [INFERRED]
  tests/test_cli.py → newsmerger/cli.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (72 total, 23 thin omitted)

### Community 0 - "make_item"
Cohesion: 0.07
Nodes (13): DBProcessingState, DBSourceItem, AnnotationTests, ConnectionTests, ContentStorageTests, DatabaseTestCase, DeleteTests, GetItemsTests (+5 more)

### Community 1 - "embed.py"
Cohesion: 0.15
Nodes (4): __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), UnavailableProcessor

### Community 2 - "test_db.py"
Cohesion: 0.08
Nodes (10): _sha256_column(), LLM, LLMUnavailableError, strip_code_fence(), Options, NoOptions, PluginOptions, Services (+2 more)

### Community 4 - "ApplicationTests"
Cohesion: 0.07
Nodes (5): __newsmerger_plugin__(), ollama_client(), OllamaLLM, ApplicationTests, OllamaTests

### Community 5 - "Artifact"
Cohesion: 0.05
Nodes (25): DBArtifact, Artifact, build_text(), build_caption(), DocumentDeliveryOptions, ItemDeliveryOptions, __newsmerger_plugin__(), Options (+17 more)

### Community 7 - "migrate_autoincrement.py"
Cohesion: 0.11
Nodes (8): Base, DBItemAnnotation, main(), migrate(), needs_autoincrement(), recreate(), make_item(), MigrateAutoincrementTests

### Community 8 - "merge_options"
Cohesion: 0.14
Nodes (5): FeedReaderProvider, __newsmerger_plugin__(), Options, merge_options(), __newsmerger_plugin__()

### Community 9 - "ollama.py"
Cohesion: 0.23
Nodes (3): FeedGeneratorTests, GroupingTests, RemixerTestCase

### Community 11 - "Context"
Cohesion: 0.16
Nodes (9): app_from_context(), cli(), deliver_cmd(), inspect_content_cmd(), inspect_deliveries_cmd(), parse_artifact_ids(), process_cmd(), resolve_cmd() (+1 more)

### Community 13 - "ProcessingScope"
Cohesion: 0.06
Nodes (12): workflow_scope(), wrapper(), Annotation, ProcessingScope, RunSummary, annotation(), CommandTests, InspectCommandTests (+4 more)

### Community 14 - "process_cmd"
Cohesion: 0.15
Nodes (8): import_cmd(), import_sources(), print_import(), print_remix(), progress_rows(), remix_cmd(), run_cmd(), run_each()

### Community 15 - "Sink"
Cohesion: 0.09
Nodes (13): delivery_runs(), entry_location(), load_plugins(), lookup(), objects_by_name(), process_runs(), remix_runs(), Run (+5 more)

### Community 17 - "TelegramChannelProvider"
Cohesion: 0.10
Nodes (12): SourceItemData, PrensaIbericaProvider, Options, page_title(), parse_article(), parse_preview(), Post, preview_url() (+4 more)

### Community 18 - "DeliveryStatus"
Cohesion: 0.10
Nodes (5): DeliveryStatus, Delivery, BaseItemSink, migrate(), GoogleChatSinkTests

### Community 21 - ".get_annotation_values"
Cohesion: 0.10
Nodes (4): _configure_sqlite_connection(), CustomJSON, _encode_value(), UTCDateTime

### Community 22 - "SourceItem"
Cohesion: 0.10
Nodes (3): SourceItem, FeedGeneratorRemixer, Options

### Community 25 - "SourceData"
Cohesion: 0.06
Nodes (12): DBSource, HTTPClient, SourceData, CastellonInformacionProvider, __newsmerger_plugin__(), discover_feed_url(), fetch_article(), fetch_feed() (+4 more)

### Community 27 - "markdownify.py"
Cohesion: 0.22
Nodes (5): MarkdownifyProcessor, __newsmerger_plugin__(), SkipItem, make_pdf(), MarkdownifyPdfTests

### Community 28 - "PrensaIbericaPlainProvider"
Cohesion: 0.15
Nodes (3): _extract_href(), __newsmerger_plugin__(), PrensaIbericaPlainProvider

### Community 29 - "cli.py Click commands"
Cohesion: 0.23
Nodes (10): cli.py Click commands, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage, SQLAlchemy models never leave db.py; DTOs cross the boundary, foundation internal library, inspect items|annotations|artifacts|deliveries, Application class (single entry point), Phases: import, enrich, remix, deliver (+2 more)

### Community 31 - "telegram_channel.py"
Cohesion: 0.18
Nodes (6): entry_date(), find_image(), parse_entry(), __newsmerger_plugin__(), __newsmerger_plugin__(), Provider

### Community 32 - "csjuntasgobierno.py"
Cohesion: 0.18
Nodes (6): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), __newsmerger_plugin__(), PreparseData, TestCSJuntasGobierno

### Community 33 - "__newsmerger_plugin__"
Cohesion: 0.19
Nodes (3): __newsmerger_plugin__(), UnavailableRemixer, DigestPluginTests

### Community 35 - "BaseRemixer"
Cohesion: 0.19
Nodes (3): DigestOptions, DigestRemixer, BaseRemixer

### Community 36 - "test_sinks.py"
Cohesion: 0.08
Nodes (6): DBDelivery, DeliveryOptions, SelectionRequiredError, ItemSinkTests, RecordingItemSink, SinkTestCase

### Community 37 - "0009: Workflows and keyed entries"
Cohesion: 0.19
Nodes (6): check_found(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), require_selection(), sort_option()

### Community 38 - "config.py"
Cohesion: 0.08
Nodes (7): CacheConfig, DatabaseConfig, DeliveryEntry, expand_variables(), MissingVariableError, ProcessEntry, RemixEntry

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.23
Nodes (12): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins, ADR 0007 Sinks and the delivery ledger, deliver SINK --force with explicit selection (+4 more)

### Community 40 - ".__init__"
Cohesion: 0.21
Nodes (8): average_between(), average_link_cluster(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer, jaccard(), score_pair(), time_decay()

### Community 41 - "command"
Cohesion: 0.21
Nodes (7): annotation_options(), artifact_options(), inspect_annotations_cmd(), inspect_artifacts_cmd(), report_user_errors(), wrapper(), scope_options()

### Community 42 - "ProcessorTestCase"
Cohesion: 0.19
Nodes (6): merge_tags(), Options, TaggerOptions, TaggerProcessor, ProcessorTestCase, TaggerTests

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "test_llm.py"
Cohesion: 0.21
Nodes (5): EmbedOptions, EmbedProcessor, Options, tags_text(), EmbedTests

### Community 45 - "config.example.yaml"
Cohesion: 0.25
Nodes (5): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), ollama LLM backend, plugins configuration section

### Community 47 - "app.py"
Cohesion: 0.25
Nodes (5): inspect_items_cmd(), print_deliver(), print_item(), print_process(), print_table()

### Community 48 - "test_app.py"
Cohesion: 0.10
Nodes (5): LockedError, write_lock(), main(), migrate(), main()

### Community 49 - "OptionsTests"
Cohesion: 0.08
Nodes (11): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options, GoogleChatError, GoogleChatSink, __newsmerger_plugin__() (+3 more)

### Community 51 - "cli.py"
Cohesion: 0.10
Nodes (6): delete_group(), deliveries_group(), inspect_group(), lexer_for(), match_snippet(), print_content()

### Community 52 - "summarize.py"
Cohesion: 0.33
Nodes (4): Options, SummarizeOptions, SummarizeProcessor, SummarizeTests

### Community 53 - "inspect_items_cmd"
Cohesion: 0.27
Nodes (5): format_value(), json_default(), preview(), print_json(), setup_logging()

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 57 - "plaza.py"
Cohesion: 0.17
Nodes (5): get_section(), __newsmerger_plugin__(), parse_datetime(), PlazaProvider, SectionNotFoundError

### Community 58 - "newsmerger CLAUDE.md agent guidelines"
Cohesion: 0.33
Nodes (5): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention

### Community 59 - "StubLLM"
Cohesion: 0.29
Nodes (3): ConsumerPluginTests, ServicesTests, StubLLM

### Community 60 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 61 - "ADR 0001 Item identity and change detection"
Cohesion: 0.40
Nodes (4): IndexSiteProvider / URLProvider, ADR 0001 Item identity and change detection, Item, Provider

### Community 65 - "ScoredItem"
Cohesion: 0.21
Nodes (7): build_score_matrix(), GroupingOptions, item_ref(), member_payload(), pair_payload(), ScoredItem, tagged_items()

### Community 77 - "GroupingRemixer"
Cohesion: 0.29
Nodes (5): AverageLinkRemixer, GroupingRemixer, __newsmerger_plugin__(), SingleLinkRemixer, GroupingPluginTests

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)`, `PluginOptions (pydantic, unknown keys rejected)`, `Annotation` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 418 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `.record_result` to `make_item`, `embed.py`, `test_db.py`, `Artifact`, `Application`, `migrate_autoincrement.py`, `ollama.py`, `.session_scope`, `__newsmerger_plugin__`, `ProcessingScope`, `Sink`, `BaseSink`, `DeliveryStatus`, `.get_annotation_values`, `SourceItem`, `.require_annotation`, `SourceData`, `BaseProcessor`, `markdownify.py`, `__newsmerger_plugin__`, `backoff_seconds`, `BaseRemixer`, `test_sinks.py`, `.__init__`, `ProcessorTestCase`, `test_llm.py`, `test_app.py`, `OptionsTests`, `summarize.py`, `Config`, `ScoredItem`, `GroupingRemixer`?**
  _High betweenness centrality (0.163) - this node is a cross-community bridge._
- **Are the 44 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 44 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `P1: plain logging and <APP>_LOG_LEVEL fix`, `External pipelines (scripts/pipeline_url.py)` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `make_item` be split into smaller, more focused modules?**
  _Cohesion score 0.07394366197183098 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `ProcessingScope` to `make_item`, `embed.py`, `test_db.py`, `ApplicationTests`, `Artifact`, `Application`, `ollama.py`, `.session_scope`, `Context`, `__newsmerger_plugin__`, `process_cmd`, `Sink`, `BaseSink`, `DeliveryStatus`, `SourceItem`, `.record_result`, `BaseProcessor`, `__newsmerger_plugin__`, `BaseRemixer`, `test_sinks.py`, `0009: Workflows and keyed entries`, `.__init__`, `command`, `app.py`, `test_app.py`, `cli.py`, `ScoredItem`, `EmbeddingGroupingTests`, `GroupingRemixer`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07964912280701754 - nodes in this community are weakly interconnected._