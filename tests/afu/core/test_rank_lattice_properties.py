"""Lattice properties of :mod:`mcd.afu.core.rank_lattice`."""
from __future__ import annotations

import itertools

import pytest

from mcd.afu.core.rank_lattice import (
    ALLOWED_PUBLIC_RANKS,
    cap_by_residuals,
    join_ranks,
    meet_ranks,
)
from mcd.afu.contracts._common import EpistemicRank


PUBLIC = sorted(ALLOWED_PUBLIC_RANKS, key=int)


def test_meet_empty_is_zero():
    assert meet_ranks() == EpistemicRank.ZERO


def test_join_empty_is_zero():
    assert join_ranks() == EpistemicRank.ZERO


@pytest.mark.parametrize("rank", PUBLIC)
def test_meet_idempotent(rank):
    assert meet_ranks(rank, rank) == rank


@pytest.mark.parametrize("rank", PUBLIC)
def test_join_idempotent(rank):
    assert join_ranks(rank, rank) == rank


@pytest.mark.parametrize("a,b", list(itertools.product(PUBLIC, repeat=2)))
def test_meet_commutative(a, b):
    assert meet_ranks(a, b) == meet_ranks(b, a)


@pytest.mark.parametrize("a,b", list(itertools.product(PUBLIC, repeat=2)))
def test_join_commutative(a, b):
    assert join_ranks(a, b) == join_ranks(b, a)


@pytest.mark.parametrize(
    "a,b,c", list(itertools.product(PUBLIC, repeat=3))
)
def test_meet_associative(a, b, c):
    assert meet_ranks(meet_ranks(a, b), c) == meet_ranks(a, meet_ranks(b, c))


def test_internal_rank_clamped_to_hypothesis_by_meet():
    # STRONG_EVIDENCE is internal → folded to HYPOTHESIS, meet with
    # HYPOTHESIS is HYPOTHESIS, meet with ZERO is ZERO.
    assert (
        meet_ranks(EpistemicRank.STRONG_EVIDENCE, EpistemicRank.HYPOTHESIS)
        == EpistemicRank.HYPOTHESIS
    )
    assert (
        meet_ranks(EpistemicRank.STRONG_EVIDENCE, EpistemicRank.ZERO)
        == EpistemicRank.ZERO
    )


def test_cap_by_residuals_no_residuals_is_identity():
    assert cap_by_residuals(EpistemicRank.CERTIFICATE, []) == EpistemicRank.CERTIFICATE
    assert cap_by_residuals(EpistemicRank.HYPOTHESIS, []) == EpistemicRank.HYPOTHESIS


def test_cap_by_residuals_blocking_downgrades_certificate():
    capped = cap_by_residuals(
        EpistemicRank.CERTIFICATE, ["transition_condition_failed"]
    )
    assert capped == EpistemicRank.HYPOTHESIS


def test_cap_by_residuals_does_not_elevate():
    capped = cap_by_residuals(
        EpistemicRank.ZERO, ["transition_condition_failed"]
    )
    assert capped == EpistemicRank.ZERO


def test_cap_by_residuals_keeps_certificate_when_no_blocker():
    # Pick a non-blocking residual code.
    from mcd.core.residual_taxonomy import _RESIDUAL_REGISTRY

    non_blockers = [
        code
        for code, spec in _RESIDUAL_REGISTRY.items()
        if not spec.blocks_certificate
    ]
    if non_blockers:
        capped = cap_by_residuals(EpistemicRank.CERTIFICATE, [non_blockers[0]])
        assert capped == EpistemicRank.CERTIFICATE
