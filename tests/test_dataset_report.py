"""Tests for dataset_report.py"""
import pytest
from mcd.evaluation.dataset_report import DatasetReport
from mcd.evaluation.dataset_schema import BenchmarkExample


def _make_example(i: int, source_type="static_gold", policy="strong_knowledge", jt="epistemic", diff="easy"):
    return BenchmarkExample(
        example_id=f"RPT-{i:03d}",
        input_text=f"example {i}",
        source_type=source_type,
        expected_certainty_policy=policy,
        expected_epistemic_status="verified" if policy in ("strong_knowledge", "near_certainty") else "suspended",
        expected_judgment_types={jt: 0.9},
        difficulty=diff,
        tags=[jt],
    )


def test_dataset_report_markdown_basic():
    examples = [_make_example(i) for i in range(10)]
    report = DatasetReport(examples=examples)
    md = report.generate_markdown()
    assert "# Dataset Report" in md
    assert "Total examples" in md


def test_dataset_report_markdown_sections():
    examples = [_make_example(i) for i in range(20)]
    report = DatasetReport(examples=examples)
    md = report.generate_markdown()
    assert "## 1. Overview" in md
    assert "## 2. Source Type Distribution" in md
    assert "## 7. Coverage Matrix" in md
    assert "## 8. Shari Examples" in md
    assert "## 11. Recommendations" in md


def test_dataset_report_empty():
    report = DatasetReport(examples=[])
    md = report.generate_markdown()
    assert "Total examples: **0**" in md


def test_dataset_report_with_shari():
    shari = BenchmarkExample(
        example_id="SH-001",
        input_text="هل الربا حرام؟",
        source_type="static_gold",
        expected_certainty_policy="suspend",
        expected_epistemic_status="suspended",
        expected_judgment_types={"shari": 0.9},
        required_warnings=["shari_evidence_required"],
        difficulty="hard",
        tags=["shari"],
    )
    report = DatasetReport(examples=[shari])
    md = report.generate_markdown()
    assert "Shari Examples" in md


def test_dataset_report_recommendations_warning_small():
    examples = [_make_example(i) for i in range(5)]
    report = DatasetReport(examples=examples)
    md = report.generate_markdown()
    assert "fewer than 250" in md


def test_dataset_report_full_dataset():
    from mcd.evaluation.dataset_loader import load_all
    examples = load_all()
    report = DatasetReport(examples=examples)
    md = report.generate_markdown()
    assert "meets 0.80 threshold" in md or "below 0.80" in md
