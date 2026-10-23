# newsmerger

Collects news from several websites, keeps the articles, and builds things
from them: markdown copies, LLM summaries and tags, event groupings, RSS
feeds and digests, and Telegram posts. It was written for local news (Castelló), but any
site can be added with a provider.

It works in four phases:

1. **import**: each configured **source** (a website) is fetched with its
   **provider**, and every article becomes an **item**. Re-importing an
   unchanged article does nothing; a changed one is updated in place.
2. **enrich**: **processors** add **annotations** to each item (its markdown,
   a summary, tags, the Telegram message it was posted as...).
3. **remix**: **remixers** combine many items into **artifacts** (an RSS feed,
   a list of events...).
4. **deliver**: **sinks** send items or artifacts to the outside world (a
   Telegram chat...) and record each **delivery**, so nothing is sent twice.

Providers, processors, remixers and sinks come from **plugins**, which are
enabled in the configuration.

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

plugins:                             # only these are loaded, in this order
  plaza:                             # empty: the plugin's defaults
  markdownify:
  ollama:                            # an LLM: listed before its users
    api_base: https://ollama.example.com
    api_key: ${OLLAMA_API_KEY}
  summarize:                         # the default LLM and its default model
  telegram:
    bot_token: ${TELEGRAM_BOT_TOKEN}
    chat_id: ${TELEGRAM_CHAT_ID}
  rssfeed:
    title: Castelló news
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

Only plugins with a section under `plugins` are loaded, and only their
providers, processors, remixers and sinks can be used. A plugin's section
holds its options: the missing ones take the defaults listed below, and
unknown or invalid ones are rejected with their path
(`plugins.summarize.max_retries: ...`). `enrich`, `remix` and `deliver` run
their objects in the order of this section.

`grouping` bundles several remixers and `telegram` two sinks, each with its
own subsection. With no subsections, all of them are enabled with their
defaults; with some, only those are.

LLM plugins (`ollama`) provide a language model to the plugins listed after
them. `summarize`, `tagger`, `embed` and `digest` take `llm` (the LLM plugin
to use; default: the first one listed) and `model` (default: that LLM's
default model). One that cannot get its LLM, because none is loaded or the
one it names is not, still loads, but `enrich` or `remix` logs an error for
it and does nothing; a processor's items stay pending. Everything else works without an LLM, but
`grouping` and `telegram` read the tags and summaries those processors write.

Changing a plugin's options never regenerates existing annotations; use
`enrich --force` for that.

## Usage

```sh
# Import every configured source
uv run newsmerger -c config.yaml import

# Import a single article URL into a configured source
uv run newsmerger -c config.yaml import-url --source castellonplaza <url>

# Run every loaded processor in order, or just one
uv run newsmerger -c config.yaml enrich
uv run newsmerger -c config.yaml enrich markdownify --source castellonplaza --limit 20

# Run every loaded remixer in order, or just one
uv run newsmerger -c config.yaml remix
uv run newsmerger -c config.yaml remix rssfeed --since 2026-10-01

# Run every loaded sink in order, or just one
uv run newsmerger -c config.yaml deliver
uv run newsmerger -c config.yaml deliver telegram --force --item 4127

# Run import, enrich, remix and deliver in turn (e.g. from cron)
uv run newsmerger -c config.yaml run

# Inspect what is stored (read-only), as a table or --format json
uv run newsmerger -c config.yaml inspect items --source castellonplaza --limit 20
uv run newsmerger -c config.yaml inspect annotations --item 4127
uv run newsmerger -c config.yaml inspect annotations --annotation 512
uv run newsmerger -c config.yaml inspect artifacts
uv run newsmerger -c config.yaml inspect artifacts --artifact rssfeed/feed > feed.xml
uv run newsmerger -c config.yaml inspect deliveries --sink telegram --status error

# Delete, without asking: the same options as inspect select what goes
uv run newsmerger -c config.yaml delete items --item 4127
uv run newsmerger -c config.yaml delete annotations --processor summarize --source castellonplaza
uv run newsmerger -c config.yaml delete artifacts --artifact digest/castellonplaza/2026-10-01_2026-10-08
```

Items and annotations are selected by their numeric id, which `inspect`
shows; artifacts by `<remixer>/<name>`. `enrich`, `remix`, `deliver`,
`inspect` and `delete` accept `--source` (a source id), `--since`,
`--until`, `--item` (repeatable) and `--limit`; `inspect` and `delete` add
`--processor`, `--key` and `--annotation` for annotations, and
`--remixer`, `--artifact` and `--limit` for artifacts. Filters combine; an
id that the selection does not return is an error.

`inspect items` lists each item's annotations as `<id> <processor>.<key>`.
`inspect annotations` shows a one-line preview per key, and one
`--annotation` prints its full value (text as is, the rest as JSON).
`inspect artifacts` loads contents only for `--artifact`, and one
`--artifact` writes the content to stdout and its metadata to stderr, so it
can be redirected. `--format json` prints full records.

`delete` never asks, so run `inspect` with the same options first. A
selection with no filter or id is refused. Deleting an item takes its
processing state, annotations and deliveries with it, and an item still in
its source's index comes back on the next `import` with a new id.
Annotations are deleted per processor (every key of that processor on the
item, with its processing state), so the item is processed again; a `--key`
or `--annotation` selection warns when that deletes other keys. Items and
artifacts with deliveries are skipped with a warning unless `--force`,
which deletes their deliveries too, so they can be delivered again.

Global options: `--log-level LEVEL` (default `warning`; also accepts specs
such as `info,db:debug`), and `-v`/`-q`, repeatable, to raise or lower it one
step each (`-v` shows progress messages, `-vv` debug). Set `DISABLE_RICH=1`
(or `RICH_DISABLED=1`, or `NO_COLOR=1`) for plain output: no colors, tables
or progress bars, one line per log record.

### How `enrich` behaves

- Each processor handles every item once. It runs again on an item only when
  the item's content changed, or when the processor itself was upgraded.
- A processor can skip items it does not apply to (e.g. `markdownify` on a
  PDF). Skipped items stay skipped until their content changes.
- Failures are retried on later runs, up to 3 attempts by default (the
  `max_retries` option), waiting longer each time (1 min, 2 min, 4 min... up
  to 24 h).
- A processor only sees items its upstream processor finished (see the
  *Reads* column below). Items skipped upstream never reach it.
- `--force` reprocesses everything in scope, skipped items included, with
  fresh retry attempts.

### Providers

Each provider is a plugin of the same name, without options.

| Provider | Site | Content |
| :--- | :--- | :--- |
| `prensaiberica`, `prensaiberica_plain` | Prensa Ibérica papers (El Periódico Mediterráneo...) | HTML |
| `castelloninformacion` | Castellón Información | HTML |
| `plaza` | Castellón Plaza | HTML |
| `theguardian` | The Guardian | HTML |
| `csjuntasgobierno` | Index page of *juntas de gobierno* minutes | PDF |

To support a new site, see
[Writing a plugin](docs/ARCHITECTURE.md#writing-a-plugin).

### Processors

| Plugin | Processor | Reads | Does |
| :--- | :--- | :--- | :--- |
| `markdownify` | `markdownify` | item content | Extracts the article's markdown from HTML items |
| `summarize` | `summarize` | `markdownify.markdown` | Summarizes the article with an LLM |
| `tagger` | `tagger` | `markdownify.markdown` | Extracts entity tags with an LLM |
| `embed` | `embed` | `tagger.tags`, `markdownify.markdown` | Embeds the tags (`tags_embedding`, plus the embedded `tags_text`) and the markdown (`markdown_embedding`) with an LLM |

Every processor takes `max_retries` (default 3). `summarize`, `tagger` and
`embed` take `llm` and `model` (see above); `embed` also takes `inputs`
(default `[tags, markdown]`).

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
| `rssfeed` | `rssfeed` | `feed` | RSS feed of the newest items in scope |
| `grouping` | `singlelink` | `current` | Clusters tagged items into events (single-link over tag overlap) |
| `grouping` | `avglink` | `current` | Clusters tagged items into events (average-link over tag overlap) |
| `grouping` | `embeddings` | `current` | Clusters tagged items by tag overlap blended with the similarity of their `embed` annotations (single-link) |
| `digest` | `digest` | `<source id>/<since>_<until>` | Markdown digest of the highlights of each source in scope, written with an LLM from `markdownify.markdown` |

Options:

- `digest`: `llm` and `model` (see above), `days` (default 7: the scope
  when it sets no `--since`), `max_items` (newest items per source, default
  50), `max_article_chars` (each article's markdown is cut to this, default
  3000) and `context_length` (the model's context window in tokens, default
  32768). Meant for one source: `remix digest --source <id>` for the last
  week, or `--since`/`--until` for another period. Each period is its own
  artifact (dates as `YYYY-MM-DD`), so `inspect artifacts --remixer digest`
  lists them and rebuilding a period overwrites it.
- `rssfeed`: `title` (default `newsmerger feed`), `link`, `description`
  (default: the title), `max_items` (default 100).
- `grouping`, per remixer: `min_score` (default 0.3), `tau_hours` (time
  decay, default 24; `null` disables it), `days` (default 7: the scope when
  it sets no `--since`). `embeddings` adds `embedding` (`tags` or
  `markdown`, default `tags`) and `embedding_weight` (0 to 1, default 0.5).
  Items without the annotations a remixer reads are left out of its groups,
  so `embeddings` needs `enrich` to have run `embed` first.

Artifacts are rebuilt each time their remixer runs, so between runs they can
lag behind the stored items. Remixers never act outside newsmerger.

### Sinks

| Plugin | Sink | Delivers |
| :--- | :--- | :--- |
| `telegram` | `telegram` | Summarized items (title, summary, link) to a Telegram chat, at most one per source every `interval` minutes |
| `telegram` | `telegram_artifacts` | The artifacts of the remixers in `artifacts` (e.g. `[digest]`), as documents |

Options of `telegram`: `bot_token` and `chat_id` (required, shared), and a
subsection per sink. Both take `max_retries` (default 3) and `lookback`
(hours, default 24); `telegram` adds `interval` (minutes, default 30) and
`telegram_artifacts` adds `artifacts` (remixer names, default none):

```yaml
plugins:
  telegram:
    bot_token: ${TELEGRAM_BOT_TOKEN}
    chat_id: ${TELEGRAM_CHAT_ID}
    telegram:
      interval: 30
    telegram_artifacts:
      artifacts: [digest]
```

How `deliver` behaves:

- Each run queues what is new, then delivers what is due. Without `--since`
  or `--item` (`--artifact` for artifact sinks), new means the subjects of
  the last `lookback` hours without a delivery yet; `telegram` only queues
  items `summarize` finished. Run `deliver` (or `run`) periodically, e.g.
  from cron every few minutes.
- Items go out oldest first per source. A failed delivery is retried like a
  processor's, holding back the rest of its source until it succeeds or runs
  out of attempts; `--requeue` gives the failed ones in scope fresh attempts.
- Nothing is delivered twice. `--force` with a SINK and `--item` or
  `--artifact` sends those subjects again, now, whatever their state.
- A delivery is marked `sending` before the call. If a run is interrupted
  there, its outcome is unknown and it is never retried on its own: check
  the chat, then settle it with
  `deliveries resolve telegram --as done` (it arrived) or `--as queued`
  (send it again).
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
added on their own. Two upgrades come with a one-shot script for existing
databases (back up first):

- `scripts/migrate_autoincrement.py -c config.yaml`: ids that are never
  reused, which `--item` and `--annotation` rely on.
- `scripts/migrate_telegram_state.py -c config.yaml`: turns the old
  `telegram/state` artifact into deliveries. Run it before the first
  `deliver telegram`, or the last `lookback` hours are posted again.

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
    feed = app.get_artifact("rssfeed", "feed")  # None if it doesn't exist
```

`scripts/pipeline_url.py` imports one URL and runs a list of processors on
it (the publish-news flow). Code that writes takes `app.lock()` first.

## Development

```sh
uv run python -m unittest discover -s tests
uv run ruff check --fix .
uv run ruff format .
```

See [docs/SPECIFICATION.md](docs/SPECIFICATION.md) for the full definition
of the application, [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the
internals and how to write a plugin, [docs/decisions/](docs/decisions/) for the recorded
design decisions and [PLAN.md](PLAN.md) for pending work.
