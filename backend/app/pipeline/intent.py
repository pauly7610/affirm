"""Intent parser: extract structured constraints from natural language query."""

from __future__ import annotations

import re
import logging
import time

from app.pipeline.state import SearchState, ParsedConstraints

logger = logging.getLogger(__name__)

CATEGORY_KEYWORDS = {
    "electronics": ["electronics", "laptop", "phone", "tablet", "headphone", "tv", "computer", "kindle", "ipad", "macbook", "samsung", "sony", "dell", "asus", "oled"],
    "travel": ["trip", "travel", "vacation", "flight", "hotel", "beach", "ski", "resort", "cancun", "miami", "nyc", "costa rica", "denver"],
    "sneakers": ["sneaker", "shoe", "jordan", "nike", "adidas", "new balance", "air max", "ultraboost"],
    "home": ["sofa", "couch", "furniture", "mattress", "desk", "shelf", "table", "vacuum", "home upgrade"],
    "fitness": ["fitness", "gym", "peloton", "bike", "garmin", "watch", "workout"],
    "gaming": ["gaming", "ps5", "playstation", "xbox", "steam deck", "razer", "game"],
    "fashion": ["fashion", "parka", "coat", "jacket", "designer"],
    "appliances": ["fridge", "washer", "dryer", "appliance", "appliances", "coffee", "coffee machine", "breville"],
}


def intent_node(state: SearchState) -> dict:
    """Parse query into structured constraints."""
    t0 = time.perf_counter()
    request_id = state.get("request_id", "unknown")
    query = state.get("sanitized_query", "")
    logger.info("intent.start", extra={"request_id": request_id})

    constraints: ParsedConstraints = {
        "max_price": None,
        "max_monthly": None,
        "only_zero_apr": False,
        "category": None,
        "sort": None,
        "raw_keywords": [],
    }

    # Apply client-side refine overrides first
    if state.get("refine_only_zero_apr"):
        constraints["only_zero_apr"] = True
    if state.get("refine_max_monthly"):
        constraints["max_monthly"] = state["refine_max_monthly"]
    if state.get("refine_sort"):
        constraints["sort"] = state["refine_sort"]
    if state.get("refine_category"):
        constraints["category"] = state["refine_category"]

    # Parse "under $X" (total price)
    price_match = re.search(r"under\s*\$\s*([\d,]+)(?!\s*/)", query)
    if price_match:
        constraints["max_price"] = float(price_match.group(1).replace(",", ""))

    # Parse "under $X/mo" or "under $X per month" or "stay under $X/mo"
    monthly_match = re.search(r"under\s*\$\s*([\d,]+)\s*(?:/\s*mo|per\s*month|monthly)", query)
    if monthly_match:
        val = float(monthly_match.group(1).replace(",", ""))
        if constraints["max_monthly"] is None or val < constraints["max_monthly"]:
            constraints["max_monthly"] = val

    # Parse "0% APR" or "zero apr" or "no interest"
    if re.search(r"0\s*%\s*apr|zero\s*%?\s*apr|no\s*interest", query):
        constraints["only_zero_apr"] = True

    # Detect category from keywords
    if constraints["category"] is None:
        for cat, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in query:
                    constraints["category"] = cat
                    break
            if constraints["category"]:
                break

    # Extract remaining keywords (non-stopword tokens)
    stopwords = {"a", "an", "the", "with", "and", "or", "for", "my", "me", "i", "under", "only", "just", "want", "need", "looking", "find", "get", "buy", "plan", "try", "cheaper", "options"}
    tokens = re.findall(r"[a-z]+", query)
    constraints["raw_keywords"] = [t for t in tokens if t not in stopwords and len(t) > 2]

    logger.info("intent.done", extra={"request_id": request_id, "constraints": str(constraints)})

    # Build human-readable applied constraints
    applied: dict = {}
    if constraints.get("max_price") is not None:
        applied["budget"] = f"${constraints['max_price']:.0f}"
    if constraints.get("max_monthly") is not None:
        applied["maxMonthly"] = f"${constraints['max_monthly']:.0f}/mo"
    if constraints.get("only_zero_apr"):
        applied["zeroApr"] = True
    if constraints.get("category"):
        applied["category"] = constraints["category"]
    if constraints.get("sort"):
        applied["sort"] = constraints["sort"]

    elapsed = round((time.perf_counter() - t0) * 1000, 1)
    trace = list(state.get("debug_trace", []))
    notes = ", ".join(f"{k}={v}" for k, v in applied.items()) or "no constraints"
    trace.append({"step": "intent", "ms": elapsed, "notes": f"extracted: {notes}"})
    return {"parsed_constraints": constraints, "applied_constraints": applied, "debug_trace": trace}
