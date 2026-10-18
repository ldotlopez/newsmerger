# newsmerger

Aggregates local news (Castelló) from several websites, stores the articles,
and runs processing steps over them: markdown extraction, LLM summaries and
tagging, Telegram publishing, event grouping and RSS feeds.

It works in three phases: **import** (providers fetch items from sources),
**enrich** (processors annotate each item) and **remix** (remixers build
artifacts from many items).

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- The internal `foundation` library (installed as a regular dependency)
- An Ollama server for the `summarize` and `tagger` processors

## Install

```sh
uv sync
```

## Configuration

Pass a YAML file with `-c/--config`. Every section is optional.

```yaml
sources:
  - id: castellonplaza               # required, stable: part of each item's key
    name: Castellón Plaza
    provider: plaza                  # module in newsmerger/providers/
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
  - name: telegram
    params:
      bot_token: ${TELEGRAM_BOT_TOKEN}
      chat_id: ${TELEGRAM_CHAT_ID}

remixers:                            # run in this order by `remix`
  - name: rssfeed
    params:
      title: Castelló news
```

`${VAR}` is replaced with the environment variable `VAR` when the file is
loaded, and a missing variable is an error. Pass secrets (API keys, bot
tokens) this way, never as literals. Write a literal `$` as `$$`.

Only configured processors and remixers can run. Their `params` go to the
plugin's constructor, and unknown params are rejected. Changing a plugin's
params never regenerates existing annotations.

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
```

`enrich` and `remix` accept `--source` (a source id), `--since`, `--until`
and `--limit`. `enrich --force` reprocesses everything in scope, ignored
items included, with fresh retry attempts.

Global options: `--log-level LEVEL` (default `info`; also accepts
`foundation.loglib` specs such as `info,db:debug`) and `-v/--verbose`
(`debug`). Set `DISABLE_RICH=1` for plain output: no colors, tables or
progress bars, one line per log record.

`enrich` runs `telegram` too when it is configured, and posts every
summarized item in scope that it hasn't posted yet. On a fresh database,
limit it with `--since`.

### Providers

`prensaiberica`, `prensaiberica_plain`, `castelloninformacion`, `plaza`,
`theguardian` (HTML articles) and `csjuntasgobierno` (PDF minutes).

### Processors

| Processor | Reads | Does |
| :--- | :--- | :--- |
| `markdownify` | item content | Extracts the article's markdown from HTML items |
| `summarize` | `markdownify.markdown` | Summarizes the article with Ollama |
| `tagger` | `markdownify.markdown` | Extracts entity tags with Ollama |
| `telegram` | `summarize.summary` | Posts title, summary and link to a Telegram chat, once per item |

### Remixers

| Remixer | Artifact | Does |
| :--- | :--- | :--- |
| `rssfeed` | `feed` | RSS feed of the newest items in scope (`title`, `link`, `description`, `max_items`) |
| `grouping_singlelink` | `current` | Clusters tagged items into events (single-link) |
| `grouping_avglink` | `current` | Clusters tagged items into events (average-link) |

## Data

- The SQLite database holds sources, item metadata, processing state, and
  references to annotations and artifacts.
- Contents live outside the database, in `content_dir`, one file per sha256:
  item contents (HTML, PDF, ...), annotation values (JSON) and artifacts.
  Text content is always stored as UTF-8.

The database runs in WAL mode, so back it up with SQLite's backup API (or
with no process using it), not by copying `data.db` alone. Back up
`content_dir` along with it.

The schema is created, never migrated: after a schema change, move the old
`data.db` and `content_dir` aside and re-import.

## Scripting

External tools use `Application`, the same core the CLI uses:

```python
from pathlib import Path

from newsmerger.app import Application

with Application.from_config_file(Path("config.yaml"), create_schema=False) as app:
    feed = app.get_artifact("rssfeed", "feed")  # None if it doesn't exist
```

`scripts/pipeline_url.py` imports one URL and runs a list of processors on
it (the publish-news flow); `scripts/group_events_embeddings.py` is an
experiment comparing tag embeddings with plain tag overlap for grouping.

## Development

```sh
uv run python -m unittest discover -s tests
uv run ruff check --fix .
uv run ruff format .
```

Set `NEWSMERGER_PICKLE_CACHE=1` to cache each source's fetched items in a
local `<source id>.pkl` file while developing providers.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the internals,
[docs/decisions/](docs/decisions/) for the recorded design decisions and
[PLAN.md](PLAN.md) for pending work.
