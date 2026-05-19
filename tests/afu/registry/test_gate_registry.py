"""Tests for the immutable, fail-closed :class:`GateRegistry`."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from mcd.afu.contracts._common import AFUContractError, EpistemicRank
from mcd.afu.core.gate import Gate, GateSpec, GateStatus, GateVerdict
from mcd.afu.registry import GateRegistry, empty_registry
from mcd.afu.theory_index import THEORY_INDEX_PATH


def _gate(gate_id: str = "g1", evaluator=None) -> Gate:
    return Gate(spec=GateSpec(gate_id=gate_id, layer="L", description="d"), evaluator=evaluator)


def test_empty_registry_has_no_gates():
    reg = empty_registry()
    assert len(reg) == 0
    assert reg.gate_ids() == ()


def test_evaluate_unknown_gate_is_fail_closed():
    verdict = empty_registry().evaluate("not_registered", state=None)
    assert verdict.status == GateStatus.UNKNOWN
    assert verdict.rank == EpistemicRank.HYPOTHESIS
    assert "unknown_gate" in verdict.residuals


def test_register_returns_new_registry_and_does_not_mutate():
    reg = empty_registry()
    reg2 = reg.register(_gate("g1"))
    assert "g1" in reg2
    assert "g1" not in reg
    assert reg2 is not reg


def test_double_registration_rejected():
    reg = empty_registry().register(_gate("g1"))
    with pytest.raises(AFUContractError):
        reg.register(_gate("g1"))


def test_registry_rejects_mismatched_key_and_gate_id():
    with pytest.raises(AFUContractError):
        GateRegistry(_gates={"g1": _gate("g2")})


def test_registry_rejects_non_gate_value():
    with pytest.raises(AFUContractError):
        GateRegistry(_gates={"g1": "not a gate"})  # type: ignore[dict-item]


def test_spec_only_gate_evaluates_as_unknown():
    reg = empty_registry().register(_gate("g_spec_only", evaluator=None))
    verdict = reg.evaluate("g_spec_only", state=None)
    assert verdict.status == GateStatus.UNKNOWN
    assert "unknown_gate" in verdict.residuals


def test_evaluator_returning_non_verdict_is_unknown_with_error_residual():
    reg = empty_registry().register(_gate("g_bad", evaluator=lambda s: "nope"))
    verdict = reg.evaluate("g_bad", state=None)
    assert verdict.status == GateStatus.UNKNOWN
    assert "unknown_gate_evaluation_error" in verdict.residuals


def test_evaluator_raising_is_unknown_with_error_residual():
    def boom(state):
        raise RuntimeError("boom")

    reg = empty_registry().register(_gate("g_raise", evaluator=boom))
    verdict = reg.evaluate("g_raise", state=None)
    assert verdict.status == GateStatus.UNKNOWN
    assert "unknown_gate_evaluation_error" in verdict.residuals
    assert "boom" in verdict.note


def test_evaluator_passing_propagates_verdict():
    passing = GateVerdict(
        gate_id="g_pass", status=GateStatus.PASSED, rank=EpistemicRank.CERTIFICATE
    )
    reg = empty_registry().register(_gate("g_pass", evaluator=lambda s: passing))
    verdict = reg.evaluate("g_pass", state=None)
    assert verdict is passing


# --- Theory index ---------------------------------------------------------------


def test_theory_index_yaml_is_valid_and_empty_but_structured():
    raw = yaml.safe_load(Path(THEORY_INDEX_PATH).read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    assert str(raw.get("schema_version", "")).strip()
    layers = raw.get("layers")
    assert isinstance(layers, list)
    # PR 2 ships the index empty; later PRs populate it.
    assert layers == []
