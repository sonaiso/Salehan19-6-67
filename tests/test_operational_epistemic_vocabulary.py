import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "spec" / "worktree" / "operational_epistemic_vocabulary.schema.json"
SPEC_PATH = ROOT / "spec" / "worktree" / "operational_epistemic_vocabulary.json"


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _nodes(spec: dict) -> dict:
    return {node["node_id"]: node for node in spec["nodes"]}


def _index(spec: dict, node_id: str) -> int:
    return spec["chain"].index(node_id)


def test_schema_validates_json() -> None:
    schema = _load_json(SCHEMA_PATH)
    spec = _load_json(SPEC_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(spec, schema)


def test_epistemic_zero_precedes_attention() -> None:
    spec = _load_json(SPEC_PATH)
    assert _index(spec, "epistemic_zero") < _index(spec, "attention")


def test_attention_precedes_distinction() -> None:
    spec = _load_json(SPEC_PATH)
    assert _index(spec, "attention") < _index(spec, "distinction")


def test_distinction_precedes_designation() -> None:
    spec = _load_json(SPEC_PATH)
    assert _index(spec, "distinction") < _index(spec, "designation")


def test_designation_precedes_domain() -> None:
    spec = _load_json(SPEC_PATH)
    assert _index(spec, "designation") < _index(spec, "domain")


def test_domain_required_before_contradiction() -> None:
    spec = _load_json(SPEC_PATH)
    node = _nodes(spec)["contradiction_check"]
    assert "domain_assignment" in node["required_inputs"]


def test_time_required_before_contradiction() -> None:
    spec = _load_json(SPEC_PATH)
    node = _nodes(spec)["contradiction_check"]
    assert "time_scope" in node["required_inputs"]


def test_aspect_required_before_contradiction() -> None:
    spec = _load_json(SPEC_PATH)
    node = _nodes(spec)["contradiction_check"]
    assert "aspect_scope" in node["required_inputs"]


def test_judgment_rank_required_before_contradiction() -> None:
    spec = _load_json(SPEC_PATH)
    node = _nodes(spec)["contradiction_check"]
    assert "rank_assignment" in node["required_inputs"]


def test_linking_comes_before_interpretation() -> None:
    spec = _load_json(SPEC_PATH)
    assert _index(spec, "linking") < _index(spec, "interpretation")


def test_interpretation_comes_before_conception() -> None:
    spec = _load_json(SPEC_PATH)
    assert _index(spec, "interpretation") < _index(spec, "conception")


def test_conception_comes_before_judgment() -> None:
    spec = _load_json(SPEC_PATH)
    assert _index(spec, "conception") < _index(spec, "judgment")


def test_no_final_judgment_outside_zero_hypothesis_certificate() -> None:
    spec = _load_json(SPEC_PATH)
    allowed = {"ZERO", "HYPOTHESIS", "CERTIFICATE"}
    assert set(spec["final_epistemic_judgments"]) == allowed
    judgment = _nodes(spec)["judgment"]
    assert set(judgment["allowed_final_judgments"]) == allowed


def test_every_node_has_residuals() -> None:
    spec = _load_json(SPEC_PATH)
    for node in spec["nodes"]:
        assert node["residuals"], f"node missing residuals: {node['node_id']}"


def test_every_node_has_forbidden_transitions() -> None:
    spec = _load_json(SPEC_PATH)
    for node in spec["nodes"]:
        assert node["forbidden_transitions"], f"node missing forbidden_transitions: {node['node_id']}"
