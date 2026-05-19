"""Tests for :class:`TraceAnchor`."""
from __future__ import annotations

import pytest

from mcd.afu.contracts._common import AFUContractError
from mcd.afu.core.trace_anchor import TraceAnchor, TraceAnchorKind


def test_anchor_requires_known_kind():
    with pytest.raises(AFUContractError):
        TraceAnchor(kind="not_a_kind", locator="x", summary="s")  # type: ignore[arg-type]


def test_anchor_requires_locator():
    with pytest.raises(AFUContractError):
        TraceAnchor(kind=TraceAnchorKind.INPUT_SEGMENT, locator="  ", summary="s")


def test_anchor_requires_summary():
    with pytest.raises(AFUContractError):
        TraceAnchor(kind=TraceAnchorKind.EVIDENCE, locator="x", summary="")


def test_anchor_strips_and_freezes():
    a = TraceAnchor(
        kind=TraceAnchorKind.EVIDENCE, locator="  x  ", summary="  s  "
    )
    assert a.locator == "x"
    assert a.summary == "s"


def test_anchor_kind_from_string_value():
    a = TraceAnchor(kind="evidence", locator="x", summary="s")  # type: ignore[arg-type]
    assert a.kind == TraceAnchorKind.EVIDENCE
