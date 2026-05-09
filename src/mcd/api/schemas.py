"""Pydantic schemas for the MCD REST API.

All request/response models are JSON-serializable.
No Enum leakage — all enum values are converted to plain strings.
No dataclass leakage — all objects are returned as plain dicts inside APIResponse.

Phase 6.1 — unified response envelope:
  {
    "request_id": "...",
    "status": "success|error",
    "data": {...},
    "warnings": [],
    "errors": [],
    "execution_time_ms": 0.0
  }
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------


class ClassifyRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Arabic text to classify")
    include_debug: bool = Field(default=False, description="Include debug info in response")


class ReasoningEvaluateRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Arabic text to evaluate")
    include_debug: bool = Field(default=False, description="Include debug info in response")


class ProfileRequest(BaseModel):
    profile: str = Field(default="quick", description="Evaluation profile name")
    output_detail: str = Field(default="summary", description="Output detail level: summary|full")


# ---------------------------------------------------------------------------
# Unified Response Envelope (Phase 6.1)
# ---------------------------------------------------------------------------


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict = Field(default_factory=dict, description="Additional error context")


class APIResponse(BaseModel):
    """Unified response envelope for all POST endpoints.

    Phase 6.1: status is 'success' or 'error'.
    Backward-compatible: 'ok' is still accepted internally but normalised.
    """
    request_id: str = Field(..., description="Unique request identifier")
    status: str = Field(..., description="success | error")
    data: dict = Field(default_factory=dict, description="Response payload")
    warnings: list[str] = Field(default_factory=list, description="Non-fatal warnings")
    errors: list[Any] = Field(default_factory=list, description="Structured error list (empty on success)")
    execution_time_ms: float = Field(..., description="Request processing time in milliseconds")

    def model_post_init(self, __context: Any) -> None:  # type: ignore[override]
        # Normalise legacy 'ok' status → 'success'
        if self.status == "ok":
            object.__setattr__(self, "status", "success")


class ErrorResponse(BaseModel):
    """Legacy flat error response — returned by exception handlers."""
    request_id: str
    error_code: str
    message: str
    details: dict = Field(default_factory=dict)
