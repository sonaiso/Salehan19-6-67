"""Architecture evidence for AFJG coding governance."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ArchitectureEvidence:
    checked_rules: list[str] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    passed: bool = True
    evidence_strength: float = 0.0

    @property
    def evidence_id(self) -> str:
        return "architecture::governance"

    def to_dict(self) -> dict:
        return {
            "checked_rules": self.checked_rules,
            "violations": self.violations,
            "passed": self.passed,
            "evidence_strength": self.evidence_strength,
            "evidence_id": self.evidence_id,
        }
