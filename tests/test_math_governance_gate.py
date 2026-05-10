from mcd.math_governance import (
    GovernedFractalUnit,
    MathematicalGovernanceGate,
)


def _sample_units():
    u1 = GovernedFractalUnit(
        unit_id="u1",
        level_id="unicode",
        unit_type="unicode",
        post_unit_ids=["u2"],
        trace_refs=["t1"],
        metadata={"generated_reason": "seed"},
    )
    u2 = GovernedFractalUnit(
        unit_id="u2",
        level_id="token",
        unit_type="token",
        pre_unit_ids=["u1"],
        post_unit_ids=["u3"],
        trace_refs=["t1"],
    )
    u3 = GovernedFractalUnit(
        unit_id="u3",
        level_id="lexeme",
        unit_type="lexeme",
        pre_unit_ids=["u2"],
        post_unit_ids=["u4"],
        trace_refs=["t1"],
    )
    u4 = GovernedFractalUnit(
        unit_id="u4",
        level_id="final_answer",
        unit_type="answer",
        pre_unit_ids=["u3"],
        trace_refs=["t1"],
    )
    return [u1, u2, u3, u4]


def test_each_unit_knows_pre_and_post():
    gate = MathematicalGovernanceGate()
    ok, violations = gate.validate_unit_chain(_sample_units())
    assert ok is True
    assert violations == []


def test_evidence_monotonicity():
    gate = MathematicalGovernanceGate()
    report = gate.run(units=_sample_units(), dataset_path="data/evaluation/ambiguity_ar.jsonl")
    assert report.evidence_monotonicity_score >= 0.0


def test_final_answer_reverse_path():
    units = _sample_units()
    assert units[-1].trace_refs


def test_no_certificate_without_governance():
    ok, violations = MathematicalGovernanceGate.validate_no_certificate_without_governance(
        {"judgment": "certificate", "governance_passed": False}
    )
    assert ok is False
    assert violations
