"""Custom API error types for structured JSON error responses."""
from __future__ import annotations

from fastapi import HTTPException
from starlette import status


class InvalidInputError(HTTPException):
    """Raised when request body fails semantic validation."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(
            status_code=422,
            detail={"error_code": "INVALID_INPUT", "message": message, "details": details or {}},
        )


class UnsupportedProfileError(HTTPException):
    """Raised when an unknown profile name is passed."""

    def __init__(self, profile: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "UNSUPPORTED_PROFILE",
                "message": f"Unsupported profile: '{profile}'",
                "details": {"profile": profile},
            },
        )


class EngineExecutionError(HTTPException):
    """Raised when an internal engine fails unexpectedly."""

    def __init__(self, engine: str, reason: str) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "ENGINE_EXECUTION_ERROR",
                "message": f"Engine '{engine}' failed: {reason}",
                "details": {"engine": engine, "reason": reason},
            },
        )


class SchemaSerializationError(HTTPException):
    """Raised when response data cannot be serialized to JSON."""

    def __init__(self, reason: str) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "SCHEMA_SERIALIZATION_ERROR",
                "message": f"Serialization failed: {reason}",
                "details": {"reason": reason},
            },
        )
