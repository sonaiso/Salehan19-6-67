from __future__ import annotations

import json
from pathlib import Path


def _mapping_by_obligation() -> dict[str, dict]:
    payload = json.loads(Path("research/formal/proof_mapping.json").read_text(encoding="utf-8"))
    return {item["obligation"]: item for item in payload["mapping"]}


def test_typed_residual_lean_file_contains_required_contracts():
    path = Path("research/formal/lean/TypedResiduals.lean")
    assert path.exists()
    text = path.read_text(encoding="utf-8")

    required_tokens = [
        "inductive Residual",
        "abbrev ResidualSet",
        "def resolvedByEvidence",
        "def residualPreserved",
    ]
    for token in required_tokens:
        assert token in text
    assert "Residual.unresolvedConflict" in text
    assert "Residual.residualErasure" in text
    assert "sorry" not in text


def test_residual_calculus_theorems_and_mapping_exist():
    path = Path("research/formal/lean/ResidualCalculus.lean")
    assert path.exists()
    text = path.read_text(encoding="utf-8")

    required_theorems = [
        "theorem residual_persistence",
        "theorem rank_gap_blocks_certificate",
        "theorem residual_erasure_blocks_certificate",
        "theorem missing_evidence_blocks_certificate",
        "theorem unresolved_conflict_blocks_certificate",
    ]
    for theorem_name in required_theorems:
        assert theorem_name in text
    assert "sorry" not in text

    mapping = _mapping_by_obligation()
    required_obligations = {
        "ResidualPersistence": "residual_persistence",
        "RankGapBlocksCertificate": "rank_gap_blocks_certificate",
        "MissingEvidenceBlocksCertificate": "missing_evidence_blocks_certificate",
        "ResidualErasureBlocksCertificate": "residual_erasure_blocks_certificate",
        "TypedResidualCalculus": "residual_persistence",
    }

    for obligation, theorem_name in required_obligations.items():
        assert obligation in mapping
        assert mapping[obligation]["runtime_invariant_name"]
        assert mapping[obligation]["lean_file"].endswith(".lean")
        theorem_contracts = mapping[obligation].get("theorem_contracts", [])
        assert theorem_name in theorem_contracts


def test_no_full_system_or_consciousness_claim_in_formal_track_artifacts():
    obligations_text = Path("research/formal/theorem_obligations.json").read_text(encoding="utf-8").lower()
    mapping_text = Path("research/formal/proof_mapping.json").read_text(encoding="utf-8").lower()

    assert "full-system proof" not in obligations_text
    assert "consciousness" not in obligations_text
    assert "full-system proof" not in mapping_text
    assert "consciousness" not in mapping_text
