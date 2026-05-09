"""Request-ID and timing middleware for MCD API.

Phase 6.1 updates:
- Records APILogTrace to in-memory TraceStore (no persistent storage).
- Adds to every response:
  - X-Request-ID header
  - X-Execution-Time-Ms header

TODO: Add authentication middleware before production.
TODO: Add rate-limiting middleware before production.
TODO: Add persistent structured logging middleware before production.
"""
from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from mcd.api.observability import APILogTrace, get_trace_store


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """Attach request_id and execution_time_ms to every response.

    Also records a trace in the in-memory TraceStore.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        start = time.monotonic()

        response: Response = await call_next(request)

        elapsed_ms = (time.monotonic() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Execution-Time-Ms"] = f"{elapsed_ms:.3f}"

        # Record trace (non-blocking, no I/O)
        trace = APILogTrace(
            request_id=request_id,
            path=request.url.path,
            method=request.method,
            status_code=response.status_code,
            execution_time_ms=round(elapsed_ms, 3),
        )
        get_trace_store().record(trace)

        return response
