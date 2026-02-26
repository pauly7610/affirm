"""Search endpoints: query, suggestions, feedback."""

from __future__ import annotations

import logging
import os

from fastapi import APIRouter, HTTPException

from app.schemas import (
    SearchQueryRequest,
    SearchQueryResponse,
    DecisionItemResponse,
    RefineChipResponse,
    MonthlyImpactResponse,
    TraceStep,
    FeedbackRequest,
    FeedbackResponse,
    SuggestionsResponse,
)
from app.pipeline.orchestrator import run_search
from app.store import get_store

_DEV_MODE = os.getenv("DEBUG", "true").lower() == "true"

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/search", tags=["search"])


@router.post("/query", response_model=SearchQueryResponse)
async def search_query(req: SearchQueryRequest):
    """Run the agentic search pipeline."""
    refine_dict = req.refine.model_dump() if req.refine else None

    result = await run_search(
        query=req.query,
        user_id=req.user_id,
        refine=refine_dict,
        personalized=req.personalized,
    )

    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])

    ranked = result.get("ranked", [])
    results = [
        DecisionItemResponse(
            id=o["id"],
            merchantName=o["merchantName"],
            productName=o["productName"],
            category=o["category"],
            imageUrl=o.get("imageUrl"),
            totalPrice=o["totalPrice"],
            termMonths=o["termMonths"],
            apr=o["apr"],
            monthlyPayment=o["monthlyPayment"],
            eligibilityConfidence=o["eligibilityConfidence"],
            reason=o.get("reason", ""),
            disclosure=o.get("disclosure", "Final approval happens at checkout."),
        )
        for o in ranked
    ]

    refine_chips = [
        RefineChipResponse(key=c["key"], label=c["label"])
        for c in result.get("refine_chips", [])
    ]

    monthly_impact = [
        MonthlyImpactResponse(label=m["label"], value=m["value"])
        for m in result.get("monthly_impact", [])
    ]

    # Agentic trace (dev only)
    debug_trace = None
    if _DEV_MODE:
        debug_trace = [
            TraceStep(step=t["step"], ms=t["ms"], notes=t["notes"])
            for t in result.get("debug_trace", [])
        ]

    return SearchQueryResponse(
        query=req.query,
        aiSummary=result.get("ai_summary", ""),
        results=results,
        refineChips=refine_chips,
        monthlyImpact=monthly_impact,
        disclaimers=result.get("disclaimers", []),
        appliedConstraints=result.get("applied_constraints", {}),
        whyThisRecommendation=result.get("why_this_recommendation", ""),
        debugTrace=debug_trace,
    )


@router.get("/suggestions", response_model=SuggestionsResponse)
async def search_suggestions(userId: str = "demo-user"):
    """Return suggested prompts and trending intents."""
    return SuggestionsResponse(
        prompts=[
            "Upgrade my laptop",
            "Plan a trip",
            "Only 0% APR",
            "Stay under $50/mo",
            "Cheaper options",
        ],
        trending=[
            "MacBook Air M3",
            "PS5 Pro",
            "Home gym setup",
            "Beach vacation under $1000",
        ],
    )


@router.post("/feedback", response_model=FeedbackResponse)
async def search_feedback(req: FeedbackRequest):
    """Store thumbs up/down feedback."""
    store = get_store()
    store.add_feedback({
        "itemId": req.item_id,
        "query": req.query,
        "rating": req.rating,
        "reason": req.reason,
    })
    logger.info("feedback.stored", extra={"item_id": req.item_id, "rating": req.rating})
    return FeedbackResponse(status="ok")
