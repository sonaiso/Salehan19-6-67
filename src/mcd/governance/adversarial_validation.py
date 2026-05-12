"""Adversarial governance validation for certificate hardening."""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.core.public_judgment import PUBLIC_FINAL_JUDGMENTS, collapse_to_public_judgment

FORBIDDEN_TRANSITIONS: tuple[str, ...] = (
    "root_or_pattern_as_factual_proof",
    "derivative_as_proof",
    "irab_as_factual_certainty",
    "emphasis_as_evidence",
    "metaphor_as_literal_certificate",
    "memory_as_external_evidence",
    "model_output_as_evidence",
    "tool_output_as_certificate_without_governance",
    "residual_erasure",
    "silent_level_skip",
    "certificate_without_proof_object",
    "certificate_without_governance_gate",
    "certificate_without_reverse_trace",
)


@dataclass
class AdversarialAttempt:
    attempt_id: str
    requested_judgment: str
    proof_object_ref: str = ""
    governance_gate_passed: bool = False
    reverse_trace_ref: str = ""
    evidence_matches_claim: bool = False
    transition_tags: list[str] = field(default_factory=list)
    residuals: list[str] = field(default_factory=list)


@dataclass
class AdversarialEvaluation:
    attempt_id: str
    public_judgment: str
    blocked_reasons: list[str] = field(default_factory=list)
    residuals: list[str] = field(default_factory=list)

    @property
    def certificate_issued(self) -> bool:
        return self.public_judgment == "certificate"

    def to_dict(self) -> dict:
        return {
            "attempt_id": self.attempt_id,
            "public_judgment": self.public_judgment,
            "certificate_issued": self.certificate_issued,
            "blocked_reasons": list(self.blocked_reasons),
            "residuals": list(self.residuals),
        }


def _blocked_certificate_reasons(attempt: AdversarialAttempt) -> list[str]:
    reasons: list[str] = []
    forbidden = set(FORBIDDEN_TRANSITIONS)
    for tag in attempt.transition_tags:
        if tag in forbidden:
            reasons.append(tag)
    if not attempt.proof_object_ref:
        reasons.append("certificate_without_proof_object")
    if not attempt.governance_gate_passed:
        reasons.append("certificate_without_governance_gate")
    if not attempt.reverse_trace_ref:
        reasons.append("certificate_without_reverse_trace")
    if not attempt.evidence_matches_claim:
        reasons.append("evidence_mismatch")
    if attempt.residuals:
        reasons.append("blocking_residual_present")
    return reasons


def evaluate_adversarial_attempt(attempt: AdversarialAttempt) -> AdversarialEvaluation:
    requested = collapse_to_public_judgment(attempt.requested_judgment)
    blocked_reasons: list[str] = []
    if requested == "certificate":
        blocked_reasons = _blocked_certificate_reasons(attempt)
    elif any(tag in FORBIDDEN_TRANSITIONS for tag in attempt.transition_tags):
        blocked_reasons = [tag for tag in attempt.transition_tags if tag in FORBIDDEN_TRANSITIONS]

    if blocked_reasons and requested == "certificate":
        public_judgment = "hypothesis"
    elif requested in PUBLIC_FINAL_JUDGMENTS:
        public_judgment = requested
    else:
        public_judgment = "zero"

    residuals = list(attempt.residuals)
    if "residual_erasure" in blocked_reasons and not residuals:
        residuals.append("residual_missing_detected")

    return AdversarialEvaluation(
        attempt_id=attempt.attempt_id,
        public_judgment=public_judgment,
        blocked_reasons=blocked_reasons,
        residuals=residuals,
    )
