# newsmerger — Working Plan

Ordered smallest-and-most-necessary → biggest-and-least-necessary.
Update statuses as we progress: `[ ]` todo, `[x]` done, `[~]` in progress.

1. [x] **Use `SourceItem.from_data()`** instead of inline `SourceItem(source=provider.source, **item_data.model_dump())` in `App.import_source`.
   Helper already exists in `models.py` for this exact purpose — avoids duplicate construction logic.
   *(Done as part of the pickle-cache edit to `import_source`.)*

2. [x] **Stop converting to markdown at ingestion — keep max context, drop only cruft.**
   Principle: don't throw away structure a postprocessor might want later; only prune identifiable cruft (nav/ads/paywall/related-content/tracking). Mechanism: `foundation.scrapelib.prune_to_spine(node, stop_at=None)` (added manually by user) — keeps `main_node`'s ancestor chain up to root with attributes intact (`lang`, `itemtype`, wrapper classes), drops siblings not on that path. Combined with `drop_selectors` for cruft inside `main_node`'s own subtree. Stores resulting HTML in `content`, not markdown. Markdown generation becomes a later postprocessor's job — deferred, see "Bigger" section below.

   - [x] `prensaiberica.py` — `main_node` (`#main-content`) → `drop_selectors` (list) → `prune_to_spine(main)` → `str(root)` stored. Dead `extract` import removed.
   - [x] `castelloninformacion.py` — `main_node` (`article.post`) → `drop_selectors(article, [".td-is-sticky"])` → `prune_to_spine(article)` → `str(root)` stored.
     - Correction (found on review): uses the *same* `drop_selectors` (plural, list) helper as `prensaiberica.py`, just called with a one-item list (`[".td-is-sticky"]`) — there is no separate singular `drop_selector` function. Earlier note claiming a deliberately different API surface was wrong.
     - Note: only one selector dropped so far — worth a visual sanity check of `article.post` on a live/sample page to confirm no related-posts/inline-ad/author-bio widgets are still nested inside before considering this fully tuned.

3. [ ] **Confirm `save_source_items` is dead code** now that `upsert_source_items` is wired in via `cli.py`. If no other caller, remove it (and the never-called insert-only path in `DBSourceItem.update`).

4. [ ] **Confirm `_get_or_create_source` (singular)** in `db.py` is unused — `save_source_items`/`upsert_source_items` both call `_get_or_create_source_bulk` directly. Remove if truly dead, or find the caller.

5. [ ] **Resolve the large commented-out block** in `_get_or_create_source_bulk` (`db.py`, ~30 lines) — superseded by `_get_or_create_bulk`. Delete, or confirm intentional and keep as reference.

6. [ ] **Add `--verbose` / `--log-level` options to `cli.py`.**
   Project CLI conventions mandate these; currently `LOGGER.setLevel(logging.DEBUG)` is hardcoded with no flags.

7. [ ] **Add `DISABLE_RICH` environment variable support** (per CLI conventions doc).

8. [ ] **Introduce `rich` for CLI output** (progress/status during import, error summaries), via `rich_click` (already used as the `click` import in `cli.py` for its help/usage formatting) for better integration between the two libraries, rather than importing plain `rich` alongside it. Additive — nothing currently violates the convention since there's no rich output yet to disable.

9. [ ] **`castelloninformacion.py` cosmetic cleanup**  stray commented-out `tags`/`section` extraction lines (`# tags = head_meta_get_value_by_property(...)`, `# section = ...`) left over from when it tracked `prensaiberica.py`'s fields; either wire them up or drop them. (Earlier note about an unused `# from readability import Document` import was stale — that import isn't in the file anymore.) No functional impact.

10. [ ] **`csjuntasgobierno.py`** — explicitly out of scope per project instructions ("ignore for now"). No action.

---

## Done

- [x] **Swap `save_source_items` → `upsert_source_items`** in `App.import_source` (`cli.py`). Insert-only save silently no-op'd on re-import of already-seen items; upsert diff-updates them properly.
- [x] **Gate the debug pickle dump behind `NEWSMERGER_PICKLE_CACHE`** env var in `App.import_source` (`cli.py`). If set and not `0`/`false`/empty: load from `{source_name}.pkl` if present, else fetch real data via `provider.retrieve_items()`; always write the pickle back afterward when caching is enabled. Unconditional dump removed.

---

## Bigger, not really necessary yet (flagged, not scheduled)

- **Markdown-generation postprocessor** — reads the cleaned HTML stored per item 2 above and converts to markdown for consumers. No consumer exists yet in this codebase; deferred until ingestion path is solid.
- **General tagging/summarizing/querying post-processing pipeline** (per project description).
- **Alembic migrations** — not needed until there's an actual schema change to migrate.
- **Generalizing `BaseProvider`/`IndexSiteProvider`** for non-news "generic information" sources — speculative; wait for a second concrete use case.

---

*Last updated: 2026-07-17*
