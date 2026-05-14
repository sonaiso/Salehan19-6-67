from mcd.patterns import (
    BridgePattern,
    ClosureJudgment,
    FormState,
    MinimumCompletion,
    Pattern,
    RoleState,
    close_layer,
    compose_form_role,
    evaluate_global_certificate,
    validate_bridge,
)


def _pattern(layer: str, pattern_id: str) -> Pattern:
    return Pattern(
        pattern_id=pattern_id,
        layer=layer,
        family="layer_default",
        form_slots=("symbols",),
        role_slots=("features",),
        binding_relation="form_role_tensor",
        governor=f"governor.{layer}",
        required_evidence_rank="HYPOTHESIS",
        closure_function=f"chi_{layer}",
        minimum_completion=f"MC_{layer}",
        residual_policy=("preserve",),
        fatal_barriers=("residual_erasure",),
        allowed_bridges=(f"{layer}_to_next",),
        forbidden_bridges=(),
        trace_policy="replayable",
    )


def _mc(layer: str) -> MinimumCompletion:
    return MinimumCompletion(
        mc_id=f"MC_{layer}",
        layer=layer,
        required_form_fields=("symbols",),
        required_role_fields=("features",),
        required_dependencies=("EV-1",),
        required_evidence_rank="HYPOTHESIS",
        residual_policy=("preserve",),
        fatal_barriers=("residual_erasure",),
    )


def _closure(layer: str, pattern_id: str):
    pattern = _pattern(layer, pattern_id)
    form = FormState(
        form_id=f"form.{layer}",
        layer=layer,
        symbols=("x",),
        invariants=("identity",),
        source_refs=("SRC-1",),
    )
    role = RoleState(
        role_id=f"role.{layer}",
        layer=layer,
        role_type="default",
        features={"features": {"ok": True}},
        rank="HYPOTHESIS",
        evidence_refs=("EV-1",),
    )
    hypothesis = compose_form_role(form, role, pattern)
    return close_layer(hypothesis, pattern, _mc(layer))


def test_bridge_pattern_required_for_ascent() -> None:
    source = _closure("morphology", "pattern.morphology")
    bridge = BridgePattern(
        bridge_id="morphology_to_semantic_role",
        source_layer="morphology",
        target_layer="semantic_role",
        source_required_judgment="certificate",
        target_minimum_completion="MC_semantic_role",
        bridge_governor="governor.semantic_role",
        required_evidence_rank="HYPOTHESIS",
        preserves=("residuals", "trace"),
        residual_policy=("preserve",),
        fatal_barriers=("residual_erasure",),
    )

    ok = validate_bridge(source, "semantic_role", bridge)
    wrong_target_layer = validate_bridge(source, "claim", bridge)

    assert ok.passed is True
    assert wrong_target_layer.passed is False
    assert "target_layer_mismatch" in wrong_target_layer.blockers


def test_local_certificate_does_not_imply_global_certificate() -> None:
    source = _closure("morphology", "pattern.morphology")
    target = _closure("semantic_role", "pattern.semantic_role")

    no_bridge_global = evaluate_global_certificate(
        local_closures={"morphology": source, "semantic_role": target},
        required_layers=("morphology", "semantic_role"),
        bridge_results=tuple(),
    )
    assert no_bridge_global == ClosureJudgment.HYPOTHESIS

    invalid_bridge = BridgePattern(
        bridge_id="morphology_to_semantic_role",
        source_layer="morphology",
        target_layer="semantic_role",
        source_required_judgment="certificate",
        target_minimum_completion="MC_semantic_role",
        bridge_governor="governor.semantic_role",
        required_evidence_rank="HYPOTHESIS",
        preserves=("residuals",),
        residual_policy=("preserve",),
        fatal_barriers=("residual_erasure",),
    )
    bridge_result = validate_bridge(source, "claim", invalid_bridge)
    global_with_bridge = evaluate_global_certificate(
        local_closures={"morphology": source, "semantic_role": target},
        required_layers=("morphology", "semantic_role"),
        bridge_results=(bridge_result,),
    )
    assert global_with_bridge == ClosureJudgment.HYPOTHESIS
