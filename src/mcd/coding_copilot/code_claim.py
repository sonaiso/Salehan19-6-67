"""Claim model for patch intent and expected effects."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ClaimType = Literal[
    "fixes_bug",
    "implements_feature",
    "preserves_behavior",
    "improves_contract",
    "restores_cli_surface",
    "aligns_governance",
]


@dataclass
class CodeClaim:
    claim_id: str
    claim_type: ClaimType
    affected_files: list[str]
    expected_effect: str
    risk_level: str = "medium"
    required_evidence: list[str] = field(default_factory=list)

    def has_required_evidence(self, available_evidence: set[str]) -> bool:
        return all(item in available_evidence for item in self.required_evidence)

    def to_dict(self) -> dict:
        return {
            "claim_id": self.claim_id,
            "claim_type": self.claim_type,
            "affected_files": self.affected_files,
            "expected_effect": self.expected_effect,
            "risk_level": self.risk_level,
            "required_evidence": self.required_evidence,
        }
