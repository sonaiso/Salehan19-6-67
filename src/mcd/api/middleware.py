"""Request-ID and timing middleware for MCD API.

Adds to every response:
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


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """Attach request_id and execution_time_ms to every response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        start = time.monotonic()

        response: Response = await call_next(request)

        elapsed_ms = (time.monotonic() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Execution-Time-Ms"] = f"{elapsed_ms:.3f}"
        return response
