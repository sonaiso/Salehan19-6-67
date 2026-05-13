from __future__ import annotations

from mcd.math_governance.level_schema import ALL_LEVELS
from mcd.qualification.layer_sovereignty_registry import LayerSovereigntyRegistry


def test_layer_sovereignty_registry_covers_all_levels() -> None:
    registry = LayerSovereigntyRegistry()
    by_layer = {entry.layer: entry for entry in registry.all()}
    assert set(by_layer) == {level.name for level in ALL_LEVELS}

    for level in ALL_LEVELS:
        entry = by_layer[level.name]
        assert entry.governor.startswith("governor.")
        assert entry.required_evidence
        assert entry.closure_function.startswith("chi_")
        assert entry.minimum_completion.startswith("MC_")
        assert "no_residual_erasure" in entry.residual_rules


def test_layer_sovereignty_registry_blocks_silent_level_skip() -> None:
    registry = LayerSovereigntyRegistry()
    entries = registry.all()

    for idx, entry in enumerate(entries):
        if idx < len(entries) - 1:
            assert entry.allowed_ascent == [entries[idx + 1].layer]
        else:
            assert entry.allowed_ascent == []
        assert entry.layer in entry.forbidden_ascent
