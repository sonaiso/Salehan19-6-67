"""Tests for ManatApplicabilityEngine."""
import pytest
from mcd.grounding.manat_engine import ManatApplicabilityEngine, ManatStatus


@pytest.fixture
def engine():
    return ManatApplicabilityEngine()


def test_all_conditions_matched_applicable(engine):
    conditions = ["وجود_نار", "وجود_حطب"]
    properties = ["وجود_نار", "وجود_حطب", "وجود_هواء"]
    result = engine.check("rule_1", "النار تحرق", conditions, "الموقد", properties)
    assert result.status == ManatStatus.APPLICABLE
    assert result.applicability_score >= 0.8


def test_some_conditions_partially_applicable(engine):
    conditions = ["وجود_نار", "وجود_حطب", "وجود_هواء", "درجة_حرارة_عالية", "جفاف"]
    properties = ["وجود_نار", "وجود_حطب"]
    result = engine.check("rule_2", "النار تحرق", conditions, "الموقد", properties)
    assert result.status == ManatStatus.PARTIALLY_APPLICABLE
    assert 0.4 <= result.applicability_score < 0.8


def test_no_conditions_matched_not_applicable(engine):
    conditions = ["وجود_ماء", "برودة_شديدة"]
    properties = ["وجود_نار", "حرارة"]
    result = engine.check("rule_3", "الماء يطفئ", conditions, "المحيط", properties)
    assert result.status == ManatStatus.NOT_APPLICABLE
    assert result.applicability_score < 0.4


def test_no_conditions_suspended(engine):
    result = engine.check("rule_4", "حكم مطلق", [], "أي واقع", [])
    assert result.status == ManatStatus.SUSPENDED
    assert result.explanation


def test_matched_missing_conditions_listed(engine):
    conditions = ["شرط_أ", "شرط_ب", "شرط_ج"]
    properties = ["شرط_أ"]
    result = engine.check("rule_5", "قاعدة", conditions, "واقع", properties)
    assert "شرط_أ" in result.matched_conditions
    assert len(result.missing_conditions) == 2


def test_result_fields(engine):
    result = engine.check("rule_x", "text", ["c1", "c2"], "reality", ["c1", "c2"])
    assert result.rule_id == "rule_x"
    assert result.target_reality == "reality"
    assert isinstance(result.applicability_conditions, list)
