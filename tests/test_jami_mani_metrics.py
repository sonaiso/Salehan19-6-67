import pytest
from mcd.fractal_kernel import JamiManiReport, JamiManiCalculator


def test_perfect_jami_mani():
    calc = JamiManiCalculator()
    required = ["نفي", "شرط", "استفهام"]
    covered = ["نفي", "شرط", "استفهام"]
    forbidden = ["توكيد_كدليل", "إعراب_كحقيقة"]
    rejected = ["توكيد_كدليل", "إعراب_كحقيقة"]
    report = calc.calculate(required, covered, forbidden, rejected)
    assert report.jami_score == 1.0
    assert report.mani_score == 1.0


def test_jami_mani_scores():
    calc = JamiManiCalculator()
    required = ["a", "b", "c", "d"]
    covered = ["a", "b"]
    forbidden = ["x", "y"]
    rejected = ["x"]
    report = calc.calculate(required, covered, forbidden, rejected)
    assert report.jami_score == 0.5
    assert report.mani_score == 0.5


def test_empty_required():
    calc = JamiManiCalculator()
    report = calc.calculate([], [], [], [])
    assert report.jami_score == 1.0
    assert report.mani_score == 1.0


def test_report_to_dict():
    report = JamiManiReport(jami_score=0.9, mani_score=0.95)
    d = report.to_dict()
    assert d["jami_score"] == 0.9
    assert d["mani_score"] == 0.95


def test_low_jami_generates_note():
    calc = JamiManiCalculator()
    required = ["a", "b", "c", "d", "e"]
    covered = ["a"]
    report = calc.calculate(required, covered, [], [])
    assert any("jami" in n.lower() for n in report.notes)


def test_blocking_invariant_coverage():
    calc = JamiManiCalculator()
    report = calc.calculate(
        required_cases=["a"],
        covered_cases=["a"],
        forbidden_cases=["x"],
        rejected_cases=["x"],
        blocking_invariants=["inv1", "inv2"],
        covered_invariants=["inv1"],
    )
    assert report.blocking_invariant_coverage == 0.5
