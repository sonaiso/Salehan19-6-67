"""FastAPI application factory for the MCD REST API.

Phase 6 — Minimal REST API.
No LLM calls. No external network calls. No GraphRAG.
Not production-ready. Pilot-ready candidate only.
"""
from __future__ import annotations

import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from mcd.api.health import router as health_router
from mcd.api.middleware import RequestTracingMiddleware
from mcd.api.routes import router as main_router
from mcd.api.version import API_VERSION, PHASE, SERVICE_NAME


def build_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title="MCD REST API",
        description=(
            f"{PHASE}\n\n"
            "Minimal Cognitive Decoder — Arabic epistemic reasoning via REST API.\n\n"
            "**Limitations:**\n"
            "- No authentication (TODO before production)\n"
            "- No rate limiting (TODO before production)\n"
            "- No external source calls\n"
            "- No LLM calls\n"
            "- No GraphRAG\n"
            "- Not production-ready; pilot-ready candidate only\n"
        ),
        version=API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # -----------------------------------------------------------------------
    # Middleware
    # -----------------------------------------------------------------------
    app.add_middleware(RequestTracingMiddleware)

    # -----------------------------------------------------------------------
    # Exception handlers — never return stack traces
    # -----------------------------------------------------------------------

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        detail = exc.detail
        if isinstance(detail, dict):
            error_code = detail.get("error_code", "HTTP_ERROR")
            message = detail.get("message", str(detail))
            details = detail.get("details", {})
        else:
            error_code = f"HTTP_{exc.status_code}"
            message = str(detail)
            details = {}
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "request_id": request_id,
                "error_code": error_code,
                "message": message,
                "details": details,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        return JSONResponse(
            status_code=422,
            content={
                "request_id": request_id,
                "error_code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"errors": exc.errors()},
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        return JSONResponse(
            status_code=500,
            content={
                "request_id": request_id,
                "error_code": "INTERNAL_ERROR",
                "message": "An unexpected internal error occurred",
                "details": {},
            },
        )

    # -----------------------------------------------------------------------
    # Routers
    # -----------------------------------------------------------------------
    app.include_router(health_router)
    app.include_router(main_router)

    return app
