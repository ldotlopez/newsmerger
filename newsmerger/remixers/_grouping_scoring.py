"""Scoring and the shared run loop of the tag-based grouping remixers
(grouping_singlelink, grouping_avglink), which differ only in how they
cluster. Not a remixer itself: it has no `Remixer` class.
"""

from __future__ import annotations

import dataclasses
import json
import logging
import math
from abc import abstractmethod
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from itertools import combinations
from typing import Any

from ..db import Database
from ..models import ItemKey, ProcessingScope, SourceItem
from . import BaseRemixer

LOGGER = logging.getLogger(__name__)

ARTIFACT_NAME = "current"


@dataclasses.dataclass(frozen=True)
class ScoredItem:
    item: SourceItem
    tags: frozenset[str]  # lowercased, for Jaccard
    raw_tags: tuple[str, ...]  # original case and order


def tagged_items(
    items: list[SourceItem], tags_by_key: dict[ItemKey, list[str]]
) -> list[ScoredItem]:
    """Pair items with their tags; untagged items can't be grouped and are dropped."""
    return [
        ScoredItem(
            item=item,
            tags=frozenset(tag.lower() for tag in tags),
            raw_tags=tuple(tags),
        )
        for item in items
        if (tags := tags_by_key.get(item.key))
    ]


def item_ref(item: SourceItem) -> str:
    """A readable, unique reference to an item in a payload."""
    return f"{item.source.id}/{item.uid}"


def jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def time_decay(a: datetime | None, b: datetime | None, tau_hours: float) -> float:
    """exp(-delta/tau): 1.0 for simultaneous items, decaying towards 0 as the
    gap between publish times grows. Missing timestamps don't penalize."""
    if a is None or b is None:
        return 1.0
    delta_hours = abs((a - b).total_seconds()) / 3600.0
    return math.exp(-delta_hours / tau_hours)


def score_pair(a: ScoredItem, b: ScoredItem, tau_hours: float | None) -> float:
    overlap = jaccard(a.tags, b.tags)
    if overlap == 0.0 or tau_hours is None:
        return overlap
    return overlap * time_decay(a.item.published_at, b.item.published_at, tau_hours)


def build_score_matrix(
    items: list[ScoredItem], tau_hours: float | None
) -> list[list[float]]:
    """Full symmetric n x n pairwise score matrix (diagonal unused)."""
    n = len(items)
    matrix = [[0.0] * n for _ in range(n)]
    for i, j in combinations(range(n), 2):
        matrix[i][j] = matrix[j][i] = score_pair(items[i], items[j], tau_hours)
    return matrix


def average_between(
    members_a: list[int], members_b: list[int], matrix: list[list[float]]
) -> float:
    scores = [matrix[i][j] for i in members_a for j in members_b]
    return sum(scores) / len(scores) if scores else 0.0


class UnionFind:
    """Minimal union-find for connected components."""

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))

    def find(self, node: int) -> int:
        while self.parent[node] != node:
            self.parent[node] = self.parent[self.parent[node]]
            node = self.parent[node]
        return node

    def union(self, a: int, b: int) -> None:
        root_a, root_b = self.find(a), self.find(b)
        if root_a != root_b:
            self.parent[root_a] = root_b


def member_payload(scored: ScoredItem) -> dict[str, Any]:
    item = scored.item
    return {
        "ref": item_ref(item),
        "source": item.source.id,
        "uid": item.uid,
        "title": item.title,
        "published_at": item.published_at.isoformat() if item.published_at else None,
        "tags": sorted(scored.tags),
    }


def pair_payload(a: ScoredItem, b: ScoredItem, score: float) -> dict[str, Any]:
    return {
        "a": item_ref(a.item),
        "b": item_ref(b.item),
        "score": score,
        "shared_tags": sorted(a.tags & b.tags),
    }


class GroupingRemixer(BaseRemixer):
    """Groups the tagged items of the last `days` into events.

    Produces one JSON artifact, "current", where every item in scope belongs
    to exactly one group, singletons included.
    """

    ALGORITHM: str

    def __init__(
        self,
        db: Database,
        *,
        min_score: float = 0.3,
        tau_hours: float | None = 24.0,
        days: int = 7,
    ) -> None:
        super().__init__(db)
        self.min_score = min_score
        self.tau_hours = tau_hours
        self.days = days

    def produce(self, scope: ProcessingScope) -> Iterator[tuple[str, str, str]]:
        if scope.since is None:
            scope = dataclasses.replace(
                scope, since=datetime.now(UTC) - timedelta(days=self.days)
            )

        items = self.db.get_items(scope)
        tags = self.db.get_annotation_values(items, processor="tagger", key="tags")
        scored = tagged_items(items, tags)
        if not scored:
            LOGGER.info(f"{self.NAME}: no tagged items in scope - nothing to group")
            return

        payload = {
            "generated_at": datetime.now(UTC).isoformat(),
            "params": {
                "algorithm": self.ALGORITHM,
                "days": self.days,
                "min_score": self.min_score,
                "tau_hours": self.tau_hours,
            },
            "groups": self.group(scored),
        }
        yield ARTIFACT_NAME, json.dumps(payload, indent=2), "application/json"

    @abstractmethod
    def group(self, items: list[ScoredItem]) -> list[dict[str, Any]]:
        """Cluster the items; return one payload dict per group, largest first."""
