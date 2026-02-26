export type EligibilityConfidence = "high" | "med" | "low";

export interface DecisionItem {
  id: string;
  merchantName: string;
  productName: string;
  category: string;
  imageUrl: string | null;
  totalPrice: number;
  termMonths: number;
  apr: number;
  monthlyPayment: number;
  eligibilityConfidence: EligibilityConfidence;
  reason: string;
  safetySignals: string[];
  disclosure: string;
}

export interface RefineChip {
  key: string;
  label: string;
}

export interface MonthlyImpactBar {
  label: string;
  value: number;
}

export interface SearchRequest {
  query: string;
  userId?: string;
  sessionId?: string;
  personalized?: boolean;
  refine?: {
    onlyZeroApr?: boolean;
    maxMonthly?: number;
    sort?: "lowest_monthly" | "lowest_total" | "shortest_term";
    category?: string;
  };
}

export interface TraceStep {
  step: string;
  ms: number;
  notes: string;
}

export interface SearchResponse {
  query: string;
  aiSummary: string;
  results: DecisionItem[];
  refineChips: RefineChip[];
  monthlyImpact: MonthlyImpactBar[];
  disclaimers: string[];
  appliedConstraints: Record<string, string | boolean>;
  whyThisRecommendation: string;
  debugTrace?: TraceStep[];
}

export interface SearchFeedback {
  itemId: string;
  query: string;
  rating: "up" | "down";
  reason?: string;
}

export interface ScorecardQueryResult {
  id: string;
  query: string;
  passed: boolean;
  constraint_ok: boolean;
  latency_ms: number;
  result_count: number;
  steps: { step: string; ms: number; notes: string }[];
}

export interface ScorecardResponse {
  total_queries: number;
  passed: number;
  failed: number;
  constraint_adherence_pct: number;
  avg_latency_ms: number;
  p95_latency_ms: number;
  step_latencies: Record<string, number>;
  queries: ScorecardQueryResult[];
}

export interface SuggestionsResponse {
  prompts: string[];
  trending: string[];
}

export interface ActivePlan {
  id: string;
  merchantName: string;
  productName: string;
  remainingBalance: number;
  monthlyPayment: number;
  nextPaymentDate: string;
  totalPaid: number;
  totalAmount: number;
  termMonths: number;
  apr: number;
}

export interface Insight {
  id: string;
  text: string;
  type: "saving" | "behavior" | "projection";
  sparklineData?: number[];
}

export interface EligibilityPreview {
  spendingPower: number;
  explanation: string;
  lastRefreshed: string;
}

export interface UserProfile {
  name: string;
  spendingPower: number;
  activePlansCount: number;
  paymentStatus: "excellent" | "good" | "fair";
  accountHealth: "strong" | "good" | "needs_attention";
}

export interface ProfileSummary {
  user: UserProfile;
  eligibility: EligibilityPreview;
  plans: ActivePlan[];
  insights: Insight[];
}
