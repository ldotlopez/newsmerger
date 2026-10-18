#!/usr/bin/env python
"""Standalone, read-only experiment: group source items into event clusters
using average-link agglomerative clustering, instead of the single-link
(connected-components) approach in group_events.py.

Why a separate script rather than a flag on group_events.py: the clustering
algorithm itself is different (iterative merge-the-best-pair-of-clusters vs.
one-shot union-find over individual edges), not just a parameter, so keeping
them as separate scripts keeps each one simple to read end-to-end.

Difference vs. group_events.py's single-link/connected-components:
    single-link merges two components the moment ANY one pair between them
    clears the threshold - one loosely-related "bridge" item can chain two
    otherwise-unrelated groups together.
    average-link instead requires the AVERAGE score across all cross-pairs
    between two clusters to clear the threshold before merging them, so a
    merge has to be justified by the whole group, not by a single edge.
    This still produces a hard partition (each item in exactly one group).

Usage:
    python scripts/group_events_avglink.py --config config.yaml
    python scripts/group_events_avglink.py --config config.yaml --days 3 --min-score 0.4
    python scripts/group_events_avglink.py --config config.yaml --no-time-decay
    DISABLE_RICH=1 python scripts/group_events_avglink.py --config config.yaml
"""  # noqa: EXE001

from __future__ import annotations

import json
import logging
import math
import os
from datetime import UTC, datetime, timedelta
from itertools import combinations
from pathlib import Path

import rich_click as click
from foundation.loglib import setup_logger

from newsmerger.app import App
from newsmerger.consts import PACKAGE_NAME
from newsmerger.db import ProcessingScope
from newsmerger.processors._grouping_scoring import ScoredItem, load_tagged_items

LOGGER = logging.getLogger(f"{PACKAGE_NAME}.tools.group_events_avglink")

DISABLE_RICH = os.environ.get("DISABLE_RICH", "0").lower() not in ("0", "false", "")


def jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    if not a or not b:
        return 0.0
    intersection = a & b
    if not intersection:
        return 0.0
    return len(intersection) / len(a | b)


def time_decay(a: datetime | None, b: datetime | None, tau_hours: float) -> float:
    """exp(-delta/tau): 1.0 for simultaneous items, decaying towards 0 as the
    gap between publish times grows. Missing timestamps don't penalize -
    tag overlap alone decides in that case.
    """
    if a is None or b is None:
        return 1.0
    delta_hours = abs((a - b).total_seconds()) / 3600.0
    return math.exp(-delta_hours / tau_hours)


def score_pair(x: ScoredItem, y: ScoredItem, tau_hours: float | None) -> float:
    j = jaccard(x.tags, y.tags)
    if j == 0.0:
        return 0.0
    if tau_hours is None:
        return j
    return j * time_decay(x.item.published_at, y.item.published_at, tau_hours)


def build_score_matrix(
    items: list[ScoredItem], tau_hours: float | None
) -> list[list[float]]:
    """Full symmetric n x n pairwise score matrix (diagonal unused)."""
    n = len(items)
    matrix = [[0.0] * n for _ in range(n)]
    for i, j in combinations(range(n), 2):
        score = score_pair(items[i], items[j], tau_hours)
        matrix[i][j] = score
        matrix[j][i] = score
    return matrix


def average_between(
    members_a: list[int], members_b: list[int], matrix: list[list[float]]
) -> float:
    """Mean pairwise score across every cross-pair between two clusters.

    Unlike single-link's "does at least one edge clear the threshold", this
    is dragged down by any unrelated pair inside the two clusters - which is
    exactly the point: the whole prospective merge has to be justified, not
    just one bridge item.
    """
    total = 0.0
    count = 0
    for i in members_a:
        for j in members_b:
            total += matrix[i][j]
            count += 1
    return total / count if count else 0.0


def average_link_cluster(
    items: list[ScoredItem], *, min_score: float, tau_hours: float | None
) -> list[list[int]]:
    """Agglomerative average-link clustering with a hard cutoff.

    Repeatedly merges the pair of clusters with the highest average
    inter-cluster score, stopping as soon as the best remaining average
    score falls below min_score. O(k^3) per merge in the number of current
    clusters - irrelevant at the pool sizes this tool targets (tens of
    items), not something to optimize prematurely.
    """
    clusters: list[list[int]] = [[i] for i in range(len(items))]
    matrix = build_score_matrix(items, tau_hours)

    while len(clusters) > 1:
        best_avg = -1.0
        best_pair: tuple[int, int] | None = None

        for a, b in combinations(range(len(clusters)), 2):
            avg = average_between(clusters[a], clusters[b], matrix)
            if avg > best_avg:
                best_avg = avg
                best_pair = (a, b)

        if best_pair is None or best_avg < min_score:
            break

        a, b = best_pair
        merged = clusters[a] + clusters[b]
        clusters = [c for idx, c in enumerate(clusters) if idx not in (a, b)]
        clusters.append(merged)

    return clusters


def render(
    items: list[ScoredItem], groups: list[list[int]], tau_hours: float | None
) -> None:
    matrix = build_score_matrix(items, tau_hours)

    multi_groups = sorted((g for g in groups if len(g) > 1), key=len, reverse=True)
    singleton_count = sum(1 for g in groups if len(g) == 1)

    header = (
        f"{len(items)} tagged items -> {len(multi_groups)} multi-item groups, "
        f"{singleton_count} singletons"
    )

    if DISABLE_RICH:
        print(header)
        print()
        for gi, member_idxs in enumerate(multi_groups, start=1):
            avg = (
                average_between(member_idxs, member_idxs, matrix)
                if len(member_idxs) > 1
                else 0.0
            )
            print(
                f"--- Group {gi} ({len(member_idxs)} items, internal avg score={avg:.3f}) ---"
            )
            for idx in member_idxs:
                si = items[idx]
                published = (
                    si.item.published_at.isoformat() if si.item.published_at else "-"
                )
                print(
                    f"  [{published}] ({si.item.source.name} / {si.item.uid}) {si.item.title}"
                )
                print(f"      tags: {sorted(si.tags)}")
            for i, j in combinations(sorted(member_idxs), 2):
                print(
                    f"      score={matrix[i][j]:.3f} shared={sorted(items[i].tags & items[j].tags)} "
                    f"({items[i].item.title[:40]!r} <-> {items[j].item.title[:40]!r})"
                )
            print()
        return

    from rich.console import Console
    from rich.table import Table

    console = Console()
    console.print(f"[bold]{header}[/bold]\n")

    for gi, member_idxs in enumerate(multi_groups, start=1):
        avg = (
            average_between(member_idxs, member_idxs, matrix)
            if len(member_idxs) > 1
            else 0.0
        )
        table = Table(
            title=f"Group {gi} ({len(member_idxs)} items, internal avg score={avg:.3f})"
        )
        table.add_column("Published")
        table.add_column("Source")
        table.add_column("UID")
        table.add_column("Title")
        table.add_column("Tags")

        for idx in member_idxs:
            si = items[idx]
            published = (
                si.item.published_at.isoformat() if si.item.published_at else "-"
            )
            table.add_row(
                published,
                si.item.source.name,
                si.item.uid,
                si.item.title,
                ", ".join(sorted(si.tags)),
            )

        console.print(table)

        for i, j in combinations(sorted(member_idxs), 2):
            console.print(
                f"    score={matrix[i][j]:.3f} shared={sorted(items[i].tags & items[j].tags)} "
                f"({items[i].item.title[:40]!r} <-> {items[j].item.title[:40]!r})"
            )
        console.print()


def build_payload(
    items: list[ScoredItem],
    groups: list[list[int]],
    matrix: list[list[float]],
    *,
    key: str,
    params: dict,
) -> dict:
    multi_groups = sorted((g for g in groups if len(g) > 1), key=len, reverse=True)
    singleton_count = sum(1 for g in groups if len(g) == 1)

    groups_payload = []
    for member_idxs in multi_groups:
        members = [
            {
                "uid": items[idx].item.uid,
                "source": items[idx].item.source.name,
                "title": items[idx].item.title,
                "published_at": (
                    items[idx].item.published_at.isoformat()
                    if items[idx].item.published_at
                    else None
                ),
                "tags": sorted(items[idx].tags),
            }
            for idx in member_idxs
        ]
        pairs_payload = [
            {
                "a_uid": items[i].item.uid,
                "b_uid": items[j].item.uid,
                "score": matrix[i][j],
                "shared_tags": sorted(items[i].tags & items[j].tags),
            }
            for i, j in combinations(sorted(member_idxs), 2)
        ]
        groups_payload.append(
            {
                "avg_score": average_between(member_idxs, member_idxs, matrix),
                "members": members,
                "pairs": pairs_payload,
            }
        )

    return {
        "key": key,
        "params": params,
        "generated_at": datetime.now(UTC).isoformat(),
        "singleton_count": singleton_count,
        "groups": groups_payload,
    }


@click.command()
@click.option(
    "-c",
    "--config",
    "config_path",
    type=Path,
    default=None,
    help="Path to config.yaml (defaults to Config() built-in defaults, e.g. platformdirs sqlite path)",
)
@click.option(
    "--days", type=int, default=7, help="Pool: items published in the last N days"
)
@click.option(
    "--min-score",
    type=float,
    default=0.3,
    help="Minimum average inter-cluster (jaccard * time-decay) score to merge two clusters",
)
@click.option(
    "--tau-hours",
    type=float,
    default=24.0,
    help="Time-decay time constant, in hours (ignored if --no-time-decay is set)",
)
@click.option(
    "--no-time-decay",
    "no_time_decay",
    is_flag=True,
    default=False,
    help="Score purely on tag Jaccard overlap; ignore publish-time proximity entirely",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output as a rich/plain table, or as a single JSON document to stdout",
)
@click.option("--verbose", is_flag=True, default=False)
@click.option("--log-level", default="INFO")
def main(
    config_path,
    days,
    min_score,
    tau_hours,
    no_time_decay,
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
    with App.from_config_file(config_path, create_schema=False) as app:
        items = load_tagged_items(app.db, scope)

    if not items:
        LOGGER.warning("no tagged items found in scope - nothing to group")
        return

    effective_tau = None if no_time_decay else tau_hours
    groups = average_link_cluster(items, min_score=min_score, tau_hours=effective_tau)

    if output_format == "json":
        matrix = build_score_matrix(items, effective_tau)
        key = (
            f"grouping-avglink-{days}d-min{min_score:g}"
            f"-tau{'none' if no_time_decay else f'{tau_hours:g}h'}"
        )
        params = {
            "algorithm": "avglink",
            "days": days,
            "min_score": min_score,
            "tau_hours": None if no_time_decay else tau_hours,
        }
        payload = build_payload(items, groups, matrix, key=key, params=params)
        print(json.dumps(payload, indent=2))
        return

    render(items, groups, effective_tau)


if __name__ == "__main__":
    main()
