from __future__ import annotations

import json
from pathlib import Path

from mcd.core.public_judgment import PUBLIC_FINAL_JUDGMENTS, collapse_to_public_judgment
from mcd.governance.adversarial_validation import AdversarialAttempt, evaluate_adversarial_attempt


def test_formal_theorem_obligations_cover_pr73_targets():
    payload = json.loads(Path("research/formal/theorem_obligations.json").read_text(encoding="utf-8"))
    assert payload["status"] == "scaffold"
    assert payload["phase_scope"] == "phase_0_governance_formal_artifacts_only"
    assert payload["runtime_behavior_changes"] is False

    obligation_ids = {item["id"] for item in payload["obligations"]}
    assert obligation_ids == {
        "NoIllicitCertification",
        "ResidualPersistence",
        "ForbiddenEscalation",
        "TriadClosure",
        "ReplayIntegrity",
    }


def test_proof_mapping_links_runtime_contracts_and_evidence_gates():
    payload = json.loads(Path("research/formal/proof_mapping.json").read_text(encoding="utf-8"))
    assert payload["status"] == "scaffold"
    mapping = {item["obligation"]: item for item in payload["mapping"]}

    for obligation in (
        "NoIllicitCertification",
        "ResidualPersistence",
        "ForbiddenEscalation",
        "TriadClosure",
        "ReplayIntegrity",
    ):
        assert obligation in mapping
        assert mapping[obligation]["runtime_contracts"]
        assert mapping[obligation]["evidence_gates"]

    assert set(mapping["NoIllicitCertification"]["evidence_gates"]) == {
        "ProofObject",
        "GovernanceGate",
        "ReverseTrace",
    }


def test_lean_and_coq_skeletons_are_placeholder_only():
    lean = Path("research/formal/lean/README.md").read_text(encoding="utf-8").lower()
    coq = Path("research/formal/coq/README.md").read_text(encoding="utf-8").lower()
    for text in (lean, coq):
        assert "skeleton-only" in text
        assert "no runtime behavior change" in text
        assert "not machine-checked proof completion yet" in text


def test_roadmap_declares_post_pr73_dependency_chain():
    roadmap = Path("research/theorem_roadmap.md").read_text(encoding="utf-8")
    assert "PR #73" in roadmap
    assert "PR #74" in roadmap
    assert "PR #75" in roadmap
    assert "downstream" in roadmap


def test_public_final_judgment_policy_is_triad_closed():
    assert set(PUBLIC_FINAL_JUDGMENTS) == {"zero", "hypothesis", "certificate"}
    assert collapse_to_public_judgment("CERTIFICATE") == "certificate"
    assert collapse_to_public_judgment("unknown-status") == "zero"


def test_certificate_cannot_be_silent_without_required_gates():
    attempt = AdversarialAttempt(
        attempt_id="PR73-CERT-001",
        requested_judgment="CERTIFICATE",
        proof_object_ref="",
        governance_gate_passed=False,
        reverse_trace_ref="",
        evidence_matches_claim=False,
    )
    result = evaluate_adversarial_attempt(attempt)
    assert result.public_judgment == "hypothesis"
    assert "certificate_without_proof_object" in result.blocked_reasons
    assert "certificate_without_governance_gate" in result.blocked_reasons
    assert "certificate_without_reverse_trace" in result.blocked_reasons
