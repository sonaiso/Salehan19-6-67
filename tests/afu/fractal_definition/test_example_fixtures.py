"""Run the §15 + §14 laws against every brief example (§§6–12).

Each YAML fixture under ``fixtures/`` is loaded, constructed, and pushed
through the full template + null-runtime contract. A single regression
points at the precise example that drifted.
"""
from __future__ import annotations

import pytest

from mcd.afu.contracts._common import EpistemicRank, LicensedOutput
from mcd.afu.fractal_definition import (
    FractalDefinition,
    NullFractalRuntime,
    is_fractal,
)

from ._fixture_loader import EXAMPLE_NAMES, load_definition


@pytest.mark.parametrize("name", EXAMPLE_NAMES)
def test_fixture_constructs_a_fractal_definition(name):
    fd = load_definition(name)
    assert isinstance(fd, FractalDefinition)
    ok, reasons = is_fractal(fd)
    assert ok, reasons


@pytest.mark.parametrize("name", EXAMPLE_NAMES)
def test_fixture_carries_all_fifteen_fields(name):
    fd = load_definition(name)
    for field in (
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
    ):
        assert hasattr(fd, field), field


@pytest.mark.parametrize("name", EXAMPLE_NAMES)
def test_fixture_forward_define_through_null_runtime(name):
    fd = load_definition(name)
    out = NullFractalRuntime(definition=fd).forward_define({})
    assert isinstance(out, LicensedOutput)
    assert out.rank == EpistemicRank.HYPOTHESIS
    assert "unknown_gate" in out.residuals
    assert fd.formation_gate in out.selected_gates


@pytest.mark.parametrize("name", EXAMPLE_NAMES)
def test_fixture_backward_verify_empty_is_hypothesis(name):
    fd = load_definition(name)
    rt = NullFractalRuntime(definition=fd)
    assert rt.backward_verify({}) == EpistemicRank.HYPOTHESIS


@pytest.mark.parametrize("name", EXAMPLE_NAMES)
def test_fixture_backward_verify_with_blocker_is_zero(name):
    fd = load_definition(name)
    rt = NullFractalRuntime(definition=fd)
    assert (
        rt.backward_verify({"residuals": ["transition_condition_failed"]})
        == EpistemicRank.ZERO
    )


@pytest.mark.parametrize("name", EXAMPLE_NAMES)
def test_fixture_to_licensed_output_round_trip(name):
    fd = load_definition(name)
    out = fd.to_licensed_output()
    assert out.selected_gates == (fd.formation_gate, fd.backward_gate)
    assert out.rank == fd.rank
