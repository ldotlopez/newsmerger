"""Shared scoring/tag-loading helpers for the grouping processors
(grouping_singlelink.py, grouping_avglink.py). Not a processor itself -
importing this as a processor name will fail (no `Processor` class), by
design; it's plumbing shared by two processors that differ only in their
clustering step.
"""

from __future__ import annotations

import dataclasses
import math
from datetime import datetime
from itertools import combinations
from typing import Any

from ..db import Database, ProcessingScope
from ..models import SourceItem


@dataclasses.dataclass(frozen=True)
class ScoredItem:
    item: SourceItem
    tags: frozenset[str]  # lowercased, for Jaccard
    raw_tags: tuple[str, ...]  # original case and order


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
    participate in tag-based grouping and never enter the scoring pool.
    """
    items = db.get_source_items(scope=scope)
    tags_by_uid = db.get_annotation_values(items, processor="tagger", key="tags")
    return [
        ScoredItem(
            item=item,
            tags=frozenset(t.lower() for t in tags),
            raw_tags=tuple(tags),
        )
        for item in items
        if (tags := tags_by_uid.get(item.uid))
    ]


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
    total = 0.0
    count = 0
    for i in members_a:
        for j in members_b:
            total += matrix[i][j]
            count += 1
    return total / count if count else 0.0


class UnionFind:
    """Minimal union-find for connected-components clustering. No union-by-
    rank - not worth it at the pool sizes this is meant for."""

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


def member_payload(si: ScoredItem) -> dict[str, Any]:
    return {
        "uid": si.item.uid,
        "source": si.item.source.name,
        "title": si.item.title,
        "published_at": si.item.published_at.isoformat()
        if si.item.published_at
        else None,
        "tags": sorted(si.tags),
    }
