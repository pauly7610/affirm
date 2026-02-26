"""Pydantic request/response schemas for API endpoints."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class RefineOptions(BaseModel):
    onlyZeroApr: Optional[bool] = None
    maxMonthly: Optional[float] = None
    sort: Optional[str] = None
    category: Optional[str] = None


class SearchQueryRequest(BaseModel):
    query: str
    userId: str = "demo-user"
    sessionId: Optional[str] = None
    refine: Optional[RefineOptions] = None


class DecisionItemResponse(BaseModel):
    id: str
    merchantName: str
    productName: str
    category: str
    imageUrl: Optional[str] = None
    totalPrice: float
    termMonths: int
    apr: float
    monthlyPayment: float
    eligibilityConfidence: str
    reason: str
    disclosure: str


class RefineChipResponse(BaseModel):
    key: str
    label: str


class MonthlyImpactResponse(BaseModel):
    label: str
    value: float


class SearchQueryResponse(BaseModel):
    query: str
    aiSummary: str
    results: list[DecisionItemResponse]
    refineChips: list[RefineChipResponse]
    monthlyImpact: list[MonthlyImpactResponse]
    disclaimers: list[str]


class FeedbackRequest(BaseModel):
    itemId: str
    query: str
    rating: str  # "up" | "down"
    reason: Optional[str] = None


class FeedbackResponse(BaseModel):
    status: str = "ok"


class SuggestionsResponse(BaseModel):
    prompts: list[str]
    trending: list[str]


class ActivePlanResponse(BaseModel):
    id: str
    merchantName: str
    productName: str
    remainingBalance: float
    monthlyPayment: float
    nextPaymentDate: str
    totalPaid: float
    totalAmount: float
    termMonths: int
    apr: float


class InsightResponse(BaseModel):
    id: str
    text: str
    type: str
    sparklineData: Optional[list[float]] = None


class EligibilityResponse(BaseModel):
    spendingPower: float
    explanation: str
    lastRefreshed: str


class UserProfileResponse(BaseModel):
    name: str
    spendingPower: float
    activePlansCount: int
    paymentStatus: str
    accountHealth: str


class ProfileSummaryResponse(BaseModel):
    user: UserProfileResponse
    eligibility: EligibilityResponse
    plans: list[ActivePlanResponse]
    insights: list[InsightResponse]
