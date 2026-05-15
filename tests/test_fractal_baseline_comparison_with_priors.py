from __future__ import annotations

from mcd.evaluation.fractal_baseline_comparison import run_fractal_baseline_comparison
from mcd.evaluation.fractal_benchmark_dataset import benchmark_dataset_summary
from mcd.knowledge.golden_prior_registry import (
    CertaintyLevel,
    CertificateBlocker,
    EvidenceRequirement,
    PriorRegistry,
    PriorRule,
    PriorScope,
    ResidualExpectation,
    ReverseTraceRequirement,
    load_golden_prior_registry,
)



def _baseline(report: dict[str, object], name: str) -> dict[str, object]:
    return report["baselines"][name]



def _case(report: dict[str, object], case_id: str) -> dict[str, object]:
    rows = _baseline(report, "GovernedProtocolBaseline")["cases"]
    return next(row for row in rows if row["case_id"] == case_id)



def test_governed_baseline_runs_with_and_without_prior_registry():
    without_priors = run_fractal_baseline_comparison()
    with_priors = run_fractal_baseline_comparison(prior_registry=load_golden_prior_registry())

    assert without_priors["deterministic"] is True
    assert with_priors["deterministic"] is True



def test_governed_baseline_uses_prior_rules_and_records_rule_ids():
    report = run_fractal_baseline_comparison(prior_registry=load_golden_prior_registry())
    case = _case(report, "coding-ci-pass-001")

    assert case["prior_rule_ids"]
    assert "prog-ci-merge-not-certificate" in case["prior_rule_ids"]



def test_prior_rule_blockers_prevent_certificate():
    report = run_fractal_baseline_comparison(prior_registry=load_golden_prior_registry())
    case = _case(report, "coding-ci-pass-001")

    assert case["predicted_decision"] != "CERTIFICATE"
    assert "prior_blocking:ci_pass_to_certificate" in set(case["error_tags"])



def test_missing_prior_rule_does_not_silently_grant_certificate():
    restrictive_registry = PriorRegistry(
        rules=(
            PriorRule(
                rule_id="strict-math-proof",
                domain="mathematics",
                layer="governance_gate",
                claim="Strict proof obligations for candidate/certificate",
                scope=PriorScope.FORMAL,
                certainty_level=CertaintyLevel.FORMAL_CERTAINTY,
                required_evidence=EvidenceRequirement(
                    required_items=(
                        "euclidean_axioms",
                        "valid_proof_path",
                        "missing_nonexistent_evidence",
                    ),
                    all_required=True,
                ),
                certificate_blockers=(
                    CertificateBlocker(
                        blocker_id="strict_missing_proof_evidence",
                        description="Missing strict evidence blocks ascent",
                        match_any=("missing_formal_proof_obligation",),
                    ),
                ),
                expected_residuals=(
                    ResidualExpectation(
                        residual_id="missing_formal_proof_obligation",
                        description="Formal proof obligation residual",
                        blocks_certificate=True,
                    ),
                ),
                forbidden_transitions=("certificate_without_proof_object",),
                reverse_trace_requirements=ReverseTraceRequirement(required=True),
                case_refs=("math-triangle-euclidean-002",),
            ),
        )
    )

    report = run_fractal_baseline_comparison(prior_registry=restrictive_registry)
    case = _case(report, "math-triangle-euclidean-002")

    assert case["predicted_decision"] == "HYPOTHESIS"
    assert any(tag.startswith("prior_missing:") for tag in case["error_tags"])



def test_prior_residuals_are_preserved_in_case_level_taxonomy():
    report = run_fractal_baseline_comparison(prior_registry=load_golden_prior_registry())
    governed_cases = _baseline(report, "GovernedProtocolBaseline")["cases"]

    assert any(
        any(tag.startswith("prior_missing:") or tag.startswith("prior_blocking:") for tag in row["error_tags"])
        for row in governed_cases
    )



def test_theorem_status_and_non_goals_remain_unchanged_with_priors():
    report = run_fractal_baseline_comparison(prior_registry=load_golden_prior_registry())
    summary = benchmark_dataset_summary()

    assert report["theorem_status"] == "STRONG_HYPOTHESIS"
    assert summary["theorem_status"] == "STRONG_HYPOTHESIS"
    assert report["trained_model_used"] is False
    assert report["external_models_used"] == []
