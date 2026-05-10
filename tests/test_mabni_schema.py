"""Tests for mabni_schema enums."""
from __future__ import annotations

import pytest
from mcd.mabni.mabni_schema import CertaintyEffect, LogicalFunction, MabniType, PragmaticFunction


def test_mabni_type_values():
    assert MabniType.negation == "negation"
    assert MabniType.interrogative == "interrogative"
    assert MabniType.conditional == "conditional"
    assert MabniType.emphasis == "emphasis"
    assert MabniType.restriction == "restriction"


def test_logical_function_values():
    assert LogicalFunction.negation == "negation"
    assert LogicalFunction.condition == "condition"
    assert LogicalFunction.qasr == "qasr"
    assert LogicalFunction.emphasis == "emphasis"


def test_pragmatic_function_values():
    assert PragmaticFunction.question == "question"
    assert PragmaticFunction.prohibition == "prohibition"
    assert PragmaticFunction.assertion == "assertion"


def test_certainty_effect_values():
    assert CertaintyEffect.none == "none"
    assert CertaintyEffect.emphasis_only == "emphasis_only"
    assert CertaintyEffect.lower == "lower"


def test_enums_are_strings():
    assert isinstance(MabniType.negation, str)
    assert isinstance(LogicalFunction.condition, str)
    assert isinstance(PragmaticFunction.question, str)
    assert isinstance(CertaintyEffect.none, str)
