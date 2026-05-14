from dataclasses import replace

from mcd.patterns import (
    ClosureJudgment,
    FormState,
    MinimumCompletion,
    Pattern,
    RoleState,
    close_layer,
    compose_form_role,
)


def _sample_pattern() -> Pattern:
    return Pattern(
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
        residual_policy=("preserve", "no_residual_erasure"),
        fatal_barriers=("residual_erasure",),
        allowed_bridges=("lexeme_to_morphology",),
        forbidden_bridges=("lexeme_to_final_judgment",),
        trace_policy="replayable",
    )


def _sample_mc() -> MinimumCompletion:
    return MinimumCompletion(
        mc_id="MC_lexeme",
        layer="lexeme",
        required_form_fields=("symbols",),
        required_role_fields=("features",),
        required_dependencies=("EV-1",),
        required_evidence_rank="HYPOTHESIS",
        residual_policy=("preserve",),
        fatal_barriers=("residual_erasure",),
    )


def _sample_form() -> FormState:
    return FormState(
        form_id="form.lexeme.1",
        layer="lexeme",
        symbols=("كتب",),
        invariants=("identity",),
        source_refs=("SRC-1",),
    )


def test_chi_returns_certificate_when_mc_is_satisfied() -> None:
    pattern = _sample_pattern()
    mc = _sample_mc()
    role = RoleState(
        role_id="role.lexeme.1",
        layer="lexeme",
        role_type="class",
        features={"features": {"wordclass": "noun"}},
        rank="HYPOTHESIS",
        evidence_refs=("EV-1",),
    )
    hypothesis = compose_form_role(_sample_form(), role, pattern)

    result = close_layer(hypothesis, pattern, mc)

    assert result.judgment == ClosureJudgment.CERTIFICATE
    assert result.mc_satisfied is True
    assert result.chi == 1


def test_hypothesis_when_domain_valid_but_mc_incomplete() -> None:
    pattern = _sample_pattern()
    mc = _sample_mc()
    role = RoleState(
        role_id="role.lexeme.2",
        layer="lexeme",
        role_type="class",
        features={"features": {}},
        rank="HYPOTHESIS",
        evidence_refs=(),
    )
    hypothesis = compose_form_role(_sample_form(), role, pattern)

    result = close_layer(hypothesis, pattern, mc)

    assert result.judgment == ClosureJudgment.HYPOTHESIS
    assert result.mc_satisfied is False


def test_zero_when_domain_fails_or_fatal_barrier_exists() -> None:
    pattern = _sample_pattern()
    mc = _sample_mc()

    wrong_layer_form = FormState(
        form_id="form.token.1",
        layer="token",
        symbols=("كتب",),
        invariants=("identity",),
        source_refs=("SRC-1",),
    )
    role = RoleState(
        role_id="role.token.1",
        layer="token",
        role_type="class",
        features={"features": {"wordclass": "noun"}},
        rank="HYPOTHESIS",
        evidence_refs=("EV-1",),
    )
    hypothesis = compose_form_role(wrong_layer_form, role, pattern)
    result_domain = close_layer(hypothesis, pattern, mc)

    assert result_domain.judgment == ClosureJudgment.ZERO

    role_2 = RoleState(
        role_id="role.lexeme.3",
        layer="lexeme",
        role_type="class",
        features={"features": {"wordclass": "noun"}},
        rank="HYPOTHESIS",
        evidence_refs=("EV-1",),
    )
    hypothesis_2 = compose_form_role(_sample_form(), role_2, pattern)
    hypothesis_2 = replace(
        hypothesis_2,
        residuals=(*hypothesis_2.residuals, "residual_erasure"),
    )
    result_fatal = close_layer(hypothesis_2, pattern, mc)
    assert result_fatal.judgment == ClosureJudgment.ZERO


def test_public_judgment_triad_is_preserved() -> None:
    assert {item.value for item in ClosureJudgment} == {"zero", "hypothesis", "certificate"}
