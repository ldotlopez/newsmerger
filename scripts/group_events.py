#!/usr/bin/env python3
"""Standalone, read-only experiment: group source items into event clusters
based on tag overlap.

This is NOT wired into the processor lifecycle, the CLI, or the DB schema.
It reads existing source items and their "tagger" annotations through the
normal Database API and does everything else (scoring + clustering) in
memory; nothing is written back. Rerun with different --min-score/--tau-hours
to explore behavior before this gets promoted into a real processor.

Usage:
    python scripts/group_events.py --config config.yaml
    python scripts/group_events.py --config config.yaml --days 3 --min-score 0.4
    DISABLE_RICH=1 python scripts/group_events.py --config config.yaml
"""  # noqa: EXE001

from __future__ import annotations

import dataclasses
import json
import logging
import math
import os
from datetime import UTC, datetime, timedelta
from itertools import combinations
from pathlib import Path

import rich_click as click
from foundation.loglib import setup_logger

from newsmerger.config import Config
from newsmerger.consts import PACKAGE_NAME
from newsmerger.db import Database, ProcessingScope
from newsmerger.models import SourceItem

LOGGER = logging.getLogger(f"{PACKAGE_NAME}.tools.group_events")

DISABLE_RICH = os.environ.get("DISABLE_RICH", "0").lower() not in ("0", "false", "")


@dataclasses.dataclass(frozen=True)
class ScoredItem:
    item: SourceItem
    tags: frozenset[str]


@dataclasses.dataclass(frozen=True)
class Edge:
    a: int
    b: int
    score: float
    shared_tags: frozenset[str]


def load_tagged_items(db: Database, scope: ProcessingScope) -> list[ScoredItem]:
    """Fetch items in scope along with their "tagger" tags annotation.

    Items with no tags annotation yet (not processed by the tagger, or
    processed with no tags produced) are skipped entirely - they can't
    participate in tag-based grouping.
    """
    items = db.get_source_items(scope=scope)
    result = []
    for item in items:
        annotations = db.get_annotations(item, processor="tagger", key="tags")
        tags = annotations.get("tagger", {}).get("tags") or []
        if not tags:
            LOGGER.debug(f"skipping '{item.title}' - no tags annotation")
            continue
        result.append(ScoredItem(item=item, tags=frozenset(t.lower() for t in tags)))

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


class UnionFind:
    """Minimal union-find for connected-components clustering. No union-by-
    rank - not worth it at the pool sizes this tool is meant for."""

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


def cluster(
    items: list[ScoredItem], *, min_score: float, tau_hours: float | None
) -> tuple[list[list[int]], list[Edge]]:
    """Score every pair, keep edges >= min_score, connected-components the rest.

    NOTE: this is transitive - if A-B and B-C both clear the threshold but
    A-C doesn't, all three still end up in the same group. Accepted tradeoff
    for a first pass; revisit with weighted/community clustering if it
    produces visibly bad merges.
    """
    uf = UnionFind(len(items))
    edges: list[Edge] = []

    for i, j in combinations(range(len(items)), 2):
        score = score_pair(items[i], items[j], tau_hours)
        if score >= min_score:
            edges.append(
                Edge(a=i, b=j, score=score, shared_tags=items[i].tags & items[j].tags)
            )
            uf.union(i, j)

    groups_by_root: dict[int, list[int]] = {}
    for idx in range(len(items)):
        groups_by_root.setdefault(uf.find(idx), []).append(idx)

    return list(groups_by_root.values()), edges


def render(items: list[ScoredItem], groups: list[list[int]], edges: list[Edge]) -> None:
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
            print(f"--- Group {gi} ({len(member_idxs)} items) ---")
            for idx in member_idxs:
                si = items[idx]
                published = (
                    si.item.published_at.isoformat() if si.item.published_at else "-"
                )
                print(
                    f"  [{published}] ({si.item.source.name} / {si.item.uid}) {si.item.title}"
                )
                print(f"      tags: {sorted(si.tags)}")
            for e in sorted(
                _internal_edges(edges, member_idxs), key=lambda e: -e.score
            ):
                print(
                    f"      score={e.score:.3f} shared={sorted(e.shared_tags)} "
                    f"({items[e.a].item.title[:40]!r} <-> {items[e.b].item.title[:40]!r})"
                )
            print()
        return

    from rich.console import Console
    from rich.table import Table

    console = Console()
    console.print(f"[bold]{header}[/bold]\n")

    for gi, member_idxs in enumerate(multi_groups, start=1):
        table = Table(title=f"Group {gi} ({len(member_idxs)} items)")
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

        for e in sorted(_internal_edges(edges, member_idxs), key=lambda e: -e.score):
            console.print(
                f"    score={e.score:.3f} shared={sorted(e.shared_tags)} "
                f"({items[e.a].item.title[:40]!r} <-> {items[e.b].item.title[:40]!r})"
            )
        console.print()


def _internal_edges(edges: list[Edge], member_idxs: list[int]) -> list[Edge]:
    member_set = set(member_idxs)
    return [e for e in edges if e.a in member_set and e.b in member_set]


def build_payload(
    items: list[ScoredItem],
    groups: list[list[int]],
    edges: list[Edge],
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
        edges_payload = [
            {
                "a_uid": items[e.a].item.uid,
                "b_uid": items[e.b].item.uid,
                "score": e.score,
                "shared_tags": sorted(e.shared_tags),
            }
            for e in sorted(_internal_edges(edges, member_idxs), key=lambda e: -e.score)
        ]
        groups_payload.append({"members": members, "edges": edges_payload})

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
    help="Minimum combined (jaccard * time-decay) score to draw an edge between two items",
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

    config = Config.from_file(config_path) if config_path else Config()
    # Read-only: never create/alter schema from this tool.
    db = Database(config.db.uri, create_schema=False)

    scope = ProcessingScope(since=datetime.now(UTC) - timedelta(days=days))
    items = load_tagged_items(db, scope)

    if not items:
        LOGGER.warning("no tagged items found in scope - nothing to group")
        return

    effective_tau = None if no_time_decay else tau_hours
    groups, edges = cluster(items, min_score=min_score, tau_hours=effective_tau)

    if output_format == "json":
        key = (
            f"grouping-singlelink-{days}d-min{min_score:g}"
            f"-tau{'none' if no_time_decay else f'{tau_hours:g}h'}"
        )
        params = {
            "algorithm": "singlelink",
            "days": days,
            "min_score": min_score,
            "tau_hours": None if no_time_decay else tau_hours,
        }
        payload = build_payload(items, groups, edges, key=key, params=params)
        print(json.dumps(payload, indent=2))
        return

    render(items, groups, edges)


if __name__ == "__main__":
    main()
