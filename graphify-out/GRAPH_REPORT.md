# Graph Report - telegram-markdown-option  (2026-10-28)

## Corpus Check
- 72 files · ~122,701 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .lock 1)

## Summary
- 1558 nodes · 4467 edges · 68 communities (51 shown, 17 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 595 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2661c361`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_db.py
- BaseProcessor
- plugins/__init__.py
- ApplicationTests
- LLM
- test_telegram.py
- Application
- TaggerProcessor
- newsmerger CLAUDE.md agent guidelines
- StubLLM
- DeleteCommandTests
- app_from_context
- models.py
- ProcessingScope
- process_cmd
- EmbedProcessor
- Delivery
- test_providers.py
- migrate_telegram_state.py
- Services
- 0009: Workflows and keyed entries
- Any
- SourceItem
- workflows
- ProcessingScope
- SourceData
- sinks.py
- markdownify.py
- PrensaIbericaPlainProvider
- deliveries table (the ledger)
- inspect_annotations_cmd
- inspect_deliveries_cmd
- group
- plugins
- Artifact
- test_telegram.py
- inspect_artifacts_cmd
- db.py
- ADR 0007 Sinks and the delivery ledger
- grouping.py
- options
- hooks
- Services object (services.llm(name))
- CSJuntasGobiernoProvider
- config.example.yaml
- .llm
- print_table
- GoogleChatError
- MissingAnnotationError
- SourceItemData
- Processor
- El Periódico Mediterráneo
- TestSourceItemDataContent
- get_section
- cli.py Click commands
- Services
- GoogleChatSinkTests
- Item
- .id_is_valid
- MigrateAutoincrementTests
- Example sources (prensaiberica_plain, castelloninformacion, plaza, theguardian)
- Artifact
- Grouping notes: NLP clustering pipeline
- news-aggregator
- workflows
- BaseRemixer

## God Nodes (most connected - your core abstractions)
1. `Database` - 159 edges
2. `ProcessingScope` - 134 edges
3. `SourceItem` - 119 edges
4. `SourceData` - 82 edges
5. `Services` - 75 edges
6. `Artifact` - 62 edges
7. `Application` - 60 edges
8. `SourceItemData` - 51 edges
9. `HTTPClient` - 46 edges
10. `ApplicationTests` - 40 edges

## Surprising Connections (you probably didn't know these)
- `Decision` --references--> `Application`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/app.py
- `Decision` --references--> `UsesLLMOptions`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/plugins/__init__.py
- `Decision` --references--> `ProcessorType`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/processors.py
- `Decision` --references--> `ProviderType`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/providers.py
- `Decision` --references--> `RemixerType`  [INFERRED]
  docs/decisions/0010-plugin-classes-and-catalog.md → newsmerger/remixers.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **markdownify -> summarize/tagger -> embed -> grouping data chain** — docs_architecture_markdownify_processor, docs_architecture_summarize_processor, docs_architecture_tagger_processor, docs_architecture_embed_processor, docs_architecture_grouping_remixers [EXTRACTED 1.00]
- **Plugin protocol types consumed by the core** — docs_specification_provider, docs_specification_processor, docs_specification_remixer, docs_specification_sink, docs_decisions_0006_llm_plugins_llm_protocol [EXTRACTED 1.00]
- **Delivery ledger mechanism** — docs_architecture_deliveries_table, docs_decisions_0007_sinks_and_delivery_ledger_delivery_states, docs_architecture_basesink_cycle, docs_decisions_0007_sinks_and_delivery_ledger_strict_fifo_per_source, docs_decisions_0007_sinks_and_delivery_ledger_lookback_window, docs_specification_write_lock [INFERRED 0.85]
- **Prensa Ibérica sample article fixtures (El Periódico Mediterráneo, July 2026)** — tests_samples_prensaiberica_item_132310503_article, tests_samples_prensaiberica_item_132340038_article, tests_samples_prensaiberica_item_132344288_article [INFERRED 0.95]

## Communities (68 total, 17 thin omitted)

### Community 0 - "test_db.py"
Cohesion: 0.05
Nodes (16): DBDelivery, DBProcessingState, DBSource, DBSourceItem, AnnotationTests, ConnectionTests, ContentStorageTests, DatabaseTestCase (+8 more)

### Community 2 - "plugins/__init__.py"
Cohesion: 0.18
Nodes (4): EmbeddingGroupingTests, FeedGeneratorTests, GroupingTests, RemixerTestCase

### Community 4 - "LLM"
Cohesion: 0.10
Nodes (6): Catalog, check_section(), Profile, Run, share_sources(), ConfigError

### Community 5 - "test_telegram.py"
Cohesion: 0.06
Nodes (20): build_card(), merge_options(), build_caption(), DocumentDeliveryOptions, ItemDeliveryOptions, __newsmerger_plugin__(), post(), TelegramArtifactSink (+12 more)

### Community 6 - "Application"
Cohesion: 0.06
Nodes (4): Application, lookup(), workflow_scope(), Workflow

### Community 7 - "TaggerProcessor"
Cohesion: 0.25
Nodes (3): SummarizeOptions, merge_tags(), TaggerProcessor

### Community 8 - "newsmerger CLAUDE.md agent guidelines"
Cohesion: 0.33
Nodes (5): pre-commit config, ruff-check and ruff-format hooks, newsmerger CLAUDE.md agent guidelines, DTO/ORM from_dto/to_dto/update convention, Consumer-side Protocol decoupling convention

### Community 9 - "StubLLM"
Cohesion: 0.15
Nodes (7): Processor, build(), EmbedTests, ProcessorTestCase, StubLLM, SummarizeTests, TaggerTests

### Community 10 - "DeleteCommandTests"
Cohesion: 0.10
Nodes (4): DeliveryStatus, Delivery, migrate(), DeleteCommandTests

### Community 11 - "app_from_context"
Cohesion: 0.16
Nodes (7): app_from_context(), cli(), delete_deliveries_cmd(), inspect_content_cmd(), parse_artifact_ids(), process_cmd(), search_cmd()

### Community 12 - "models.py"
Cohesion: 0.14
Nodes (14): __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__(), PluginTypes, __newsmerger_plugin__(), __newsmerger_plugin__() (+6 more)

### Community 13 - "ProcessingScope"
Cohesion: 0.09
Nodes (7): Annotation, RunSummary, annotation(), CommandTests, InspectCommandTests, invoke(), LogLevelTests

### Community 14 - "process_cmd"
Cohesion: 0.15
Nodes (8): import_cmd(), import_sources(), print_import(), print_remix(), progress_rows(), remix_cmd(), run_cmd(), run_each()

### Community 15 - "EmbedProcessor"
Cohesion: 0.28
Nodes (3): EmbedOptions, EmbedProcessor, tags_text()

### Community 16 - "Delivery"
Cohesion: 0.09
Nodes (3): ArtifactNames, BaseItemSink, BaseSink

### Community 17 - "test_providers.py"
Cohesion: 0.09
Nodes (17): CSJuntasGobiernoProvider, find_parent_by_tag_name(), get_date_from_text(), PreparseData, Options, Options, NoOptions, PluginOptions (+9 more)

### Community 18 - "migrate_telegram_state.py"
Cohesion: 0.05
Nodes (12): LockedError, write_lock(), Base, main(), migrate(), needs_autoincrement(), recreate(), main() (+4 more)

### Community 19 - "Services"
Cohesion: 0.12
Nodes (8): ids_of(), in_default(), Kind, Use, DeliveryEntry, options_error(), ProcessEntry, RemixEntry

### Community 20 - "0009: Workflows and keyed entries"
Cohesion: 0.33
Nodes (5): 0009: Workflows and keyed entries, Consequences, Context, Decision, Rejected options

### Community 21 - "Any"
Cohesion: 0.11
Nodes (5): _configure_sqlite_connection(), CustomJSON, DBItemAnnotation, _encode_value(), UTCDateTime

### Community 22 - "SourceItem"
Cohesion: 0.09
Nodes (4): ItemKey, SourceItem, DigestRemixer, SearchTests

### Community 23 - "workflows"
Cohesion: 0.33
Nodes (6): sink, workflows, deliver, name, process, sources

### Community 24 - "ProcessingScope"
Cohesion: 0.12
Nodes (6): ProcessingScope, Remixer, BaseArtifactSink, Sink, DigestRemixerTests, MigrateTelegramStateTests

### Community 25 - "SourceData"
Cohesion: 0.08
Nodes (17): HTTPClient, SourceData, SourceItemData, CastellonInformacionProvider, FeedReaderProvider, fetch_article(), PlazaProvider, PrensaIbericaProvider (+9 more)

### Community 27 - "markdownify.py"
Cohesion: 0.14
Nodes (6): MarkdownifyProcessor, ProcessorOptions, SkipItem, ClassRegisterTests, make_pdf(), MarkdownifyPdfTests

### Community 29 - "deliveries table (the ledger)"
Cohesion: 0.33
Nodes (4): BaseSink deliver cycle (queue, select, send), deliveries table (the ledger), ADR 0005 Remixers with external side effects, Strict FIFO per source

### Community 31 - "inspect_annotations_cmd"
Cohesion: 0.13
Nodes (14): annotation_options(), artifact_options(), check_found(), delete_annotations_cmd(), delete_artifacts_cmd(), delete_items_cmd(), delivery_options(), inspect_annotations_cmd() (+6 more)

### Community 32 - "inspect_deliveries_cmd"
Cohesion: 0.20
Nodes (6): inspect_deliveries_cmd(), inspect_items_cmd(), print_deliver(), print_item(), print_process(), print_table()

### Community 34 - "plugins"
Cohesion: 0.11
Nodes (18): lookback, title, url, api_base, api_key, chat_model, embed_model, plugins (+10 more)

### Community 35 - "Artifact"
Cohesion: 0.07
Nodes (10): DBArtifact, Artifact, SelectionRequiredError, ArtifactTests, MigrateFeedNamesTests, ArtifactSinkTests, ItemSinkTests, RecordingArtifactSink (+2 more)

### Community 37 - "inspect_artifacts_cmd"
Cohesion: 0.40
Nodes (3): inspect_artifacts_cmd(), lexer_for(), print_content()

### Community 38 - "db.py"
Cohesion: 0.08
Nodes (10): Duration, ProcessingStatus, _sha256_column(), __newsmerger_plugin__(), UsesLLMOptions, __newsmerger_plugin__(), __newsmerger_plugin__(), __newsmerger_plugin__() (+2 more)

### Community 39 - "ADR 0007 Sinks and the delivery ledger"
Cohesion: 0.18
Nodes (14): Architecture, AUTOINCREMENT integer ids, External pipelines (scripts/pipeline_url.py), ADR 0001 Item identity and change detection, ADR 0002 Processing state lifecycle, ADR 0003 Plugin types and core scope, ADR 0004 Annotation and artifact contents on disk, ADR 0006 LLM plugins (+6 more)

### Community 40 - "grouping.py"
Cohesion: 0.10
Nodes (20): average_between(), average_link_cluster(), AverageLinkRemixer, build_score_matrix(), cosine_similarity(), EmbeddingsOptions, EmbeddingsRemixer, GroupingOptions (+12 more)

### Community 41 - "options"
Cohesion: 0.15
Nodes (14): options, artifacts, chat_id, interval, item_image, item_url_preview, item_url_text, markdown (+6 more)

### Community 42 - "hooks"
Cohesion: 0.15
Nodes (12): exclude, args, entry, files, id, language, name, pass_filenames (+4 more)

### Community 43 - "Services object (services.llm(name))"
Cohesion: 0.22
Nodes (12): digest remixer, embed processor, grouping remixers (singlelink, avglink, embeddings), markdownify processor, summarize processor, tagger processor, telegram bundle (telegram, telegram_artifacts sinks), LLM plugins must be listed before their consumers (+4 more)

### Community 44 - "CSJuntasGobiernoProvider"
Cohesion: 0.10
Nodes (9): chat_image_url(), GoogleChatSink, __newsmerger_plugin__(), WebhookOptions, card_widgets(), ChatImageUrlTests, GoogleChatSinkTests, OptionsTests (+1 more)

### Community 45 - "config.example.yaml"
Cohesion: 0.11
Nodes (15): cache, expiration, llms, input, processors, options, processor, remixers (+7 more)

### Community 46 - ".llm"
Cohesion: 0.22
Nodes (6): 0010: Plugin classes and the configuration catalog, Consequences, Context, Rejected options, factory(), factory()

### Community 47 - "print_table"
Cohesion: 0.13
Nodes (6): format_value(), json_default(), match_snippet(), preview(), print_json(), setup_logging()

### Community 50 - "SourceItemData"
Cohesion: 0.17
Nodes (3): Entry, LLMEntry, own_entries()

### Community 54 - "Processor"
Cohesion: 0.29
Nodes (6): UnavailableProcessor / UnavailableRemixer / UnavailableSink, Annotation, Delivery, Exponential backoff 60s*2^(n-1), capped 24h, max_retries, Processor, Sink

### Community 55 - "El Periódico Mediterráneo"
Cohesion: 0.43
Nodes (7): El Periódico Mediterráneo, Prensa Ibérica article HTML format (og:/article: meta tags), Telegram t.me/s channel preview HTML (tgme_widget_message, data-post), El eco perdido de las fiestas de julio nacidas del asedio carlista sobre Castellón (sample article), El Grau se vuelca en las fiestas de la Virgen del Carmen (sample article), Castellón apoya a la selección española desde la plaza Mayor (sample article), Telegram channel mediterraneoelperiodico (sample web preview)

### Community 57 - "get_section"
Cohesion: 0.29
Nodes (3): get_section(), parse_datetime(), SectionNotFoundError

### Community 58 - "cli.py Click commands"
Cohesion: 0.23
Nodes (10): cli.py Click commands, Database (db.py, only SQLite/storage access), foundation.storage.DiskStorage content-addressed storage, SQLAlchemy models never leave db.py; DTOs cross the boundary, foundation internal library, inspect items|annotations|artifacts|deliveries, Application class (single entry point), Phases: import, enrich, remix, deliver (+2 more)

### Community 59 - "Services"
Cohesion: 0.06
Nodes (16): Decision, LLM, LLMType, LLMUnavailableError, strip_code_fence(), DigestOptions, ClassRegister, Services (+8 more)

### Community 60 - "GoogleChatSinkTests"
Cohesion: 0.29
Nodes (7): discover_feed_url(), entry_date(), fetch_feed(), find_image(), __newsmerger_plugin__(), parse_entry(), select_article()

### Community 61 - "Item"
Cohesion: 0.40
Nodes (3): IndexSiteProvider / URLProvider, Item, Provider

### Community 63 - ".id_is_valid"
Cohesion: 0.15
Nodes (5): CacheConfig, DatabaseConfig, expand_variables(), MissingVariableError, parse_duration()

### Community 73 - "workflows"
Cohesion: 0.50
Nodes (4): foundation.plugin.Register plugin loading, __newsmerger_plugin__(services, **options) entry point, PluginOptions (pydantic, unknown keys rejected), plugins configuration section

## Knowledge Gaps
- **13 isolated node(s):** `news-aggregator`, `External pipelines (scripts/pipeline_url.py)`, `Annotation`, `Telegram t.me/s channel preview HTML (tgme_widget_message, data-post)`, `pre-commit config` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 457 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `sinks.py` to `test_db.py`, `BaseProcessor`, `plugins/__init__.py`, `test_telegram.py`, `Application`, `TaggerProcessor`, `StubLLM`, `DeleteCommandTests`, `models.py`, `ProcessingScope`, `EmbedProcessor`, `Delivery`, `migrate_telegram_state.py`, `Any`, `SourceItem`, `ProcessingScope`, `SourceData`, `markdownify.py`, `Artifact`, `test_telegram.py`, `db.py`, `grouping.py`, `CSJuntasGobiernoProvider`, `Services`, `BaseRemixer`?**
  _High betweenness centrality (0.159) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `Database` (e.g. with `Application` and `Annotation`) actually correct?**
  _`Database` has 43 INFERRED edges - model-reasoned connections that need verification._
- **What connects `news-aggregator`, `External pipelines (scripts/pipeline_url.py)`, `Annotation` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_db.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05347985347985348 - nodes in this community are weakly interconnected._
- **Why does `ProcessingScope` connect `ProcessingScope` to `test_db.py`, `BaseProcessor`, `plugins/__init__.py`, `ApplicationTests`, `test_telegram.py`, `Application`, `StubLLM`, `DeleteCommandTests`, `app_from_context`, `models.py`, `ProcessingScope`, `process_cmd`, `Delivery`, `migrate_telegram_state.py`, `SourceItem`, `sinks.py`, `inspect_annotations_cmd`, `inspect_deliveries_cmd`, `Artifact`, `db.py`, `grouping.py`, `print_table`, `Services`, `BaseRemixer`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `ProcessingScope` (e.g. with `Application` and `delete_annotations_cmd()`) actually correct?**
  _`ProcessingScope` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Should `ApplicationTests` be split into smaller, more focused modules?**
  _Cohesion score 0.059395801331285206 - nodes in this community are weakly interconnected._