"""Soundness checks for Formal Epistemic Transition Core."""
from __future__ import annotations

import pytest

from mcd.core.epistemic_rank import EpistemicRank, is_rank_sufficient, required_rank_for_judgment
from mcd.core.forbidden_transitions import ForbiddenTransition, validate_transition
from mcd.core.legitimacy_state import LegitimacyState
from mcd.core.proof_object import CertificateRequirementError, ProofObject, require_certificate_ready


def test_no_certificate_without_proof() -> None:
    legitimacy = LegitimacyState(
        context_valid=True,
        evidence_valid=True,
        rank_valid=True,
        contradiction_free=True,
        governance_passed=True,
    )
    proof = ProofObject(
        evidence_chain=[],
        transition_chain=["Reality->Linking"],
        governance_log=["gate_passed"],
        contradiction_checks=[True],
        confidence=0.9,
        rank=EpistemicRank.CERTIFICATE.name,
    )

    with pytest.raises(CertificateRequirementError):
        require_certificate_ready(proof, legitimacy)


def test_forbidden_transition() -> None:
    with pytest.raises(ForbiddenTransition):
        validate_transition("ZERO", "CERTIFICATE")

    validate_transition("HYPOTHESIS", "HYPOTHESIS")


def test_rank_enforcement() -> None:
    required = required_rank_for_judgment("CERTIFICATE")
    assert not is_rank_sufficient(EpistemicRank.WEAK_EVIDENCE, required)
    assert is_rank_sufficient(EpistemicRank.STRONG_EVIDENCE, EpistemicRank.HYPOTHESIS)
