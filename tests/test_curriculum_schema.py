"""Tests for curriculum_schema constants."""
from __future__ import annotations

import pytest
from mcd.curriculum.curriculum_schema import (
    VALID_LEVELS, VALID_TARGET_LAYERS, VALID_CERTAINTY_POLICIES, VALID_DIFFICULTIES,
    LEVEL_NAMES, LEVEL_PRIMARY_LAYERS,
)


def test_valid_levels_non_empty():
    assert len(VALID_LEVELS) > 0


def test_valid_levels_contains_1_to_8():
    for i in range(1, 9):
        assert i in VALID_LEVELS


def test_valid_target_layers_non_empty():
    assert len(VALID_TARGET_LAYERS) > 0


def test_valid_target_layers_contains_expected():
    expected = ["thing", "property", "action", "relation", "cause", "effect",
                "instrument", "time", "place", "evidence", "certainty", "mixed_reasoning"]
    for layer in expected:
        assert layer in VALID_TARGET_LAYERS


def test_valid_certainty_policies_non_empty():
    assert len(VALID_CERTAINTY_POLICIES) > 0


def test_valid_certainty_policies_contains_expected():
    for policy in ["certain_knowledge", "probable_knowledge", "insufficient_evidence", "suspend_judgment"]:
        assert policy in VALID_CERTAINTY_POLICIES


def test_valid_difficulties_non_empty():
    assert len(VALID_DIFFICULTIES) > 0


def test_valid_difficulties_contains_expected():
    for diff in ["easy", "medium", "hard", "adversarial"]:
        assert diff in VALID_DIFFICULTIES


def test_level_names_covers_all_levels():
    for level in VALID_LEVELS:
        assert level in LEVEL_NAMES


def test_level_primary_layers_covers_all_levels():
    for level in VALID_LEVELS:
        assert level in LEVEL_PRIMARY_LAYERS
        assert len(LEVEL_PRIMARY_LAYERS[level]) > 0
