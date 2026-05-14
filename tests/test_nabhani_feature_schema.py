from __future__ import annotations

import copy
from pathlib import Path

import jsonschema
import pytest

from mcd.ml.dataset_schema import (
    load_answer_birth_training_example_schema,
    load_json_file,
    load_nabhani_features_schema,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "data" / "examples" / "answer_birth"


def _load_example(name: str) -> dict:
    return load_json_file(EXAMPLES_DIR / name)


def test_nabhani_feature_schema_is_valid_json_schema() -> None:
    jsonschema.Draft202012Validator.check_schema(load_nabhani_features_schema())


def test_reference_example_nabhani_features_validate() -> None:
    schema = load_nabhani_features_schema()
    sample = _load_example("complete_birth_not_final_certificate.json")
    jsonschema.validate(instance=sample["nabhani_features"], schema=schema)


def test_answer_birth_schema_requires_nabhani_features() -> None:
    schema = load_answer_birth_training_example_schema()
    broken = copy.deepcopy(_load_example("minimal_hypothesis.json"))
    del broken["nabhani_features"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=broken, schema=schema)
