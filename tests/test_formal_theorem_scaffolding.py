from __future__ import annotations

import json
from pathlib import Path


def test_formal_theorem_scaffolding_contains_required_theorems():
    payload = json.loads(Path("research/formal/theorem_scaffolding.json").read_text(encoding="utf-8"))
    theorem_names = {item["name"] for item in payload["theorems"]}
    theorem_map = {item["name"]: item["statement"] for item in payload["theorems"]}

    assert payload["status"] == "scaffold"
    assert payload["phase_scope"] == "phase_0_governance_formal_artifacts_only"
    assert {
        "no_illicit_certification",
        "monotonicity_boundaries",
        "residual_persistence",
        "forbidden_escalation",
        "triad_closure",
        "replay_integrity",
    }.issubset(theorem_names)
    assert all(theorem_map[name].strip() for name in theorem_names)
    assert "ProofObject" in theorem_map["no_illicit_certification"]
    assert "GovernanceGate" in theorem_map["no_illicit_certification"]
    assert "ReverseTrace" in theorem_map["no_illicit_certification"]
