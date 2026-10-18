#!/usr/bin/env python
"""Standalone, read-only experiment: does embedding each item's tags add
anything over plain tag-Jaccard for event grouping?

This is NOT wired into the processor lifecycle, the CLI, or the DB schema.
It reads existing source items and their "tagger" annotations through
Application and does everything else (embedding + scoring +
clustering) in memory/on-disk-cache; nothing is written back to the DB.

Why this exists: the grouping_singlelink/grouping_avglink remixers cluster
purely on tag-Jaccard, which misses synonym/variant tags ("BCE" vs "Banco Central
Europeo") since it requires literal string overlap. This script embeds the
*same* tags (via Ollama, matching tagger.py's local-model setup - no new
external dependency) and blends cosine similarity with Jaccard, so it's
possible to see, on real data, whether that actually changes groupings for
the better or just adds noise/cost. See conversation notes: since the
embedding is derived from the same tags as Jaccard rather than the full
article text, the two signals are expected to correlate a fair amount -
this script's "candidate synonym pairs" report exists specifically to
check whether there's a real independent signal here before promoting
anything into a processor.

Usage:
    python scripts/group_events_embeddings.py --config config.yaml
    python scripts/group_events_embeddings.py --config config.yaml --embedding-weight 0.4
    python scripts/group_events_embeddings.py --config config.yaml --review-threshold 0.75
    DISABLE_RICH=1 python scripts/group_events_embeddings.py --config config.yaml

Requires an Ollama server reachable at OLLAMA_API_BASE (default
http://localhost:11434, authenticated with OLLAMA_API_KEY if set) with an
embedding-capable model pulled (e.g. `ollama pull nomic-embed-text`).
"""  # noqa: EXE001

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import time
from datetime import UTC, datetime, timedelta
from itertools import combinations
from pathlib import Path

import ollama
import rich_click as click
from foundation.loglib import setup_logger

from newsmerger.app import Application
from newsmerger.consts import DISABLE_RICH, PACKAGE_NAME
from newsmerger.llm import DEFAULT_OLLAMA_URL, ollama_client
from newsmerger.models import ItemKey, ProcessingScope
from newsmerger.remixers._grouping_scoring import (
    ScoredItem,
    UnionFind,
    item_ref,
    jaccard,
    tagged_items,
    time_decay,
)

LOGGER = logging.getLogger(f"{PACKAGE_NAME}.tools.group_events_embeddings")

DEFAULT_EMBEDDING_MODEL = os.environ.get("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


# --- Embedding generation (Ollama, disk-cached) -----------------------------


class EmbeddingCache:
    """Flat JSON file: {"model:sha256(tag-text)": [floats]}.

    Deliberately simple - this is a throwaway experiment cache, not the
    real annotation store. Keyed on the *text actually embedded*, so
    changing the tag-joining strategy or the model invalidates naturally
    (different key), no explicit version field needed at this stage.
    """

    def __init__(self, path: Path):
        self.path = path
        self._data: dict[str, list[float]] = {}
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text())
            except (json.JSONDecodeError, OSError):
                LOGGER.warning(
                    f"could not read embedding cache at {self.path}, starting fresh"
                )
                self._data = {}

    @staticmethod
    def _key(model: str, text: str) -> str:
        return f"{model}:{hashlib.sha256(text.encode()).hexdigest()}"

    def get(self, model: str, text: str) -> list[float] | None:
        return self._data.get(self._key(model, text))

    def set(self, model: str, text: str, embedding: list[float]) -> None:
        self._data[self._key(model, text)] = embedding

    def save(self) -> None:
        self.path.write_text(json.dumps(self._data))


def tags_to_text(raw_tags: tuple[str, ...]) -> str:
    """Join tags into the string actually sent for embedding. Sorted for a
    stable cache key regardless of tag order; comma-separated reads
    naturally to an embedding model, unlike e.g. a Python list repr."""
    return ", ".join(sorted(raw_tags, key=str.lower))


def embed_text(
    client: ollama.Client, model: str, text: str, *, max_attempts: int = 3
) -> list[float]:
    """Call Ollama's embedding endpoint with a small retry/backoff - this is
    a live network call per item (minus cache hits), and Ollama can be
    momentarily busy generating something else."""
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            resp = client.embed(model=model, input=text)
            return list(resp.embeddings[0])
        except Exception as e:  # noqa: BLE001 - broad on purpose, see retry below
            last_error = e
            if attempt < max_attempts:
                delay = 2 ** (attempt - 1)
                LOGGER.warning(
                    f"embedding call failed (attempt {attempt}/{max_attempts}): {e} "
                    f"- retrying in {delay}s"
                )
                time.sleep(delay)
    assert last_error is not None
    raise last_error


def build_embeddings(
    items: list[ScoredItem],
    *,
    client: ollama.Client,
    model: str,
    cache: EmbeddingCache,
) -> dict[ItemKey, list[float]]:
    """item key -> embedding, one call per distinct tag-text not already cached."""
    embeddings: dict[ItemKey, list[float]] = {}
    cache_hits = 0
    cache_misses = 0

    for si in items:
        text = tags_to_text(si.raw_tags)
        cached = cache.get(model, text)
        if cached is not None:
            embeddings[si.item.key] = cached
            cache_hits += 1
            continue

        embedding = embed_text(client, model, text)
        cache.set(model, text, embedding)
        embeddings[si.item.key] = embedding
        cache_misses += 1

    LOGGER.info(f"embeddings: {cache_hits} cache hits, {cache_misses} computed")
    return embeddings


# --- Scoring / clustering ----------------------------------------------------


def build_matrices(
    items: list[ScoredItem],
    embeddings: dict[ItemKey, list[float]],
    tau_hours: float | None,
) -> tuple[list[list[float]], list[list[float]], list[list[float]]]:
    """Three separate n x n matrices (diagonal unused): Jaccard, cosine, and
    time-decay. Kept apart rather than pre-combined so different
    --embedding-weight values can be explored without recomputing
    embeddings or re-walking all pairs."""
    n = len(items)
    jaccard_m = [[0.0] * n for _ in range(n)]
    cosine_m = [[0.0] * n for _ in range(n)]
    decay_m = [[1.0] * n for _ in range(n)]

    for i, j in combinations(range(n), 2):
        jv = jaccard(items[i].tags, items[j].tags)
        cv = max(
            cosine_similarity(
                embeddings[items[i].item.key], embeddings[items[j].item.key]
            ),
            0.0,
        )
        dv = (
            time_decay(
                items[i].item.published_at, items[j].item.published_at, tau_hours
            )
            if tau_hours is not None
            else 1.0
        )
        jaccard_m[i][j] = jaccard_m[j][i] = jv
        cosine_m[i][j] = cosine_m[j][i] = cv
        decay_m[i][j] = decay_m[j][i] = dv

    return jaccard_m, cosine_m, decay_m


def combine_matrix(
    jaccard_m: list[list[float]],
    cosine_m: list[list[float]],
    decay_m: list[list[float]],
    *,
    embedding_weight: float,
) -> list[list[float]]:
    """combined = (embedding_weight * cosine + (1 - embedding_weight) * jaccard) * decay
    embedding_weight=0.0 reproduces the plain-Jaccard baseline exactly."""
    n = len(jaccard_m)
    combined = [[0.0] * n for _ in range(n)]
    for i, j in combinations(range(n), 2):
        blended = (
            embedding_weight * cosine_m[i][j] + (1 - embedding_weight) * jaccard_m[i][j]
        )
        score = blended * decay_m[i][j]
        combined[i][j] = combined[j][i] = score
    return combined


def cluster_from_matrix(
    matrix: list[list[float]], *, min_score: float
) -> list[list[int]]:
    """Single-link connected components over a precomputed score matrix -
    same transitivity tradeoff as the grouping_singlelink remixer."""
    n = len(matrix)
    uf = UnionFind(n)
    for i, j in combinations(range(n), 2):
        if matrix[i][j] >= min_score:
            uf.union(i, j)

    groups_by_root: dict[int, list[int]] = {}
    for idx in range(n):
        groups_by_root.setdefault(uf.find(idx), []).append(idx)
    return list(groups_by_root.values())


def group_id_map(groups: list[list[int]]) -> dict[int, int]:
    """item-index -> group-index, for membership comparisons between two
    different clusterings of the same item list."""
    return {idx: gi for gi, members in enumerate(groups) for idx in members}


# --- Diagnostics: does the embedding signal add anything new? ---------------


def find_candidate_synonym_pairs(
    items: list[ScoredItem],
    jaccard_m: list[list[float]],
    cosine_m: list[list[float]],
    *,
    review_threshold: float,
    top_n: int,
) -> list[tuple[int, int, float]]:
    """Pairs with ZERO tag overlap but high cosine similarity - the exact
    case Jaccard structurally cannot catch. This is the list worth reading
    by hand: each one is either "yes, embeddings caught a real synonym/
    related-entity match" or "no, this is embedding noise" - and the ratio
    between those two outcomes is the actual answer to "is this worth it".
    """
    n = len(items)
    candidates = [
        (i, j, cosine_m[i][j])
        for i, j in combinations(range(n), 2)
        if jaccard_m[i][j] == 0.0 and cosine_m[i][j] >= review_threshold
    ]
    candidates.sort(key=lambda t: -t[2])
    return candidates[:top_n]


def diff_group_membership(
    items: list[ScoredItem],
    baseline_groups: list[list[int]],
    hybrid_groups: list[list[int]],
) -> list[str]:
    """Human-readable list of items whose group composition changed between
    the plain-Jaccard baseline and the hybrid clustering."""
    baseline_map = group_id_map(baseline_groups)
    hybrid_map = group_id_map(hybrid_groups)

    baseline_members = {
        gi: frozenset(members) for gi, members in enumerate(baseline_groups)
    }
    hybrid_members = {
        gi: frozenset(members) for gi, members in enumerate(hybrid_groups)
    }

    lines = []
    for idx, si in enumerate(items):
        b_group = baseline_members[baseline_map[idx]]
        h_group = hybrid_members[hybrid_map[idx]]
        if b_group != h_group:
            lines.append(
                f"  '{si.item.title[:60]}' - baseline group size={len(b_group)}, "
                f"hybrid group size={len(h_group)}"
            )
    return lines


# --- Rendering ---------------------------------------------------------------


def render_groups(label: str, items: list[ScoredItem], groups: list[list[int]]) -> None:
    multi_groups = sorted((g for g in groups if len(g) > 1), key=len, reverse=True)
    singleton_count = sum(1 for g in groups if len(g) == 1)
    header = (
        f"[{label}] {len(items)} items -> {len(multi_groups)} multi-item groups, "
        f"{singleton_count} singletons"
    )

    if DISABLE_RICH:
        print(header)
        for gi, member_idxs in enumerate(multi_groups, start=1):
            print(f"  --- Group {gi} ({len(member_idxs)} items) ---")
            for idx in member_idxs:
                si = items[idx]
                print(f"    {si.item.title[:70]} | tags: {sorted(si.tags)}")
        print()
        return

    from rich.console import Console

    console = Console()
    console.print(f"[bold]{header}[/bold]")
    for gi, member_idxs in enumerate(multi_groups, start=1):
        console.print(f"  [cyan]Group {gi}[/cyan] ({len(member_idxs)} items)")
        for idx in member_idxs:
            si = items[idx]
            console.print(f"    {si.item.title[:70]} | tags: {sorted(si.tags)}")
    console.print()


def render_candidate_pairs(
    items: list[ScoredItem], candidates: list[tuple[int, int, float]]
) -> None:
    if not candidates:
        print("No zero-Jaccard/high-cosine candidate pairs found at this threshold.\n")
        return

    header = (
        f"{len(candidates)} candidate synonym pair(s) (jaccard=0, cosine >= threshold):"
    )
    if DISABLE_RICH:
        print(header)
        for i, j, cos in candidates:
            print(f"  cosine={cos:.3f}")
            print(f"    A: {items[i].item.title[:60]} | tags: {sorted(items[i].tags)}")
            print(f"    B: {items[j].item.title[:60]} | tags: {sorted(items[j].tags)}")
        print()
        return

    from rich.console import Console

    console = Console()
    console.print(f"[bold]{header}[/bold]")
    for i, j, cos in candidates:
        console.print(f"  cosine=[yellow]{cos:.3f}[/yellow]")
        console.print(
            f"    A: {items[i].item.title[:60]} | tags: {sorted(items[i].tags)}"
        )
        console.print(
            f"    B: {items[j].item.title[:60]} | tags: {sorted(items[j].tags)}"
        )
    console.print()


def build_json_payload(
    items: list[ScoredItem],
    baseline_groups: list[list[int]],
    hybrid_groups: list[list[int]],
    candidates: list[tuple[int, int, float]],
    *,
    params: dict,
) -> dict:
    def groups_payload(groups: list[list[int]]) -> list[dict]:
        return [
            {
                "members": [
                    {"ref": item_ref(items[idx].item), "title": items[idx].item.title}
                    for idx in member_idxs
                ]
            }
            for member_idxs in sorted(groups, key=len, reverse=True)
            if len(member_idxs) > 1
        ]

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "params": params,
        "baseline_groups": groups_payload(baseline_groups),
        "hybrid_groups": groups_payload(hybrid_groups),
        "candidate_synonym_pairs": [
            {
                "a": item_ref(items[i].item),
                "b": item_ref(items[j].item),
                "a_title": items[i].item.title,
                "b_title": items[j].item.title,
                "cosine": cos,
            }
            for i, j, cos in candidates
        ],
    }


@click.command()
@click.option(
    "-c",
    "--config",
    "config_path",
    type=Path,
    default=None,
    help="Path to config.yaml (defaults to Config() built-in defaults)",
)
@click.option(
    "--days", type=int, default=7, help="Pool: items published in the last N days"
)
@click.option(
    "--min-score",
    type=float,
    default=0.3,
    help="Minimum combined score to draw an edge between two items (applied to both baseline and hybrid)",
)
@click.option(
    "--tau-hours", type=float, default=24.0, help="Time-decay time constant, in hours"
)
@click.option(
    "--no-time-decay",
    "no_time_decay",
    is_flag=True,
    default=False,
    help="Ignore publish-time proximity entirely",
)
@click.option(
    "--embedding-model",
    default=DEFAULT_EMBEDDING_MODEL,
    help="Ollama embedding model name (default: $OLLAMA_EMBEDDING_MODEL or 'nomic-embed-text')",
)
@click.option(
    "--embedding-weight",
    type=float,
    default=0.5,
    help="Weight of cosine similarity vs Jaccard in the hybrid score (0=pure Jaccard, 1=pure embeddings)",
)
@click.option(
    "--review-threshold",
    type=float,
    default=0.8,
    help="Cosine threshold for the zero-Jaccard 'candidate synonym pairs' report",
)
@click.option(
    "--top-pairs",
    type=int,
    default=20,
    help="Max candidate synonym pairs to show",
)
@click.option(
    "--cache-file",
    type=Path,
    default=Path(".embedding_cache.json"),
    help="Disk cache for embeddings, keyed by model+tag-text",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
)
@click.option("--verbose", is_flag=True, default=False)
@click.option("--log-level", default="INFO")
def main(
    config_path,
    days,
    min_score,
    tau_hours,
    no_time_decay,
    embedding_model,
    embedding_weight,
    review_threshold,
    top_pairs,
    cache_file,
    output_format,
    verbose,
    log_level,
):
    setup_logger(PACKAGE_NAME)
    logging.getLogger(PACKAGE_NAME).setLevel(
        logging.DEBUG if verbose else log_level.upper()
    )

    scope = ProcessingScope(since=datetime.now(UTC) - timedelta(days=days))
    # Read-only: never create/alter schema from this tool.
    with Application.from_config_file(config_path, create_schema=False) as app:
        source_items = app.get_items(scope)
        tags = app.get_annotation_values(source_items, processor="tagger", key="tags")
    items = tagged_items(source_items, tags)

    if not items:
        LOGGER.warning("no tagged items found in scope - nothing to group")
        return

    client = ollama_client(
        os.environ.get("OLLAMA_API_BASE", DEFAULT_OLLAMA_URL),
        os.environ.get("OLLAMA_API_KEY"),
    )

    cache = EmbeddingCache(cache_file)
    embeddings = build_embeddings(
        items, client=client, model=embedding_model, cache=cache
    )
    cache.save()

    effective_tau = None if no_time_decay else tau_hours
    jaccard_m, cosine_m, decay_m = build_matrices(items, embeddings, effective_tau)

    baseline_matrix = combine_matrix(jaccard_m, cosine_m, decay_m, embedding_weight=0.0)
    hybrid_matrix = combine_matrix(
        jaccard_m, cosine_m, decay_m, embedding_weight=embedding_weight
    )

    baseline_groups = cluster_from_matrix(baseline_matrix, min_score=min_score)
    hybrid_groups = cluster_from_matrix(hybrid_matrix, min_score=min_score)

    candidates = find_candidate_synonym_pairs(
        items, jaccard_m, cosine_m, review_threshold=review_threshold, top_n=top_pairs
    )

    if output_format == "json":
        params = {
            "days": days,
            "min_score": min_score,
            "tau_hours": effective_tau,
            "embedding_model": embedding_model,
            "embedding_weight": embedding_weight,
            "review_threshold": review_threshold,
        }
        payload = build_json_payload(
            items, baseline_groups, hybrid_groups, candidates, params=params
        )
        print(json.dumps(payload, indent=2))
        return

    render_groups("baseline: pure Jaccard", items, baseline_groups)
    render_groups(
        f"hybrid: {1 - embedding_weight:.2f}*jaccard + {embedding_weight:.2f}*cosine",
        items,
        hybrid_groups,
    )

    diff_lines = diff_group_membership(items, baseline_groups, hybrid_groups)
    print(f"Items whose grouping changed: {len(diff_lines)}")
    for line in diff_lines:
        print(line)
    print()

    render_candidate_pairs(items, candidates)


if __name__ == "__main__":
    main()
