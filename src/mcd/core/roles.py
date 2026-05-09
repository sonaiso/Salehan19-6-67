"""Role enums and role vector."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RoleType(str, Enum):
    ROOT_RADICAL = "root_radical"
    PREFIX = "prefix"
    SUFFIX = "suffix"
    PATTERN_MARKER = "pattern_marker"
    CASE_MARKER = "case_marker"
    DEFINITE_ARTICLE = "definite_article"
    DIACRITIC_MARKER = "diacritic_marker"
    WEAK_RADICAL = "weak_radical"
    FUNCTIONAL_PARTICLE = "functional_particle"
    UNKNOWN = "unknown"


@dataclass
class RoleVector:
    probabilities: dict[str, float] = field(default_factory=dict)

    def top_role(self) -> str:
        if not self.probabilities:
            return RoleType.UNKNOWN.value
        return max(self.probabilities, key=lambda k: self.probabilities[k])

    def to_dict(self) -> dict:
        return dict(self.probabilities)
