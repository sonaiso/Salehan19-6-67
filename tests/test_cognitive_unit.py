"""Tests for CognitiveUnit dataclass."""
from __future__ import annotations

import json
import pytest
from mcd.curriculum.cognitive_unit import CognitiveUnit
from mcd.curriculum.reality_frame import RealityFrame


def _make_unit() -> CognitiveUnit:
    return CognitiveUnit(
        unit_id="CURR-L01-0001",
        input_text="النار شيء.",
        level=1,
        target_layer="thing",
        expected_frame=RealityFrame(things=["النار"], certainty_policy="certain_knowledge"),
        certainty_policy="certain_knowledge",
        difficulty="easy",
        tags=["things"],
    )


def test_cognitive_unit_creation():
    unit = _make_unit()
    assert unit.unit_id == "CURR-L01-0001"
    assert unit.input_text == "النار شيء."
    assert unit.level == 1
    assert unit.target_layer == "thing"
    assert unit.certainty_policy == "certain_knowledge"
    assert unit.difficulty == "easy"
    assert unit.tags == ["things"]


def test_cognitive_unit_to_dict_has_all_keys():
    unit = _make_unit()
    d = unit.to_dict()
    expected_keys = [
        "unit_id", "input_text", "level", "target_layer", "expected_frame",
        "expected_warnings", "forbidden_confusions", "evidence_need",
        "certainty_policy", "difficulty", "tags", "metadata",
    ]
    for key in expected_keys:
        assert key in d, f"Missing key: {key}"


def test_cognitive_unit_to_dict_values():
    unit = _make_unit()
    d = unit.to_dict()
    assert d["unit_id"] == "CURR-L01-0001"
    assert d["level"] == 1
    assert d["target_layer"] == "thing"
    assert isinstance(d["expected_frame"], dict)


def test_cognitive_unit_json_serializable():
    unit = _make_unit()
    result = json.dumps(unit.to_dict(), ensure_ascii=False)
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert parsed["unit_id"] == "CURR-L01-0001"


def test_cognitive_unit_default_fields():
    unit = _make_unit()
    assert unit.expected_warnings == []
    assert unit.forbidden_confusions == []
    assert unit.evidence_need == []
    assert unit.metadata == {}


def test_cognitive_unit_with_forbidden_confusions():
    unit = _make_unit()
    unit.forbidden_confusions = ["property_as_thing"]
    d = unit.to_dict()
    assert d["forbidden_confusions"] == ["property_as_thing"]
