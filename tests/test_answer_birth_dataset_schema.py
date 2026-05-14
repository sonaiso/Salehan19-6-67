from __future__ import annotations

import copy
from pathlib import Path

import jsonschema
import pytest

from mcd.ml.dataset_schema import (
    load_answer_birth_training_example_schema,
    load_concept_graph_schema,
    load_governed_trace_schema,
    load_json_file,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "data" / "examples" / "answer_birth"


def _load_example(name: str) -> dict:
    return load_json_file(EXAMPLES_DIR / name)


@pytest.mark.parametrize(
    "schema_loader",
    [
        load_answer_birth_training_example_schema,
        load_concept_graph_schema,
        load_governed_trace_schema,
    ],
)
def test_schemas_are_valid_json_schema(schema_loader) -> None:
    jsonschema.Draft202012Validator.check_schema(schema_loader())


@pytest.mark.parametrize(
    "fixture_name",
    [
        "minimal_hypothesis.json",
        "complete_birth_not_final_certificate.json",
        "scientific_method_worldview_blocked.json",
    ],
)
def test_fixtures_validate_against_answer_birth_schema(fixture_name: str) -> None:
    schema = load_answer_birth_training_example_schema()
    sample = _load_example(fixture_name)
    jsonschema.validate(instance=sample, schema=schema)


def test_fixture_subcontracts_validate_against_dedicated_schemas() -> None:
    sample = _load_example("minimal_hypothesis.json")
    jsonschema.validate(instance=sample["concept_graph"], schema=load_concept_graph_schema())
    jsonschema.validate(instance=sample["thought_trace"], schema=load_governed_trace_schema())


def test_public_judgment_triad_is_enforced_by_schema() -> None:
    schema = load_answer_birth_training_example_schema()
    broken = copy.deepcopy(_load_example("minimal_hypothesis.json"))
    broken["expected"]["final_judgment"] = "pending"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=broken, schema=schema)


def test_birth_and_final_judgment_fields_are_both_required() -> None:
    schema = load_answer_birth_training_example_schema()
    broken = copy.deepcopy(_load_example("minimal_hypothesis.json"))
    del broken["expected"]["birth_judgment"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=broken, schema=schema)
