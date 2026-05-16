from __future__ import annotations

from mcd.core.transition_governance import assess_transition


def test_assess_transition_flags_semantic_corruption_skip():
    transition = assess_transition(
        "definition",
        "judgment",
        gate="semantic_layer_separation_gate",
        gate_passed=False,
    )
    assert transition.allowed is False
    assert transition.residual == "invalid_semantic_transition"


def test_assess_transition_flags_gate_block_when_order_is_legal():
    transition = assess_transition(
        "evidence",
        "inference",
        gate="inference_gate",
        gate_passed=False,
    )
    assert transition.allowed is False
    assert transition.residual == "gate_blocked"
