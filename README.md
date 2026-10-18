# newsmerger

Collects news from several websites, keeps the articles, and builds things
from them: markdown copies, LLM summaries and tags, Telegram posts, event
groupings and RSS feeds. It was written for local news (Castelló), but any
site can be added with a provider.

It works in three phases:

1. **import**: each configured **source** (a website) is fetched with its
   **provider**, and every article becomes an **item**. Re-importing an
   unchanged article does nothing; a changed one is updated in place.
2. **enrich**: **processors** add **annotations** to each item (its markdown,
   a summary, tags, the Telegram message it was posted as...).
3. **remix**: **remixers** combine many items into **artifacts** (an RSS feed,
   a list of events...).

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- An Ollama server for the `summarize` and `tagger` processors and the
  `grouping_embeddings` remixer

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

processors:                          # run in this order by `enrich`
  - name: markdownify
  - name: summarize
    params:
      model: gemma4:12b
      api_base: https://ollama.example.com
      api_key: ${OLLAMA_API_KEY}

remixers:                            # run in this order by `remix`
  - name: telegram
    params:
      bot_token: ${TELEGRAM_BOT_TOKEN}
      chat_id: ${TELEGRAM_CHAT_ID}
      interval: 30                   # minutes between posts of the same source
  - name: rssfeed
    params:
      title: Castelló news
```

A source's `id` identifies its items: its `url` and `provider` can change
without losing anything, but renaming the `id` starts the source from
scratch. Removing a source from the file keeps its items; they just stop
being updated.

`${VAR}` is replaced with the environment variable `VAR` when the file is
loaded, or with `VAR` from a `.env` file next to the config file (the real
environment wins). A missing variable is an error. Pass secrets (API keys,
bot tokens) this way, never as literals; `.env` is git-ignored. Write a
literal `$` as `$$`, comments included.

```sh
# .env
OLLAMA_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

Only configured processors and remixers can run. Their `params` go to the
plugin, and unknown params are rejected. Changing a plugin's params never
regenerates existing annotations; use `enrich --force` for that.

## Usage

```sh
# Import every configured source
uv run newsmerger -c config.yaml import

# Import a single article URL into a configured source
uv run newsmerger -c config.yaml import-url --source castellonplaza <url>

# Run every configured processor in order, or just one
uv run newsmerger -c config.yaml enrich
uv run newsmerger -c config.yaml enrich markdownify --source castellonplaza --limit 20

# Run every configured remixer in order, or just one
uv run newsmerger -c config.yaml remix
uv run newsmerger -c config.yaml remix rssfeed --since 2026-10-01

# Inspect what is stored (read-only)
uv run newsmerger -c config.yaml items --source castellonplaza --limit 20
uv run newsmerger -c config.yaml annotations --source castellonplaza --uid <uid>
uv run newsmerger -c config.yaml annotations --source castellonplaza --uid <uid> --key summary
uv run newsmerger -c config.yaml artifacts
uv run newsmerger -c config.yaml artifact rssfeed feed > feed.xml
```

`enrich`, `remix` and `items` accept `--source` (a source id), `--since`,
`--until`, `--uid` (repeatable, within `--source`) and `--limit`.

`annotations` shows a one-line preview per key; `--key` prints full values
(text as is, the rest as JSON). `artifact` writes the content to stdout and
its metadata to stderr, so it can be redirected; a missing item or artifact
is an error.

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
  `max_retries` param), waiting longer each time (1 min, 2 min, 4 min... up
  to 24 h).
- A processor only sees items its upstream processor finished (see the
  *Reads* column below). Items skipped upstream never reach it.
- `--force` reprocesses everything in scope, skipped items included, with
  fresh retry attempts.

### Providers

| Provider | Site | Content |
| :--- | :--- | :--- |
| `prensaiberica`, `prensaiberica_plain` | Prensa Ibérica papers (El Periódico Mediterráneo...) | HTML |
| `castelloninformacion` | Castellón Información | HTML |
| `plaza` | Castellón Plaza | HTML |
| `theguardian` | The Guardian | HTML |
| `csjuntasgobierno` | Index page of *juntas de gobierno* minutes | PDF |

To support a new site, see
[Writing a provider](docs/ARCHITECTURE.md#writing-a-provider).

### Processors

| Processor | Reads | Does |
| :--- | :--- | :--- |
| `markdownify` | item content | Extracts the article's markdown from HTML items |
| `summarize` | `markdownify.markdown` | Summarizes the article with Ollama |
| `tagger` | `markdownify.markdown` | Extracts entity tags with Ollama |

### Remixers

| Remixer | Artifact | Does |
| :--- | :--- | :--- |
| `telegram` | `state` | Posts summarized items (title, summary, link) to a Telegram chat, at most one per source every `interval` minutes (`bot_token`, `chat_id`, `interval`) |
| `rssfeed` | `feed` | RSS feed of the newest items in scope (`title`, `link`, `description`, `max_items`) |
| `grouping_singlelink` | `current` | Clusters tagged items into events (single-link) |
| `grouping_avglink` | `current` | Clusters tagged items into events (average-link) |
| `grouping_embeddings` | `current` | Clusters tagged items by tag overlap blended with tag embeddings (Ollama, single-link) |

Artifacts are rebuilt each time their remixer runs, so between runs they can
lag behind the stored items.

`telegram` keeps a FIFO queue per source. Each run queues the summarized
items not queued or posted yet, oldest first, and posts the head of every
queue whose source last posted at least `interval` minutes ago, so run
`remix telegram` periodically (e.g. from cron every few minutes). Its first
run only records the time: by default, only items published after it are
queued. To queue older items, pass `--since` or `--source` with `--uid`. An
item is never posted twice. A failed post is logged and stays at the head of
its queue, holding back that source until it succeeds; the queue, the posted
items and the last post per source are in `artifact telegram state`.

## Data and backups

Everything lives in two places: the SQLite database (`db.uri`) and the
content directory (`db.content_dir`), which holds article contents,
annotation values and artifacts. Back up both together. The database runs in
WAL mode, so back it up with SQLite's backup API (or with no process using
it), not by copying `data.db` alone.

The schema is created, never migrated: after an upgrade that changes it,
move the old `data.db` and `content_dir` aside and re-import.

Run one newsmerger command at a time against the same data.

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
it (the publish-news flow).

## Development

```sh
uv run python -m unittest discover -s tests
uv run ruff check --fix .
uv run ruff format .
```

See [docs/SPECIFICATION.md](docs/SPECIFICATION.md) for the full definition
of the application, [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the
internals and how to write a provider, [docs/decisions/](docs/decisions/) for the recorded
design decisions and [PLAN.md](PLAN.md) for pending work.
