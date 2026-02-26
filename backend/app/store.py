"""In-memory data store. Used when USE_MOCK_DB=true (default).
Drop-in replacement for Postgres queries — same interface, backed by Python lists.
Includes BM25-style lexical search alongside vector search for hybrid retrieval.
"""

from __future__ import annotations

import math
import re
import numpy as np
from collections import Counter
from typing import Optional

from app.seed import build_offers, MOCK_PLANS, MOCK_INSIGHTS, MOCK_USER, MOCK_ELIGIBILITY, _deterministic_embedding


def _tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split on whitespace."""
    return re.findall(r"[a-z0-9]+", text.lower())


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
        # BM25 index
        self._doc_tokens: list[list[str]] = []
        self._doc_freqs: Counter = Counter()
        self._avg_dl: float = 0.0

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
        self._build_bm25_index()

    def _build_bm25_index(self) -> None:
        """Build in-memory BM25 index over offer text fields."""
        self._doc_tokens = []
        self._doc_freqs = Counter()
        for o in self.offers:
            text = f"{o.get('merchantName', '')} {o.get('productName', '')} {o.get('category', '')}"
            tokens = _tokenize(text)
            self._doc_tokens.append(tokens)
            unique = set(tokens)
            for t in unique:
                self._doc_freqs[t] += 1
        total_len = sum(len(dt) for dt in self._doc_tokens)
        self._avg_dl = total_len / max(len(self._doc_tokens), 1)

    def bm25_search(self, query: str, top_k: int = 20) -> list[dict]:
        """BM25 scoring over offer text (merchantName + productName + category)."""
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        n = len(self.offers)
        k1 = 1.5
        b = 0.75
        scores: list[float] = []

        for i, doc_tokens in enumerate(self._doc_tokens):
            dl = len(doc_tokens)
            tf_map = Counter(doc_tokens)
            score = 0.0
            for qt in query_tokens:
                df = self._doc_freqs.get(qt, 0)
                if df == 0:
                    continue
                idf = math.log((n - df + 0.5) / (df + 0.5) + 1.0)
                tf = tf_map.get(qt, 0)
                tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / self._avg_dl))
                score += idf * tf_norm
            scores.append(score)

        top_idx = sorted(range(n), key=lambda i: scores[i], reverse=True)[:top_k]
        results = []
        for idx in top_idx:
            if scores[idx] > 0:
                offer = dict(self.offers[idx])
                offer["_bm25_score"] = scores[idx]
                results.append(offer)
        return results

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
