"""Tests for the 15-field shape of :class:`FractalDefinition`."""
from __future__ import annotations

import pytest

from mcd.afu.contracts._common import EpistemicRank, LicensedOutput
from mcd.afu.fractal_definition import (
    Evidence,
    FractalDefinition,
    Residual,
    is_fractal,
)
from mcd.afu.core.trace_anchor import TraceAnchor, TraceAnchorKind


def _minimal_kwargs(**overrides) -> dict:
    base = dict(
        name="X",
        layer="phonological",
        carrier="carrier",
        domain="domain",
        function="function",
        formation_gate="gate_forward",
        backward_gate="gate_backward",
        output_contract="licensed X",
        distinction=("X vs Y",),
    )
    base.update(overrides)
    return base


def test_fields_present_in_declared_order():
    fd = FractalDefinition.build(**_minimal_kwargs())
    fields = [f.name for f in fd.__dataclass_fields__.values()]
    assert fields == [
        "name",
        "layer",
        "carrier",
        "domain",
        "prior_information",
        "distinction",
        "relation_before",
        "relation_after",
        "function",
        "formation_gate",
        "backward_gate",
        "evidence",
        "residuals",
        "rank",
        "output_contract",
    ]


def test_is_fractal_true_on_minimal():
    fd = FractalDefinition.build(**_minimal_kwargs())
    ok, reasons = is_fractal(fd)
    assert ok and reasons == ()


def test_to_licensed_output_exposes_gates_and_rank():
    fd = FractalDefinition.build(**_minimal_kwargs())
    out = fd.to_licensed_output()
    assert isinstance(out, LicensedOutput)
    assert out.selected_gates == ("gate_forward", "gate_backward")
    assert out.rank == EpistemicRank.HYPOTHESIS


def test_strings_are_stripped_and_tuples_frozen():
    fd = FractalDefinition.build(
        **_minimal_kwargs(
            name="  X  ",
            prior_information=["  a  ", "", "b"],
            relation_before=("", "  one  "),
            distinction=("  d  ",),
        )
    )
    assert fd.name == "X"
    assert fd.prior_information == ("a", "b")
    assert fd.relation_before == ("one",)
    assert isinstance(fd.prior_information, tuple)


def test_rank_clamped_to_public_lattice():
    fd = FractalDefinition.build(
        **_minimal_kwargs(rank=EpistemicRank.STRONG_EVIDENCE)
    )
    # Internal kernel rank → folded to HYPOTHESIS.
    assert fd.rank == EpistemicRank.HYPOTHESIS


def test_certificate_downgraded_by_blocking_residual():
    fd = FractalDefinition.build(
        **_minimal_kwargs(
            rank=EpistemicRank.CERTIFICATE,
            residuals=[Residual.of("transition_condition_failed")],
        )
    )
    # Residual is preserved; rank is downgraded.
    assert fd.rank == EpistemicRank.HYPOTHESIS
    assert fd.residual_codes() == ("transition_condition_failed",)


def test_evidence_summary_is_deterministic():
    ev = Evidence(source="raw_prompt", claim="contains-arabic")
    fd = FractalDefinition.build(**_minimal_kwargs(evidence=[ev]))
    assert fd.evidence_summaries() == ("raw_prompt::contains-arabic",)


def test_evidence_certificate_requires_anchor():
    anchor = TraceAnchor(
        kind=TraceAnchorKind.INPUT_SEGMENT,
        locator="0:10",
        summary="first ten chars",
    )
    ev = Evidence(
        source="raw_prompt",
        claim="contains-arabic",
        strength=EpistemicRank.CERTIFICATE,
        anchor=anchor,
    )
    fd = FractalDefinition.build(**_minimal_kwargs(evidence=[ev]))
    assert fd.evidence[0].strength == EpistemicRank.CERTIFICATE


def test_residual_string_promoted_to_residual_instance():
    fd = FractalDefinition.build(
        **_minimal_kwargs(residuals=["transition_condition_unknown"])
    )
    assert isinstance(fd.residuals[0], Residual)
    assert fd.residuals[0].blocking is True


def test_residual_must_be_residual_or_string():
    with pytest.raises(Exception):
        FractalDefinition.build(**_minimal_kwargs(residuals=[123]))


def test_frozen_dataclass_immutable():
    fd = FractalDefinition.build(**_minimal_kwargs())
    with pytest.raises(Exception):
        fd.name = "Y"  # type: ignore[misc]
