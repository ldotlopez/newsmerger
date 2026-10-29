# 0011: Environment overrides, relative paths and one storage directory

- **Status:** accepted
- **Date:** 2026-10-29

## Context

The configuration came only from the YAML file, with `${VAR}` references for
secrets. Setting a key from the environment meant writing a reference for it
in the file first. The database URI, the content directory and the cache
directory were three separate keys, each defaulting to a user directory, and
paths had to be absolute to be independent of where newstool was started.

## Decision

- **`Config` is a pydantic-settings `BaseSettings`.** Any key can be set by a
  `NEWSTOOL_`-prefixed variable, `__` nesting (`NEWSTOOL_CACHE__EXPIRATION`),
  from the environment or from the `.env` next to the config file (one
  environment, the process's over the file's: unknown `NEWSTOOL_*` names are
  ignored in both). Priority,
  highest first: environment, `.env`, YAML, aliases, defaults. Lists stay
  YAML-only.
- **Aliases** map well-known variables of external systems to a key, below the
  YAML so an ambient shell variable never overrides an explicit setting:
  `OLLAMA_HOST` to `plugins.ollama.api_base`, `OLLAMA_API_KEY` to
  `plugins.ollama.api_key`. `OLLAMA_HOST` is converted to a URL the way Ollama
  reads it: a bare host gets `http://` and port 11434, `0.0.0.0` becomes
  `localhost`.
- **`${VAR}` templates are unchanged** and apply to the YAML only. The other
  sources are taken literally: the shell and dotenv already expanded them, and
  a second pass would break secrets containing `$`.
- **Paths are relative to the config file.** `storage_dir` and `cache_dir` are
  `ConfigPath`s: `~` is expanded and a relative path is anchored at the config
  file's directory (the current directory without a file).
- **One storage directory.** `storage_dir` (default: the user data directory,
  as before) holds `data.db` and `content/`; `cache_dir` (default: the user
  cache directory) holds the HTTP cache. `db.uri`, `db.content_dir` and
  `cache.base_dir` are removed.

## Consequences

- Default locations do not change, so existing data needs no migration.
- A config with `db:` or `cache.base_dir` is rejected (unknown key). A custom
  database location must become a `storage_dir`: move `data.db` and `content/`
  into it.
- A plugin's own well-known variables need an entry in `ENV_ALIASES`.
