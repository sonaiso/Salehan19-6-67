"""Canonical public final-judgment contract utilities."""
from __future__ import annotations

PUBLIC_FINAL_JUDGMENTS: tuple[str, ...] = ("zero", "hypothesis", "certificate")
INTERNAL_SUSPEND = "suspend"


def collapse_to_public_judgment(status: str) -> str:
    """Collapse internal/intermediate status to public triad."""
    normalized = (status or "").strip().lower()
    if normalized in PUBLIC_FINAL_JUDGMENTS:
        return normalized
    if normalized == INTERNAL_SUSPEND:
        return "hypothesis"
    return "zero"


def is_public_final_judgment(status: str) -> bool:
    """Return True iff status is one of the canonical public judgments."""
    return (status or "").strip().lower() in PUBLIC_FINAL_JUDGMENTS

