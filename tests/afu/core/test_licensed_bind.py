"""Properties of :func:`mcd.afu.core.licensed_bind.bind_licensed`."""
from __future__ import annotations

import pytest

from mcd.afu.contracts._common import EpistemicRank, LicensedOutput
from mcd.afu.core.licensed_bind import bind_licensed


def _lo(**overrides) -> LicensedOutput:
    base = dict(
        selected_gates=("g1",),
        evidence=("e1",),
        residuals=(),
        rank=EpistemicRank.HYPOTHESIS,
    )
    base.update(overrides)
    return LicensedOutput(**base)


def test_rank_monotonicity_meet():
    cert = _lo(rank=EpistemicRank.CERTIFICATE)
    hypo = _lo(rank=EpistemicRank.HYPOTHESIS)
    assert bind_licensed(cert, hypo).rank == EpistemicRank.HYPOTHESIS
    assert bind_licensed(hypo, cert).rank == EpistemicRank.HYPOTHESIS


def test_residual_preservation_no_erasure():
    a = _lo(residuals=("transition_condition_failed",))
    b = _lo(residuals=("transition_condition_unknown",))
    out = bind_licensed(a, b)
    assert "transition_condition_failed" in out.residuals
    assert "transition_condition_unknown" in out.residuals


def test_blocking_residual_caps_combined_rank():
    cert = _lo(rank=EpistemicRank.CERTIFICATE)
    with_blocker = _lo(
        rank=EpistemicRank.CERTIFICATE,
        residuals=("transition_condition_failed",),
    )
    out = bind_licensed(cert, with_blocker)
    assert out.rank == EpistemicRank.HYPOTHESIS


def test_gates_and_evidence_unioned_with_first_seen_order():
    a = _lo(selected_gates=("g1", "g2"), evidence=("e1",))
    b = _lo(selected_gates=("g2", "g3"), evidence=("e2", "e1"))
    out = bind_licensed(a, b)
    assert out.selected_gates == ("g1", "g2", "g3")
    assert out.evidence == ("e1", "e2")


def test_bind_rejects_non_licensed_output():
    with pytest.raises(TypeError):
        bind_licensed(_lo(), {"rank": "HYPOTHESIS"})  # type: ignore[arg-type]


def test_associativity_under_union_semantics():
    a = _lo(selected_gates=("g1",), evidence=("e1",))
    b = _lo(selected_gates=("g2",), evidence=("e2",))
    c = _lo(selected_gates=("g3",), evidence=("e3",))
    left = bind_licensed(bind_licensed(a, b), c)
    right = bind_licensed(a, bind_licensed(b, c))
    assert set(left.selected_gates) == set(right.selected_gates)
    assert set(left.evidence) == set(right.evidence)
    assert set(left.residuals) == set(right.residuals)
    assert left.rank == right.rank
