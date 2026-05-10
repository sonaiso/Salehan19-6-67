import pytest
from mcd.fractal_kernel import FoldOperation, UnfoldOperation, RefoldCheck, FoldLawEnforcer


def make_fold(**kwargs):
    defaults = dict(
        fold_id="FOLD-001",
        input_unit_ids=["U1", "U2"],
        output_fold_unit_id="FOLD-OUT-001",
        preserved_relations=["agent_of"],
        preserved_vectors=["evidence_vector"],
    )
    defaults.update(kwargs)
    return FoldOperation(**defaults)


def test_fold_does_not_raise_certainty():
    enforcer = FoldLawEnforcer()
    ok, warnings = enforcer.check_certainty_non_increase(0.5, 0.5)
    assert ok is True


def test_fold_raises_certainty_violation():
    enforcer = FoldLawEnforcer()
    ok, warnings = enforcer.check_certainty_non_increase(0.3, 0.8)
    assert ok is False
    assert len(warnings) > 0


def test_trace_preservation_ok():
    enforcer = FoldLawEnforcer()
    fold = make_fold()
    ok, warnings = enforcer.check_trace_preservation(fold, ["T-001"])
    assert ok is True


def test_trace_preservation_missing():
    enforcer = FoldLawEnforcer()
    fold = make_fold()
    ok, warnings = enforcer.check_trace_preservation(fold, [])
    assert ok is False


def test_refold_preserves_residual_type():
    enforcer = FoldLawEnforcer()
    fold1 = make_fold(fold_id="F1", preserved_relations=["agent_of"], preserved_vectors=["evidence_vector"])
    fold2 = make_fold(fold_id="F2", preserved_relations=["agent_of"], preserved_vectors=["evidence_vector"])
    result = enforcer.check_refold_consistency(fold1, fold2)
    assert result.passed is True
    assert result.consistency_score == 1.0


def test_refold_loses_relation():
    enforcer = FoldLawEnforcer()
    fold1 = make_fold(fold_id="F1", preserved_relations=["agent_of", "patient_of"])
    fold2 = make_fold(fold_id="F2", preserved_relations=["agent_of"])
    result = enforcer.check_refold_consistency(fold1, fold2)
    assert result.passed is False
    assert len(result.lost_in_refold) > 0


def test_no_proof_from_fold_alone():
    enforcer = FoldLawEnforcer()
    ok, warnings = enforcer.check_no_proof_from_fold_alone([], is_certificate=True)
    assert ok is False


def test_fold_to_dict():
    fold = make_fold()
    d = fold.to_dict()
    assert d["fold_id"] == "FOLD-001"
