"""Profile endpoint: user summary, plans, insights, eligibility."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas import (
    ProfileSummaryResponse,
    UserProfileResponse,
    EligibilityResponse,
    ActivePlanResponse,
    InsightResponse,
)
from app.store import get_store

router = APIRouter(prefix="/v1/profile", tags=["profile"])


@router.get("/summary", response_model=ProfileSummaryResponse)
async def profile_summary(userId: str = "demo-user"):
    """Return full profile summary with plans, insights, eligibility."""
    store = get_store()

    user = UserProfileResponse(**store.user)
    eligibility = EligibilityResponse(**store.eligibility)
    plans = [ActivePlanResponse(**p) for p in store.plans]
    insights = [InsightResponse(**i) for i in store.insights]

    return ProfileSummaryResponse(
        user=user,
        eligibility=eligibility,
        plans=plans,
        insights=insights,
    )
