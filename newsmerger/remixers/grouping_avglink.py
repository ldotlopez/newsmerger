"""Groups items into events with average-link agglomerative clustering and a
hard cutoff.

A merge between two clusters must be justified by the average score across
all their cross-pairs, so one loosely related "bridge" item can't chain two
unrelated clusters together the way grouping_singlelink allows.
"""

from itertools import combinations
from typing import Any

from ._grouping_scoring import (
    GroupingRemixer,
    ScoredItem,
    average_between,
    build_score_matrix,
    member_payload,
    pair_payload,
)


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


class Remixer(GroupingRemixer):
    NAME = "grouping_avglink"
    ALGORITHM = "avglink"

    def group(self, items: list[ScoredItem]) -> list[dict[str, Any]]:
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
