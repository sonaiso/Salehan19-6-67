"""Final public judgments for AFJG coding copilot simulation."""
from __future__ import annotations

from enum import Enum


class CodingStatus(str, Enum):
    ZERO = "zero"
    HYPOTHESIS = "hypothesis"
    CERTIFICATE = "certificate"


PUBLIC_FINAL_CODING_JUDGMENTS: tuple[str, ...] = tuple(s.value for s in CodingStatus)
INTERNAL_SUSPEND = "suspend"


def collapse_to_public_status(status: str) -> str:
    """Collapse internal/intermediate statuses to the 3 public AFJG coding statuses."""
    normalized = (status or "").strip().lower()
    if normalized in PUBLIC_FINAL_CODING_JUDGMENTS:
        return normalized
    if normalized == INTERNAL_SUSPEND:
        return CodingStatus.HYPOTHESIS.value
    return CodingStatus.ZERO.value


def is_public_final_coding_judgment(status: str) -> bool:
    return (status or "").strip().lower() in PUBLIC_FINAL_CODING_JUDGMENTS
