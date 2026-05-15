from __future__ import annotations

from mcd.knowledge.golden_prior_registry import (
    CertaintyLevel,
    CertificateBlocker,
    EvidenceRequirement,
    GoldenRuleMaturityLevel,
    PriorRule,
    PriorScope,
    ResidualExpectation,
    ReverseTraceRequirement,
    load_golden_prior_registry,
    qualify_golden_rule,
)


def _base_rule() -> PriorRule:
    return PriorRule(
        rule_id="rule-1",
        domain="mathematics",
        layer="claim_to_evidence",
        claim="Formal rule",
        scope=PriorScope.FORMAL,
        certainty_level=CertaintyLevel.FORMAL_CERTAINTY,
        required_evidence=EvidenceRequirement(required_items=("proof",)),
        certificate_blockers=(
            CertificateBlocker(
                blocker_id="missing-proof",
                description="Missing proof blocks certificate",
                match_any=("missing_proof",),
            ),
        ),
        expected_residuals=(
            ResidualExpectation(
                residual_id="missing_proof",
                description="proof residual",
                blocks_certificate=True,
            ),
        ),
        forbidden_transitions=("certificate_without_proof_object",),
        reverse_trace_requirements=ReverseTraceRequirement(required=True),
        test_refs=("tests/test_golden_rule_qualification.py",),
    )


def test_rule_without_scope_cannot_be_golden_rule():
    rule = _base_rule().__class__(**{**_base_rule().__dict__, "scope_complete": False})
    result = qualify_golden_rule(rule)
    assert result.maturity_level != GoldenRuleMaturityLevel.GOLDEN_RULE
    assert "scope" in result.missing_requirements


def test_rule_without_certificate_blockers_cannot_govern_certificate():
    rule = _base_rule().__class__(**{**_base_rule().__dict__, "certificate_blockers": tuple()})
    result = qualify_golden_rule(rule)
    assert result.can_block_certificate is False
    assert "certificate_blockers" in result.missing_requirements


def test_rule_without_residual_expectations_is_not_full_uncertainty_governance():
    rule = _base_rule().__class__(**{**_base_rule().__dict__, "expected_residuals": tuple()})
    result = qualify_golden_rule(rule)
    assert "expected_residuals" in result.missing_requirements


def test_rule_without_tests_cannot_reach_golden_rule():
    rule = _base_rule().__class__(**{**_base_rule().__dict__, "test_refs": tuple(), "examples": tuple(), "case_refs": tuple()})
    result = qualify_golden_rule(rule)
    assert result.maturity_level != GoldenRuleMaturityLevel.GOLDEN_RULE
    assert "test_cases" in result.missing_requirements


def test_empirical_rules_require_explicit_scope_conditions():
    rule = _base_rule().__class__(
        **{
            **_base_rule().__dict__,
            "domain": "physical_reality",
            "certainty_level": CertaintyLevel.EMPIRICAL_UNDER_CONDITIONS,
            "scope_complete": False,
        }
    )
    result = qualify_golden_rule(rule)
    assert "scope" in result.missing_requirements


def test_fixture_rules_receive_maturity_and_have_candidates_or_golden():
    registry = load_golden_prior_registry()
    maturities = [qualify_golden_rule(rule).maturity_level for rule in registry.rules]
    assert all(isinstance(level, GoldenRuleMaturityLevel) for level in maturities)
    assert any(
        level in {GoldenRuleMaturityLevel.GOLDEN_RULE_CANDIDATE, GoldenRuleMaturityLevel.GOLDEN_RULE}
        for level in maturities
    )
