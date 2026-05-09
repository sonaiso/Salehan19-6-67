"""Tests for CognitiveMeasureBuilder."""
from __future__ import annotations

import pytest

from mcd.nabhani.cognitive_measure import CognitiveMeasureBuilder, MEASURE_CERTAINTY_THRESHOLD


@pytest.fixture
def builder():
    return CognitiveMeasureBuilder()


QUALIFYING_CLAIM = {
    "text": "النار تحرق",
    "certainty": 0.90,
    "evidence_strength": 0.88,
    "domain": "causality",
    "has_conflict": False,
}


class TestCognitiveMeasureRequiresHighCertainty:
    def test_low_certainty_returns_none(self, builder):
        claim = {**QUALIFYING_CLAIM, "certainty": 0.70}
        assert builder.build(claim) is None

    def test_below_threshold_returns_none(self, builder):
        claim = {**QUALIFYING_CLAIM, "certainty": MEASURE_CERTAINTY_THRESHOLD - 0.01}
        assert builder.build(claim) is None

    def test_conflict_prevents_measure(self, builder):
        claim = {**QUALIFYING_CLAIM, "has_conflict": True}
        assert builder.build(claim) is None

    def test_missing_domain_prevents_measure(self, builder):
        claim = {**QUALIFYING_CLAIM, "domain": ""}
        assert builder.build(claim) is None

    def test_low_evidence_strength_prevents_measure(self, builder):
        claim = {**QUALIFYING_CLAIM, "evidence_strength": 0.40}
        assert builder.build(claim) is None


class TestCognitiveMeasureBuiltWhenSufficient:
    def test_measure_built_for_qualifying_claim(self, builder):
        measure = builder.build(QUALIFYING_CLAIM)
        assert measure is not None

    def test_measure_has_id(self, builder):
        measure = builder.build(QUALIFYING_CLAIM)
        assert measure.measure_id.startswith("measure_")

    def test_measure_domain_matches(self, builder):
        measure = builder.build(QUALIFYING_CLAIM)
        assert measure.domain == "causality"

    def test_measure_certainty_correct(self, builder):
        measure = builder.build(QUALIFYING_CLAIM)
        assert measure.certainty == pytest.approx(0.90, abs=0.001)

    def test_measure_rule_contains_text(self, builder):
        measure = builder.build(QUALIFYING_CLAIM)
        assert "النار" in measure.rule or "causality" in measure.rule
