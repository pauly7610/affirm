"""Quality scorecard endpoint — runs eval suite and returns metrics as JSON."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.pipeline.orchestrator import run_search

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/quality", tags=["quality"])

# Inline eval queries (subset of evals/queries.yaml for the live scorecard)
SCORECARD_QUERIES = [
    {"id": "q1", "query": "laptop under $800", "constraints": {"category": "electronics", "max_price": 800}},
    {"id": "q2", "query": "laptop under $800 with 0% APR", "constraints": {"category": "electronics", "max_price": 800, "only_zero_apr": True}},
    {"id": "q3", "query": "travel vacation under $1000", "constraints": {"category": "travel", "max_price": 1000}},
    {"id": "q4", "query": "stay under $50/mo", "constraints": {"max_monthly": 50}},
    {"id": "q5", "query": "only 0% apr", "constraints": {"only_zero_apr": True}},
    {"id": "q6", "query": "peloton bike", "constraints": {"category": "fitness"}},
    {"id": "q7", "query": "sneakers under $200 0% apr", "constraints": {"category": "sneakers", "max_price": 200, "only_zero_apr": True}},
    {"id": "q8", "query": "coffee machine under $700", "constraints": {"category": "appliances", "max_price": 700}},
]


class QueryResult(BaseModel):
    id: str
    query: str
    passed: bool
    constraint_ok: bool
    latency_ms: float
    result_count: int
    steps: list[dict]


class ScorecardResponse(BaseModel):
    total_queries: int
    passed: int
    failed: int
    constraint_adherence_pct: float
    avg_latency_ms: float
    p95_latency_ms: float
    step_latencies: dict[str, float]
    queries: list[QueryResult]


def _check_constraints(ranked: list[dict], constraints: dict) -> bool:
    """Check if top results respect constraints."""
    max_price = constraints.get("max_price")
    max_monthly = constraints.get("max_monthly")
    only_zero = constraints.get("only_zero_apr", False)
    category = constraints.get("category")

    # Only check items that should be strictly within constraints
    top = ranked[:2]  # check top 2 (relaxation may pad #3+)
    for item in top:
        if max_price and item.get("totalPrice", 0) > max_price:
            return False
        if max_monthly and item.get("monthlyPayment", 0) > max_monthly:
            return False
        if only_zero and item.get("apr", 1) != 0:
            return False
        if category and item.get("category") != category:
            return False
    return True


@router.get("/scorecard", response_model=ScorecardResponse)
async def get_scorecard():
    """Run eval queries and return quality metrics."""
    results: list[QueryResult] = []
    latencies: list[float] = []
    step_sums: dict[str, list[float]] = {}
    constraint_pass = 0
    total_constraint_checks = 0

    for sq in SCORECARD_QUERIES:
        t0 = time.perf_counter()
        try:
            result = await run_search(query=sq["query"])
            elapsed = round((time.perf_counter() - t0) * 1000, 1)
            ranked = result.get("ranked", [])
            trace = result.get("debug_trace", [])

            c_ok = _check_constraints(ranked, sq["constraints"])
            total_constraint_checks += 1
            if c_ok:
                constraint_pass += 1

            # Collect step latencies
            for step in trace:
                step_sums.setdefault(step["step"], []).append(step["ms"])

            results.append(QueryResult(
                id=sq["id"],
                query=sq["query"],
                passed=c_ok and len(ranked) > 0,
                constraint_ok=c_ok,
                latency_ms=elapsed,
                result_count=len(ranked),
                steps=[{"step": s["step"], "ms": s["ms"], "notes": s["notes"]} for s in trace],
            ))
            latencies.append(elapsed)
        except Exception as e:
            elapsed = round((time.perf_counter() - t0) * 1000, 1)
            results.append(QueryResult(
                id=sq["id"], query=sq["query"], passed=False,
                constraint_ok=False, latency_ms=elapsed, result_count=0, steps=[],
            ))
            latencies.append(elapsed)
            logger.error("scorecard.query_failed", extra={"id": sq["id"], "error": str(e)})

    passed = sum(1 for r in results if r.passed)
    avg_latency = round(sum(latencies) / len(latencies), 1) if latencies else 0
    sorted_lat = sorted(latencies)
    p95_idx = int(len(sorted_lat) * 0.95)
    p95 = sorted_lat[min(p95_idx, len(sorted_lat) - 1)] if sorted_lat else 0

    step_avgs = {
        k: round(sum(v) / len(v), 1) for k, v in step_sums.items()
    }

    adherence = round(constraint_pass / total_constraint_checks * 100, 0) if total_constraint_checks else 0

    return ScorecardResponse(
        total_queries=len(results),
        passed=passed,
        failed=len(results) - passed,
        constraint_adherence_pct=adherence,
        avg_latency_ms=avg_latency,
        p95_latency_ms=round(p95, 1),
        step_latencies=step_avgs,
        queries=results,
    )
