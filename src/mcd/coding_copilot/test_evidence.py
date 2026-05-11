"""Executable test evidence for coding judgment."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TestEvidence:
    test_command: str
    passed: bool
    failures: list[str] = field(default_factory=list)
    coverage_notes: str = ""
    evidence_strength: float = 0.0

    @property
    def evidence_id(self) -> str:
        return f"test::{self.test_command}"

    def to_dict(self) -> dict:
        return {
            "test_command": self.test_command,
            "passed": self.passed,
            "failures": self.failures,
            "coverage_notes": self.coverage_notes,
            "evidence_strength": self.evidence_strength,
            "evidence_id": self.evidence_id,
        }
