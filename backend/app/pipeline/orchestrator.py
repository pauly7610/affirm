"""LangGraph orchestrator: wires pipeline nodes into a stateful graph."""

from __future__ import annotations

import logging
import uuid
from typing import Literal

from langgraph.graph import StateGraph, END

from app.pipeline.state import SearchState
from app.pipeline.ingress import ingress_node
from app.pipeline.intent import intent_node
from app.pipeline.retrieve import retrieve_node
from app.pipeline.rerank import rerank_node
from app.pipeline.rank import rank_node
from app.pipeline.summarize import summarize_node

logger = logging.getLogger(__name__)


def router_node(state: SearchState) -> dict:
    """Classify query complexity. Complex queries could trigger multi-step retrieval."""
    constraints = state.get("parsed_constraints", {})
    has_price = constraints.get("max_price") is not None
    has_monthly = constraints.get("max_monthly") is not None
    has_category = constraints.get("category") is not None
    has_apr = constraints.get("only_zero_apr", False)

    constraint_count = sum([has_price, has_monthly, has_category, has_apr])

    route = "complex" if constraint_count >= 2 else "simple"
    logger.info("router.decision", extra={
        "request_id": state.get("request_id", ""),
        "route": route,
        "constraint_count": constraint_count,
    })
    return {"route": route}


def should_continue(state: SearchState) -> Literal["retrieve", "__end__"]:
    """Check if ingress produced an error — if so, short-circuit."""
    if state.get("error"):
        return "__end__"
    return "retrieve"


def route_after_router(state: SearchState) -> Literal["retrieve"]:
    """Both simple and complex routes go to retrieve (complex could loop in production)."""
    return "retrieve"


def build_search_graph() -> StateGraph:
    """Construct the LangGraph search pipeline."""
    graph = StateGraph(SearchState)

    # Add nodes
    graph.add_node("ingress", ingress_node)
    graph.add_node("intent", intent_node)
    graph.add_node("router", router_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("rerank", rerank_node)
    graph.add_node("rank", rank_node)
    graph.add_node("summarize", summarize_node)

    # Wire edges
    graph.set_entry_point("ingress")
    graph.add_conditional_edges("ingress", should_continue, {
        "retrieve": "intent",
        "__end__": END,
    })
    graph.add_edge("intent", "router")
    graph.add_edge("router", "retrieve")
    graph.add_edge("retrieve", "rerank")
    graph.add_edge("rerank", "rank")
    graph.add_edge("rank", "summarize")
    graph.add_edge("summarize", END)

    return graph


# Compile once at module level
_compiled_graph = None


def get_search_graph():
    global _compiled_graph
    if _compiled_graph is None:
        graph = build_search_graph()
        _compiled_graph = graph.compile()
    return _compiled_graph


async def run_search(
    query: str,
    user_id: str = "demo-user",
    refine: dict | None = None,
) -> SearchState:
    """Execute the full agentic search pipeline."""
    request_id = str(uuid.uuid4())[:8]
    logger.info("pipeline.start", extra={"request_id": request_id, "query": query[:100]})

    initial_state: SearchState = {
        "query": query,
        "sanitized_query": "",
        "request_id": request_id,
        "user_id": user_id,
        "parsed_constraints": {},
        "route": "",
        "candidates": [],
        "reranked": [],
        "ranked": [],
        "ai_summary": "",
        "refine_chips": [],
        "monthly_impact": [],
        "disclaimers": [],
        "error": None,
    }

    # Apply refine overrides
    if refine:
        initial_state["refine_only_zero_apr"] = refine.get("onlyZeroApr")
        initial_state["refine_max_monthly"] = refine.get("maxMonthly")
        initial_state["refine_sort"] = refine.get("sort")
        initial_state["refine_category"] = refine.get("category")

    graph = get_search_graph()
    result = await graph.ainvoke(initial_state)

    logger.info("pipeline.done", extra={
        "request_id": request_id,
        "result_count": len(result.get("ranked", [])),
        "has_error": bool(result.get("error")),
    })

    return result
