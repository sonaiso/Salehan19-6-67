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

import os
import time
import uuid
from collections import defaultdict, deque
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from mcd.api.observability import APILogTrace, get_trace_store
from mcd.observability import log_governance_event


_RATE_BUCKETS: dict[str, deque[float]] = defaultdict(deque)
_RATE_LOCK = Lock()
_RATE_WINDOW_SECONDS = 60.0
_DEFAULT_RATE_LIMIT = 120


def _api_profile() -> str:
    return os.environ.get("MCD_API_PROFILE", "local").strip().lower()


def _requires_auth(path: str) -> bool:
    return path.startswith("/v1/") and path not in {
        "/v1/health",
        "/v1/version",
        "/v1/pilot/readiness",
        "/v1/readiness",
        "/v1/production/livez",
        "/v1/production/readyz",
    }


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """Attach request_id and execution_time_ms to every response.

    Also records a trace in the in-memory TraceStore.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        replay_id = str(uuid.uuid4())
        start = time.monotonic()

        profile = _api_profile()
        token = request.headers.get("x-api-key", "")
        if profile in {"staging", "production"} and _requires_auth(request.url.path):
            expected = os.environ.get("MCD_API_KEY", "")
            if not expected or token != expected:
                return JSONResponse(
                    status_code=401,
                    content={
                        "request_id": request_id,
                        "error_code": "AUTHENTICATION_REQUIRED",
                        "message": "Missing or invalid API key",
                        "details": {"profile": profile},
                    },
                )

        if profile == "production" and _requires_auth(request.url.path):
            role = request.headers.get("x-role", "").strip().lower()
            if role not in {"operator", "auditor", "admin"}:
                return JSONResponse(
                    status_code=403,
                    content={
                        "request_id": request_id,
                        "error_code": "AUTHORIZATION_FAILED",
                        "message": "Role is not authorized for this endpoint",
                        "details": {"required_roles": ["operator", "auditor", "admin"]},
                    },
                )

        if _requires_auth(request.url.path):
            limit = int(os.environ.get("MCD_RATE_LIMIT_PER_MIN", str(_DEFAULT_RATE_LIMIT)))
            # Baseline fallback for unauthenticated callers.
            # For production behind proxies, use trusted proxy-aware identity plumbing.
            client_host = request.client.host if request.client else "unknown"
            key = request.headers.get("x-api-key", f"ip:{client_host}")
            now = time.monotonic()
            with _RATE_LOCK:
                bucket = _RATE_BUCKETS[key]
                while bucket and now - bucket[0] > _RATE_WINDOW_SECONDS:
                    bucket.popleft()
                if len(bucket) >= limit:
                    return JSONResponse(
                        status_code=429,
                        content={
                            "request_id": request_id,
                            "error_code": "RATE_LIMITED",
                            "message": "Rate limit exceeded",
                            "details": {"limit_per_min": limit},
                        },
                    )
                bucket.append(now)

        response: Response = await call_next(request)

        elapsed_ms = (time.monotonic() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Replay-ID"] = replay_id
        response.headers["X-Execution-Time-Ms"] = f"{elapsed_ms:.3f}"
        response.headers["X-Profile"] = profile

        # Record trace (non-blocking, no I/O)
        trace = APILogTrace(
            request_id=request_id,
            replay_id=replay_id,
            path=request.url.path,
            method=request.method,
            status_code=response.status_code,
            execution_time_ms=round(elapsed_ms, 3),
        )
        get_trace_store().record(trace)
        log_governance_event(trace.to_dict())

        return response
