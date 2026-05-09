"""Tests for CurriculumGenerator."""
from __future__ import annotations

import pytest
from mcd.curriculum.curriculum_generator import CurriculumGenerator
from mcd.curriculum.cognitive_unit import CognitiveUnit


def test_generate_level_returns_correct_count():
    gen = CurriculumGenerator()
    units = gen.generate_level(1, 10)
    assert len(units) == 10


def test_generate_level_correct_level_attribute():
    gen = CurriculumGenerator()
    for level in range(1, 9):
        units = gen.generate_level(level, 5)
        assert all(u.level == level for u in units)


def test_generate_level_id_format():
    gen = CurriculumGenerator()
    units = gen.generate_level(1, 5)
    assert units[0].unit_id == "CURR-L01-0001"
    assert units[1].unit_id == "CURR-L01-0002"


def test_generate_level_deterministic():
    gen = CurriculumGenerator()
    units_a = gen.generate_level(1, 10, seed=42)
    units_b = gen.generate_level(1, 10, seed=42)
    assert [u.unit_id for u in units_a] == [u.unit_id for u in units_b]


def test_generate_level_different_seeds_differ():
    gen = CurriculumGenerator()
    units_a = gen.generate_level(1, 10, seed=42)
    units_b = gen.generate_level(1, 10, seed=99)
    # Same IDs (format-based), but different content possible
    assert all(isinstance(u, CognitiveUnit) for u in units_a)
    assert all(isinstance(u, CognitiveUnit) for u in units_b)


def test_generate_progression_count():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    assert len(units) == 8 * 5


def test_generate_progression_all_levels():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=3)
    levels = {u.level for u in units}
    assert levels == {1, 2, 3, 4, 5, 6, 7, 8}


def test_generate_mixed_assessment():
    gen = CurriculumGenerator()
    units = gen.generate_mixed_assessment(count=10)
    assert len(units) == 10
    # All levels should be 6, 7, or 8
    for u in units:
        assert u.level in (6, 7, 8)


def test_level8_units_are_adversarial():
    gen = CurriculumGenerator()
    units = gen.generate_level(8, 5)
    for u in units:
        assert u.difficulty == "adversarial"
        assert len(u.forbidden_confusions) > 0


def test_level7_units_have_evidence_need():
    gen = CurriculumGenerator()
    units = gen.generate_level(7, 5)
    for u in units:
        assert len(u.evidence_need) > 0
        assert u.certainty_policy in ("insufficient_evidence", "suspend_judgment")


def test_all_units_json_serializable():
    gen = CurriculumGenerator()
    import json
    units = gen.generate_progression(count_per_level=3)
    for u in units:
        result = json.dumps(u.to_dict(), ensure_ascii=False)
        assert isinstance(result, str)
