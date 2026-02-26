"""In-memory data store. Used when USE_MOCK_DB=true (default).
Drop-in replacement for Postgres queries — same interface, backed by Python lists.
"""

from __future__ import annotations

import numpy as np
from typing import Optional

from app.seed import build_offers, MOCK_PLANS, MOCK_INSIGHTS, MOCK_USER, MOCK_ELIGIBILITY, _deterministic_embedding


class InMemoryStore:
    """Singleton in-memory store seeded on first access."""

    _instance: Optional["InMemoryStore"] = None

    def __init__(self) -> None:
        self.offers: list[dict] = []
        self.plans: list[dict] = list(MOCK_PLANS)
        self.insights: list[dict] = list(MOCK_INSIGHTS)
        self.user: dict = dict(MOCK_USER)
        self.eligibility: dict = dict(MOCK_ELIGIBILITY)
        self.feedback: list[dict] = []
        self._embeddings: Optional[np.ndarray] = None

    @classmethod
    def get(cls) -> "InMemoryStore":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._seed()
        return cls._instance

    def _seed(self) -> None:
        self.offers = build_offers()
        emb_list = [o["embedding"] for o in self.offers]
        self._embeddings = np.array(emb_list, dtype=np.float32)

    def vector_search(self, query_embedding: list[float], top_k: int = 20) -> list[dict]:
        """Cosine similarity search over offer embeddings."""
        q = np.array(query_embedding, dtype=np.float32)
        q = q / (np.linalg.norm(q) + 1e-9)
        norms = np.linalg.norm(self._embeddings, axis=1, keepdims=True) + 1e-9
        normed = self._embeddings / norms
        scores = normed @ q
        top_idx = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_idx:
            offer = dict(self.offers[int(idx)])
            offer["_similarity"] = float(scores[int(idx)])
            results.append(offer)
        return results

    def filter_offers(
        self,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        max_monthly: Optional[float] = None,
        only_zero_apr: bool = False,
    ) -> list[dict]:
        """SQL-like filter on offers."""
        results = list(self.offers)
        if category:
            results = [o for o in results if o["category"] == category.lower()]
        if max_price is not None:
            results = [o for o in results if o["totalPrice"] <= max_price]
        if max_monthly is not None:
            results = [o for o in results if o["monthlyPayment"] <= max_monthly]
        if only_zero_apr:
            results = [o for o in results if o["apr"] == 0]
        return results

    def get_embedding(self, text: str) -> list[float]:
        """Generate query embedding (deterministic hash-based or real model)."""
        return _deterministic_embedding(text)

    def add_feedback(self, feedback: dict) -> None:
        self.feedback.append(feedback)


def get_store() -> InMemoryStore:
    return InMemoryStore.get()
