"""EvidenceGate: evaluate evidence quality before accepting claims."""
from __future__ import annotations

from dataclasses import dataclass
from mcd.core.evidence import Evidence
from mcd.knowledge.facts import Fact


@dataclass
class GateResult:
    accepted: bool
    evidence_strength: float
    reason: str


class EvidenceGate:
    ACCEPTANCE_THRESHOLD = 0.30

    def evaluate(
        self,
        claim: str,
        evidence: list[Evidence],
        prior_facts: list[Fact] | None = None,
    ) -> GateResult:
        if not evidence:
            return GateResult(
                accepted=False,
                evidence_strength=0.0,
                reason="No evidence provided — claim rejected by gate",
            )

        strength = self._compute_strength(evidence)

        # Boost if corroborated by prior facts
        if prior_facts:
            for fact in prior_facts:
                if claim.lower() in fact.claim.lower() or fact.claim.lower() in claim.lower():
                    strength = min(1.0, strength + 0.10)
                    break

        accepted = strength >= self.ACCEPTANCE_THRESHOLD
        reason = (
            f"Evidence accepted (strength={strength:.2f})"
            if accepted
            else f"Evidence too weak (strength={strength:.2f}) — below threshold {self.ACCEPTANCE_THRESHOLD}"
        )
        return GateResult(accepted=accepted, evidence_strength=strength, reason=reason)

    def _compute_strength(self, evidence: list[Evidence]) -> float:
        if not evidence:
            return 0.0
        total = sum(e.strength * e.reliability for e in evidence)
        return total / len(evidence)
