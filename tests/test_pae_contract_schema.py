import copy
import json
from pathlib import Path

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "spec/worktree/pae_contract.schema.json"
CONTRACT_PATH = ROOT / "spec/worktree/pae_contract.json"


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _validate(instance: dict, schema: dict) -> None:
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(instance=instance, schema=schema)


def test_schema_validates_contract() -> None:
    schema = _load_json(SCHEMA_PATH)
    contract = _load_json(CONTRACT_PATH)
    _validate(contract, schema)


def test_required_fields_enforced() -> None:
    schema = _load_json(SCHEMA_PATH)
    contract = _load_json(CONTRACT_PATH)
    broken = copy.deepcopy(contract)
    del broken["certificate_requirements"]
    with pytest.raises(jsonschema.ValidationError):
        _validate(broken, schema)


def test_enum_validation_enforced() -> None:
    schema = _load_json(SCHEMA_PATH)
    contract = _load_json(CONTRACT_PATH)
    broken = copy.deepcopy(contract)
    broken["engine_name"] = "PAE_V2"
    with pytest.raises(jsonschema.ValidationError):
        _validate(broken, schema)


def test_no_certificate_without_required_gates() -> None:
    schema = _load_json(SCHEMA_PATH)
    contract = _load_json(CONTRACT_PATH)
    broken = copy.deepcopy(contract)
    broken["output_examples"][0] = {
        "id": "invalid-certificate",
        "judgment": "CERTIFICATE",
        "proof_object": None,
        "governance_gate": "failed",
        "reverse_trace": [],
        "residuals": ["certificate_without_governance_gate"],
        "transition_tags": ["certificate_without_governance_gate"]
    }
    with pytest.raises(jsonschema.ValidationError):
        _validate(broken, schema)


def test_residual_preservation_for_blocking_tags() -> None:
    schema = _load_json(SCHEMA_PATH)
    contract = _load_json(CONTRACT_PATH)
    broken = copy.deepcopy(contract)
    broken["output_examples"][0]["transition_tags"] = ["certificate_without_reverse_trace"]
    broken["output_examples"][0]["residuals"] = []
    with pytest.raises(jsonschema.ValidationError):
        _validate(broken, schema)


def test_silent_level_skip_prevention() -> None:
    schema = _load_json(SCHEMA_PATH)
    contract = _load_json(CONTRACT_PATH)
    broken = copy.deepcopy(contract)
    broken["output_examples"][0]["transition_tags"] = ["silent_level_skip"]
    broken["output_examples"][0]["residuals"] = ["silent_level_skip"]
    with pytest.raises(jsonschema.ValidationError):
        _validate(broken, schema)
