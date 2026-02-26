"""Retrieve node: vector similarity search + structured SQL-like filters."""

from __future__ import annotations

import logging

from app.store import get_store
from app.pipeline.state import SearchState

logger = logging.getLogger(__name__)


def retrieve_node(state: SearchState) -> dict:
    """Retrieve candidate offers via vector search + constraint filters."""
    request_id = state.get("request_id", "unknown")
    query = state.get("sanitized_query", "")
    constraints = state.get("parsed_constraints", {})
    logger.info("retrieve.start", extra={"request_id": request_id})

    store = get_store()

    # Step 1: Vector similarity search (top 20 candidates)
    query_embedding = store.get_embedding(query)
    vector_results = store.vector_search(query_embedding, top_k=20)

    # Step 2: Apply structured filters from parsed constraints
    filtered = vector_results
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

    # If filters are too aggressive and we have < 3 results, relax and use vector-only
    if len(filtered) < 3:
        logger.info("retrieve.relaxed_filters", extra={
            "request_id": request_id,
            "filtered_count": len(filtered),
            "relaxing": True,
        })
        # Keep what we have but pad with vector results that don't duplicate
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
    })

    return {"candidates": filtered}
