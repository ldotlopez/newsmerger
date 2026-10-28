# newsmerger

Collects news from several websites, keeps the articles, and builds things
from them: markdown copies, LLM summaries and tags, event groupings, RSS
feeds and digests, and Telegram posts. It was written for local news (Castelló), but any
site can be added with a provider.

It works in four phases:

1. **import**: each configured **source** (a website) is fetched with its
   **provider**, and every article becomes an **item**. Re-importing an
   unchanged article does nothing; a changed one is updated in place.
2. **process**: **processors** add **annotations** to each item (its markdown,
   a summary, tags, the Telegram message it was posted as...).
3. **remix**: **remixers** combine many items into **artifacts** (an RSS feed,
   a list of events...).
4. **deliver**: **sinks** send items or artifacts to the outside world (a
   Telegram chat...) and record each **delivery**, so nothing is sent twice.

Providers, processors, remixers and sinks come from **plugins**, which are
enabled in the configuration. A **workflow** says which sources to use and
what to process, remix and deliver from them; the configuration's root keys
are the `default` workflow, and `workflows` adds more (e.g. one source posted
to its own Telegram chat).

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- Optionally, an Ollama server for the `ollama` LLM plugin, which
  `summarize`, `tagger`, `embed` and `digest` use

## Install

```sh
uv sync
```

## Configuration

Pass a YAML file with `-c/--config`. Every section is optional;
`config.example.yaml` is a starting point.

```yaml
sources:
  - id: castellonplaza               # required, stable: part of each item's key
    name: Castellón Plaza
    provider: plaza                  # see "Providers" below
    url: https://castellonplaza.com/castellon9/

db:
  uri: sqlite:////path/to/data.db    # default: <user data dir>/newsmerger/data.db
  content_dir: /path/to/content      # default: <user data dir>/newsmerger/content

cache:
  expiration: 21600                  # HTTP cache lifetime, in seconds

plugins:                             # plugins and their options, in this order
  ollama:                            # an LLM, for the plugins that use one
    api_base: https://ollama.example.com
    api_key: ${OLLAMA_API_KEY}
  tagger:                            # empty or missing: the plugin's defaults
    model: gemma4:12b
  telegram:
    bot_token: ${TELEGRAM_BOT_TOKEN}
    chat_id: ${TELEGRAM_CHAT_ID}       # the default for every delivery entry
  feedgenerator:
    title: Castelló news

process:                             # processor runs, in order
  - markdownify
  - summarize
  - tagger

remix:                               # remixer runs, in order
  - feedgenerator

deliver:                             # sink runs, in order
  - telegram
```

A source's `id` identifies its items: its `url` and `provider` can change
without losing anything, but renaming the `id` starts the source from
scratch. Removing a source from the file keeps its items; they just stop
being updated.

`${VAR}` in a value is replaced with the environment variable `VAR` when the
file is loaded, or with `VAR` from a `.env` file next to the config file (the
real environment wins). A missing variable is an error. Pass secrets (API
keys, bot tokens) this way, never as literals; `.env` is git-ignored.
Comments and keys are left alone. Write a literal `$` in a value as `$$`,
and quote a reference inside `{...}` or `[...]` (`{api_key: '${KEY}'}`).

```sh
# .env
OLLAMA_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

A plugin's section under `plugins` holds its options: the missing ones
take the defaults listed below, and unknown or invalid ones are rejected
with their path (`plugins.summarize.max_retries: ...`). Plugins with a
section are loaded in its order. Then, a provider that a source names or a
processor that a `process` entry names, if no listed plugin provides it,
loads the plugin of the same name with its defaults, and so does a
remixer or sink that a `remix` or `deliver` entry names; so a plugin needs
a section only for options. A name no plugin provides fails every command at
start-up (`sources.<id>.provider: no plugin provides '<name>'`). Only the
entries run: a processor, remixer or sink that is loaded but not listed
never does.

The `process` section lists the processor runs, in order. An entry is a
processor's name, or a processor with `key` and `options` for that run.
Every run writes one annotation **key**, the processor's own unless the
entry names another with `key` (lowercase words, optionally in
`/`-separated parts: `summary`, `summary/es`). A key is written by one entry
per item (see *Workflows*), so a processor can run several times with
different options and keys:

```yaml
process:
  - markdownify                      # writes `markdown`
  - processor: summarize             # writes `summary`
  - processor: summarize
    key: summary/es
    options:
      prompt: "Resume en español el siguiente artículo:\n\n"
      model: gemma4:27b
```

A run's options override, for that run only, those of the processor's
plugin section; the ones a processor takes are listed below. An entry whose
processor is not loaded, or that gives it an option it does not take, fails
every command at start-up with the option's path
(`process.1.options.temperature: Extra inputs are not permitted`).

`remix` and `deliver` entries work the same way: a remixer's or sink's name,
or one with `key` and `options`. A remix entry saves its artifacts under its
key (default: the remixer's name), so a remixer can run twice with different
options; remix keys are unique across workflows. A deliver entry records
its deliveries under its key (default: the sink's name), unique within its
workflow, so a sink can post to several places:

```yaml
remix:
  - feedgenerator                    # artifacts `feedgenerator/...`
  - remixer: feedgenerator           # artifacts `short/...`
    key: short
    options: {title: Headlines, max_items: 10}

deliver:
  - telegram                         # the section's chat_id
  - sink: telegram
    key: telegram-politics
    options: {chat_id: "-1001234", interval: 30, max_per_run: 1}
  - sink: telegram_artifacts
    options: {artifacts: [digest]}
```

`grouping` bundles several remixers, each with its own subsection, whose
options are the defaults of its entries. With no subsections, all of them
are enabled with their defaults; with some, only those are. `telegram`
provides both its sinks.

### Workflows

The root `process`, `remix` and `deliver` are the `default` workflow, which
uses every source except those with `default: false`. `workflows` lists
more, each with the ids of its sources and its own entries:

```yaml
sources:
  - {id: castellonplaza, name: Castellón Plaza, provider: plaza, url: ...}
  - {id: juntas, name: Juntas, provider: csjuntasgobierno, url: ..., default: false}

workflows:
  - name: juntas-channel
    sources: [juntas]
    process: [markdownify, summarize]
    deliver:
      - sink: telegram
        options: {chat_id: "-1009876", interval: 30, max_per_run: 1}
```

Commands run `default` unless given `-w/--workflow NAME`, so each workflow
is its own cron line (`newsmerger run -w juntas-channel`). A workflow only
touches its sources: `import` fetches them, and `process`, `remix` and
`deliver` see only their items.

Annotations belong to items, so two workflows may write the same key only
if they share no source; within a workflow, or between workflows that
share one, a key is written by one entry. Remix keys are unique across all
workflows, since artifacts belong to no source. A workflow's deliveries are
recorded as `<workflow>/<key>` (the bare key in `default`): the same item
delivered by two workflows is sent by each, and renaming a workflow or a
deliver key starts its record from scratch, so its last `lookback` hours
are sent again (`max_per_run` limits how many at once). Workflow names and
remix and deliver keys use lowercase letters, digits, `_` and `-`;
`default` is reserved.

LLM plugins (`ollama`) provide a language model to the plugins loaded after
them: list them in `plugins`, before the listed plugins that use them
(processors loaded on their own always come after). `summarize`, `tagger`,
`embed` and `digest` take `llm` (the LLM plugin to use; default: the first
one listed) and `model` (default: that LLM's default model). One that cannot
get its LLM, because none is loaded or the one it names is not, still
loads, but `process` or `remix` logs an error for
it and does nothing; a processor's items stay pending. Everything else works without an LLM, but
`grouping` and `telegram` read the tags and summaries those processors write.

Changing a plugin's or an entry's options never regenerates existing
annotations; use `process --force` for that.

## Usage

```sh
# Import every configured source
uv run newsmerger -c config.yaml import

# Run every process entry in order, or only one processor's
uv run newsmerger -c config.yaml process
uv run newsmerger -c config.yaml process markdownify --source castellonplaza --limit 20

# Run every remix entry in order, or just one, by key
uv run newsmerger -c config.yaml remix
uv run newsmerger -c config.yaml remix feedgenerator --since 2026-10-01

# Run every deliver entry in order, or just one, by key
uv run newsmerger -c config.yaml deliver
uv run newsmerger -c config.yaml deliver telegram --force --item 4127

# Run import, process, remix and deliver in turn (e.g. from cron)
uv run newsmerger -c config.yaml run

# The same, for another workflow (every phase command takes -w)
uv run newsmerger -c config.yaml run -w juntas-channel
uv run newsmerger -c config.yaml deliver -w juntas-channel telegram

# Inspect what is stored (read-only), as a table or --format json
uv run newsmerger -c config.yaml inspect items --source castellonplaza --limit 20
uv run newsmerger -c config.yaml inspect items --item 4127
uv run newsmerger -c config.yaml inspect content --sha256 <sha256> > item.html
uv run newsmerger -c config.yaml inspect annotations --item 4127
uv run newsmerger -c config.yaml inspect annotations --annotation 512
uv run newsmerger -c config.yaml inspect artifacts
uv run newsmerger -c config.yaml inspect artifacts --artifact feedgenerator/feed > feed.xml
uv run newsmerger -c config.yaml inspect deliveries --sink telegram --status error

# Delete, without asking: the same options as inspect select what goes
uv run newsmerger -c config.yaml delete items --item 4127
uv run newsmerger -c config.yaml delete annotations --processor summarize --source castellonplaza
uv run newsmerger -c config.yaml delete artifacts --artifact digest/castellonplaza/2026-10-01_2026-10-08
```

Items and annotations are selected by their numeric id, which `inspect`
shows; artifacts by `<remix key>/<name>`, and deliveries by their recorded
key (`<workflow>/<key>`, or the bare key in `default`). `process`, `remix`, `deliver`,
`inspect` and `delete` accept `--source` (a source id), `--since`,
`--until`, `--item` (repeatable) and `--limit`; `inspect` adds
`--processor`, `--key` and `--annotation` for annotations (`delete` only
`--processor`, and no `--limit`), and both add
`--remixer`, `--artifact` and `--limit` for artifacts. Filters combine; an
id that the selection does not return is an error.

`inspect` and `delete` sort with `--sort` (default `updated`), always
ascending, so dates go oldest first; the sort also decides which rows
`--limit` keeps. The keys: `id`, `source`, `published`, `updated` and
`title` for items; `id`, `item`, `processor` and `updated` for
annotations; `id`, `type`, `created` and `updated` for artifacts; `id`,
`sink`, `status` and `updated` for deliveries.

`inspect items` lists each item's annotations as `<id> <processor>.<key>`;
one `--item` shows all its fields, a row per annotation, and the
`inspect content --sha256 <sha256>` command that writes its stored content
to stdout as is.
`inspect annotations` shows a one-line preview per key, and one
`--annotation` prints its full value (text as is, the rest as JSON).
`inspect artifacts` loads contents only for `--artifact`, and one
`--artifact` writes the content to stdout and its metadata to stderr, so it
can be redirected. `--format json` prints full records.

`delete` never asks, so run `inspect` with the same options first. A
selection with no filter or id is refused. Deleting an item takes its
processing state, annotations and deliveries with it, and an item still in
its source's index comes back on the next `import` with a new id.
Annotations are deleted per processor (every key that processor wrote on
the item, with their processing state), so every run of it processes the
item again; `delete` selects them by processor, not by key or id. Items and
artifacts with deliveries are skipped with a warning unless `--force`,
which deletes their deliveries too, so they can be delivered again.

Global options: `--log-level LEVEL` (also accepts specs such as
`info,db:debug`), and `-v`/`-q`, repeatable, to raise or lower it one step
each from `warning` (`-v` shows progress messages, `-vv` debug). Without
them, the level comes from `NEWSMERGER_LOG_LEVEL`, then from `log_level` in
the config, then `warning`.

Results (tables, `inspect` output, contents, `--help`, and the summaries of
`run`, `import`, `process`, `remix` and `deliver`) go to stdout; progress and
logs go to stderr. Each stream is rich only when it is a terminal, so
`newsmerger run > summary.txt` keeps the progress rows on screen and writes
tab-separated tables, and with stderr redirected (cron) there is no progress
and logs are one plain line per record. The progress shows a row per phase
in `run` and a row per source, processor, remixer or sink while it runs.
Set `DISABLE_RICH=1` (or `RICH_DISABLED=1`), or `TERM=dumb`, for plain
output on both streams; `NO_COLOR=1` only drops the colors.

### How `process` behaves

- Each entry handles every item once, and keeps its own state per item
  under its key. It runs again on an item only when the item's content
  changed, or when the processor itself was upgraded.
- A processor can skip items it does not apply to (e.g. `markdownify` on a
  PDF). Skipped items stay skipped until their content changes.
- Failures are retried on later runs, up to 3 attempts by default (the
  `max_retries` option), waiting longer each time (1 min, 2 min, 4 min... up
  to 24 h).
- A run only sees items whose run of the key it reads finished (see the
  *Reads* column below). Items skipped upstream never reach it.
- `--force` reprocesses everything in scope, skipped items included, with
  fresh retry attempts.

### Providers

Each provider is a plugin of the same name, without options except
`telegram_channel` and `feedreader`.

| Provider | Site | Content |
| :--- | :--- | :--- |
| `prensaiberica`, `prensaiberica_plain` | Prensa Ibérica papers (El Periódico Mediterráneo...) | HTML |
| `castelloninformacion` | Castellón Información | HTML |
| `plaza` | Castellón Plaza | HTML |
| `theguardian` | The Guardian | HTML |
| `csjuntasgobierno` | Index page of *juntas de gobierno* minutes | PDF |
| `telegram_channel` | Articles linked from a public Telegram channel (`url: https://t.me/<channel>`) | HTML |
| `feedreader` | Any RSS or Atom feed (`url:` the feed) | The feed's HTML or text, or the article's HTML with `article_selector` |

`telegram_channel` reads the channel's web preview, which only public
channels have, and imports one item per linked article, keyed by its
canonical URL; the post id, text and photo go into the item's `data`. Links that
resolve to the site's front page, such as a daily front-page post, are
skipped. Its `pages`
option (default 1, 20 posts each) reads further back. The preview is always
fetched fresh, never from the HTTP cache.

`feedreader` imports one item per feed entry: its full content (or summary),
author, categories as `tags` (the first also as `section`) and an image.
Feeds that carry only a summary can set `article_selector`, a CSS selector
of the article body: each entry's link is then fetched and that element
becomes the item's content. Set it in the plugin's section for every feed,
or per source in its `options`, which win:

```yaml
sources:
  - id: some-blog
    name: Some blog
    provider: feedreader
    url: https://blog.example.com/feed.xml
    options:
      article_selector: article .post-body
```

To support a new site, see
[Writing a plugin](docs/ARCHITECTURE.md#writing-a-plugin).

### Processors

| Plugin | Processor | Reads | Writes | Does |
| :--- | :--- | :--- | :--- | :--- |
| `markdownify` | `markdownify` | item content | `markdown` | Extracts the article's markdown from HTML and PDF items |
| `summarize` | `summarize` | `markdown` | `summary` | Summarizes the article with an LLM |
| `tagger` | `tagger` | `markdown` | `tags` | Extracts entity tags with an LLM |
| `embed` | `embed` | `tags` or `markdown` | `<input>_embedding` | Embeds the tags (sorted and comma-separated) or the markdown with an LLM |

Every processor takes `max_retries` (default 3) in its plugin section, and
`summarize`, `tagger` and `embed` take `llm` (see above). The rest can be
set in the section, as the default, or per entry: `model` (`summarize`,
`tagger`, `embed`), `prompt` (`summarize`, followed by the article's
markdown) and `input` (`embed`: `tags`, the default, or `markdown`; one
entry per input). Consumers read annotations by key:
`telegram` reads `summary`, `grouping` reads `tags` and
`<embedding>_embedding`, and `digest` and `search` read `markdown`.

### LLMs

| Plugin | LLM | Does |
| :--- | :--- | :--- |
| `ollama` | `ollama` | Prompts and embeddings with an Ollama server |

Options of `ollama`: `api_base` (default `http://localhost:11434`),
`api_key`, `chat_model` (default `gemma4:12b`) and `embed_model` (default
`mxbai-embed-large:latest`).

### Remixers

| Plugin | Remixer | Artifact | Does |
| :--- | :--- | :--- | :--- |
| `feedgenerator` | `feedgenerator` | `feed` | RSS feed of the newest items in scope |
| `grouping` | `singlelink` | `current` | Clusters tagged items into events (single-link over tag overlap) |
| `grouping` | `avglink` | `current` | Clusters tagged items into events (average-link over tag overlap) |
| `grouping` | `embeddings` | `current` | Clusters tagged items by tag overlap blended with the similarity of their `tags_embedding` or `markdown_embedding` (single-link) |
| `digest` | `digest` | `<source id>/<since>_<until>` | Markdown digest of the highlights of each source in scope, written with an LLM from `markdown` |

Options, in the plugin section as defaults or per entry (except `llm`,
section only):

- `digest`: `llm` and `model` (see above), `days` (default 7: the scope
  when it sets no `--since`), `max_items` (newest items per source, default
  50), `max_article_chars` (each article's markdown is cut to this, default
  3000) and `context_length` (the model's context window in tokens, default
  32768). Meant for one source: `remix digest --source <id>` for the last
  week, or `--since`/`--until` for another period. Each period is its own
  artifact (dates as `YYYY-MM-DD`), so `inspect artifacts --remixer digest`
  (the entry's key) lists them and rebuilding a period overwrites it.
- `feedgenerator`: `title` (default `newsmerger feed`), `link`, `description`
  (default: the title), `max_items` (default 100).
- `grouping`, per remixer subsection: `min_score` (default 0.3), `tau_hours` (time
  decay, default 24; `null` disables it), `days` (default 7: the scope when
  it sets no `--since`). `embeddings` adds `embedding` (`tags` or
  `markdown`, default `tags`) and `embedding_weight` (0 to 1, default 0.5).
  Items without the annotations a remixer reads are left out of its groups,
  so `embeddings` needs `process` to have run `embed` with that input first.

Artifacts are rebuilt each time their remixer runs, so between runs they can
lag behind the stored items. Remixers never act outside newsmerger.

### Sinks

| Plugin | Sink | Delivers |
| :--- | :--- | :--- |
| `telegram` | `telegram` | Summarized items (title, summary, link) to a Telegram chat |
| `telegram` | `telegram_artifacts` | The artifacts of the remix keys in `artifacts` (e.g. `[digest]`), as documents |
| `googlechat` | `googlechat` | Summarized items to a Google Chat space, by incoming webhook |

Every deliver entry takes `interval` (minutes between its deliveries,
default 0: no pacing), `max_per_run` (deliveries per run at most, default
5), `max_retries` (default 3) and `lookback` (hours, default 24).
`telegram` adds `item_image` (post the item's image, when it has one, as a
photo with the text as its caption; default true), `item_url_text` (the
text of the link to the article, default `original article`) and
`item_url_preview` (let Telegram show the link's preview on messages
without an image, default false).
`telegram_artifacts` adds `artifacts` (remix keys, default none).

Every `telegram` and `telegram_artifacts` entry needs a `bot_token` and a
`chat_id`, its own or the `telegram` section's, which holds their defaults
and is optional: entries can post with different bots, and a workflow can
give its entries both with no section at all. The
`googlechat` section or entry gives the webhook as `url`, or as `channel`
(the space id) and `token`. Its entries take `item_image` (the item's image,
when it has one, as a card below the text; default true),
`item_url_text`, as `telegram`'s, and `summary` (the annotation key posted
as the summary, e.g. `summary/es`; default `summary`); Chat has no link
preview to control.

```yaml
plugins:
  telegram:
    bot_token: ${TELEGRAM_BOT_TOKEN}
    chat_id: ${TELEGRAM_CHAT_ID}
  googlechat:
    url: ${GOOGLECHAT_WEBHOOK_URL}
deliver:
  - {sink: telegram, options: {interval: 30}}
  - {sink: telegram_artifacts, options: {artifacts: [digest]}}
  - googlechat
```

How `deliver` behaves:

- Each run queues what is new, then delivers what is due. Without `--since`
  or `--item` (`--artifact` for artifact sinks), new means the subjects of
  the last `lookback` hours without a delivery yet; `telegram` only queues
  items whose `summary` run finished. Run `deliver` (or `run`)
  periodically, e.g. from cron every few minutes.
- Items go out oldest first. With an `interval`, an entry delivers one
  subject once its last delivery is that old, whatever the source; without
  one, every due subject, up to `max_per_run` per run.
- A failed delivery is retried like a processor's, holding back the rest of
  its source until it succeeds or runs out of attempts; `--requeue` gives
  the failed ones in scope fresh attempts.
- Nothing is delivered twice by the same entry. `--force` with a KEY and
  `--item` or `--artifact` sends those subjects again, now, whatever their
  state, with no pacing.
- A delivery is marked `sending` before the call. If a run is interrupted
  there, its outcome is unknown and it is never retried on its own: check
  the chat, then settle it with
  `deliveries resolve telegram --as done` (it arrived) or `--as queued`
  (send it again), with the key `inspect deliveries` shows.
- `inspect deliveries` shows the ledger: each subject, its state, attempts
  and last error.

## Data and backups

Everything lives in two places: the SQLite database (`db.uri`) and the
content directory (`db.content_dir`), which holds article contents,
annotation values and artifacts. Back up both together. The database runs in
WAL mode, so back it up with SQLite's backup API (or with no process using
it), not by copying `data.db` alone.

The schema is created, never migrated: after an upgrade that changes it,
move the old `data.db` and `content_dir` aside and re-import. New tables are
added on their own. Three upgrades come with a one-shot script for existing
databases (back up first):

- `scripts/migrate_autoincrement.py -c config.yaml`: ids that are never
  reused, which `--item` and `--annotation` rely on.
- `scripts/migrate_telegram_state.py -c config.yaml`: turns the old
  `telegram/state` artifact into deliveries. Run it before the first
  `deliver telegram`, or the last `lookback` hours are posted again.
- `sqlite3 -bail data.db < scripts/migrate_annotation_keys.sql`: keys
  processing state and annotations by annotation key (the `process` section),
  keeping every row and id. Run it before the first `process` on the new
  schema.

Workflows and keyed remix and deliver entries need no migration: existing
artifacts and deliveries are those of the `default` entries with the
remixer's or sink's name as key. Configurations need updating, though:
remixers and sinks run only when `remix` and `deliver` list them, and the
`telegram` subsections become deliver entries.

Commands that write take a lock next to the database (`data.db.lock`), so
a second one fails at once instead of running alongside the first.

## Known limitations

- The same article in two sources is stored, and processed, twice.
- Items of a removed source still appear in artifacts unless the remixer
  filters them out.

## Scripting

Other tools use `Application`, the same core the CLI uses:

```python
from pathlib import Path

from newsmerger.app import Application

with Application.from_config_file(Path("config.yaml"), create_schema=False) as app:
    feed = app.get_artifact("feedgenerator", "feed")  # None if it doesn't exist
```

Code that writes takes `app.lock()` first.

## Development

```sh
DISABLE_RICH=1 uv run python -m unittest discover -s tests
uv run ruff check --fix .
uv run ruff format .
```

See [docs/SPECIFICATION.md](docs/SPECIFICATION.md) for the full definition
of the application, [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the
internals and how to write a plugin, [docs/decisions/](docs/decisions/) for the recorded
design decisions and [PLAN.md](PLAN.md) for pending work.
