from __future__ import annotations

from pathlib import Path

from mcd.evaluation.fractal_benchmark_dataset import iter_all_cases
from mcd.knowledge.golden_prior_registry import (
    CertaintyLevel,
    DEFAULT_GOLDEN_PRIOR_DIR,
    PriorRegistry,
    evaluate_case_against_priors,
    load_golden_prior_registry,
    load_prior_rules_file,
    validate_prior_rule,
)


def _find_case(case_id: str) -> dict[str, object]:
    return next(case for case in iter_all_cases() if case["id"] == case_id)


def test_all_prior_fixture_files_load():
    expected_files = {
        "mathematics.json",
        "programming_governance.json",
        "physics.json",
        "chemistry.json",
        "general_language.json",
        "arabic_vocalized.json",
        "arabic_morphology_syntax.json",
    }
    fixture_files = {path.name for path in DEFAULT_GOLDEN_PRIOR_DIR.glob("*.json")}
    assert expected_files.issubset(fixture_files)

    for name in expected_files:
        loaded = load_prior_rules_file(DEFAULT_GOLDEN_PRIOR_DIR / name)
        assert loaded


def test_every_prior_rule_has_required_fields_and_valid_certainty_level():
    registry = load_golden_prior_registry()
    assert registry.rules
    assert registry.validate() == {}

    for rule in registry.rules:
        validation = validate_prior_rule(rule)
        assert validation.valid
        assert rule.rule_id
        assert rule.domain
        assert rule.layer
        assert rule.claim
        assert isinstance(rule.certainty_level, CertaintyLevel)
        assert rule.certificate_blockers


def test_forbidden_transitions_include_required_certificate_guards():
    registry = load_golden_prior_registry()

    prog = next(rule for rule in registry.rules if rule.rule_id == "prog-ci-merge-not-certificate")
    physics = next(rule for rule in registry.rules if rule.rule_id == "physics-smoke-fire-conditional")
    math = next(rule for rule in registry.rules if rule.rule_id == "math-euclidean-triangle-sum")

    assert "score_only_certificate" in set(prog.forbidden_transitions)
    assert "CI_PASS_TO_CERTIFICATE" in set(prog.forbidden_transitions)
    assert "SMOKE_ONLY_TO_FIRE_CERTIFICATE" in set(physics.forbidden_transitions)
    assert "TRIANGLE_WITHOUT_GEOMETRY_SCOPE_TO_CERTIFICATE" in set(math.forbidden_transitions)


def test_triangle_without_geometry_scope_cannot_become_certificate():
    registry = load_golden_prior_registry()
    case = _find_case("math-triangle-001")
    rules = registry.find_case_rules(case)

    prior_missing, prior_blocking, _prior_rule_ids, tags = evaluate_case_against_priors(case, rules)

    assert any(tag.startswith("prior_blocking:") for tag in tags)
    assert "triangle_missing_geometry_scope" in prior_blocking
    assert prior_missing


def test_floating_haraka_rule_declares_local_zero_in_path_residual():
    registry = load_golden_prior_registry()
    rule = next(rule for rule in registry.rules if rule.rule_id == "ar-vocalized-haraka-anchor")
    residual_ids = {residual.residual_id for residual in rule.expected_residuals}
    local_only_ids = {residual.residual_id for residual in rule.expected_residuals if residual.local_only}

    assert "floating_haraka_local_zero_in_path" in residual_ids
    assert "floating_haraka_local_zero_in_path" in local_only_ids


def test_local_path_failure_preserves_remaining_paths_contract():
    case = _find_case("arabic-zero-in-path-local-004")
    assert case["local_zero_in_path"] is True
    assert case["global_zero"] is False
    assert case["remaining_paths"]

    registry = load_golden_prior_registry()
    rules = registry.find_case_rules(case)
    assert any(rule.rule_id == "ar-morph-syntax-path-preservation" for rule in rules)


def test_registry_find_rules_by_domain_layer_and_claim():
    registry = load_golden_prior_registry()

    results = registry.find_rules(
        domain="coding_pr_governance",
        layer="governance_gate",
        claim="CI_PASS and MERGED alone do not imply CERTIFICATE",
    )
    assert results
    assert results[0].rule_id == "prog-ci-merge-not-certificate"


def test_empty_registry_is_valid_structure():
    registry = PriorRegistry()
    assert registry.validate() == {}
    assert registry.find_rules(domain="mathematics") == []
