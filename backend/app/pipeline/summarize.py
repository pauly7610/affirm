"""Summarize node: generate AI summary + per-item reasons + refine chips + monthly impact."""

from __future__ import annotations

import logging

from app.pipeline.state import SearchState

logger = logging.getLogger(__name__)

REFINE_CHIPS = [
    {"key": "lowest_monthly", "label": "Lower monthly"},
    {"key": "only_zero_apr", "label": "Only 0% APR"},
    {"key": "lowest_total", "label": "Cheaper total"},
    {"key": "compare_brands", "label": "Compare brands"},
    {"key": "shortest_term", "label": "Shorter term"},
]


def _build_summary(constraints: dict, ranked: list[dict]) -> str:
    """Template-based AI summary — no LLM required."""
    parts = ["We prioritized options that"]
    factors = []

    if constraints.get("max_monthly"):
        factors.append(f"fit under ${constraints['max_monthly']:.0f}/mo")
    elif constraints.get("max_price"):
        factors.append(f"stay under ${constraints['max_price']:.0f}")
    else:
        factors.append("fit your budget")

    if constraints.get("only_zero_apr"):
        factors.append("offer 0% APR")
    else:
        factors.append("minimize interest")

    factors.append("match your eligibility")

    parts.append(", ".join(factors) + ".")

    if ranked:
        top = ranked[0]
        if top["apr"] == 0:
            parts.append(f"Top pick: {top['productName']} at ${top['monthlyPayment']:.0f}/mo with no interest.")
        else:
            parts.append(f"Top pick: {top['productName']} at ${top['monthlyPayment']:.0f}/mo.")

    return " ".join(parts)


def _build_item_reason(offer: dict, rank_idx: int, constraints: dict) -> str:
    """Per-item 'why you're seeing this' explanation."""
    reasons = []

    if rank_idx == 0:
        reasons.append("Recommended based on your spending profile.")
    elif offer["apr"] == 0:
        reasons.append("0% APR keeps your total cost low.")
    elif offer["eligibilityConfidence"] == "high":
        reasons.append("High eligibility based on your payment history.")

    if constraints.get("max_monthly") and offer["monthlyPayment"] <= constraints["max_monthly"]:
        reasons.append(f"Fits your ${constraints['max_monthly']:.0f}/mo target.")

    if offer["eligibilityConfidence"] == "high" and rank_idx > 0:
        reasons.append("Strong approval likelihood.")

    if not reasons:
        reasons.append("Matches your search criteria.")

    return " ".join(reasons[:2])


def _build_monthly_impact(ranked: list[dict]) -> list[dict]:
    """Small bar chart data: monthly payment comparison across results."""
    return [
        {"label": o["merchantName"][:8], "value": o["monthlyPayment"]}
        for o in ranked[:5]
    ]


def summarize_node(state: SearchState) -> dict:
    """Generate all output artifacts from ranked results."""
    request_id = state.get("request_id", "unknown")
    ranked = state.get("ranked", [])
    constraints = state.get("parsed_constraints", {})
    logger.info("summarize.start", extra={"request_id": request_id})

    # Build AI summary
    ai_summary = _build_summary(constraints, ranked)

    # Add per-item reasons
    for i, o in enumerate(ranked):
        o["reason"] = _build_item_reason(o, i, constraints)

    # Monthly impact visualization data
    monthly_impact = _build_monthly_impact(ranked)

    disclaimers = [
        "Estimates shown. Terms may vary at checkout.",
        "Checking eligibility won't affect your credit score.",
    ]

    logger.info("summarize.done", extra={"request_id": request_id, "summary_len": len(ai_summary)})

    return {
        "ranked": ranked,
        "ai_summary": ai_summary,
        "refine_chips": REFINE_CHIPS,
        "monthly_impact": monthly_impact,
        "disclaimers": disclaimers,
    }
