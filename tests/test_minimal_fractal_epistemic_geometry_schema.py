import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "spec/worktree/minimal_fractal_epistemic_geometry.json"
SCHEMA_PATH = ROOT / "spec/worktree/minimal_fractal_epistemic_geometry.schema.json"


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def test_schema_validates_geometry_spec():
    schema = _load_json(SCHEMA_PATH)
    spec = _load_json(SPEC_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(spec, schema)


def test_final_judgment_set_not_expanded():
    spec = _load_json(SPEC_PATH)
    assert set(spec["invariants"]["final_judgments"]) == {"ZERO", "HYPOTHESIS", "CERTIFICATE"}

