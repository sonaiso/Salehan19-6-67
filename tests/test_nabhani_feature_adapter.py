from __future__ import annotations

from pathlib import Path

from mcd.ml.dataset_schema import load_json_file
from mcd.ml.nabhani_features import (
    derive_nabhani_features_from_example,
    nabhani_features_to_training_vector,
    validate_nabhani_features,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "data" / "examples" / "answer_birth"


def _load_example(name: str) -> dict:
    return load_json_file(EXAMPLES_DIR / name)


def test_derive_nabhani_features_from_example_keeps_explicit_tokens() -> None:
    sample = _load_example("complete_birth_not_final_certificate.json")
    frame = derive_nabhani_features_from_example(sample)
    assert frame.method_type == "rational"
    assert frame.thinking_type == "deep"
    assert frame.thinking_domain_scope == "rational_general"
    assert frame.has_evidence is True
    assert frame.certainty_rank == "certificate"


def test_validate_nabhani_features_rejects_invalid_source_when_source_missing() -> None:
    sample = _load_example("minimal_hypothesis.json")
    broken = dict(sample["nabhani_features"])
    broken["source_type"] = "repository_artifact"
    report = validate_nabhani_features(broken)
    assert not report.valid
    assert any(error.field == "source_type" for error in report.errors)


def test_training_vector_has_stable_governed_keys() -> None:
    sample = _load_example("complete_birth_not_final_certificate.json")
    vector = nabhani_features_to_training_vector(sample["nabhani_features"])
    assert set(vector.keys()) == {
        "has_reality",
        "has_source",
        "has_prior_information",
        "has_linking",
        "has_correspondence",
        "has_evidence",
        "method_type",
        "judgment_domain",
        "thinking_type",
        "thinking_domain_scope",
        "thinking_topic",
        "certainty_rank",
    }


def test_validate_nabhani_features_rejects_topic_thinking_mismatch() -> None:
    sample = _load_example("complete_birth_not_final_certificate.json")
    broken = dict(sample["nabhani_features"])
    broken["thinking_topic"] = "society"
    broken["thinking_type"] = "deep"
    report = validate_nabhani_features(broken)
    assert not report.valid
    assert any(error.field == "thinking_type" for error in report.errors)


def test_validate_nabhani_features_allows_scientific_worldview_only_when_marked_misaligned() -> None:
    sample = _load_example("scientific_method_worldview_blocked.json")
    report = validate_nabhani_features(sample["nabhani_features"])
    assert report.valid

    broken = dict(sample["nabhani_features"])
    broken["matrix_method_alignment"] = True
    broken_report = validate_nabhani_features(broken)
    assert not broken_report.valid
    assert any(error.field == "matrix_method_alignment" for error in broken_report.errors)
