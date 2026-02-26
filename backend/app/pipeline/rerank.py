"""Rerank node: semantic relevance boost (BGE / fallback) + category preference."""

from __future__ import annotations

import logging
import re
import time
from typing import Optional

from app.config import get_settings
from app.pipeline.state import SearchState

logger = logging.getLogger(__name__)

_reranker = None

MAX_CATEGORY_BOOST = 0.3


def _get_reranker():
    """Lazy-load BGE reranker model. Returns None if model is 'none'."""
    global _reranker
    settings = get_settings()
    if settings.RERANKER_MODEL == "none":
        return None
    if _reranker is None:
        try:
            from sentence_transformers import CrossEncoder
            t0 = time.perf_counter()
            _reranker = CrossEncoder(settings.RERANKER_MODEL)
            load_ms = round((time.perf_counter() - t0) * 1000, 1)
            logger.info("rerank.model_loaded", extra={"model": settings.RERANKER_MODEL, "load_ms": load_ms})
        except Exception as e:
            logger.warning("rerank.model_failed", extra={"error": str(e)})
            return None
    return _reranker


def _normalize_tokens(text: str) -> set[str]:
    """Lowercase, strip punctuation, remove numeric-only tokens (e.g. '$800')."""
    tokens = re.findall(r"[a-z]+", text.lower())
    return set(t for t in tokens if len(t) > 1)


def _deterministic_rerank_score(query: str, offer: dict) -> float:
    """Fallback reranker: normalized keyword overlap + similarity score."""
    query_tokens = _normalize_tokens(query)
    text = f"{offer.get('category', '')} {offer.get('merchantName', '')} {offer.get('productName', '')}"
    offer_tokens = _normalize_tokens(text)
    overlap = len(query_tokens & offer_tokens)
    similarity = offer.get("_similarity", 0.5)
    return overlap * 0.3 + similarity * 0.7


def _category_preference_boost(offer: dict, constraints: dict) -> float:
    """Boost offers matching the detected category or brand keywords. Clamped to MAX_CATEGORY_BOOST."""
    boost = 0.0
    target_cat = constraints.get("category")
    if target_cat and offer.get("category", "").lower() == target_cat.lower():
        boost += 0.15
    # Brand keyword overlap with raw_keywords
    raw_kw = set(constraints.get("raw_keywords", []))
    if raw_kw:
        merchant_tokens = _normalize_tokens(offer.get("merchantName", ""))
        product_tokens = _normalize_tokens(offer.get("productName", ""))
        overlap = len(raw_kw & (merchant_tokens | product_tokens))
        boost += overlap * 0.1
    return min(boost, MAX_CATEGORY_BOOST)


def rerank_node(state: SearchState) -> dict:
    """Rerank: semantic relevance (BGE / keyword fallback) + category/brand preference.
    Only scores top RERANK_TOP_K candidates; tail candidates keep original order."""
    t0 = time.perf_counter()
    request_id = state.get("request_id", "unknown")
    query = state.get("sanitized_query", "")
    candidates = state.get("candidates", [])
    constraints = state.get("parsed_constraints", {})
    logger.info("rerank.start", extra={"request_id": request_id, "count": len(candidates)})

    if not candidates:
        return {"reranked": []}

    # Top-K: only rerank the first N candidates (from config budget)
    settings = get_settings()
    rerank_top_k = settings.MAX_RERANK_CANDIDATES
    rerank_timeout_ms = settings.RERANK_TIMEOUT_MS

    head = candidates[:rerank_top_k]
    tail = candidates[rerank_top_k:]

    reranker = _get_reranker()
    used_model = False
    timed_out = False

    personalized = state.get("personalized", True)

    if reranker is not None:
        # Real BGE reranker: score query-passage pairs
        rerank_t0 = time.perf_counter()
        pairs = [
            (query, f"{c['merchantName']} {c['productName']} ${c['totalPrice']} {c['apr']}% APR {c['termMonths']} months {c['category']}")
            for c in head
        ]
        scores = reranker.predict(pairs)
        rerank_elapsed = (time.perf_counter() - rerank_t0) * 1000
        if rerank_elapsed > rerank_timeout_ms:
            timed_out = True
            logger.warning("rerank.timeout", extra={"request_id": request_id, "ms": rerank_elapsed})
        for i, c in enumerate(head):
            boost = _category_preference_boost(c, constraints) if personalized else 0.0
            c["_rerank_score"] = float(scores[i]) + boost
        used_model = True
    else:
        # Deterministic fallback (fast-path): keyword overlap + similarity + category preference
        for c in head:
            boost = _category_preference_boost(c, constraints) if personalized else 0.0
            c["_rerank_score"] = _deterministic_rerank_score(query, c) + boost

    # Sort head by rerank score descending, append unsorted tail
    reranked = sorted(head, key=lambda x: x.get("_rerank_score", 0), reverse=True) + tail

    logger.info("rerank.done", extra={
        "request_id": request_id,
        "reranked_count": len(head),
        "top_score": reranked[0].get("_rerank_score", 0) if reranked else 0,
    })

    elapsed = round((time.perf_counter() - t0) * 1000, 1)
    trace = list(state.get("debug_trace", []))
    mode = "full-rerank" if used_model else "fast-path"
    method = "bge-crossencoder" if used_model else "keyword+similarity"
    top_str = f", top={reranked[0].get('_rerank_score', 0):.2f}" if reranked else ""
    pers_str = ", personalized" if personalized else ", generic"
    timeout_str = ", TIMEOUT" if timed_out else ""
    trace.append({"step": "rerank", "ms": elapsed, "notes": f"mode={mode}, {method}, scored {len(head)}/{len(candidates)}{top_str}{pers_str}{timeout_str}"})
    return {"reranked": reranked, "debug_trace": trace}
