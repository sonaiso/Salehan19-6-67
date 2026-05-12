from __future__ import annotations

import json
from pathlib import Path

from mcd.core.public_judgment import PUBLIC_FINAL_JUDGMENTS, collapse_to_public_judgment
from mcd.governance.adversarial_validation import AdversarialAttempt, evaluate_adversarial_attempt


EXPECTED_OBLIGATION_IDS = {
    "NoIllicitCertification",
    "ResidualPersistence",
    "ForbiddenEscalation",
    "TriadClosure",
    "ReplayIntegrity",
    "RankSoundness",
    "InsufficientRankBlocksCertificate",
    "RankGapBlocksCertificate",
    "MissingEvidenceBlocksCertificate",
    "ResidualErasureBlocksCertificate",
    "TypedResidualCalculus",
}


def test_formal_theorem_obligations_contain_required_obligations():
    payload = json.loads(Path("research/formal/theorem_obligations.json").read_text(encoding="utf-8"))
    assert payload["status"] in {
        "scaffold",
        "scaffold_plus_rank_residual_extension",
    }
    assert payload["phase_scope"] == "phase_0_governance_formal_artifacts_only"
    assert payload["runtime_behavior_changes"] is False

    obligation_ids = {item["id"] for item in payload["obligations"]}
    assert EXPECTED_OBLIGATION_IDS.issubset(obligation_ids)


def test_proof_mapping_links_runtime_contracts_and_evidence_gates():
    payload = json.loads(Path("research/formal/proof_mapping.json").read_text(encoding="utf-8"))
    assert payload["status"] in {
        "scaffold",
        "scaffold_plus_minimal_machine_checkable_core",
        "scaffold_plus_rank_residual_machine_checkable_extension",
    }
    mapping = {item["obligation"]: item for item in payload["mapping"]}

    for obligation in EXPECTED_OBLIGATION_IDS:
        assert obligation in mapping
        assert mapping[obligation]["runtime_contracts"]
        assert mapping[obligation]["evidence_gates"]
        assert mapping[obligation]["python_file"]
        assert mapping[obligation]["test_file"]
        assert mapping[obligation]["lean_file"]
        assert mapping[obligation]["claim_boundary"]
        assert "full" not in mapping[obligation]["claim_boundary"].lower()

    assert set(mapping["NoIllicitCertification"]["evidence_gates"]) == {
        "ProofObject",
        "GovernanceGate",
        "ReverseTrace",
    }
    assert set(mapping["NoIllicitCertification"]["theorem_contracts"]) == {
        "no_illicit_certification",
        "missing_gate_blocks_certificate",
        "forbidden_transition_blocks_certificate",
        "residual_erasure_blocks_certificate",
        "complete_gates_enable_certificate",
    }


def test_lean_core_files_exist_and_are_non_placeholder():
    lean_files = [
        Path("research/formal/lean/CoreJudgment.lean"),
        Path("research/formal/lean/NoIllicitCertification.lean"),
        Path("research/formal/lean/TriadClosure.lean"),
        Path("research/formal/lean/RankSoundness.lean"),
        Path("research/formal/lean/TypedResiduals.lean"),
        Path("research/formal/lean/ResidualCalculus.lean"),
    ]
    for path in lean_files:
        assert path.exists()
        text = path.read_text(encoding="utf-8")
        assert "theorem" in text or "inductive" in text
        assert "sorry" not in text


def test_lean_and_coq_readme_boundary_claims_are_accurate():
    lean = Path("research/formal/lean/README.md").read_text(encoding="utf-8").lower()
    coq = Path("research/formal/coq/README.md").read_text(encoding="utf-8").lower()
    assert "minimal machine-checkable core proof model" in lean
    assert "not full-project proof completion" in lean
    assert "does not claim proof of consciousness" in lean
    assert "skeleton-only" in coq
    assert "not machine-checked proof completion yet" in coq


def test_roadmap_declares_downstream_dependency_chain():
    roadmap = Path("research/theorem_roadmap.md").read_text(encoding="utf-8")
    assert "Formal Theorem Verification Track" in roadmap
    assert "Minimal Machine-Checkable Core" in roadmap
    assert "Rank Soundness" in roadmap
    assert "Replay integrity formalization" in roadmap
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
