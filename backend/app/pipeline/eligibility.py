"""Eligibility preview node: mock tool call that estimates approval confidence per offer."""

from __future__ import annotations

import logging
import time

from app.store import get_store
from app.pipeline.state import SearchState

logger = logging.getLogger(__name__)

TIER_CAPS = {
    "high": float("inf"),
    "med": 1500.0,
    "low": 500.0,
}

CONFIDENCE_BOOST = {
    "high": 0.10,
    "med": 0.0,
    "low": -0.05,
}


def eligibility_preview(user_id: str, amount: float) -> dict:
    """Mock tool call: estimate approval confidence for a given amount.

    In production this would hit a real eligibility service.
    Returns confidence tier + max spend estimate.
    """
    store = get_store()
    spending_power = store.user.get("spendingPower", 3000)

    if amount <= spending_power * 0.5:
        tier = "high"
    elif amount <= spending_power * 0.9:
        tier = "med"
    else:
        tier = "low"

    return {
        "tier": tier,
        "max_spend": spending_power,
        "amount_requested": amount,
    }


def eligibility_node(state: SearchState) -> dict:
    """Run eligibility preview on ranked results, cap/boost based on tier."""
    t0 = time.perf_counter()
    request_id = state.get("request_id", "unknown")
    user_id = state.get("user_id", "demo-user")
    ranked = state.get("ranked", [])
    logger.info("eligibility.start", extra={"request_id": request_id, "count": len(ranked)})

    if not ranked:
        return {"ranked": ranked}

    capped = 0
    for o in ranked:
        preview = eligibility_preview(user_id, o["totalPrice"])
        tier = preview["tier"]
        o["eligibilityConfidence"] = tier

        # Boost/penalize rank score based on eligibility tier
        boost = CONFIDENCE_BOOST.get(tier, 0.0)
        o["_rank_score"] = o.get("_rank_score", 0.5) + boost

        # Cap: items above spending power get flagged
        if o["totalPrice"] > preview["max_spend"]:
            o["_rank_score"] = max(o["_rank_score"] - 0.3, 0.0)
            capped += 1

    # Re-sort after eligibility adjustments
    ranked = sorted(ranked, key=lambda x: x.get("_rank_score", 0), reverse=True)

    logger.info("eligibility.done", extra={
        "request_id": request_id,
        "capped": capped,
    })

    elapsed = round((time.perf_counter() - t0) * 1000, 1)
    trace = list(state.get("debug_trace", []))
    trace.append({
        "step": "eligibility",
        "ms": elapsed,
        "notes": f"preview applied to {len(ranked)} items, {capped} capped above spending power",
    })
    return {"ranked": ranked, "debug_trace": trace}
