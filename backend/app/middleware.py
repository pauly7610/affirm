"""Middleware: request ID injection, structured logging, PII stripping."""

from __future__ import annotations

import uuid
import logging
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Inject X-Request-Id header and log request lifecycle."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-Id", str(uuid.uuid4())[:8])
        start = time.perf_counter()

        logger.info("request.start", extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
        })

        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        response.headers["X-Request-Id"] = request_id
        logger.info("request.done", extra={
            "request_id": request_id,
            "status": response.status_code,
            "elapsed_ms": f"{elapsed_ms:.1f}",
        })

        return response


# TODO: Rate limiting — naive per-IP in-memory counter
# For production, use Redis-backed sliding window or a middleware like slowapi.
# class RateLimitMiddleware(BaseHTTPMiddleware):
#     ...
