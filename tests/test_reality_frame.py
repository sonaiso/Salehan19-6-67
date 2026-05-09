"""Tests for RealityFrame and RelationTriple dataclasses."""
from __future__ import annotations

import json
import pytest
from mcd.curriculum.reality_frame import RealityFrame, RelationTriple


def test_relation_triple_creation():
    rt = RelationTriple(source="A", relation="supports", target="B")
    assert rt.source == "A"
    assert rt.relation == "supports"
    assert rt.target == "B"
    assert rt.qualifier is None


def test_relation_triple_with_qualifier():
    rt = RelationTriple(source="A", relation="supports", target="B", qualifier="strongly")
    assert rt.qualifier == "strongly"


def test_relation_triple_to_dict():
    rt = RelationTriple(source="الدليل", relation="supports", target="الحكم")
    d = rt.to_dict()
    assert d["source"] == "الدليل"
    assert d["relation"] == "supports"
    assert d["target"] == "الحكم"
    assert d["qualifier"] is None


def test_relation_triple_json_serializable():
    rt = RelationTriple(source="A", relation="supports", target="B")
    result = json.dumps(rt.to_dict(), ensure_ascii=False)
    assert isinstance(result, str)


def test_reality_frame_defaults():
    frame = RealityFrame()
    assert frame.things == []
    assert frame.properties == []
    assert frame.actions == []
    assert frame.agents == []
    assert frame.patients == []
    assert frame.instruments == []
    assert frame.times == []
    assert frame.places == []
    assert frame.causes == []
    assert frame.effects == []
    assert frame.relations == []
    assert frame.evidence_need == []
    assert frame.certainty_policy == "probable_knowledge"
    assert frame.warnings == []


def test_reality_frame_with_things():
    frame = RealityFrame(things=["النار", "الماء"], certainty_policy="certain_knowledge")
    assert frame.things == ["النار", "الماء"]
    assert frame.certainty_policy == "certain_knowledge"


def test_reality_frame_to_dict_has_all_keys():
    frame = RealityFrame(things=["النار"])
    d = frame.to_dict()
    expected_keys = [
        "things", "properties", "actions", "agents", "patients", "instruments",
        "times", "places", "causes", "effects", "relations",
        "evidence_need", "certainty_policy", "warnings",
    ]
    for key in expected_keys:
        assert key in d, f"Missing key: {key}"


def test_reality_frame_to_dict_with_relations():
    triple = RelationTriple("A", "supports", "B")
    frame = RealityFrame(things=["A", "B"], relations=[triple])
    d = frame.to_dict()
    assert len(d["relations"]) == 1
    assert d["relations"][0]["source"] == "A"


def test_reality_frame_json_serializable():
    frame = RealityFrame(
        things=["النار"],
        relations=[RelationTriple("النار", "causes", "الحرارة")],
        certainty_policy="certain_knowledge",
    )
    result = json.dumps(frame.to_dict(), ensure_ascii=False)
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert parsed["things"] == ["النار"]
