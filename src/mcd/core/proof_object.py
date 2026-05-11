"""Proof object contract for certificate eligibility."""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.core.epistemic_rank import EpistemicRank, is_rank_sufficient
from mcd.core.legitimacy_state import LegitimacyState


class CertificateRequirementError(ValueError):
    """Raised when certificate issuance requirements are not met."""


@dataclass
class ProofObject:
    evidence_chain: list[str] = field(default_factory=list)
    transition_chain: list[str] = field(default_factory=list)
    governance_log: list[str] = field(default_factory=list)
    contradiction_checks: list[bool] = field(default_factory=list)
    confidence: float = 0.0
    rank: str = EpistemicRank.HYPOTHESIS.name

    def has_valid_chains(self) -> bool:
        return bool(self.evidence_chain and self.transition_chain and self.governance_log)

    def contradiction_free(self) -> bool:
        return bool(self.contradiction_checks) and all(self.contradiction_checks)

    def rank_allows_certificate(self) -> bool:
        return is_rank_sufficient(self.rank, EpistemicRank.CERTIFICATE)

    def confidence_valid(self) -> bool:
        return 0.0 <= self.confidence <= 1.0

    def certificate_ready(self, legitimacy: LegitimacyState | None = None) -> bool:
        legitimacy_ok = legitimacy.legitimate if legitimacy is not None else True
        return (
            self.has_valid_chains()
            and self.contradiction_free()
            and self.rank_allows_certificate()
            and self.confidence_valid()
            and legitimacy_ok
        )


def require_certificate_ready(proof: ProofObject, legitimacy: LegitimacyState | None = None) -> None:
    if not proof.certificate_ready(legitimacy):
        raise CertificateRequirementError("certificate requirements are not satisfied")
