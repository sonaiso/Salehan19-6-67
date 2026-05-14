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
        "certainty_rank",
    }
