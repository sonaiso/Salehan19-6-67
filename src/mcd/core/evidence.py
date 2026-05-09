"""Evidence dataclass and types."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class EvidenceType(str, Enum):
    SENSORY = "sensory"
    TEXTUAL = "textual"
    EXPERIMENTAL = "experimental"
    LINGUISTIC = "linguistic"
    HISTORICAL = "historical"
    LOGICAL = "logical"
    CONTEXTUAL = "contextual"


@dataclass
class Evidence:
    source_id: str
    source_type: str
    description: str
    strength: float
    reliability: float
