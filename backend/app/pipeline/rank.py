"""Rank node: deterministic affordability scoring with refine-toggle weighting."""

from __future__ import annotations

import logging

from app.pipeline.state import SearchState

logger = logging.getLogger(__name__)

CONFIDENCE_SCORES = {"high": 1.0, "med": 0.6, "low": 0.3}


def rank_node(state: SearchState) -> dict:
    """Score and rank reranked candidates by affordability, APR, confidence, and rerank score."""
    request_id = state.get("request_id", "unknown")
    reranked = state.get("reranked", [])
    constraints = state.get("parsed_constraints", {})
    sort_mode = constraints.get("sort")
    logger.info("rank.start", extra={"request_id": request_id, "count": len(reranked)})

    if not reranked:
        return {"ranked": []}

    # Normalize values for scoring
    max_monthly = max(o["monthlyPayment"] for o in reranked) or 1
    max_total = max(o["totalPrice"] for o in reranked) or 1
    max_apr = max(o["apr"] for o in reranked) or 1

    for o in reranked:
        # Component scores (0-1, higher is better)
        affordability = 1.0 - (o["monthlyPayment"] / max_monthly)
        apr_score = 1.0 - (o["apr"] / max_apr) if max_apr > 0 else 1.0
        confidence = CONFIDENCE_SCORES.get(o["eligibilityConfidence"], 0.5)
        rerank = o.get("_rerank_score", 0.5)
        total_score = 1.0 - (o["totalPrice"] / max_total)

        # Weighted composite — weights shift based on sort mode
        if sort_mode == "lowest_monthly":
            score = affordability * 0.5 + apr_score * 0.15 + confidence * 0.15 + rerank * 0.2
        elif sort_mode == "lowest_total":
            score = total_score * 0.5 + apr_score * 0.15 + confidence * 0.15 + rerank * 0.2
        elif sort_mode == "shortest_term":
            term_score = 1.0 - (o["termMonths"] / 24)
            score = term_score * 0.4 + affordability * 0.2 + confidence * 0.2 + rerank * 0.2
        else:
            # Default: balanced
            score = affordability * 0.3 + apr_score * 0.2 + confidence * 0.2 + rerank * 0.3

        o["_rank_score"] = score

    ranked = sorted(reranked, key=lambda x: x.get("_rank_score", 0), reverse=True)

    # Cap at 5 results (1 recommended + 4 alternatives)
    ranked = ranked[:5]

    logger.info("rank.done", extra={
        "request_id": request_id,
        "top": ranked[0]["productName"] if ranked else "none",
    })

    return {"ranked": ranked}
