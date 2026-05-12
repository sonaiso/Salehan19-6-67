from __future__ import annotations

import json
from pathlib import Path


def test_formal_scientific_validation_baseline_has_required_sections():
    path = Path("benchmarks/formal_scientific_validation_baseline.json")
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["suite_id"]
    assert payload["scope"] == "formal_scientific_validation_and_adversarial_governance"
    assert len(payload["strategic_order"]) == 7
    assert "adversarial_governance_validation" in payload["strategic_order"]
    assert "formal_theorem_system" in payload["strategic_order"]

    assert "fake_certification" in payload["attack_harness"]
    assert "residual_erasure" in payload["attack_harness"]
    assert "no_certificate_without_proof_object" in payload["required_invariants"]
    assert "final_judgment_in_public_triad" in payload["required_invariants"]


def test_formal_scientific_validation_order_starts_with_adversarial_validation():
    path = Path("benchmarks/formal_scientific_validation_baseline.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["strategic_order"][0] == "adversarial_governance_validation"
