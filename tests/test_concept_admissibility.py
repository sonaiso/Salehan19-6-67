from __future__ import annotations

import json
from pathlib import Path

from mcd.knowledge.concept_admissibility import NewConceptClaim, evaluate_concept_against_golden_rules
from mcd.knowledge.golden_prior_registry import load_golden_prior_registry


CASES_PATH = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "golden_prior_knowledge"
    / "concept_admissibility_cases.json"
)


def _load_case(case_id: str) -> dict[str, object]:
    rows = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    return next(row for row in rows if row["concept_id"] == case_id)


def _to_claim(row: dict[str, object]) -> NewConceptClaim:
    return NewConceptClaim(
        concept_id=str(row["concept_id"]),
        claim=str(row["claim"]),
        domain=str(row["domain"]),
        layer=str(row["layer"]),
        required_evidence=tuple(row.get("required_evidence", [])),
        proposed_decision_level=str(row.get("proposed_decision_level", "HYPOTHESIS")),
        residuals=tuple(row.get("residuals", [])),
        trace={k: str(v) for k, v in dict(row.get("trace", {})).items()},
    )


def test_artificial_consciousness_certificate_claim_is_blocked():
    registry = load_golden_prior_registry()
    claim = _to_claim(_load_case("concept-artificial-consciousness-certificate"))

    result = evaluate_concept_against_golden_rules(claim, registry)
    assert result.decision_level == "HYPOTHESIS"
    assert result.certificate_blocked is True


def test_trained_fgn_claim_is_blocked_without_training_proof_evidence():
    registry = load_golden_prior_registry()
    claim = NewConceptClaim(
        concept_id="concept-trained-fgn",
        claim="FGN is trained and globally certified",
        domain="coding_pr_governance",
        layer="governance_gate",
        required_evidence=("ci_pass",),
        proposed_decision_level="CERTIFICATE",
        residuals=("score_only_certificate",),
        trace={
            "input": "training claim",
            "candidate": "certificate",
            "evidence": "ci pass only",
            "decision_path": "claim->blocked",
        },
    )

    result = evaluate_concept_against_golden_rules(claim, registry)
    assert result.decision_level == "HYPOTHESIS"
    assert result.certificate_blocked is True


def test_fractal_embedding_conceptual_foundation_stays_hypothesis_not_certificate():
    registry = load_golden_prior_registry()
    claim = _to_claim(_load_case("concept-fractal-embedding-foundation"))

    result = evaluate_concept_against_golden_rules(claim, registry)
    assert result.decision_level == "HYPOTHESIS"


def test_linguistic_metaphor_can_remain_strong_path_without_certificate():
    registry = load_golden_prior_registry()
    claim = _to_claim(_load_case("concept-arabic-metaphor-strong"))

    result = evaluate_concept_against_golden_rules(claim, registry)
    assert result.decision_level == "HYPOTHESIS"
    assert result.certificate_blocked is False


def test_euclidean_scope_with_proof_can_reach_certificate_when_requirements_satisfied():
    registry = load_golden_prior_registry()
    claim = _to_claim(_load_case("concept-euclidean-triangle-certificate"))

    result = evaluate_concept_against_golden_rules(claim, registry)
    assert result.decision_level == "CERTIFICATE"


def test_missing_golden_rule_emits_coverage_gap_residual():
    registry = load_golden_prior_registry()
    claim = NewConceptClaim(
        concept_id="concept-unknown-domain",
        claim="Unknown domain claim",
        domain="unknown_domain",
        layer="governance_gate",
        required_evidence=(),
        proposed_decision_level="CERTIFICATE",
        residuals=(),
        trace={
            "input": "x",
            "candidate": "certificate",
            "evidence": "none",
            "decision_path": "none",
        },
    )

    result = evaluate_concept_against_golden_rules(claim, registry)
    assert "golden_rule_coverage_gap" in result.residuals
