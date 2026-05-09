"""Health endpoint."""
from __future__ import annotations

from fastapi import APIRouter
from mcd.api.version import SERVICE_NAME

router = APIRouter()


@router.get("/health", tags=["health"])
def health() -> dict:
    """Liveness check — always returns ok."""
    return {"status": "ok", "service": SERVICE_NAME}
