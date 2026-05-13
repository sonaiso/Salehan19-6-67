from mcd.math_governance import (
    CERTIFICATE,
    HYPOTHESIS,
    ZERO,
    GovernedFractalUnit,
    LayerClosureAlgebra,
    build_default_units_for_text,
    local_certificate,
)


def test_layer_closure_soundness_and_completeness_hold_per_layer():
    units = build_default_units_for_text("ضرب زيد عمرًا", final_judgment="hypothesis")
    vector = LayerClosureAlgebra().evaluate(units)
    for cert in vector.local_certificates.values():
        assert cert.minimum_completeness == cert.closure


def test_no_global_certificate_without_local_closure():
    units = build_default_units_for_text("ضرب زيد عمرًا", final_judgment="hypothesis")
    token_unit = next(unit for unit in units if unit.level_id == "token")
    token_unit.trace_refs = []
    vector = LayerClosureAlgebra().evaluate(units)
    assert vector.global_judgment == HYPOTHESIS
    assert any("local certificate" in reason for reason in vector.reasons)


def test_no_global_certificate_without_valid_bridges():
    units = build_default_units_for_text("ضرب زيد عمرًا", final_judgment="hypothesis")
    lexeme_unit = next(unit for unit in units if unit.level_id == "lexeme")
    lexeme_unit.pre_unit_ids = []
    vector = LayerClosureAlgebra().evaluate(units)
    assert vector.global_judgment == HYPOTHESIS
    assert any("bridge ascend" in reason for reason in vector.reasons)


def test_no_layer_theft_when_bridge_fails():
    units = build_default_units_for_text("ضرب زيد عمرًا", final_judgment="hypothesis")
    lexeme_unit = next(unit for unit in units if unit.level_id == "lexeme")
    lexeme_unit.pre_unit_ids = []
    vector = LayerClosureAlgebra().evaluate(units)
    assert any(not bridge.passed for bridge in vector.bridge_evaluations)
    reasons = [reason for bridge in vector.bridge_evaluations for reason in bridge.reasons]
    assert "layer_theft_blocked" in reasons


def test_scoped_certificate_local_not_equal_global():
    units = build_default_units_for_text("ضرب زيد عمرًا", final_judgment="hypothesis")
    final_unit = next(unit for unit in units if unit.level_id == "final_judgment")
    final_unit.metadata["fatal_barrier"] = True
    vector = LayerClosureAlgebra().evaluate(units, required_layers=["raw_text", "final_judgment"])
    assert vector.local_certificates["raw_text"].judgment == CERTIFICATE
    assert vector.global_judgment == ZERO


def test_non_derivational_tree_prevents_absolute_zero():
    unit = GovernedFractalUnit(
        unit_id="u-root-1",
        level_id="root",
        unit_type="demonstrative",
        surface="هذا",
        normalized="هذا",
        raw_text="هذا",
        normalized_text="هذا",
        raw_span=(0, 3),
        normalized_span=(0, 3),
        trace_refs=["TR-1"],
        beta_status="valid_uncertified",
        metadata={"fatal_barrier": True, "non_derivational_category": "demonstrative"},
    )
    cert = local_certificate(unit)
    assert cert.judgment == HYPOTHESIS
