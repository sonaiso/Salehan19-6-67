from mcd.math_governance import FoldRecord, UnfoldRecord, FoldUnfoldRefoldLaws


def test_fold_does_not_increase_certainty():
    original = FoldRecord(
        fold_id="f1",
        input_unit_ids=["u1"],
        folded_unit_id="fu1",
        preserved_trace_refs=["t1"],
        preserved_evidence_needs=["need1"],
        residuals=["r1"],
        preserved_relations=["rel1"],
    )
    unfolded = UnfoldRecord("u1", "fu1", ["u1"], restored_relations=["rel1"], restored_trace_refs=["t1"])
    refolded = FoldRecord(
        fold_id="f2",
        input_unit_ids=["u1"],
        folded_unit_id="fu2",
        preserved_trace_refs=["t1"],
        preserved_evidence_needs=["need1"],
        residuals=["r1"],
        preserved_relations=["rel1"],
    )
    result = FoldUnfoldRefoldLaws.evaluate(original, unfolded, refolded, certainty_before=0.4, certainty_after=0.4)
    assert result.passed is True


def test_residual_not_erased():
    original = FoldRecord("f1", ["u1"], "fu1", residuals=["r1"], preserved_relations=["rel1"], preserved_trace_refs=["t1"], preserved_evidence_needs=["need1"])
    unfolded = UnfoldRecord("u1", "fu1", ["u1"], restored_relations=["rel1"], restored_trace_refs=["t1"])
    refolded = FoldRecord("f2", ["u1"], "fu2", residuals=[], preserved_relations=["rel1"], preserved_trace_refs=["t1"], preserved_evidence_needs=["need1"])
    result = FoldUnfoldRefoldLaws.evaluate(original, unfolded, refolded, certainty_before=0.4, certainty_after=0.4)
    assert result.passed is False
    assert result.lost_residuals == ["r1"]
