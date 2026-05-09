"""Tests for EvidenceGate."""
from __future__ import annotations

import pytest
from mcd.engines.evidence_gate import EvidenceGate
from mcd.core.evidence import Evidence, EvidenceType


@pytest.fixture
def gate():
    return EvidenceGate()


def _make_evidence(strength: float, reliability: float) -> Evidence:
    return Evidence(
        source_id="test",
        source_type=EvidenceType.EXPERIMENTAL.value,
        description="test evidence",
        strength=strength,
        reliability=reliability,
    )


def test_empty_evidence_rejected(gate):
    result = gate.evaluate("النار تحرق", [])
    assert result.accepted is False
    assert result.evidence_strength == 0.0


def test_empty_evidence_has_reason(gate):
    result = gate.evaluate("claim", [])
    assert result.reason


def test_strong_evidence_accepted(gate):
    ev = _make_evidence(0.95, 0.95)
    result = gate.evaluate("النار تحرق", [ev])
    assert result.accepted is True
    assert result.evidence_strength > 0.5


def test_weak_evidence_low_strength(gate):
    ev = _make_evidence(0.1, 0.1)
    result = gate.evaluate("claim", [ev])
    assert result.evidence_strength < 0.3


def test_reason_always_populated(gate):
    for ev_list in [[], [_make_evidence(0.5, 0.5)]]:
        result = gate.evaluate("test", ev_list)
        assert result.reason


def test_compute_strength_weighted(gate):
    evs = [_make_evidence(0.8, 0.9), _make_evidence(0.6, 0.7)]
    result = gate.evaluate("claim", evs)
    expected = (0.8 * 0.9 + 0.6 * 0.7) / 2
    assert abs(result.evidence_strength - expected) < 0.01
