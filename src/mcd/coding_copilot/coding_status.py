"""Final public judgments for AFJG coding copilot simulation."""
from __future__ import annotations

from enum import Enum

from mcd.core.public_judgment import collapse_to_public_judgment, is_public_final_judgment


class CodingStatus(str, Enum):
    ZERO = "zero"
    HYPOTHESIS = "hypothesis"
    CERTIFICATE = "certificate"


PUBLIC_FINAL_CODING_JUDGMENTS: tuple[str, ...] = tuple(s.value for s in CodingStatus)
INTERNAL_SUSPEND = "suspend"


def collapse_to_public_status(status: str) -> str:
    """Collapse internal/intermediate statuses to the 3 public AFJG coding statuses."""
    return collapse_to_public_judgment(status)


def is_public_final_coding_judgment(status: str) -> bool:
    return is_public_final_judgment(status)
