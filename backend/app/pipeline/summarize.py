"""Summarize node: generate AI summary + per-item reasons + refine chips + monthly impact."""

from __future__ import annotations

import logging
import time

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


def _build_item_reason(offer: dict, rank_idx: int, constraints: dict, profile: dict) -> str:
    """Per-item reason — tight product microcopy, 1 sentence, ≤90 chars."""
    monthly = offer["monthlyPayment"]
    existing = profile.get("existing_monthly", 0)
    spending_power = profile.get("spendingPower", 3000)
    apr = offer["apr"]

    # Comfort range + APR combo (most informative single sentence)
    if existing > 0:
        lo = max(30, round(existing / max(profile.get("plan_count", 1), 1) * 0.5, -1))
        hi = round(existing / max(profile.get("plan_count", 1), 1) * 1.2, -1)
        if lo <= monthly <= hi:
            if apr == 0:
                return f"Fits your usual ${lo:.0f}\u2013${hi:.0f}/mo range, 0% APR keeps cost flat."[:90]
            return f"Fits your usual ${lo:.0f}\u2013${hi:.0f}/mo range and stays within spending power."[:90]

    # 0% APR + budget
    if apr == 0 and constraints.get("max_monthly") and monthly <= constraints["max_monthly"]:
        return f"0% APR keeps cost flat, under your ${constraints['max_monthly']:.0f}/mo target."[:90]

    # 0% APR standalone
    if apr == 0:
        if spending_power and offer["totalPrice"] <= spending_power:
            return "0% APR keeps cost flat and stays within your spending power."[:90]
        return "0% APR keeps total cost down with no interest charges."[:90]

    # Budget fit
    if constraints.get("max_monthly") and monthly <= constraints["max_monthly"]:
        return f"Under your ${constraints['max_monthly']:.0f}/mo target with {apr}% APR."[:90]

    # Spending power fit
    if spending_power and offer["totalPrice"] <= spending_power:
        return f"Stays within your spending power at ${monthly:.0f}/mo."[:90]

    return "Matches your search criteria."[:90]


def _build_safety_signals(offer: dict, profile: dict) -> list[str]:
    """Per-item context signals — explains what the UI already shows, no new claims."""
    signals = []
    existing = profile.get("existing_monthly", 0)
    spending_power = profile.get("spendingPower", 3000)
    monthly = offer["monthlyPayment"]

    # Deterministic facts first (green-worthy)
    if offer["apr"] == 0:
        signals.append("0% APR keeps total cost down")

    # Obligations stability
    new_total = existing + monthly
    if existing > 0 and (new_total < existing * 1.35):
        signals.append("Keeps monthly obligations steady")

    # Spending power
    if spending_power and offer["totalPrice"] <= spending_power:
        signals.append("Stays within your spending power")

    # Eligibility estimate (always framed as estimate)
    if offer["eligibilityConfidence"] == "high":
        signals.append("Estimate: higher approval odds for this amount")
    elif offer["eligibilityConfidence"] == "med":
        signals.append("Estimate: moderate approval odds for this amount")

    # Comfort range
    if existing > 0:
        lo = max(30, round(existing / max(profile.get("plan_count", 1), 1) * 0.5, -1))
        hi = round(existing / max(profile.get("plan_count", 1), 1) * 1.2, -1)
        if lo <= monthly <= hi:
            signals.append("Fits your usual monthly range")

    return signals[:2]


def _build_monthly_impact(ranked: list[dict]) -> list[dict]:
    """Small bar chart data: monthly payment comparison across results."""
    return [
        {"label": o["merchantName"][:8], "value": o["monthlyPayment"]}
        for o in ranked[:5]
    ]


def _build_why_recommendation(constraints: dict, ranked: list[dict]) -> str:
    """Single sentence citing constraints that drove the top pick."""
    if not ranked:
        return "No results matched your criteria."
    top = ranked[0]
    parts = []
    if constraints.get("max_price") is not None:
        parts.append(f"under ${constraints['max_price']:.0f}")
    if constraints.get("max_monthly") is not None:
        parts.append(f"under ${constraints['max_monthly']:.0f}/mo")
    if constraints.get("only_zero_apr"):
        parts.append("0% APR")
    if constraints.get("category"):
        parts.append(constraints["category"])
    parts.append(f"{top['eligibilityConfidence']} confidence")
    text = f"{top['productName']}: {', '.join(parts)}."
    return text[:120]


def summarize_node(state: SearchState) -> dict:
    """Generate all output artifacts from ranked results."""
    t0 = time.perf_counter()
    request_id = state.get("request_id", "unknown")
    ranked = state.get("ranked", [])
    constraints = state.get("parsed_constraints", {})
    profile = state.get("user_profile", {})
    logger.info("summarize.start", extra={"request_id": request_id})

    # Build AI summary
    ai_summary = _build_summary(constraints, ranked)

    # Add per-item reasons + safety signals
    for i, o in enumerate(ranked):
        o["reason"] = _build_item_reason(o, i, constraints, profile)
        o["safetySignals"] = _build_safety_signals(o, profile)

    # Monthly impact visualization data
    monthly_impact = _build_monthly_impact(ranked)

    # Why this recommendation — single sentence citing constraints
    why = _build_why_recommendation(constraints, ranked)

    disclaimers = [
        "Estimates shown. Terms may vary at checkout.",
        "Checking eligibility won't affect your credit score.",
    ]

    logger.info("summarize.done", extra={"request_id": request_id, "summary_len": len(ai_summary)})

    elapsed = round((time.perf_counter() - t0) * 1000, 1)
    trace = list(state.get("debug_trace", []))
    trace.append({"step": "summarize", "ms": elapsed, "notes": f"summary={len(ai_summary)} chars, reasons={len(ranked)} items"})

    return {
        "ranked": ranked,
        "ai_summary": ai_summary,
        "refine_chips": REFINE_CHIPS,
        "monthly_impact": monthly_impact,
        "disclaimers": disclaimers,
        "why_this_recommendation": why,
        "debug_trace": trace,
    }
