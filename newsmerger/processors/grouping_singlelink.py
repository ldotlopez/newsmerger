"""ArtifactProcessor: group source items into event clusters using single-
link clustering (connected components over a pairwise tag-overlap graph).

Groups two items the moment ANY pairwise score between them clears
`min_score` - transitive, so a single "bridge" item can chain two otherwise-
unrelated clusters together. See grouping_avglink.py for the alternative
that requires the whole merge to be justified by the average score across
all cross-pairs.

Produces one artifact (name="current", content_type="application/json")
containing every item in scope, each assigned to exactly one group -
including groups of size 1, so no item is dropped from the output.
"""

from __future__ import annotations

import dataclasses
import json
import logging
from datetime import datetime, timedelta, timezone
from itertools import combinations
from typing import Iterator

from ..db import ProcessingScope
from . import ArtifactProcessor
from ._grouping_scoring import (
    Edge,
    ScoredItem,
    UnionFind,
    load_tagged_items,
    member_payload,
    score_pair,
)

LOGGER = logging.getLogger(__name__)

ARTIFACT_NAME = "current"


def cluster(
    items: list[ScoredItem], *, min_score: float, tau_hours: float | None
) -> tuple[list[list[int]], list[Edge]]:
    """Score every pair, keep edges >= min_score, connected-components the rest."""
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


def build_payload(
    items: list[ScoredItem], groups: list[list[int]], edges: list[Edge], *, params: dict
) -> dict:
    # edges_by_pair = {(e.a, e.b): e for e in edges}

    groups_payload = []
    for member_idxs in sorted(groups, key=len, reverse=True):
        member_set = set(member_idxs)
        internal_edges = [e for e in edges if e.a in member_set and e.b in member_set]
        groups_payload.append(
            {
                "members": [member_payload(items[idx]) for idx in member_idxs],
                "edges": [
                    {
                        "a_uid": items[e.a].item.uid,
                        "b_uid": items[e.b].item.uid,
                        "score": e.score,
                        "shared_tags": sorted(e.shared_tags),
                    }
                    for e in sorted(internal_edges, key=lambda e: -e.score)
                ],
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "params": params,
        "groups": groups_payload,
    }


class Processor(ArtifactProcessor):
    NAME = "grouping_singlelink"

    def __init__(
        self,
        *args,
        min_score: float = 0.3,
        tau_hours: float | None = 24.0,
        days: int = 7,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.min_score = min_score
        self.tau_hours = tau_hours
        self.days = days

    def produce(self, scope: ProcessingScope) -> Iterator[tuple[str, str, str]]:
        if scope.since is None:
            scope = dataclasses.replace(
                scope, since=datetime.now(timezone.utc) - timedelta(days=self.days)
            )

        items = load_tagged_items(self.db, scope)
        if not items:
            LOGGER.info(f"{self.NAME}: no tagged items in scope - nothing to group")
            return

        groups, edges = cluster(
            items, min_score=self.min_score, tau_hours=self.tau_hours
        )
        params = {
            "algorithm": "singlelink",
            "days": self.days,
            "min_score": self.min_score,
            "tau_hours": self.tau_hours,
        }
        content = json.dumps(
            build_payload(items, groups, edges, params=params), indent=2
        )
        yield ARTIFACT_NAME, content, "application/json"
