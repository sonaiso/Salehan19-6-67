"""Tests for IndustrialBridge."""
from __future__ import annotations

import re
import pytest
from mcd.curriculum.industrial_bridge import IndustrialBridge, CurriculumIndustrialCase
from mcd.curriculum.curriculum_generator import CurriculumGenerator


def test_convert_returns_only_l7_l8():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    bridge = IndustrialBridge()
    cases = bridge.convert(units)
    assert len(cases) == 10  # 5 L7 + 5 L8


def test_convert_returns_industrial_cases():
    gen = CurriculumGenerator()
    units = gen.generate_level(7, 5)
    bridge = IndustrialBridge()
    cases = bridge.convert(units)
    assert all(isinstance(c, CurriculumIndustrialCase) for c in cases)


def test_case_id_format():
    gen = CurriculumGenerator()
    units = gen.generate_level(7, 5)
    bridge = IndustrialBridge()
    cases = bridge.convert(units)
    for case in cases:
        assert re.match(r"CURR-IND-\d{4}$", case.case_id), f"Bad case_id: {case.case_id}"


def test_expected_behavior_valid():
    gen = CurriculumGenerator()
    units = gen.generate_progression(count_per_level=5)
    bridge = IndustrialBridge()
    cases = bridge.convert(units)
    valid_behaviors = {"suspend", "answer_with_evidence", "lower_certainty"}
    for case in cases:
        assert case.expected_behavior in valid_behaviors, f"Bad behavior: {case.expected_behavior}"


def test_source_unit_id_preserved():
    gen = CurriculumGenerator()
    units = gen.generate_level(7, 5)
    bridge = IndustrialBridge()
    cases = bridge.convert(units)
    source_ids = {u.unit_id for u in units}
    for case in cases:
        assert case.source_unit_id in source_ids


def test_l7_units_get_suspend_behavior():
    gen = CurriculumGenerator()
    units = gen.generate_level(7, 10)
    bridge = IndustrialBridge()
    cases = bridge.convert(units)
    for case in cases:
        assert case.expected_behavior == "suspend"


def test_l8_units_get_suspend_behavior():
    gen = CurriculumGenerator()
    units = gen.generate_level(8, 10)
    bridge = IndustrialBridge()
    cases = bridge.convert(units)
    for case in cases:
        assert case.expected_behavior == "suspend"


def test_export_to_jsonl():
    gen = CurriculumGenerator()
    units = gen.generate_level(7, 3)
    bridge = IndustrialBridge()
    cases = bridge.convert(units)
    jsonl_str = bridge.export_to_jsonl(cases)
    lines = [line for line in jsonl_str.split("\n") if line.strip()]
    assert len(lines) == 3


def test_case_to_dict_has_expected_keys():
    gen = CurriculumGenerator()
    units = gen.generate_level(7, 1)
    bridge = IndustrialBridge()
    cases = bridge.convert(units)
    d = cases[0].to_dict()
    for key in ["case_id", "input_text", "source_unit_id", "expected_behavior",
                "expected_minimum_warnings", "forbidden_behaviors",
                "expected_certainty_policy", "difficulty", "tags"]:
        assert key in d


def test_convert_empty_input():
    bridge = IndustrialBridge()
    cases = bridge.convert([])
    assert cases == []


def test_non_l7_l8_units_excluded():
    gen = CurriculumGenerator()
    units = gen.generate_level(1, 10) + gen.generate_level(3, 10)
    bridge = IndustrialBridge()
    cases = bridge.convert(units)
    assert cases == []
