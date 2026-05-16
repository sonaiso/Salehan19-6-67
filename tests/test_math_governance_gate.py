from mcd.math_governance import (
    GovernedFractalUnit,
    MathematicalGovernanceGate,
)


def _sample_units():
    levels = [
        ("raw_text", "raw_text_to_unicode"),
        ("unicode", "unicode_to_grapheme"),
        ("grapheme", "grapheme_to_orthographic_unit"),
        ("orthographic_unit", "orthographic_unit_to_token"),
        ("token", "token_to_lexeme"),
        ("lexeme", "lexeme_to_morphology"),
        ("morphology", "morphology_to_phrase"),
        ("phrase", "phrase_to_clause"),
        ("clause", "clause_to_sentence"),
        ("sentence", "sentence_to_paragraph"),
        ("paragraph", "paragraph_to_section"),
        ("section", "section_to_full_text"),
        ("full_text", "full_text_to_discourse_graph"),
        ("discourse_graph", "discourse_graph_to_claim_graph"),
        ("claim_graph", "claim_graph_to_proof_object"),
        ("proof_object", "proof_object_to_final_judgment"),
        ("final_judgment", ""),
    ]
    units: list[GovernedFractalUnit] = []
    for i, (level, morph_out) in enumerate(levels):
        unit_id = f"u{i+1}"
        pre = [f"u{i}"] if i > 0 else []
        post = [f"u{i+2}"] if i < len(levels) - 1 else []
        unit_type = "hypothesis" if level == "final_judgment" else level
        unit = GovernedFractalUnit(
            unit_id=unit_id,
            level_id=level,
            unit_type=unit_type,
            surface="زيد كاتب",
            normalized="زيد كاتب",
            raw_span=(0, 8),
            normalized_span=(0, 8),
            raw_text="زيد كاتب",
            normalized_text="زيد كاتب",
            pre_unit_ids=pre,
            post_unit_ids=post,
            morphism_in=levels[i - 1][1] if i > 0 else None,
            morphism_out=morph_out or None,
            pre_to_post_relation="ascent_step" if post else "",
            trace_refs=["t1", "U-000001"],
            residuals=[],
            beta_status="valid_uncertified" if post else "valid_certified",
            metadata={"generated_reason": "seed"} if i == 0 else {},
        )
        units.append(unit)
    return units


def test_each_unit_knows_pre_and_post():
    gate = MathematicalGovernanceGate()
    ok, violations = gate.validate_unit_chain(_sample_units())
    assert ok is True
    assert violations == []


def test_evidence_monotonicity():
    gate = MathematicalGovernanceGate()
    report = gate.run(units=_sample_units(), dataset_path="data/evaluation/ambiguity_ar.jsonl")
    assert report.evidence_monotonicity_score >= 0.0


def test_final_judgment_reverse_path():
    units = _sample_units()
    assert units[-1].trace_refs


def test_no_certificate_without_governance():
    ok, violations = MathematicalGovernanceGate.validate_no_certificate_without_governance(
        {"judgment": "certificate", "governance_passed": False}
    )
    assert ok is False
    assert any("governance gate pass" in v for v in violations)
    assert any("proof object" in v for v in violations)
    assert any("reverse trace" in v for v in violations)


def test_certificate_governance_passes_with_required_refs():
    ok, violations = MathematicalGovernanceGate.validate_no_certificate_without_governance(
        {
            "judgment": "certificate",
            "governance_passed": True,
            "proof_object_ref": "PO-1",
            "reverse_trace_ref": "RT-1",
        }
    )
    assert ok is True
    assert violations == []
