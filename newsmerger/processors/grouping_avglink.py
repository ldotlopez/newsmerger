"""ArtifactProcessor: group source items into event clusters using average-
link agglomerative clustering with a hard cutoff.

Unlike grouping_singlelink.py, a merge between two clusters must be
justified by the AVERAGE score across all their cross-pairs, not by any
single pair clearing the threshold - one loosely-related "bridge" item can't
chain two otherwise-unrelated clusters together on its own.

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
    ScoredItem,
    average_between,
    build_score_matrix,
    load_tagged_items,
    member_payload,
)

LOGGER = logging.getLogger(__name__)

ARTIFACT_NAME = "current"


def average_link_cluster(
    items: list[ScoredItem], *, min_score: float, tau_hours: float | None
) -> list[list[int]]:
    """Repeatedly merge the pair of clusters with the highest average
    inter-cluster score, stopping once the best remaining average falls
    below min_score. O(k^3) per merge in the current cluster count -
    irrelevant at the pool sizes this targets (tens of items)."""
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


def build_payload(
    items: list[ScoredItem],
    groups: list[list[int]],
    matrix: list[list[float]],
    *,
    params: dict,
) -> dict:
    groups_payload = []
    for member_idxs in sorted(groups, key=len, reverse=True):
        groups_payload.append(
            {
                "avg_score": (
                    average_between(member_idxs, member_idxs, matrix)
                    if len(member_idxs) > 1
                    else None
                ),
                "members": [member_payload(items[idx]) for idx in member_idxs],
                "pairs": [
                    {
                        "a_uid": items[i].item.uid,
                        "b_uid": items[j].item.uid,
                        "score": matrix[i][j],
                        "shared_tags": sorted(items[i].tags & items[j].tags),
                    }
                    for i, j in combinations(sorted(member_idxs), 2)
                ],
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "params": params,
        "groups": groups_payload,
    }


class Processor(ArtifactProcessor):
    NAME = "grouping_avglink"

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

        groups = average_link_cluster(
            items, min_score=self.min_score, tau_hours=self.tau_hours
        )
        matrix = build_score_matrix(items, self.tau_hours)
        params = {
            "algorithm": "avglink",
            "days": self.days,
            "min_score": self.min_score,
            "tau_hours": self.tau_hours,
        }
        content = json.dumps(
            build_payload(items, groups, matrix, params=params), indent=2
        )
        yield ARTIFACT_NAME, content, "application/json"
