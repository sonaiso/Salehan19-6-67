"""Tests for MathematicalPatternMiner."""
import pytest
from mcd.foldable_learning.mathematical_pattern_miner import MathematicalPatternMiner, MinedPattern
from mcd.residual_learning.residual_schema import CognitiveResidual


def _make_residual(rtype, pid="p1"):
    return CognitiveResidual(residual_id=f"r-{pid}", proposal_id=pid, residual_types=[rtype])


def test_no_residuals_returns_empty():
    miner = MathematicalPatternMiner()
    assert miner.mine([]) == []


def test_repeated_residual_proposes_invariant():
    miner = MathematicalPatternMiner()
    residuals = [_make_residual("evidence_residual", f"p{i}") for i in range(5)]
    patterns = miner.mine(residuals)
    assert patterns
    assert any("evidence_residual" == p.residual_type for p in patterns)


def test_threshold_is_three():
    miner = MathematicalPatternMiner()
    # Only 2 residuals — below threshold
    residuals = [_make_residual("metaphor_residual", f"p{i}") for i in range(2)]
    patterns = miner.mine(residuals)
    assert not any(p.residual_type == "metaphor_residual" for p in patterns)
    # 3 residuals — at threshold
    residuals.append(_make_residual("metaphor_residual", "p3"))
    patterns = miner.mine(residuals)
    assert any(p.residual_type == "metaphor_residual" for p in patterns)


def test_mined_pattern_has_proposed_invariant():
    miner = MathematicalPatternMiner()
    residuals = [_make_residual("harm_haram_residual", f"p{i}") for i in range(4)]
    patterns = miner.mine(residuals)
    for p in patterns:
        assert p.proposed_invariant
        assert p.proposed_test


def test_get_proposed_invariants():
    miner = MathematicalPatternMiner()
    residuals = [_make_residual("injection_residual", f"p{i}") for i in range(3)]
    invariants = miner.get_proposed_invariants(residuals)
    assert invariants


def test_mined_pattern_to_dict():
    miner = MathematicalPatternMiner()
    residuals = [_make_residual("evidence_residual", f"p{i}") for i in range(3)]
    patterns = miner.mine(residuals)
    for p in patterns:
        d = p.to_dict()
        assert "pattern_id" in d
        assert "frequency" in d
