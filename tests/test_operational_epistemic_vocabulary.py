import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "spec/worktree/operational_epistemic_vocabulary.json"
SCHEMA_PATH = ROOT / "spec/worktree/operational_epistemic_vocabulary.schema.json"


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def test_schema_validates_json_spec():
    schema = _load_json(SCHEMA_PATH)
    spec = _load_json(SPEC_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(spec, schema)


def test_chain_order_dependencies():
    spec = _load_json(SPEC_PATH)
    chain = spec["chain_order"]
    expected_chain = [
        "epistemic_zero",
        "attention",
        "distinction",
        "identity",
        "universal",
        "particular",
        "designation",
        "linking",
        "aspect",
        "temporal_scope",
        "judgment_rank",
        "domain",
        "contradiction_check",
        "interpretation",
        "conception",
        "judgment",
    ]

    assert chain == expected_chain


def test_contradiction_requires_domain_time_aspect_and_rank():
    spec = _load_json(SPEC_PATH)
    required_inputs = set(spec["nodes"]["contradiction_check"]["required_inputs"])

    assert "domain" in required_inputs
    assert "temporal_scope" in required_inputs
    assert "aspect" in required_inputs
    assert "judgment_rank" in required_inputs


def test_final_judgment_values_are_limited_to_three_states():
    spec = _load_json(SPEC_PATH)
    allowed = set(spec["final_judgments"])

    assert allowed == {"ZERO", "HYPOTHESIS", "CERTIFICATE"}


def test_every_node_defines_residuals_and_forbidden_transitions():
    spec = _load_json(SPEC_PATH)

    for node_name, node in spec["nodes"].items():
        assert node["residuals"], f"{node_name} must define residuals"
        assert node["forbidden_transitions"], f"{node_name} must define forbidden transitions"
