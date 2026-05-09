"""Dependency injection helpers for the MCD API.

Used with FastAPI's Depends() mechanism.
"""
from __future__ import annotations

import uuid
import time

# TODO: Add authentication dependency (e.g., API key or JWT) before production.
# TODO: Add rate-limiting dependency before production.


def new_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def current_timestamp_ms() -> float:
    """Return current epoch time in milliseconds."""
    return time.monotonic() * 1000
