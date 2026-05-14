from mcd.patterns import (
    FormState,
    Pattern,
    RoleState,
    compose_form_role,
    wrap_pattern_operator_as_morphological_pattern,
)


def test_compose_form_role_creates_hypothesis() -> None:
    form = FormState(
        form_id="form.lexeme.1",
        layer="lexeme",
        symbols=("كتب",),
        invariants=("identity",),
        source_refs=("SRC-1",),
    )
    role = RoleState(
        role_id="role.lexeme.1",
        layer="lexeme",
        role_type="class",
        features={"features": {"wordclass": "noun"}},
        rank="HYPOTHESIS",
        evidence_refs=("EV-1",),
    )
    pattern = Pattern(
        pattern_id="pattern.lexeme",
        layer="lexeme",
        family="wordclass",
        form_slots=("symbols",),
        role_slots=("features",),
        binding_relation="form_role_tensor",
        governor="governor.lexeme",
        required_evidence_rank="HYPOTHESIS",
        closure_function="chi_lexeme",
        minimum_completion="MC_lexeme",
        residual_policy=("preserve",),
        fatal_barriers=("residual_erasure",),
        allowed_bridges=("lexeme_to_morphology",),
        forbidden_bridges=(),
        trace_policy="replayable",
    )

    hypothesis = compose_form_role(form, role, pattern)

    assert hypothesis.layer == "lexeme"
    assert hypothesis.pattern_id == "pattern.lexeme"
    assert hypothesis.form == form
    assert hypothesis.role == role
    assert set(hypothesis.trace_refs) == {"SRC-1", "EV-1"}


def test_wrap_pattern_operator_registry_as_morphological_pattern() -> None:
    pattern = wrap_pattern_operator_as_morphological_pattern("faail")
    assert pattern is not None
    assert pattern.layer == "morphology"
    assert pattern.pattern_form == "فاعِل"
    assert pattern.operator_vector.get("agency", 0) > 0.5
