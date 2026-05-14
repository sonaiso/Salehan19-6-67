from __future__ import annotations

import json
from pathlib import Path

from mcd.ml.example_validator import validate_training_example
from mcd.ml.synthetic_generator import (
    CATEGORY_SPECS,
    SyntheticAnswerBirthDatasetGenerator,
    generate_synthetic_answer_birth_dataset,
)


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_generator_is_deterministic_with_seed() -> None:
    g1 = SyntheticAnswerBirthDatasetGenerator(seed=123)
    g2 = SyntheticAnswerBirthDatasetGenerator(seed=123)

    e1 = g1.generate_examples(total_examples=120)
    e2 = g2.generate_examples(total_examples=120)

    assert e1 == e2


def test_generated_samples_validate_with_existing_validators() -> None:
    generator = SyntheticAnswerBirthDatasetGenerator(seed=11)
    samples = generator.generate_examples(total_examples=125)

    for sample in samples:
        report = validate_training_example(sample)
        assert report.valid, "\n".join(f"{e.field}: {e.message}" for e in report.errors)


def test_generator_covers_all_declared_categories() -> None:
    generator = SyntheticAnswerBirthDatasetGenerator(seed=7)
    samples = generator.generate_examples(total_examples=250)

    categories_seen = {sample["context"].split("category:", 1)[-1] for sample in samples}
    expected = {spec.key for spec in CATEGORY_SPECS}
    assert expected.issubset(categories_seen)


def test_certificate_and_birth_governance_constraints_hold() -> None:
    generator = SyntheticAnswerBirthDatasetGenerator(seed=19)
    samples = generator.generate_examples(total_examples=250)

    for sample in samples:
        expected = sample["expected"]
        trace = sample["thought_trace"]
        features = sample["nabhani_features"]

        assert expected["birth_judgment"] in {"zero", "hypothesis", "certificate"}
        assert expected["final_judgment"] in {"zero", "hypothesis", "certificate"}

        if expected["birth_judgment"] == "certificate":
            assert trace["trace_path_complete"] is True
            assert trace["trace_evidence_complete"] is True

        if expected["final_judgment"] == "certificate":
            assert sample["proof_object_ref"]
            assert sample["governance_gate_passed"] is True
            assert sample["reverse_trace_ref"]
            assert features["has_reality"] is True
            assert features["has_correspondence"] is True
            assert features["has_evidence"] is True
            assert features["evidence_matches_claim_domain"] is True


def test_missing_features_residuals_and_scientific_blockers_are_preserved() -> None:
    generator = SyntheticAnswerBirthDatasetGenerator(seed=5)
    samples = generator.generate_examples(total_examples=300)

    for sample in samples:
        features = sample["nabhani_features"]
        residuals = set(sample["expected"]["residuals"])
        feature_residuals = set(features["feature_residuals"])
        blockers = set(sample["expected"]["blockers"])

        for token in features["missing_features"]:
            residual_token = f"missing_{token}"
            assert residual_token in feature_residuals
            assert residual_token in residuals

        if sample["thinking_method"]["method_type"] == "scientific":
            output_kind = sample["mentality_frame"]["output_kind"]
            if output_kind == "worldview":
                assert "scientific_method_as_worldview" in blockers
                assert sample["expected"]["final_judgment"] == "zero"
                assert "scientific_method_as_worldview" in residuals
            if output_kind in {"normative", "legal", "shari"}:
                assert "scientific_method_as_normative_judgment" in blockers
                assert sample["expected"]["final_judgment"] == "zero"
                assert "scientific_method_as_normative_judgment" in residuals


def test_script_writer_outputs_expected_split_files_and_stats(tmp_path: Path) -> None:
    out_dir = tmp_path / "answer_birth"
    report = generate_synthetic_answer_birth_dataset(
        output_dir=out_dir,
        seed=101,
        total_examples=250,
        train_size=200,
        validation_size=25,
        test_size=25,
    )

    train_path = out_dir / "train.jsonl"
    val_path = out_dir / "validation.jsonl"
    test_path = out_dir / "test.jsonl"
    stats_path = out_dir / "stats.json"

    assert train_path.exists()
    assert val_path.exists()
    assert test_path.exists()
    assert stats_path.exists()

    assert len(_read_jsonl(train_path)) == 200
    assert len(_read_jsonl(val_path)) == 25
    assert len(_read_jsonl(test_path)) == 25

    stats = json.loads(stats_path.read_text(encoding="utf-8"))
    assert stats["total_examples"] == 250
    assert stats["splits"] == {"train": 200, "validation": 25, "test": 25}

    counts = stats["counts"]
    assert "intent_status" in counts
    assert "method_type" in counts
    assert "judgment_domain" in counts
    assert "means_type" in counts
    assert "birth_judgment" in counts
    assert "final_judgment" in counts
    assert "blocker" in counts
    assert "residual" in counts
    assert "certainty_rank" in counts
    assert "nabhani_feature_completeness" in counts

    assert report["stats"]["splits"]["train"] == 200
