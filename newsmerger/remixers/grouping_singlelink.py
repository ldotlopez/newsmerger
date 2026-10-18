"""Groups items into events with single-link clustering: connected components
over the pairwise tag-overlap graph.

Two items join the moment any pairwise score between them clears
`min_score`. It is transitive, so one "bridge" item can chain two unrelated
clusters together; grouping_avglink avoids that.
"""

from typing import Any

from ._grouping_scoring import (
    GroupingRemixer,
    ScoredItem,
    build_score_matrix,
    single_link_groups,
)


class Remixer(GroupingRemixer):
    NAME = "grouping_singlelink"
    ALGORITHM = "singlelink"

    def group(self, items: list[ScoredItem]) -> list[dict[str, Any]]:
        scores = build_score_matrix(items, self.tau_hours)
        return single_link_groups(items, scores, self.min_score)
