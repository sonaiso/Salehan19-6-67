"""Tests for CurriculumDataset."""
from __future__ import annotations

import pytest
from mcd.curriculum.curriculum_dataset import CurriculumDataset
from mcd.curriculum.cognitive_unit import CognitiveUnit


def test_load_level_returns_list():
    ds = CurriculumDataset()
    units = ds.load_level(1)
    assert isinstance(units, list)


def test_load_level_returns_50_for_each_level():
    ds = CurriculumDataset()
    for level in range(1, 9):
        units = ds.load_level(level)
        assert len(units) >= 50, f"Level {level}: expected >= 50, got {len(units)}"


def test_load_level_returns_cognitive_units():
    ds = CurriculumDataset()
    units = ds.load_level(1)
    assert len(units) > 0
    assert all(isinstance(u, CognitiveUnit) for u in units)


def test_load_level_correct_level_attribute():
    ds = CurriculumDataset()
    for level in range(1, 9):
        units = ds.load_level(level)
        for u in units:
            assert u.level == level


def test_load_all_returns_400_units():
    ds = CurriculumDataset()
    units = ds.load_all()
    assert len(units) >= 400


def test_load_all_returns_list_of_cognitive_units():
    ds = CurriculumDataset()
    units = ds.load_all()
    assert all(isinstance(u, CognitiveUnit) for u in units)


def test_load_levels_subset():
    ds = CurriculumDataset()
    units = ds.load_levels([1, 2, 3])
    assert len(units) >= 150


def test_count_by_level_returns_dict():
    ds = CurriculumDataset()
    counts = ds.count_by_level()
    assert isinstance(counts, dict)
    assert set(range(1, 9)).issubset(set(counts.keys()))


def test_count_by_level_values_are_50():
    ds = CurriculumDataset()
    counts = ds.count_by_level()
    for level, count in counts.items():
        if level <= 8:
            assert count >= 50, f"Level {level}: expected >= 50, got {count}"


def test_load_missing_level_returns_empty():
    ds = CurriculumDataset()
    units = ds.load_level(99)
    assert units == []
