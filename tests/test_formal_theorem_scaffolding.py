from __future__ import annotations

import json
from pathlib import Path


def test_formal_theorem_scaffolding_contains_required_theorems():
    payload = json.loads(Path("research/formal/theorem_scaffolding.json").read_text(encoding="utf-8"))
    theorem_names = {item["name"] for item in payload["theorems"]}
    assert payload["status"] == "scaffold"
    assert {
        "no_illicit_certification",
        "monotonicity_boundaries",
        "residual_persistence",
    }.issubset(theorem_names)
