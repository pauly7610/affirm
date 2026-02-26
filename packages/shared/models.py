"""Shared Pydantic models — mirrors packages/shared/types.ts"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EligibilityConfidence(str, Enum):
    high = "high"
    med = "med"
    low = "low"


class DecisionItem(BaseModel):
    id: str
    merchant_name: str = Field(alias="merchantName")
    product_name: str = Field(alias="productName")
    category: str
    image_url: Optional[str] = Field(None, alias="imageUrl")
    total_price: float = Field(alias="totalPrice")
    term_months: int = Field(alias="termMonths")
    apr: float
    monthly_payment: float = Field(alias="monthlyPayment")
    eligibility_confidence: EligibilityConfidence = Field(alias="eligibilityConfidence")
    reason: str
    disclosure: str

    model_config = {"populate_by_name": True}


class RefineChip(BaseModel):
    key: str
    label: str


class MonthlyImpactBar(BaseModel):
    label: str
    value: float


class RefineOptions(BaseModel):
    only_zero_apr: Optional[bool] = Field(None, alias="onlyZeroApr")
    max_monthly: Optional[float] = Field(None, alias="maxMonthly")
    sort: Optional[str] = None
    category: Optional[str] = None

    model_config = {"populate_by_name": True}


class SearchRequest(BaseModel):
    query: str
    user_id: Optional[str] = Field("demo-user", alias="userId")
    session_id: Optional[str] = Field(None, alias="sessionId")
    refine: Optional[RefineOptions] = None

    model_config = {"populate_by_name": True}


class SearchResponse(BaseModel):
    query: str
    ai_summary: str = Field(alias="aiSummary")
    results: list[DecisionItem]
    refine_chips: list[RefineChip] = Field(alias="refineChips")
    monthly_impact: list[MonthlyImpactBar] = Field(alias="monthlyImpact")
    disclaimers: list[str]

    model_config = {"populate_by_name": True}


class SearchFeedback(BaseModel):
    item_id: str = Field(alias="itemId")
    query: str
    rating: str  # "up" | "down"
    reason: Optional[str] = None

    model_config = {"populate_by_name": True}


class SuggestionsResponse(BaseModel):
    prompts: list[str]
    trending: list[str]


class ActivePlan(BaseModel):
    id: str
    merchant_name: str = Field(alias="merchantName")
    product_name: str = Field(alias="productName")
    remaining_balance: float = Field(alias="remainingBalance")
    monthly_payment: float = Field(alias="monthlyPayment")
    next_payment_date: str = Field(alias="nextPaymentDate")
    total_paid: float = Field(alias="totalPaid")
    total_amount: float = Field(alias="totalAmount")
    term_months: int = Field(alias="termMonths")
    apr: float

    model_config = {"populate_by_name": True}


class Insight(BaseModel):
    id: str
    text: str
    type: str  # "saving" | "behavior" | "projection"
    sparkline_data: Optional[list[float]] = Field(None, alias="sparklineData")

    model_config = {"populate_by_name": True}


class EligibilityPreview(BaseModel):
    spending_power: float = Field(alias="spendingPower")
    explanation: str
    last_refreshed: str = Field(alias="lastRefreshed")

    model_config = {"populate_by_name": True}


class UserProfile(BaseModel):
    name: str
    spending_power: float = Field(alias="spendingPower")
    active_plans_count: int = Field(alias="activePlansCount")
    payment_status: str = Field(alias="paymentStatus")
    account_health: str = Field(alias="accountHealth")

    model_config = {"populate_by_name": True}


class ProfileSummary(BaseModel):
    user: UserProfile
    eligibility: EligibilityPreview
    plans: list[ActivePlan]
    insights: list[Insight]

    model_config = {"populate_by_name": True}
