"""Static evidence for coding judgment (lint/type/security checks)."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StaticEvidence:
    tool_name: str
    passed: bool
    findings: list[str] = field(default_factory=list)
    evidence_strength: float = 0.0

    @property
    def evidence_id(self) -> str:
        return f"static::{self.tool_name}"

    def to_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "passed": self.passed,
            "findings": self.findings,
            "evidence_strength": self.evidence_strength,
            "evidence_id": self.evidence_id,
        }
