"""Tests for :class:`Gate`, :class:`GateSpec`, :class:`GateVerdict`."""
from __future__ import annotations

import pytest

from mcd.afu.contracts._common import AFUContractError, EpistemicRank
from mcd.afu.core.gate import (
    Gate,
    GateSpec,
    GateStatus,
    GateVerdict,
    unknown_gate_verdict,
)


def _spec(gate_id: str = "gate_x") -> GateSpec:
    return GateSpec(gate_id=gate_id, layer="L", description="d")


def test_gate_spec_requires_non_empty_fields():
    with pytest.raises(AFUContractError):
        GateSpec(gate_id="", layer="L", description="d")
    with pytest.raises(AFUContractError):
        GateSpec(gate_id="g", layer="", description="d")
    with pytest.raises(AFUContractError):
        GateSpec(gate_id="g", layer="L", description="")


def test_gate_spec_strips_and_freezes_collections():
    spec = GateSpec(
        gate_id=" g ",
        layer=" L ",
        description=" d ",
        expected_evidence_kinds=("", "  raw_text "),
        possible_residuals=("a", "  b "),
    )
    assert spec.gate_id == "g"
    assert spec.expected_evidence_kinds == ("raw_text",)
    assert spec.possible_residuals == ("a", "b")


def test_gate_verdict_unknown_blocks_certificate():
    v = GateVerdict(
        gate_id="g",
        status=GateStatus.UNKNOWN,
        rank=EpistemicRank.CERTIFICATE,
    )
    assert v.rank == EpistemicRank.HYPOTHESIS


def test_gate_verdict_failed_is_zero_regardless_of_input_rank():
    v = GateVerdict(
        gate_id="g",
        status=GateStatus.FAILED,
        rank=EpistemicRank.CERTIFICATE,
    )
    assert v.rank == EpistemicRank.ZERO


def test_gate_verdict_blocking_residual_caps_passed_certificate():
    v = GateVerdict(
        gate_id="g",
        status=GateStatus.PASSED,
        rank=EpistemicRank.CERTIFICATE,
        residuals=("transition_condition_failed",),
    )
    assert v.rank == EpistemicRank.HYPOTHESIS
    # Residual is preserved (no erasure).
    assert "transition_condition_failed" in v.residuals


def test_gate_verdict_passes_clean_certificate_when_no_blocker():
    v = GateVerdict(
        gate_id="g",
        status=GateStatus.PASSED,
        rank=EpistemicRank.CERTIFICATE,
    )
    assert v.rank == EpistemicRank.CERTIFICATE


def test_gate_requires_a_spec():
    with pytest.raises(AFUContractError):
        Gate(spec="not a spec")  # type: ignore[arg-type]


def test_unknown_gate_verdict_is_blocking_hypothesis():
    v = unknown_gate_verdict("g")
    assert v.status == GateStatus.UNKNOWN
    assert v.rank == EpistemicRank.HYPOTHESIS
    assert "unknown_gate" in v.residuals


def test_unknown_gate_verdict_uses_placeholder_for_blank_id():
    v = unknown_gate_verdict("")
    assert v.gate_id == "<unknown>"
