"""Tests for :class:`FractalDefinitionRuntime` and :class:`NullFractalRuntime`."""
from __future__ import annotations

import pytest

from mcd.afu.contracts._common import (
    AFUContractError,
    EpistemicRank,
    LicensedOutput,
)
from mcd.afu.fractal_definition import (
    FractalDefinition,
    FractalDefinitionRuntime,
    NullFractalRuntime,
    Residual,
)


def _definition(**overrides) -> FractalDefinition:
    base = dict(
        name="X",
        layer="L",
        carrier="C",
        domain="D",
        function="F",
        formation_gate="gate_forward",
        backward_gate="gate_backward",
        output_contract="OC",
        distinction=("d",),
    )
    base.update(overrides)
    return FractalDefinition.build(**base)


def test_runtime_requires_a_definition():
    with pytest.raises(AFUContractError):
        FractalDefinitionRuntime(definition="not a definition")  # type: ignore[arg-type]


def test_base_runtime_forward_define_raises_not_implemented():
    rt = FractalDefinitionRuntime(definition=_definition())
    with pytest.raises(NotImplementedError):
        rt.forward_define({})


def test_base_runtime_backward_verify_raises_not_implemented():
    rt = FractalDefinitionRuntime(definition=_definition())
    with pytest.raises(NotImplementedError):
        rt.backward_verify({})


def test_null_runtime_forward_records_formation_gate_and_unknown_residual():
    rt = NullFractalRuntime(definition=_definition())
    out = rt.forward_define({})
    assert isinstance(out, LicensedOutput)
    assert out.selected_gates == ("gate_forward",)
    assert "unknown_gate" in out.residuals
    # unknown_gate is a blocking residual → rank capped at HYPOTHESIS.
    assert out.rank == EpistemicRank.HYPOTHESIS


def test_null_runtime_backward_with_empty_effect_is_hypothesis():
    rt = NullFractalRuntime(definition=_definition())
    assert rt.backward_verify({}) == EpistemicRank.HYPOTHESIS
    assert rt.backward_verify(None) == EpistemicRank.HYPOTHESIS


def test_null_runtime_backward_with_blocking_residual_is_zero():
    rt = NullFractalRuntime(definition=_definition())
    assert (
        rt.backward_verify({"residuals": ["transition_condition_failed"]})
        == EpistemicRank.ZERO
    )


def test_null_runtime_backward_accepts_residual_instances():
    rt = NullFractalRuntime(definition=_definition())
    blocker = Residual.of("transition_condition_unknown")
    assert (
        rt.backward_verify({"residuals": [blocker]}) == EpistemicRank.ZERO
    )


def test_null_runtime_backward_accepts_licensed_output_as_effect():
    rt = NullFractalRuntime(definition=_definition())
    effect = LicensedOutput(residuals=("transition_condition_failed",))
    assert rt.backward_verify(effect) == EpistemicRank.ZERO


def test_null_runtime_preserves_existing_blocking_residual_from_definition():
    fd = _definition(residuals=["transition_condition_failed"])
    rt = NullFractalRuntime(definition=fd)
    out = rt.forward_define({})
    # Both the original blocker and the unknown_gate residual are kept.
    assert "transition_condition_failed" in out.residuals
    assert "unknown_gate" in out.residuals
    assert out.rank == EpistemicRank.HYPOTHESIS


def test_null_runtime_is_frozen():
    rt = NullFractalRuntime(definition=_definition())
    with pytest.raises(Exception):
        rt.definition = _definition()  # type: ignore[misc]
