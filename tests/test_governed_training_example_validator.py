from __future__ import annotations

import copy
from pathlib import Path

from mcd.ml.dataset_schema import load_json_file
from mcd.ml.example_validator import validate_training_example


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "data" / "examples" / "answer_birth"


def _load_example(name: str) -> dict:
    return load_json_file(EXAMPLES_DIR / name)


def _remove_residual_from_example(example: dict, residual_name: str) -> None:
    example["expected"]["residuals"] = [item for item in example["expected"]["residuals"] if item != residual_name]


def test_reference_examples_pass_validator() -> None:
    for name in [
        "minimal_hypothesis.json",
        "complete_birth_not_final_certificate.json",
        "scientific_method_worldview_blocked.json",
    ]:
        report = validate_training_example(_load_example(name))
        assert report.valid, "\n".join(f"{error.field}: {error.message}" for error in report.errors)


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


def test_valid_rational_example_with_full_nabhani_features_passes() -> None:
    report = validate_training_example(_load_example("complete_birth_not_final_certificate.json"))
    assert report.valid, "\n".join(f"{error.field}: {error.message}" for error in report.errors)


def test_missing_reality_blocks_final_certificate() -> None:
    broken = copy.deepcopy(_load_example("complete_birth_not_final_certificate.json"))
    broken["nabhani_features"]["has_reality"] = False
    broken["nabhani_features"]["reality_status"] = "missing"
    broken["nabhani_features"]["feature_residuals"].append("missing_reality")
    broken["expected"]["final_judgment"] = "certificate"
    broken["proof_object_ref"] = "proof:1"
    broken["governance_gate_passed"] = True
    broken["reverse_trace_ref"] = "reverse:1"

    report = validate_training_example(broken)
    assert not report.valid
    assert any(error.field == "expected.final_judgment" for error in report.errors)


def test_missing_source_requires_missing_source_residual() -> None:
    broken = copy.deepcopy(_load_example("minimal_hypothesis.json"))
    broken["expected"]["residuals"] = ["intent_not_fully_explicit"]

    report = validate_training_example(broken)
    assert not report.valid
    assert any("missing_source" in error.message for error in report.errors)


def test_missing_prior_information_requires_residual_for_rational_method() -> None:
    broken = copy.deepcopy(_load_example("minimal_hypothesis.json"))
    _remove_residual_from_example(broken, "missing_prior_information")

    report = validate_training_example(broken)
    assert not report.valid
    assert any("missing_prior_information" in error.message for error in report.errors)


def test_missing_linking_requires_missing_linking_residual() -> None:
    broken = copy.deepcopy(_load_example("minimal_hypothesis.json"))
    _remove_residual_from_example(broken, "missing_linking")

    report = validate_training_example(broken)
    assert not report.valid
    assert any("missing_linking" in error.message for error in report.errors)


def test_invalid_linking_requires_invalid_linking_blocker() -> None:
    broken = copy.deepcopy(_load_example("complete_birth_not_final_certificate.json"))
    broken["nabhani_features"]["linking_validity"] = "invalid"
    broken["expected"]["blockers"] = []

    report = validate_training_example(broken)
    assert not report.valid
    assert any("invalid_linking" in error.message for error in report.errors)


def test_missing_correspondence_blocks_final_certificate() -> None:
    broken = copy.deepcopy(_load_example("complete_birth_not_final_certificate.json"))
    broken["nabhani_features"]["has_correspondence"] = False
    broken["nabhani_features"]["correspondence_type"] = "missing"
    broken["nabhani_features"]["feature_residuals"] = ["missing_correspondence"]
    broken["expected"]["residuals"].append("missing_correspondence")
    broken["expected"]["final_judgment"] = "certificate"
    broken["proof_object_ref"] = "proof:1"
    broken["governance_gate_passed"] = True
    broken["reverse_trace_ref"] = "reverse:1"

    report = validate_training_example(broken)
    assert not report.valid
    assert any(error.field == "expected.final_judgment" for error in report.errors)


def test_missing_evidence_blocks_certificate_eligibility() -> None:
    broken = copy.deepcopy(_load_example("complete_birth_not_final_certificate.json"))
    broken["nabhani_features"]["has_evidence"] = False
    broken["nabhani_features"]["evidence_type"] = "none"
    broken["nabhani_features"]["evidence_sufficiency"] = "absent"
    broken["expected"]["certificate_eligibility"] = True

    report = validate_training_example(broken)
    assert not report.valid
    assert any(error.field == "expected.certificate_eligibility" for error in report.errors)


def test_birth_certificate_does_not_imply_final_certificate() -> None:
    sample = _load_example("complete_birth_not_final_certificate.json")
    report = validate_training_example(sample)
    assert report.valid
    assert sample["expected"]["birth_judgment"] == "certificate"
    assert sample["expected"]["final_judgment"] == "hypothesis"


def test_final_certificate_requires_all_governance_gates() -> None:
    broken = copy.deepcopy(_load_example("complete_birth_not_final_certificate.json"))
    broken["expected"]["final_judgment"] = "certificate"
    broken["proof_object_ref"] = ""
    broken["governance_gate_passed"] = False
    broken["reverse_trace_ref"] = ""
    broken["nabhani_features"]["has_correspondence"] = True
    broken["nabhani_features"]["has_evidence"] = True

    report = validate_training_example(broken)
    assert not report.valid
    fields = {error.field for error in report.errors}
    assert "proof_object_ref" in fields
    assert "governance_gate_passed" in fields
    assert "reverse_trace_ref" in fields
