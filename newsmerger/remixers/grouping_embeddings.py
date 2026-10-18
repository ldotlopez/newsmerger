"""Groups items into events by tag overlap blended with the similarity of
their tags' embeddings (Ollama), single-link.

Plain tag overlap misses variants of the same entity ("BCE" vs "Banco
Central Europeo"); embeddings of the joined tags catch some of them. The
score is (weight * cosine + (1 - weight) * jaccard) * time decay, so
`embedding_weight=0` reproduces grouping_singlelink.

Embeddings are recomputed on every run, in one batched call.
shortcut: no embedding cache; add one if runs over large pools get slow.
"""

import math
from itertools import combinations
from typing import Any

from ..db import Database
from ..llm import DEFAULT_OLLAMA_URL, ollama_client
from ._grouping_scoring import (
    GroupingRemixer,
    ScoredItem,
    jaccard,
    single_link_groups,
    time_decay,
)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def tags_text(item: ScoredItem) -> str:
    """The text embedded for an item: its tags, sorted and comma-separated."""
    return ", ".join(sorted(item.raw_tags, key=str.lower))


class Remixer(GroupingRemixer):
    NAME = "grouping_embeddings"
    ALGORITHM = "embeddings"

    def __init__(
        self,
        db: Database,
        *,
        model: str,
        embedding_weight: float = 0.5,
        api_base: str = DEFAULT_OLLAMA_URL,
        api_key: str | None = None,
        min_score: float = 0.3,
        tau_hours: float | None = 24.0,
        days: int = 7,
    ) -> None:
        super().__init__(db, min_score=min_score, tau_hours=tau_hours, days=days)
        self.model = model
        self.embedding_weight = embedding_weight
        self.client = ollama_client(api_base, api_key)

    def params(self) -> dict[str, Any]:
        return {
            **super().params(),
            "model": self.model,
            "embedding_weight": self.embedding_weight,
        }

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

    def group(self, items: list[ScoredItem]) -> list[dict[str, Any]]:
        response = self.client.embed(
            model=self.model, input=[tags_text(item) for item in items]
        )
        embeddings = [list(embedding) for embedding in response.embeddings]

        scores = [[0.0] * len(items) for _ in items]
        for i, j in combinations(range(len(items)), 2):
            scores[i][j] = scores[j][i] = self.score(
                items[i], items[j], embeddings[i], embeddings[j]
            )
        return single_link_groups(items, scores, self.min_score)
