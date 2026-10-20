"""Groups tagged items into events. Every remixer produces one JSON
artifact, "current", where every item in scope belongs to exactly one
group, singletons included; items without the annotations a remixer reads
are left out.

- `singlelink`: connected components over the pairwise tag-overlap graph.
  Two items join the moment any pairwise score between them clears
  `min_score`; it is transitive, so one "bridge" item can chain two
  unrelated clusters together.
- `avglink`: average-link agglomerative clustering with a hard cutoff. A
  merge must be justified by the average score across all cross-pairs, so a
  bridge item can't chain clusters together.
- `embeddings`: single-link over tag overlap blended with the cosine
  similarity of the items' `embed` annotations (tags or markdown), which
  catches variants of the same entity ("BCE" vs "Banco Central Europeo").
  The score is (weight * cosine + (1 - weight) * jaccard) * time decay, so
  `embedding_weight=0` reproduces `singlelink`.

Without per-remixer sections all three are enabled with their defaults;
with sections, only the listed ones are.
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
from typing import Any, Literal

import pydantic

from ..db import Database
from ..models import ItemKey, ProcessingScope, SourceItem
from ..remixers import BaseRemixer, Remixer
from . import PluginObjects, PluginOptions, Services

LOGGER = logging.getLogger(__name__)

ARTIFACT_NAME = "current"


class GroupingOptions(PluginOptions):
    min_score: float = 0.3
    tau_hours: float | None = 24.0
    days: int = 7  # scope when it sets no `since`


class EmbeddingsOptions(GroupingOptions):
    embedding: Literal["tags", "markdown"] = "tags"
    embedding_weight: float = pydantic.Field(default=0.5, ge=0.0, le=1.0)


class Options(PluginOptions):
    singlelink: GroupingOptions = GroupingOptions()
    avglink: GroupingOptions = GroupingOptions()
    embeddings: EmbeddingsOptions = EmbeddingsOptions()

    @pydantic.field_validator("singlelink", "avglink", "embeddings", mode="before")
    @classmethod
    def empty_section_takes_defaults(cls, value: Any) -> Any:
        return {} if value is None else value


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


def single_link_groups(
    items: list[ScoredItem], scores: list[list[float]], min_score: float
) -> list[dict[str, Any]]:
    """Connected components of the pairs scoring at least `min_score`, one
    payload dict per group (largest first) with its internal edges."""
    union_find = UnionFind(len(items))
    edges: list[tuple[int, int, float]] = []
    for i, j in combinations(range(len(items)), 2):
        if scores[i][j] >= min_score:
            edges.append((i, j, scores[i][j]))
            union_find.union(i, j)

    groups: dict[int, list[int]] = {}
    for idx in range(len(items)):
        groups.setdefault(union_find.find(idx), []).append(idx)

    payload = []
    for members in sorted(groups.values(), key=len, reverse=True):
        member_set = set(members)
        payload.append(
            {
                "members": [member_payload(items[idx]) for idx in members],
                "edges": [
                    pair_payload(items[i], items[j], score)
                    for i, j, score in sorted(edges, key=lambda edge: -edge[2])
                    if i in member_set and j in member_set
                ],
            }
        )
    return payload


def average_link_cluster(
    matrix: list[list[float]], *, min_score: float
) -> list[list[int]]:
    """Repeatedly merge the two clusters with the highest average score, until
    the best remaining average falls below min_score. O(k^3) per merge, fine
    at the pool sizes this targets (tens of items)."""
    clusters: list[list[int]] = [[i] for i in range(len(matrix))]

    while len(clusters) > 1:
        best_avg, a, b = max(
            (average_between(clusters[a], clusters[b], matrix), a, b)
            for a, b in combinations(range(len(clusters)), 2)
        )
        if best_avg < min_score:
            break
        merged = clusters[a] + clusters[b]
        clusters = [c for idx, c in enumerate(clusters) if idx not in (a, b)]
        clusters.append(merged)

    return clusters


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class GroupingRemixer(BaseRemixer):
    """Groups the tagged items of the last `days` into events."""

    def __init__(self, cfg: GroupingOptions) -> None:
        self.cfg = cfg
        self.min_score = cfg.min_score
        self.tau_hours = cfg.tau_hours
        self.days = cfg.days

    def produce(
        self, db: Database, scope: ProcessingScope
    ) -> Iterator[tuple[str, str, str]]:
        if scope.since is None:
            scope = dataclasses.replace(
                scope, since=datetime.now(UTC) - timedelta(days=self.days)
            )

        items = db.get_items(scope)
        tags = db.get_annotation_values(items, processor="tagger", key="tags")
        scored = tagged_items(items, tags)
        if not scored:
            LOGGER.info(f"{self.name}: no tagged items in scope - nothing to group")
            return

        payload = {
            "generated_at": datetime.now(UTC).isoformat(),
            "params": {"algorithm": self.name, **self.cfg.model_dump()},
            "groups": self.group(db, scored),
        }
        yield ARTIFACT_NAME, json.dumps(payload, indent=2), "application/json"

    @abstractmethod
    def group(self, db: Database, items: list[ScoredItem]) -> list[dict[str, Any]]:
        """Cluster the items; return one payload dict per group, largest first."""


class SingleLinkRemixer(GroupingRemixer):
    name = "singlelink"

    def group(self, db: Database, items: list[ScoredItem]) -> list[dict[str, Any]]:
        scores = build_score_matrix(items, self.tau_hours)
        return single_link_groups(items, scores, self.min_score)


class AverageLinkRemixer(GroupingRemixer):
    name = "avglink"

    def group(self, db: Database, items: list[ScoredItem]) -> list[dict[str, Any]]:
        matrix = build_score_matrix(items, self.tau_hours)
        clusters = average_link_cluster(matrix, min_score=self.min_score)

        return [
            {
                "avg_score": (
                    average_between(members, members, matrix)
                    if len(members) > 1
                    else None
                ),
                "members": [member_payload(items[idx]) for idx in members],
                "pairs": [
                    pair_payload(items[i], items[j], matrix[i][j])
                    for i, j in combinations(sorted(members), 2)
                ],
            }
            for members in sorted(clusters, key=len, reverse=True)
        ]


class EmbeddingsRemixer(GroupingRemixer):
    name = "embeddings"

    def __init__(self, cfg: EmbeddingsOptions) -> None:
        super().__init__(cfg)
        self.embedding_key = f"{cfg.embedding}_embedding"
        self.embedding_weight = cfg.embedding_weight

    def score(
        self,
        a: ScoredItem,
        b: ScoredItem,
        embedding_a: list[float],
        embedding_b: list[float],
    ) -> float:
        cosine = max(cosine_similarity(embedding_a, embedding_b), 0.0)
        blended = self.embedding_weight * cosine + (
            1 - self.embedding_weight
        ) * jaccard(a.tags, b.tags)
        if self.tau_hours is None:
            return blended
        return blended * time_decay(
            a.item.published_at, b.item.published_at, self.tau_hours
        )

    def group(self, db: Database, items: list[ScoredItem]) -> list[dict[str, Any]]:
        vectors = db.get_annotation_values(
            [scored.item for scored in items], processor="embed", key=self.embedding_key
        )
        embedded = [scored for scored in items if scored.item.key in vectors]
        if skipped := len(items) - len(embedded):
            LOGGER.info(
                f"{self.name}: {skipped} item(s) without embed.{self.embedding_key}"
            )
        embeddings = [vectors[scored.item.key] for scored in embedded]

        scores = [[0.0] * len(embedded) for _ in embedded]
        for i, j in combinations(range(len(embedded)), 2):
            scores[i][j] = scores[j][i] = self.score(
                embedded[i], embedded[j], embeddings[i], embeddings[j]
            )
        return single_link_groups(embedded, scores, self.min_score)


def __newsmerger_plugin__(services: Services, **options: Any) -> PluginObjects:
    cfg = Options.model_validate(options)
    builders = {
        "singlelink": lambda: SingleLinkRemixer(cfg.singlelink),
        "avglink": lambda: AverageLinkRemixer(cfg.avglink),
        "embeddings": lambda: EmbeddingsRemixer(cfg.embeddings),
    }
    enabled = [name for name in options if name in builders] or list(builders)
    remixers = [builders[name]() for name in enabled]
    return [(remixer.name, Remixer, remixer) for remixer in remixers]
