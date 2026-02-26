"""Ingress node: sanitize, normalize, and guard against disallowed intents."""

from __future__ import annotations

import re
import logging
import time

from app.pipeline.state import SearchState

logger = logging.getLogger(__name__)

DISALLOWED_PATTERNS = [
    r"hack\s+credit",
    r"steal\s+identity",
    r"fraud",
    r"launder",
    r"exploit\s+",
    r"bypass\s+approval",
]

PII_PATTERNS = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN_REDACTED]"),        # SSN
    (r"\b\d{16}\b", "[CARD_REDACTED]"),                     # Card number
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL_REDACTED]"),
    (r"\b\d{3}[-.]\d{3}[-.]\d{4}\b", "[PHONE_REDACTED]"),
]


def ingress_node(state: SearchState) -> dict:
    """Sanitize query, strip PII, reject disallowed intents."""
    t0 = time.perf_counter()
    request_id = state.get("request_id", "unknown")
    query = state.get("query", "").strip()

    logger.info("ingress.start", extra={"request_id": request_id, "raw_query": query[:100]})

    # Strip PII
    cleaned = query
    for pattern, replacement in PII_PATTERNS:
        cleaned = re.sub(pattern, replacement, cleaned)

    # Normalize
    cleaned = cleaned.lower().strip()
    cleaned = re.sub(r"\s+", " ", cleaned)

    # Guardrail: disallowed intents
    for pattern in DISALLOWED_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            logger.warning("ingress.blocked", extra={"request_id": request_id, "pattern": pattern})
            return {"sanitized_query": cleaned, "error": "This query isn't supported. Try searching for a product or category."}

    if len(cleaned) < 2:
        return {"sanitized_query": cleaned, "error": "Please enter a longer search query."}

    logger.info("ingress.done", extra={"request_id": request_id, "sanitized": cleaned[:100]})
    elapsed = round((time.perf_counter() - t0) * 1000, 1)
    trace = list(state.get("debug_trace", []))
    trace.append({"step": "ingress", "ms": elapsed, "notes": f"sanitized, pii-stripped, len={len(cleaned)}"})
    return {"sanitized_query": cleaned, "error": None, "debug_trace": trace}
