"""Pydantic request/response schemas for API endpoints.

Source of truth: packages/shared/models.py (core domain models).
This module re-exports shared models and adds backend-only schemas.
"""

from __future__ import annotations

import sys
import os
from typing import Optional
from pydantic import BaseModel, Field

# Ensure packages/shared is importable
_packages_dir = os.path.join(os.path.dirname(__file__), "..", "..", "packages")
if _packages_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(_packages_dir))

from shared.models import (
    DecisionItem,
    RefineChip,
    MonthlyImpactBar,
    RefineOptions as SharedRefineOptions,
    SearchRequest as SharedSearchRequest,
    SearchResponse as SharedSearchResponse,
    SearchFeedback,
    SuggestionsResponse,
    ActivePlan,
    Insight,
    EligibilityPreview,
    UserProfile,
    ProfileSummary,
)

# ── Re-export shared models under API-friendly names ──
# These aliases keep existing imports working across the backend.

RefineOptions = SharedRefineOptions
SearchQueryRequest = SharedSearchRequest
DecisionItemResponse = DecisionItem
RefineChipResponse = RefineChip
MonthlyImpactResponse = MonthlyImpactBar
FeedbackRequest = SearchFeedback
ActivePlanResponse = ActivePlan
InsightResponse = Insight
EligibilityResponse = EligibilityPreview
UserProfileResponse = UserProfile
ProfileSummaryResponse = ProfileSummary


# ── Agentic trace models (backend-only) ──

class TraceStep(BaseModel):
    step: str
    ms: float
    notes: str


class SearchQueryResponse(BaseModel):
    """Extended search response with agentic trace fields."""
    query: str
    aiSummary: str = Field(alias="aiSummary")
    results: list[DecisionItemResponse]
    refineChips: list[RefineChipResponse] = Field(alias="refineChips")
    monthlyImpact: list[MonthlyImpactResponse] = Field(alias="monthlyImpact")
    disclaimers: list[str]
    # Agentic fields
    appliedConstraints: dict = Field(default_factory=dict, alias="appliedConstraints")
    whyThisRecommendation: str = Field(default="", alias="whyThisRecommendation")
    debugTrace: Optional[list[TraceStep]] = Field(default=None, alias="debugTrace")

    model_config = {"populate_by_name": True}


class FeedbackResponse(BaseModel):
    status: str = "ok"
