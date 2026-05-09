"""Source dataclass."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Source:
    source_id: str
    source_type: str
    name: str
    reliability: float
    language: str = "ar"
    description: str = ""
