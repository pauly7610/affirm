"""Tests for the agentic search pipeline."""

import pytest
from app.pipeline.ingress import ingress_node
from app.pipeline.intent import intent_node
from app.pipeline.retrieve import retrieve_node
from app.pipeline.rerank import rerank_node
from app.pipeline.rank import rank_node
from app.pipeline.summarize import summarize_node
from app.store import get_store


def test_ingress_sanitizes_query():
    state = {"query": "  Laptop Under $800  ", "request_id": "test"}
    result = ingress_node(state)
    assert result["sanitized_query"] == "laptop under $800"
    assert result["error"] is None


def test_ingress_strips_pii():
    state = {"query": "laptop for john@email.com SSN 123-45-6789", "request_id": "test"}
    result = ingress_node(state)
    assert "john@email.com" not in result["sanitized_query"]
    assert "123-45-6789" not in result["sanitized_query"]


def test_ingress_blocks_disallowed():
    state = {"query": "hack credit score", "request_id": "test"}
    result = ingress_node(state)
    assert result["error"] is not None


def test_intent_parses_price():
    state = {"sanitized_query": "laptop under $800", "request_id": "test"}
    result = intent_node(state)
    c = result["parsed_constraints"]
    assert c["max_price"] == 800
    assert c["category"] == "electronics"


def test_intent_parses_monthly():
    state = {"sanitized_query": "stay under $50/mo", "request_id": "test"}
    result = intent_node(state)
    c = result["parsed_constraints"]
    assert c["max_monthly"] == 50


def test_intent_parses_zero_apr():
    state = {"sanitized_query": "0% apr laptop", "request_id": "test"}
    result = intent_node(state)
    c = result["parsed_constraints"]
    assert c["only_zero_apr"] is True
    assert c["category"] == "electronics"


def test_intent_applies_refine_overrides():
    state = {
        "sanitized_query": "laptop",
        "request_id": "test",
        "refine_only_zero_apr": True,
        "refine_max_monthly": 60.0,
    }
    result = intent_node(state)
    c = result["parsed_constraints"]
    assert c["only_zero_apr"] is True
    assert c["max_monthly"] == 60.0


def test_store_vector_search():
    store = get_store()
    emb = store.get_embedding("laptop electronics")
    results = store.vector_search(emb, top_k=5)
    assert len(results) == 5
    assert all("_similarity" in r for r in results)


def test_store_filter():
    store = get_store()
    filtered = store.filter_offers(category="electronics", only_zero_apr=True)
    assert all(o["category"] == "electronics" for o in filtered)
    assert all(o["apr"] == 0 for o in filtered)


def test_rank_produces_ordered_results():
    mock_reranked = [
        {"id": "a", "monthlyPayment": 100, "totalPrice": 1000, "apr": 10, "termMonths": 12, "eligibilityConfidence": "med", "productName": "A", "_rerank_score": 0.5},
        {"id": "b", "monthlyPayment": 40, "totalPrice": 400, "apr": 0, "termMonths": 12, "eligibilityConfidence": "high", "productName": "B", "_rerank_score": 0.8},
        {"id": "c", "monthlyPayment": 200, "totalPrice": 2000, "apr": 15, "termMonths": 24, "eligibilityConfidence": "low", "productName": "C", "_rerank_score": 0.3},
    ]
    state = {"reranked": mock_reranked, "parsed_constraints": {}, "request_id": "test"}
    result = rank_node(state)
    ranked = result["ranked"]
    assert len(ranked) == 3
    # B should rank highest (lowest payment, 0% APR, high confidence, high rerank)
    assert ranked[0]["id"] == "b"


# ── Pipeline stage: retrieve ──

def test_retrieve_returns_candidates():
    store = get_store()
    state = {
        "sanitized_query": "laptop",
        "parsed_constraints": {"category": "electronics"},
        "request_id": "test",
        "debug_trace": [],
    }
    result = retrieve_node(state)
    assert "candidates" in result
    assert len(result["candidates"]) >= 1
    assert all("id" in c for c in result["candidates"])


def test_retrieve_respects_price_filter():
    state = {
        "sanitized_query": "laptop",
        "parsed_constraints": {"max_price": 500, "category": None},
        "request_id": "test",
        "debug_trace": [],
    }
    result = retrieve_node(state)
    # With relaxation, we may get some above threshold; but first few should respect it
    strict = [c for c in result["candidates"] if c["totalPrice"] <= 500]
    assert len(strict) >= 1


# ── Pipeline stage: rerank ──

def test_rerank_scores_candidates():
    candidates = [
        {"id": "x", "merchantName": "Apple", "productName": "MacBook", "category": "electronics",
         "totalPrice": 1200, "apr": 0, "termMonths": 12, "monthlyPayment": 100,
         "eligibilityConfidence": "high", "_similarity": 0.9},
        {"id": "y", "merchantName": "Sony", "productName": "TV OLED", "category": "electronics",
         "totalPrice": 800, "apr": 5, "termMonths": 6, "monthlyPayment": 140,
         "eligibilityConfidence": "med", "_similarity": 0.4},
    ]
    state = {
        "sanitized_query": "macbook laptop",
        "candidates": candidates,
        "parsed_constraints": {"category": "electronics", "raw_keywords": ["macbook"]},
        "request_id": "test",
        "debug_trace": [],
    }
    result = rerank_node(state)
    assert len(result["reranked"]) == 2
    assert all("_rerank_score" in c for c in result["reranked"])
    # MacBook should score higher (keyword match + category match)
    assert result["reranked"][0]["id"] == "x"


def test_rerank_category_preference_boost():
    """Verify category preference boost differentiates two otherwise-similar items."""
    candidates = [
        {"id": "a", "merchantName": "Store", "productName": "Widget", "category": "travel",
         "totalPrice": 500, "apr": 0, "termMonths": 6, "monthlyPayment": 83,
         "eligibilityConfidence": "high", "_similarity": 0.5},
        {"id": "b", "merchantName": "Store", "productName": "Widget", "category": "electronics",
         "totalPrice": 500, "apr": 0, "termMonths": 6, "monthlyPayment": 83,
         "eligibilityConfidence": "high", "_similarity": 0.5},
    ]
    state = {
        "sanitized_query": "widget",
        "candidates": candidates,
        "parsed_constraints": {"category": "electronics", "raw_keywords": []},
        "request_id": "test",
        "debug_trace": [],
    }
    result = rerank_node(state)
    # Electronics item should rank higher due to category boost
    assert result["reranked"][0]["id"] == "b"


# ── Pipeline stage: summarize ──

def test_summarize_produces_outputs():
    ranked = [
        {"id": "a", "merchantName": "Apple", "productName": "MacBook Air",
         "monthlyPayment": 66, "totalPrice": 800, "apr": 0, "termMonths": 12,
         "eligibilityConfidence": "high", "_rank_score": 0.9},
    ]
    state = {
        "ranked": ranked,
        "parsed_constraints": {"max_price": 800, "only_zero_apr": True, "category": "electronics"},
        "request_id": "test",
        "debug_trace": [],
    }
    result = summarize_node(state)
    assert "ai_summary" in result
    assert len(result["ai_summary"]) > 10
    assert result["ranked"][0]["reason"] != ""
    assert "monthly_impact" in result
    assert "refine_chips" in result


def test_summarize_why_this_recommendation():
    ranked = [
        {"id": "a", "merchantName": "Apple", "productName": "MacBook Air",
         "monthlyPayment": 66, "totalPrice": 800, "apr": 0, "termMonths": 12,
         "eligibilityConfidence": "high", "_rank_score": 0.9},
    ]
    state = {
        "ranked": ranked,
        "parsed_constraints": {"max_price": 800, "only_zero_apr": True},
        "request_id": "test",
        "debug_trace": [],
    }
    result = summarize_node(state)
    why = result["why_this_recommendation"]
    assert "MacBook Air" in why
    assert "0% APR" in why
    assert "under $800" in why


# ── Trace fields ──

def test_ingress_emits_trace():
    state = {"query": "laptop", "request_id": "test", "debug_trace": []}
    result = ingress_node(state)
    assert "debug_trace" in result
    assert len(result["debug_trace"]) == 1
    assert result["debug_trace"][0]["step"] == "ingress"
    assert isinstance(result["debug_trace"][0]["ms"], float)


def test_intent_emits_applied_constraints():
    state = {"sanitized_query": "laptop under $800 0% apr", "request_id": "test", "debug_trace": []}
    result = intent_node(state)
    ac = result["applied_constraints"]
    assert "budget" in ac
    assert "zeroApr" in ac
    assert ac["zeroApr"] is True


# ── BM25 store tests ──

def test_bm25_search_returns_results():
    store = get_store()
    results = store.bm25_search("macbook laptop", top_k=5)
    assert len(results) >= 1
    assert all("_bm25_score" in r for r in results)


def test_bm25_search_prefers_exact_match():
    store = get_store()
    results = store.bm25_search("peloton", top_k=5)
    assert results[0]["merchantName"] == "Peloton"


# ── Guardrails: fintech trust language ──

BANNED_CERTAINTY_PHRASES = [
    "you will be approved",
    "guaranteed approval",
    "you are approved",
    "based on your personal spending history",
    "we guarantee",
]


def test_why_recommendation_no_certainty_language():
    """Ensure why_this_recommendation never claims approval certainty."""
    ranked = [
        {"id": "a", "merchantName": "Apple", "productName": "MacBook Air",
         "monthlyPayment": 66, "totalPrice": 800, "apr": 0, "termMonths": 12,
         "eligibilityConfidence": "high", "_rank_score": 0.9},
    ]
    state = {
        "ranked": ranked,
        "parsed_constraints": {"max_price": 800, "only_zero_apr": True, "category": "electronics"},
        "request_id": "test",
        "debug_trace": [],
    }
    result = summarize_node(state)
    why = result["why_this_recommendation"].lower()
    for phrase in BANNED_CERTAINTY_PHRASES:
        assert phrase not in why, f"Banned phrase '{phrase}' found in why_this_recommendation"


def test_item_reasons_no_certainty_language():
    """Ensure per-item reasons never claim approval certainty."""
    ranked = [
        {"id": "a", "merchantName": "Apple", "productName": "MacBook Air",
         "monthlyPayment": 66, "totalPrice": 800, "apr": 0, "termMonths": 12,
         "eligibilityConfidence": "high", "_rank_score": 0.9},
        {"id": "b", "merchantName": "Dell", "productName": "XPS 14",
         "monthlyPayment": 75, "totalPrice": 899, "apr": 0, "termMonths": 12,
         "eligibilityConfidence": "med", "_rank_score": 0.7},
    ]
    state = {
        "ranked": ranked,
        "parsed_constraints": {"max_price": 1000},
        "request_id": "test",
        "debug_trace": [],
    }
    result = summarize_node(state)
    for item in result["ranked"]:
        reason = item["reason"].lower()
        for phrase in BANNED_CERTAINTY_PHRASES:
            assert phrase not in reason, f"Banned phrase '{phrase}' found in reason for {item['id']}"


def test_ingress_blocks_fraud_intents():
    """Verify multiple disallowed patterns are caught."""
    for query in ["hack credit score", "steal identity info", "launder money", "bypass approval check"]:
        result = ingress_node({"query": query, "request_id": "test"})
        assert result["error"] is not None, f"Should have blocked: {query}"


# ── Circuit breaker tests ──

def test_retrieve_circuit_breaker_vector_fail(monkeypatch):
    """If vector search raises, retrieve falls back to BM25-only."""
    store = get_store()
    monkeypatch.setattr(store, "get_embedding", lambda q: (_ for _ in ()).throw(RuntimeError("embed fail")))
    state = {
        "sanitized_query": "laptop",
        "parsed_constraints": {"category": "electronics"},
        "request_id": "test",
        "debug_trace": [],
    }
    result = retrieve_node(state)
    assert len(result["candidates"]) >= 1
    # Trace should show bm25-only path
    trace_notes = result["debug_trace"][-1]["notes"]
    assert "bm25-only" in trace_notes


def test_retrieve_circuit_breaker_both_fail(monkeypatch):
    """If both vector and BM25 fail, retrieve falls back to unfiltered store offers."""
    store = get_store()
    monkeypatch.setattr(store, "get_embedding", lambda q: (_ for _ in ()).throw(RuntimeError("embed fail")))
    monkeypatch.setattr(store, "bm25_search", lambda q, top_k=20: (_ for _ in ()).throw(RuntimeError("bm25 fail")))
    state = {
        "sanitized_query": "laptop",
        "parsed_constraints": {},
        "request_id": "test",
        "debug_trace": [],
    }
    result = retrieve_node(state)
    # Should still return results from raw store offers
    assert len(result["candidates"]) >= 1
    trace_notes = result["debug_trace"][-1]["notes"]
    assert "fallback-unfiltered" in trace_notes


def test_rank_penalizes_constraint_violators():
    """Items that violate user constraints should rank below strict matches."""
    reranked = [
        {"id": "a", "monthlyPayment": 50, "totalPrice": 500, "apr": 0, "termMonths": 12,
         "eligibilityConfidence": "high", "productName": "Cheap", "_rerank_score": 0.5},
        {"id": "b", "monthlyPayment": 100, "totalPrice": 1200, "apr": 0, "termMonths": 12,
         "eligibilityConfidence": "high", "productName": "Expensive", "_rerank_score": 0.9},
    ]
    state = {"reranked": reranked, "parsed_constraints": {"max_price": 800}, "request_id": "test"}
    result = rank_node(state)
    ranked = result["ranked"]
    # "Cheap" ($500) should rank above "Expensive" ($1200) despite lower rerank score
    assert ranked[0]["id"] == "a", "Constraint-violating item should rank lower"


# ── Integration test ──

@pytest.mark.asyncio
async def test_search_endpoint_shape_and_ordering():
    """Hit the full pipeline and verify response shape + ordering rules."""
    from app.pipeline.orchestrator import run_search

    result = await run_search(query="laptop under $800 with 0% APR")

    assert result.get("error") is None
    ranked = result.get("ranked", [])
    assert len(ranked) >= 1
    assert len(ranked) <= 5

    # Every item must have required fields
    required_keys = {"id", "merchantName", "productName", "totalPrice", "apr", "monthlyPayment", "reason"}
    for item in ranked:
        assert required_keys.issubset(item.keys()), f"Missing keys: {required_keys - item.keys()}"

    # Ordering: rank scores should be descending
    scores = [item.get("_rank_score", 0) for item in ranked]
    assert scores == sorted(scores, reverse=True), "Results not sorted by rank score"

    # Agentic fields
    assert result.get("ai_summary", "") != ""
    assert len(result.get("debug_trace", [])) >= 3
    assert result.get("why_this_recommendation", "") != ""
    assert isinstance(result.get("applied_constraints"), dict)

    # Guardrail: no certainty language in pipeline output
    why = result.get("why_this_recommendation", "").lower()
    for phrase in BANNED_CERTAINTY_PHRASES:
        assert phrase not in why, f"Banned phrase '{phrase}' in integration test output"
