"""Groups items into events with single-link clustering: connected components
over the pairwise tag-overlap graph.

Two items join the moment any pairwise score between them clears
`min_score`. It is transitive, so one "bridge" item can chain two unrelated
clusters together; grouping_avglink avoids that.
"""

from itertools import combinations
from typing import Any

from ._grouping_scoring import (
    GroupingRemixer,
    ScoredItem,
    UnionFind,
    member_payload,
    pair_payload,
    score_pair,
)


class Remixer(GroupingRemixer):
    NAME = "grouping_singlelink"
    ALGORITHM = "singlelink"

    def group(self, items: list[ScoredItem]) -> list[dict[str, Any]]:
        union_find = UnionFind(len(items))
        edges: list[tuple[int, int, float]] = []
        for i, j in combinations(range(len(items)), 2):
            score = score_pair(items[i], items[j], self.tau_hours)
            if score >= self.min_score:
                edges.append((i, j, score))
                union_find.union(i, j)

        groups: dict[int, list[int]] = {}
        for idx in range(len(items)):
            groups.setdefault(union_find.find(idx), []).append(idx)

        payload = []
        for members in sorted(groups.values(), key=len, reverse=True):
            member_set = set(members)
            internal = [
                edge
                for edge in edges
                if edge[0] in member_set and edge[1] in member_set
            ]
            payload.append(
                {
                    "members": [member_payload(items[idx]) for idx in members],
                    "edges": [
                        pair_payload(items[i], items[j], score)
                        for i, j, score in sorted(internal, key=lambda edge: -edge[2])
                    ],
                }
            )
        return payload
