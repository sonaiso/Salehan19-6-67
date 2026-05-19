"""§15 constructional law tests for :class:`FractalDefinition`.

Each test asserts a *single* failure mode is rejected, so a regression
points at the precise field that drifted.
"""
from __future__ import annotations

import pytest

from mcd.afu.contracts._common import AFUContractError, EpistemicRank
from mcd.afu.fractal_definition import (
    Evidence,
    FractalDefinition,
    ForwardTransition,
    Residual,
    is_fractal,
)
from mcd.afu.core.trace_anchor import TraceAnchor, TraceAnchorKind


def _kwargs(**overrides) -> dict:
    base = dict(
        name="X",
        layer="phonological",
        carrier="carrier",
        domain="domain",
        function="function",
        formation_gate="gate_forward",
        backward_gate="gate_backward",
        output_contract="licensed X",
        distinction=("d",),
    )
    base.update(overrides)
    return base


@pytest.mark.parametrize(
    "blank_field",
    [
        "name",
        "layer",
        "carrier",
        "domain",
        "function",
        "output_contract",
    ],
)
def test_blank_scalar_field_is_rejected(blank_field):
    kwargs = _kwargs(**{blank_field: "   "})
    with pytest.raises(AFUContractError) as exc:
        FractalDefinition.build(**kwargs)
    assert blank_field in str(exc.value)


def test_missing_formation_gate_is_not_fractal():
    with pytest.raises(AFUContractError, match="not_fractal"):
        FractalDefinition.build(**_kwargs(formation_gate="  "))


def test_missing_backward_gate_is_not_fractal():
    with pytest.raises(AFUContractError, match="not_fractal"):
        FractalDefinition.build(**_kwargs(backward_gate=""))


def test_distinction_must_be_nonempty():
    with pytest.raises(AFUContractError, match="distinction"):
        FractalDefinition.build(**_kwargs(distinction=()))


def test_empty_distinction_is_caught_by_is_fractal_on_mapping():
    ok, reasons = is_fractal(
        {
            "name": "X",
            "layer": "L",
            "carrier": "C",
            "domain": "D",
            "function": "F",
            "formation_gate": "g1",
            "backward_gate": "g2",
            "output_contract": "OC",
            "distinction": [],
        }
    )
    assert ok is False
    assert "missing_or_empty:distinction" in reasons


def test_is_fractal_lists_all_missing_fields_on_mapping():
    ok, reasons = is_fractal({"name": "X"})
    assert ok is False
    # Every required scalar except `name` is missing; plus distinction.
    for f in (
        "layer",
        "carrier",
        "domain",
        "function",
        "formation_gate",
        "backward_gate",
        "output_contract",
        "distinction",
    ):
        assert any(r.endswith(f) for r in reasons), (f, reasons)


def test_is_fractal_rejects_non_definition_input():
    ok, reasons = is_fractal(42)
    assert ok is False
    assert any("expected FractalDefinition" in r for r in reasons)


def test_evidence_certificate_without_anchor_is_rejected():
    with pytest.raises(AFUContractError, match="certificate_without_reverse_trace"):
        Evidence(
            source="raw_prompt",
            claim="x",
            strength=EpistemicRank.CERTIFICATE,
            anchor=None,
        )


def test_evidence_certificate_with_wrong_anchor_kind_is_rejected():
    bad_anchor = TraceAnchor(
        kind=TraceAnchorKind.PRIOR_OUTPUT,
        locator="stage:linker",
        summary="prior",
    )
    with pytest.raises(AFUContractError, match="certificate_without_reverse_trace"):
        Evidence(
            source="raw_prompt",
            claim="x",
            strength=EpistemicRank.CERTIFICATE,
            anchor=bad_anchor,
        )


def test_residual_with_empty_code_is_rejected():
    from mcd.core.residual_taxonomy import classify_residual

    spec = classify_residual("any")
    with pytest.raises(AFUContractError):
        Residual(code="   ", spec=spec)


def test_residual_unknown_code_round_trips_as_blocking():
    r = Residual.of("totally_new_residual_code")
    assert r.code == "totally_new_residual_code"
    assert r.blocking is True
    assert r.family in {"unknown"}


def test_forward_transition_self_loop_rejected():
    with pytest.raises(AFUContractError, match="silent_level_skip"):
        ForwardTransition(from_layer="L", to_layer="L", gate_id="g")
