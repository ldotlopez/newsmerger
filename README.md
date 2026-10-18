# newsmerger

Aggregates local news (Castelló) from several websites, stores the articles,
and runs processing steps over them: markdown extraction, LLM summaries and
tagging, event grouping, RSS feeds and Telegram publishing.

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
  - name: Castellón Plaza
    provider: plaza                  # module in newsmerger/providers/
    url: https://castellonplaza.com/castellon9/

db:
  uri: sqlite:////path/to/data.db    # default: <user data dir>/newsmerger/data.db
  content_dir: /path/to/content      # default: <user data dir>/newsmerger/content

cache:
  expiration: 21600                  # HTTP cache lifetime, in seconds

processors:                          # default params per processor
  - name: summarize
    params:
      model: gemma4:12b

pipelines:                           # ordered processor steps
  - name: publish-news
    steps:
      - processor: markdownify
      - processor: summarize
      - processor: telegram
        params:
          chat_id: "..."
```

Step `params` override the processor's defaults. Keep secrets (API keys, bot
tokens) out of files under version control.

## Usage

```sh
# Import every configured source
uv run newsmerger -c config.yaml import

# Import a single article URL with a given provider
uv run newsmerger -c config.yaml import-url -p prensaiberica_plain <url>

# Import one URL and run a configured pipeline on it
uv run newsmerger -c config.yaml pipeline-url publish-news -p plaza <url>

# Run one processor over stored items
uv run newsmerger -c config.yaml process markdownify --source "Castellón Plaza" --limit 20
```

`process` accepts `--source`, `--since`, `--until`, `--limit` and `--force`
(reprocess items already done or ignored).

### Providers

`prensaiberica`, `prensaiberica_plain`, `castelloninformacion`, `plaza`,
`theguardian` (HTML articles) and `csjuntasgobierno` (PDF minutes).

### Processors

| Processor | Kind | Does |
| :--- | :--- | :--- |
| `markdownify` | item | Extracts markdown and plain text from HTML items |
| `summarize` | item | Summarizes the extracted text with Ollama |
| `tagger` | item | Extracts entity tags with Ollama |
| `telegram` | item | Posts title, summary and link to a Telegram chat |
| `rssfeed` | artifact | Builds an RSS feed from the items in scope |
| `grouping_singlelink` | artifact | Clusters items into events (single-link) |
| `grouping_avglink` | artifact | Clusters items into events (average-link) |

## Data

- The SQLite database holds sources, items, processing state, annotations
  and artifacts.
- Item contents (HTML, PDF, ...) live outside the database, in `content_dir`,
  one file per sha256. Text content is always stored as UTF-8.

The database runs in WAL mode, so back it up with SQLite's backup API (or
with no process using it), not by copying `data.db` alone.

## Scripting

Scripts build the same core the CLI uses:

```python
from pathlib import Path

from newsmerger.app import App

with App.from_config_file(Path("config.yaml"), create_schema=False) as app:
    feed = app.db.get_artifact("rssfeed", "feed")
```

## Development

```sh
uv run python -m unittest discover -s tests
uv run ruff check --fix .
uv run ruff format .
```

Set `NEWSMERGER_PICKLE_CACHE=1` to cache each source's fetched items in a
local `<source name>.pkl` file while developing providers.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the internals and
[PLAN.md](PLAN.md) for pending work.
