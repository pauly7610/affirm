"""Rerank node: BGE reranker (or deterministic fallback) on retrieved candidates."""

from __future__ import annotations

import logging
from typing import Optional

from app.config import get_settings
from app.pipeline.state import SearchState

logger = logging.getLogger(__name__)

_reranker = None


def _get_reranker():
    """Lazy-load BGE reranker model. Returns None if model is 'none'."""
    global _reranker
    settings = get_settings()
    if settings.RERANKER_MODEL == "none":
        return None
    if _reranker is None:
        try:
            from sentence_transformers import CrossEncoder
            _reranker = CrossEncoder(settings.RERANKER_MODEL)
            logger.info("rerank.model_loaded", extra={"model": settings.RERANKER_MODEL})
        except Exception as e:
            logger.warning("rerank.model_failed", extra={"error": str(e)})
            return None
    return _reranker


def _deterministic_rerank_score(query: str, offer: dict) -> float:
    """Fallback reranker: keyword overlap + similarity score."""
    query_tokens = set(query.lower().split())
    text = f"{offer.get('category', '')} {offer.get('merchantName', '')} {offer.get('productName', '')}".lower()
    offer_tokens = set(text.split())
    overlap = len(query_tokens & offer_tokens)
    similarity = offer.get("_similarity", 0.5)
    return overlap * 0.3 + similarity * 0.7


def rerank_node(state: SearchState) -> dict:
    """Rerank candidates using BGE CrossEncoder or deterministic fallback."""
    request_id = state.get("request_id", "unknown")
    query = state.get("sanitized_query", "")
    candidates = state.get("candidates", [])
    logger.info("rerank.start", extra={"request_id": request_id, "count": len(candidates)})

    if not candidates:
        return {"reranked": []}

    reranker = _get_reranker()

    if reranker is not None:
        # Real BGE reranker: score query-passage pairs
        pairs = [
            (query, f"{c['merchantName']} {c['productName']} ${c['totalPrice']} {c['apr']}% APR {c['termMonths']} months {c['category']}")
            for c in candidates
        ]
        scores = reranker.predict(pairs)
        for i, c in enumerate(candidates):
            c["_rerank_score"] = float(scores[i])
    else:
        # Deterministic fallback
        for c in candidates:
            c["_rerank_score"] = _deterministic_rerank_score(query, c)

    # Sort by rerank score descending
    reranked = sorted(candidates, key=lambda x: x.get("_rerank_score", 0), reverse=True)

    logger.info("rerank.done", extra={
        "request_id": request_id,
        "top_score": reranked[0].get("_rerank_score", 0) if reranked else 0,
    })

    return {"reranked": reranked}
