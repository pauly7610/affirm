"""Tests for the agentic search pipeline."""

import pytest
from app.pipeline.ingress import ingress_node
from app.pipeline.intent import intent_node
from app.pipeline.rank import rank_node
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
