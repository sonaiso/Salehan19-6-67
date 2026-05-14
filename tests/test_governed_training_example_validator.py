from __future__ import annotations

import copy
from pathlib import Path

from mcd.ml.dataset_schema import load_json_file
from mcd.ml.example_validator import validate_training_example


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "data" / "examples" / "answer_birth"


def _load_example(name: str) -> dict:
    return load_json_file(EXAMPLES_DIR / name)


def test_reference_examples_pass_validator() -> None:
    for name in [
        "minimal_hypothesis.json",
        "complete_birth_not_final_certificate.json",
        "scientific_method_worldview_blocked.json",
    ]:
        report = validate_training_example(_load_example(name))
        assert report.valid, [f"{error.field}: {error.message}" for error in report.errors]


def test_validator_blocks_silent_promotion_from_hypothesis() -> None:
    broken = copy.deepcopy(_load_example("minimal_hypothesis.json"))
    broken["requested_public_judgment"] = "hypothesis"
    broken["expected"]["birth_judgment"] = "certificate"

    report = validate_training_example(broken)
    assert not report.valid
    assert any("silent promotion" in error.message for error in report.errors)


def test_validator_rejects_means_issuing_judgment() -> None:
    broken = copy.deepcopy(_load_example("minimal_hypothesis.json"))
    broken["thinking_means"]["can_issue_judgment"] = True

    report = validate_training_example(broken)
    assert not report.valid
    assert any(error.field == "thinking_means.can_issue_judgment" for error in report.errors)


def test_validator_requires_scientific_worldview_blocker() -> None:
    broken = copy.deepcopy(_load_example("scientific_method_worldview_blocked.json"))
    broken["expected"]["blockers"] = []

    report = validate_training_example(broken)
    assert not report.valid
    assert any(error.field == "expected.blockers" for error in report.errors)


def test_validator_rejects_unrecognized_evidence_rank_token() -> None:
    broken = copy.deepcopy(_load_example("minimal_hypothesis.json"))
    broken["thought_trace"]["evidence_rank"]["thinking"] = "ultra"

    report = validate_training_example(broken)
    assert not report.valid
    assert any(error.field == "thought_trace.evidence_rank.thinking" for error in report.errors)


def test_validator_requires_separate_trace_path_and_evidence_fields() -> None:
    broken = copy.deepcopy(_load_example("minimal_hypothesis.json"))
    del broken["thought_trace"]["trace_evidence_complete"]

    report = validate_training_example(broken)
    assert not report.valid
    assert any(error.field.startswith("thought_trace") for error in report.errors)


def test_certificate_example_requires_gate_residuals_when_gates_missing() -> None:
    broken = copy.deepcopy(_load_example("complete_birth_not_final_certificate.json"))
    broken["expected"]["residuals"] = []

    report = validate_training_example(broken)
    assert not report.valid
    assert any("certificate_without_proof_object" in error.message for error in report.errors)
