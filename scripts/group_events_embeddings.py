#!/usr/bin/env python
"""Standalone, read-only experiment: does embedding each item's tags add
anything over plain tag-Jaccard for event grouping?

This is NOT wired into the processor lifecycle, the CLI, or the DB schema.
It reads existing source items and their "tagger" annotations through the
normal Database API and does everything else (embedding + scoring +
clustering) in memory/on-disk-cache; nothing is written back to the DB.

Why this exists: group_events.py/group_events_avglink.py cluster purely on
tag-Jaccard, which misses synonym/variant tags ("BCE" vs "Banco Central
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

Requires an Ollama server reachable at OLLAMA_API_BASE (default matches
tagger.py: http://localhost:11343 - note this is NOT Ollama's usual default
port, 11434; kept identical to tagger.py's existing default for
consistency, not verified here) with an embedding-capable model pulled
(e.g. `ollama pull nomic-embed-text`).
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import logging
import math
import os
import time
from datetime import datetime, timedelta, timezone
from itertools import combinations
from pathlib import Path

import ollama
import rich_click as click
from foundation.logging import setup as setup_logging

from newsmerger.config import Config
from newsmerger.consts import PACKAGE_NAME
from newsmerger.db import Database, ProcessingScope
from newsmerger.models import SourceItem

LOGGER = logging.getLogger(f"{PACKAGE_NAME}.tools.group_events_embeddings")

DISABLE_RICH = os.environ.get("DISABLE_RICH", "0").lower() not in ("0", "false", "")

DEFAULT_EMBEDDING_MODEL = os.environ.get("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")


@dataclasses.dataclass(frozen=True)
class ScoredItem:
    item: SourceItem
    tags: frozenset[str]  # lowercased, for Jaccard - matches the other scripts
    raw_tags: tuple[str, ...]  # original case/order, for the embedding text


def load_tagged_items(db: Database, scope: ProcessingScope) -> list[ScoredItem]:
    """Fetch items in scope along with their "tagger" tags annotation.

    Items with no tags annotation yet are skipped entirely - they can't
    participate in tag-based grouping either way.
    """
    items = db.get_source_items(scope=scope)
    result = []
    for item in items:
        annotations = db.get_annotations(item, processor="tagger", key="tags")
        tags = annotations.get("tagger", {}).get("tags") or []
        if not tags:
            LOGGER.debug(f"skipping '{item.title}' - no tags annotation")
            continue
        result.append(
            ScoredItem(
                item=item,
                tags=frozenset(t.lower() for t in tags),
                raw_tags=tuple(tags),
            )
        )

    LOGGER.info(f"{len(result)}/{len(items)} items in scope have tags")
    return result


def jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    if not a or not b:
        return 0.0
    intersection = a & b
    if not intersection:
        return 0.0
    return len(intersection) / len(a | b)


def time_decay(a: datetime | None, b: datetime | None, tau_hours: float) -> float:
    if a is None or b is None:
        return 1.0
    delta_hours = abs((a - b).total_seconds()) / 3600.0
    return math.exp(-delta_hours / tau_hours)


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
) -> dict[str, list[float]]:
    """uid -> embedding, one call per distinct tag-text not already cached."""
    embeddings: dict[str, list[float]] = {}
    cache_hits = 0
    cache_misses = 0

    for si in items:
        text = tags_to_text(si.raw_tags)
        cached = cache.get(model, text)
        if cached is not None:
            embeddings[si.item.uid] = cached
            cache_hits += 1
            continue

        embedding = embed_text(client, model, text)
        cache.set(model, text, embedding)
        embeddings[si.item.uid] = embedding
        cache_misses += 1

    LOGGER.info(f"embeddings: {cache_hits} cache hits, {cache_misses} computed")
    return embeddings


# --- Scoring / clustering ----------------------------------------------------


def build_matrices(
    items: list[ScoredItem], embeddings: dict[str, list[float]], tau_hours: float | None
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
                embeddings[items[i].item.uid], embeddings[items[j].item.uid]
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


class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> None:
        rx, ry = self.find(x), self.find(y)
        if rx != ry:
            self.parent[rx] = ry


def cluster_from_matrix(
    matrix: list[list[float]], *, min_score: float
) -> list[list[int]]:
    """Single-link connected components over a precomputed score matrix -
    same transitivity tradeoff as group_events.py."""
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
                    {"uid": items[idx].item.uid, "title": items[idx].item.title}
                    for idx in member_idxs
                ]
            }
            for member_idxs in sorted(groups, key=len, reverse=True)
            if len(member_idxs) > 1
        ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "params": params,
        "baseline_groups": groups_payload(baseline_groups),
        "hybrid_groups": groups_payload(hybrid_groups),
        "candidate_synonym_pairs": [
            {
                "a_uid": items[i].item.uid,
                "b_uid": items[j].item.uid,
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
    setup_logging(PACKAGE_NAME)
    logging.getLogger(PACKAGE_NAME).setLevel(
        logging.DEBUG if verbose else log_level.upper()
    )

    config = Config.from_file(config_path) if config_path else Config()
    # Read-only: never create/alter schema from this tool.
    db = Database(config.db.uri, create_schema=False)

    scope = ProcessingScope(since=datetime.now(timezone.utc) - timedelta(days=days))
    items = load_tagged_items(db, scope)

    if not items:
        LOGGER.warning("no tagged items found in scope - nothing to group")
        return

    api_base = os.environ.get("OLLAMA_API_BASE", "http://localhost:11343")
    api_key = os.environ.get("OLLAMA_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    client = ollama.Client(host=api_base, headers=headers)

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
