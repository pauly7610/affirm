"""Search quality evaluation harness.

Runs queries from evals/queries.yaml against the pipeline,
checks constraint adherence, result relevance, explanation quality,
and reports precision/recall metrics + per-step latency.

Usage:
    python -m evals.run_eval
    make eval
"""

from __future__ import annotations

import asyncio
import sys
import time
import os
from pathlib import Path

import yaml

# Ensure backend root is on path
_backend_root = str(Path(__file__).resolve().parent.parent)
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

from app.pipeline.orchestrator import run_search


def load_eval_suite() -> dict:
    path = Path(__file__).parent / "queries.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


class EvalResult:
    def __init__(self, query_id: str):
        self.query_id = query_id
        self.passed: list[str] = []
        self.failed: list[str] = []
        self.latency_by_step: dict[str, float] = {}
        self.total_ms: float = 0.0

    @property
    def ok(self) -> bool:
        return len(self.failed) == 0

    def check(self, name: str, condition: bool, detail: str = ""):
        if condition:
            self.passed.append(name)
        else:
            self.failed.append(f"{name}: {detail}" if detail else name)


async def eval_query(spec: dict, explanation_rules: dict) -> EvalResult:
    """Evaluate a single query spec against the pipeline."""
    result = EvalResult(spec["id"])
    t0 = time.perf_counter()

    pipeline_result = await run_search(query=spec["query"])
    result.total_ms = round((time.perf_counter() - t0) * 1000, 1)

    # Extract latency per step from debug trace
    for t in pipeline_result.get("debug_trace", []):
        result.latency_by_step[t["step"]] = t["ms"]

    # --- Error queries ---
    if spec.get("expected_error"):
        result.check("expected_error", pipeline_result.get("error") is not None,
                      "Expected error but got success")
        return result

    # --- Non-error queries ---
    result.check("no_error", pipeline_result.get("error") is None,
                  f"Got error: {pipeline_result.get('error')}")
    if pipeline_result.get("error"):
        return result

    ranked = pipeline_result.get("ranked", [])
    constraints = pipeline_result.get("applied_constraints", {})
    top_k = spec.get("top_k", 3)
    top_results = ranked[:top_k]

    # --- Constraint parsing checks ---
    expected_constraints = spec.get("expected_constraints", {})
    if "category" in expected_constraints:
        result.check("constraint_category",
                      constraints.get("category") == expected_constraints["category"],
                      f"Expected {expected_constraints['category']}, got {constraints.get('category')}")
    if "max_price" in expected_constraints:
        result.check("constraint_max_price",
                      "budget" in constraints,
                      f"Expected budget constraint, got {constraints}")
    if "max_monthly" in expected_constraints:
        result.check("constraint_max_monthly",
                      "maxMonthly" in constraints,
                      f"Expected maxMonthly constraint, got {constraints}")
    if expected_constraints.get("only_zero_apr"):
        result.check("constraint_zero_apr",
                      constraints.get("zeroApr") is True,
                      f"Expected zeroApr=True, got {constraints}")

    # --- Result relevance checks ---
    must_exclude = spec.get("must_exclude", {})
    if must_exclude.get("max_price") and top_results:
        cap = must_exclude["max_price"]
        violations = [r for r in top_results if r["totalPrice"] > cap]
        result.check("price_adherence",
                      len(violations) == 0,
                      f"{len(violations)}/{len(top_results)} exceed ${cap}")

    if must_exclude.get("max_monthly") and top_results:
        cap = must_exclude["max_monthly"]
        violations = [r for r in top_results if r["monthlyPayment"] > cap]
        result.check("monthly_adherence",
                      len(violations) == 0,
                      f"{len(violations)}/{len(top_results)} exceed ${cap}/mo")

    if must_exclude.get("only_zero_apr") and top_results:
        violations = [r for r in top_results if r["apr"] != 0]
        result.check("apr_adherence",
                      len(violations) == 0,
                      f"{len(violations)}/{len(top_results)} have non-zero APR")

    must_cats = spec.get("must_include_categories", [])
    if must_cats and top_results:
        cats_found = {r["category"] for r in top_results}
        result.check("category_relevance",
                      bool(cats_found & set(must_cats)),
                      f"Expected one of {must_cats}, got {cats_found}")

    must_merchants = spec.get("must_include_merchants", [])
    if must_merchants and ranked:
        merchants_found = {r["merchantName"] for r in ranked[:5]}
        result.check("merchant_presence",
                      bool(merchants_found & set(must_merchants)),
                      f"Expected one of {must_merchants} in top 5, got {merchants_found}")

    must_product_sub = spec.get("must_include_product_substring")
    if must_product_sub and ranked:
        found = any(must_product_sub.lower() in r["productName"].lower() for r in ranked[:5])
        result.check("product_substring",
                      found,
                      f"'{must_product_sub}' not in top 5 product names")

    # --- Explanation quality checks ---
    if explanation_rules and ranked:
        max_reason_len = explanation_rules.get("max_reason_length", 90)
        banned = explanation_rules.get("banned_phrases", [])
        must_cite = explanation_rules.get("must_cite_one_of", [])

        # Check per-item reasons
        for i, item in enumerate(top_results):
            reason = item.get("reason", "")
            result.check(f"reason_length[{i}]",
                          len(reason) <= max_reason_len,
                          f"len={len(reason)}, max={max_reason_len}: '{reason[:50]}...'")

            for phrase in banned:
                result.check(f"reason_no_banned[{i}]",
                              phrase.lower() not in reason.lower(),
                              f"Found '{phrase}' in reason")

            cited = any(kw.lower() in reason.lower() for kw in must_cite)
            result.check(f"reason_cites_factor[{i}]",
                          cited,
                          f"Reason doesn't cite any of {must_cite[:5]}...")

        # Check whyThisRecommendation
        why = pipeline_result.get("why_this_recommendation", "")
        max_why_len = explanation_rules.get("max_why_recommendation_length", 120)
        result.check("why_length",
                      len(why) <= max_why_len,
                      f"len={len(why)}, max={max_why_len}")
        for phrase in banned:
            result.check("why_no_banned",
                          phrase.lower() not in why.lower(),
                          f"Found '{phrase}' in whyThisRecommendation")

    return result


async def run_eval_suite():
    suite = load_eval_suite()
    queries = suite["queries"]
    explanation_rules = suite.get("explanation_rules", {})

    print(f"\n{'='*70}")
    print(f"  Search Quality Evaluation — {len(queries)} queries")
    print(f"{'='*70}\n")

    results: list[EvalResult] = []
    total_checks = 0
    total_passed = 0
    step_latencies: dict[str, list[float]] = {}

    for spec in queries:
        er = await eval_query(spec, explanation_rules)
        results.append(er)
        total_checks += len(er.passed) + len(er.failed)
        total_passed += len(er.passed)

        # Collect latencies
        for step, ms in er.latency_by_step.items():
            step_latencies.setdefault(step, []).append(ms)

        status = "✓ PASS" if er.ok else "✗ FAIL"
        print(f"  {status}  {er.query_id}: {spec['query'][:50]:<50}  ({er.total_ms:.0f}ms)")
        if not er.ok:
            for f in er.failed:
                print(f"         ↳ {f}")

    # --- Summary ---
    passed_queries = sum(1 for r in results if r.ok)
    failed_queries = len(results) - passed_queries

    print(f"\n{'─'*70}")
    print(f"  Results: {passed_queries}/{len(results)} queries passed")
    print(f"  Checks: {total_passed}/{total_checks} passed")
    print(f"{'─'*70}")

    # Constraint adherence
    constraint_checks = [c for r in results for c in r.passed + r.failed if "adherence" in c or "constraint" in c]
    constraint_passed = [c for r in results for c in r.passed if "adherence" in c or "constraint" in c]
    if constraint_checks:
        rate = len(constraint_passed) / len(constraint_checks) * 100
        print(f"  Constraint adherence: {rate:.0f}% ({len(constraint_passed)}/{len(constraint_checks)})")

    # Explanation quality
    explanation_checks = [c for r in results for c in r.passed + r.failed if "reason" in c or "why" in c]
    explanation_passed = [c for r in results for c in r.passed if "reason" in c or "why" in c]
    if explanation_checks:
        rate = len(explanation_passed) / len(explanation_checks) * 100
        print(f"  Explanation quality:  {rate:.0f}% ({len(explanation_passed)}/{len(explanation_checks)})")

    # Average latency by step
    if step_latencies:
        print(f"\n  Avg latency by step:")
        for step in ["ingress", "intent", "router", "retrieve", "rerank", "rank", "summarize"]:
            if step in step_latencies:
                vals = step_latencies[step]
                avg = sum(vals) / len(vals)
                print(f"    {step:<12} {avg:6.1f}ms  (n={len(vals)})")

    total_latencies = [r.total_ms for r in results]
    if total_latencies:
        avg_total = sum(total_latencies) / len(total_latencies)
        p95 = sorted(total_latencies)[int(len(total_latencies) * 0.95)]
        print(f"    {'total':<12} {avg_total:6.1f}ms avg, {p95:.1f}ms p95")

    print(f"\n{'='*70}\n")

    return failed_queries == 0


if __name__ == "__main__":
    success = asyncio.run(run_eval_suite())
    sys.exit(0 if success else 1)
