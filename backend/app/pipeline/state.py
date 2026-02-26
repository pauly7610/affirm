"""Search pipeline state — flows through every LangGraph node."""

from __future__ import annotations

from typing import TypedDict, Optional, Any


class ParsedConstraints(TypedDict, total=False):
    max_price: Optional[float]
    max_monthly: Optional[float]
    only_zero_apr: bool
    category: Optional[str]
    sort: Optional[str]
    raw_keywords: list[str]


class SearchState(TypedDict, total=False):
    # Input
    query: str
    sanitized_query: str
    request_id: str
    user_id: str

    # Refine overrides from client
    refine_only_zero_apr: Optional[bool]
    refine_max_monthly: Optional[float]
    refine_sort: Optional[str]
    refine_category: Optional[str]

    # Privacy / personalization
    personalized: bool

    # Pipeline stages
    parsed_constraints: ParsedConstraints
    route: str  # "simple" | "complex"
    candidates: list[dict]
    reranked: list[dict]
    ranked: list[dict]

    # Output
    ai_summary: str
    refine_chips: list[dict]
    monthly_impact: list[dict]
    disclaimers: list[str]
    error: Optional[str]

    # Agentic trace (dev only)
    debug_trace: list[dict]
    applied_constraints: dict
    why_this_recommendation: str
