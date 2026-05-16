from mcd.math_governance import GovernedFractalUnit, MathematicalGovernanceGate, validate_text_ascent_chain
from mcd.traceability.trace_builder import TraceBuilder


def _build_full_chain(final_unit_type: str = "hypothesis") -> list[GovernedFractalUnit]:
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
        uid = f"u{i+1}"
        pre = [f"u{i}"] if i > 0 else []
        post = [f"u{i+2}"] if i < len(levels) - 1 else []
        units.append(
            GovernedFractalUnit(
                unit_id=uid,
                level_id=level,
                unit_type=final_unit_type if level == "final_judgment" else level,
                surface="النص الكامل",
                normalized="النص الكامل",
                raw_span=(0, 10),
                normalized_span=(0, 10),
                raw_text="النص الكامل",
                normalized_text="النص الكامل",
                pre_unit_ids=pre,
                post_unit_ids=post,
                morphism_in=levels[i - 1][1] if i > 0 else None,
                morphism_out=morph_out or None,
                pre_to_post_relation="ascent_step" if post else "",
                trace_refs=["TR-1", "U-000001"],
                beta_status="valid_uncertified" if post else "valid_certified",
                metadata={"generated_reason": "seed"} if i == 0 else {},
            )
        )
    return units


def test_raw_text_to_unicode_units():
    b = TraceBuilder()
    text = "سلام"
    bundle = b.build(text)
    assert len(bundle.unicode_units) == len(text)


def test_unicode_to_grapheme_cluster_arabic_diacritics():
    b = TraceBuilder()
    bundle = b.build("عَلِمَ")
    assert len(bundle.graphemes) == 3


def test_grapheme_to_token_trace_preserved():
    b = TraceBuilder()
    bundle = b.build("كتب زيد")
    for tok in [t for t in bundle.tokens if t.token_type != "whitespace"]:
        assert tok.unicode_trace_ids
        assert tok.grapheme_ids


def test_paragraph_to_full_text_trace_preserved():
    units = _build_full_chain()
    paragraph = next(u for u in units if u.level_id == "paragraph")
    section = next(u for u in units if u.level_id == "section")
    full_text = next(u for u in units if u.level_id == "full_text")
    assert section.unit_id in paragraph.post_unit_ids
    assert full_text.unit_id in section.post_unit_ids


def test_certificate_reverse_traces_to_unicode_offsets():
    units = _build_full_chain(final_unit_type="certificate")
    report = validate_text_ascent_chain(units)
    assert report.passed is True


def test_hypothesis_reverse_traces_to_sentence_and_tokens():
    units = _build_full_chain(final_unit_type="hypothesis")
    report = validate_text_ascent_chain(units)
    assert report.passed is True


def test_zero_reports_broken_unicode_or_token_trace():
    units = _build_full_chain(final_unit_type="zero")
    final = units[-1]
    final.pre_unit_ids = []
    report = validate_text_ascent_chain(units)
    assert report.passed is False
    assert any("unicode" in v.lower() for v in report.violations)


def test_forbidden_transition_marker_is_blocked():
    units = _build_full_chain(final_unit_type="hypothesis")
    token = next(u for u in units if u.level_id == "token")
    token.metadata["forbidden_transitions"] = ["silent_level_skip"]
    report = validate_text_ascent_chain(units)
    assert report.passed is False
    assert any("forbidden transitions detected" in v for v in report.violations)


def test_certificate_requires_governance_gate_signal():
    units = _build_full_chain(final_unit_type="certificate")
    final = units[-1]
    final.metadata["governance_gate_passed"] = False
    report = validate_text_ascent_chain(units)
    assert report.passed is False
    assert any("certificate_without_governance_gate" in v for v in report.violations)


def test_certificate_with_residual_is_rejected():
    units = _build_full_chain(final_unit_type="certificate")
    final = units[-1]
    final.residuals = ["open_gap"]
    report = validate_text_ascent_chain(units)
    assert report.passed is False
    assert any("residual" in v.lower() for v in report.violations)


def test_no_final_status_without_unicode_to_fulltext_path():
    units = _build_full_chain()
    units.pop()
    gate = MathematicalGovernanceGate()
    ok, violations = gate.validate_unit_chain(units)
    assert ok is False
    assert any("final_judgment" in v for v in violations)


def test_shadda_fatha_grapheme_single_cluster():
    b = TraceBuilder()
    bundle = b.build("مُحَمَّد")
    assert any("ّ" in g.surface for g in bundle.graphemes)


def test_tanween_preserved_in_grapheme():
    b = TraceBuilder()
    bundle = b.build("كتابٌ")
    assert any("ٌ" in g.surface for g in bundle.graphemes)


def test_bidi_text_does_not_break_offsets():
    b = TraceBuilder()
    text = "ABC العربية 123"
    bundle = b.build(text)
    assert [u.char_index for u in bundle.unicode_units] == list(range(len(text)))
