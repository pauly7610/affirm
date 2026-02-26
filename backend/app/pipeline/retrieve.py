"""Retrieve node: hybrid search (vector + BM25) + structured filters."""

from __future__ import annotations

import logging
import time

from app.store import get_store
from app.pipeline.state import SearchState

logger = logging.getLogger(__name__)

MAX_CANDIDATES = 50


def retrieve_node(state: SearchState) -> dict:
    """Retrieve candidate offers via hybrid search (vector + BM25) + constraint filters.

    Circuit breakers:
      - If embedder fails → fall back to BM25-only retrieval
      - If BM25 also fails → fall back to unfiltered store offers
    """
    t0 = time.perf_counter()
    request_id = state.get("request_id", "unknown")
    query = state.get("sanitized_query", "")
    constraints = state.get("parsed_constraints", {})
    logger.info("retrieve.start", extra={"request_id": request_id})

    store = get_store()
    retrieval_path = "hybrid"

    # Step 1a: Vector similarity search (with circuit breaker)
    vector_results: list[dict] = []
    try:
        query_embedding = store.get_embedding(query)
        vector_results = store.vector_search(query_embedding, top_k=20)
    except Exception as e:
        retrieval_path = "bm25-only"
        logger.warning("retrieve.vector_failed", extra={"request_id": request_id, "error": str(e)})

    # Step 1b: BM25 lexical search (with circuit breaker)
    bm25_results: list[dict] = []
    try:
        bm25_results = store.bm25_search(query, top_k=20)
    except Exception as e:
        if retrieval_path == "bm25-only":
            retrieval_path = "fallback-unfiltered"
        logger.warning("retrieve.bm25_failed", extra={"request_id": request_id, "error": str(e)})

    # Step 1c: Union + dedup (vector results take priority for _similarity)
    seen_ids: set[str] = set()
    merged: list[dict] = []
    for o in vector_results:
        if o["id"] not in seen_ids:
            merged.append(o)
            seen_ids.add(o["id"])
    for o in bm25_results:
        if o["id"] not in seen_ids:
            merged.append(o)
            seen_ids.add(o["id"])

    # Fallback: if both search paths failed, use raw store offers
    if not merged and retrieval_path == "fallback-unfiltered":
        logger.warning("retrieve.total_fallback", extra={"request_id": request_id})
        merged = [dict(o) for o in store.offers[:MAX_CANDIDATES]]

    merged = merged[:MAX_CANDIDATES]

    bm25_only_count = len([o for o in merged if "_bm25_score" in o and "_similarity" not in o])

    # Step 2: Apply structured filters from parsed constraints
    filtered = merged
    category = constraints.get("category")
    max_price = constraints.get("max_price")
    max_monthly = constraints.get("max_monthly")
    only_zero_apr = constraints.get("only_zero_apr", False)

    if category:
        filtered = [o for o in filtered if o["category"] == category]

    if max_price is not None:
        filtered = [o for o in filtered if o["totalPrice"] <= max_price]

    if max_monthly is not None:
        filtered = [o for o in filtered if o["monthlyPayment"] <= max_monthly]

    if only_zero_apr:
        filtered = [o for o in filtered if o["apr"] == 0]

    # If filters are too aggressive and we have < 3 results, relax by padding from vector pool
    relaxed_triggered = False
    if len(filtered) < 3:
        relaxed_triggered = True
        strict_count = len(filtered)
        logger.info("retrieve.relaxed_filters", extra={
            "request_id": request_id,
            "filtered_count": strict_count,
            "relaxing": True,
        })
        seen_ids = {o["id"] for o in filtered}
        for o in vector_results:
            if o["id"] not in seen_ids:
                filtered.append(o)
                seen_ids.add(o["id"])
            if len(filtered) >= 8:
                break

    logger.info("retrieve.done", extra={
        "request_id": request_id,
        "candidates": len(filtered),
        "relaxed": relaxed_triggered,
    })

    elapsed = round((time.perf_counter() - t0) * 1000, 1)
    trace = list(state.get("debug_trace", []))
    notes = f"{retrieval_path} → {len(merged)} merged, {bm25_only_count} bm25-only → {len(filtered)} after filter"
    if relaxed_triggered:
        notes += f" (relaxed from {strict_count})"
    trace.append({"step": "retrieve", "ms": elapsed, "notes": notes})
    return {"candidates": filtered, "debug_trace": trace}
