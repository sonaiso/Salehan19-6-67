"""Pydantic schemas for the MCD REST API.

All request/response models are JSON-serializable.
No Enum leakage — all enum values are converted to plain strings.
No dataclass leakage — all objects are returned as plain dicts inside APIResponse.
"""
from __future__ import annotations

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
# Responses
# ---------------------------------------------------------------------------


class APIResponse(BaseModel):
    request_id: str = Field(..., description="Unique request identifier")
    status: str = Field(..., description="ok | error")
    data: dict = Field(default_factory=dict, description="Response payload")
    warnings: list[str] = Field(default_factory=list, description="Non-fatal warnings")
    errors: list[str] = Field(default_factory=list, description="Error messages")
    execution_time_ms: float = Field(..., description="Request processing time in milliseconds")


class ErrorResponse(BaseModel):
    request_id: str
    error_code: str
    message: str
    details: dict = Field(default_factory=dict)
