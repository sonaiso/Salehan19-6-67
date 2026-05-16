from __future__ import annotations

from dataclasses import dataclass, field

from mcd.math_governance.dataset_math_annotator import DatasetMathAnnotator
from mcd.math_governance.fold_unfold_laws import FoldRecord, FoldUnfoldRefoldLaws, UnfoldRecord
from mcd.math_governance.fractal_unit_governance import GovernedFractalUnit
from mcd.math_governance.jami_mani_calculator import JamiManiCalculator, JamiManiDefinition
from mcd.math_governance.level_morphism_registry import LevelMorphismRegistry
from mcd.math_governance.operator_algebra import CognitiveOperator, OperatorAlgebra
from mcd.math_governance.text_ascent_chain import validate_text_ascent_chain


@dataclass
class MathematicalGovernanceReport:
    passed: bool
    governance_score: float
    morphism_score: float
    operator_law_score: float
    fold_stability_score: float
    jami_score: float
    mani_score: float
    dataset_annotation_score: float
    evidence_monotonicity_score: float
    residual_preservation_score: float
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "governance_score": self.governance_score,
            "morphism_score": self.morphism_score,
            "operator_law_score": self.operator_law_score,
            "fold_stability_score": self.fold_stability_score,
            "jami_score": self.jami_score,
            "mani_score": self.mani_score,
            "dataset_annotation_score": self.dataset_annotation_score,
            "evidence_monotonicity_score": self.evidence_monotonicity_score,
            "residual_preservation_score": self.residual_preservation_score,
            "violations": self.violations,
            "warnings": self.warnings,
        }


class MathematicalGovernanceGate:
    TARGET = 0.97

    def __init__(self) -> None:
        self._morphisms = LevelMorphismRegistry()
        self._algebra = OperatorAlgebra()
        self._fold_laws = FoldUnfoldRefoldLaws()
        self._jami_mani = JamiManiCalculator()
        self._annotator = DatasetMathAnnotator()

    def validate_unit_chain(self, units: list[GovernedFractalUnit]) -> tuple[bool, list[str]]:
        violations = []
        for i, unit in enumerate(units):
            violations.extend(unit.validate(final_pipeline=(i < len(units) - 1)))
            if i > 0 and units[i - 1].unit_id not in unit.pre_unit_ids:
                violations.append(f"{unit.unit_id}: missing pre link to previous unit")
            if i < len(units) - 1 and units[i + 1].unit_id not in unit.post_unit_ids:
                violations.append(f"{unit.unit_id}: missing post link to next unit")
        ascent = validate_text_ascent_chain(units)
        violations.extend(ascent.violations)
        return len(violations) == 0, violations

    def validate_morphisms(self, units: list[GovernedFractalUnit]) -> tuple[float, list[str]]:
        violations = []
        if len(units) < 2:
            return 1.0, []
        passed = 0
        for i in range(len(units) - 1):
            ok, msgs = self._morphisms.validate_transition(units[i].level_id, units[i + 1].level_id)
            if ok:
                passed += 1
            violations.extend(msgs)
        return round(passed / (len(units) - 1), 4), violations

    def validate_operator_laws(self, operators: list[CognitiveOperator]) -> tuple[float, list[str]]:
        ok, violations = self._algebra.validate_laws(operators)
        return (1.0 if ok else 0.0), violations

    def validate_fold_laws(self, folds: list[tuple[FoldRecord, UnfoldRecord, FoldRecord]]) -> tuple[float, list[str]]:
        if not folds:
            return 1.0, []
        scores = []
        violations = []
        for original, unfolded, refolded in folds:
            result = self._fold_laws.evaluate(
                original,
                unfolded,
                refolded,
                certainty_before=0.4,
                certainty_after=0.4,
            )
            scores.append(result.stability_score)
            violations.extend(result.violations)
        return round(sum(scores) / len(scores), 4), violations

    def validate_jami_mani(self, definitions: list[JamiManiDefinition]) -> tuple[float, float, list[str]]:
        if not definitions:
            return 1.0, 1.0, []
        jami_scores = []
        mani_scores = []
        warnings = []
        for d in definitions:
            report = self._jami_mani.calculate(d, d.positive_cases, d.negative_cases)
            jami_scores.append(report.jami_score)
            mani_scores.append(report.mani_score)
            warnings.extend(report.boundary_warnings)
        return round(sum(jami_scores) / len(jami_scores), 4), round(sum(mani_scores) / len(mani_scores), 4), warnings

    def validate_dataset_annotations(self, path: str) -> tuple[float, list[str]]:
        report = self._annotator.run(path, write=False)
        warnings = []
        if report.dataset_annotation_score < 1.0:
            warnings.append("dataset annotations are incomplete")
        return report.dataset_annotation_score, warnings

    @staticmethod
    def validate_no_certificate_without_governance(proof: dict) -> tuple[bool, list[str]]:
        violations = []
        if proof.get("judgment") == "certificate":
            if not proof.get("governance_passed", False):
                violations.append("certificate requires governance gate pass")
            if not proof.get("proof_object_ref"):
                violations.append("certificate requires proof object reference")
            if not proof.get("reverse_trace_ref"):
                violations.append("certificate requires reverse trace reference")
        return len(violations) == 0, violations

    def run(
        self,
        *,
        units: list[GovernedFractalUnit],
        operators: list[CognitiveOperator] | None = None,
        folds: list[tuple[FoldRecord, UnfoldRecord, FoldRecord]] | None = None,
        definitions: list[JamiManiDefinition] | None = None,
        dataset_path: str = "data/evaluation/ambiguity_ar.jsonl",
    ) -> MathematicalGovernanceReport:
        operators = operators or []
        folds = folds or []
        definitions = definitions or []

        violations: list[str] = []
        warnings: list[str] = []

        unit_ok, unit_violations = self.validate_unit_chain(units)
        violations.extend(unit_violations)

        morphism_score, morphism_violations = self.validate_morphisms(units)
        violations.extend(morphism_violations)

        operator_law_score, operator_violations = self.validate_operator_laws(operators)
        violations.extend(operator_violations)

        fold_stability_score, fold_violations = self.validate_fold_laws(folds)
        violations.extend(fold_violations)

        jami_score, mani_score, jami_warnings = self.validate_jami_mani(definitions)
        warnings.extend(jami_warnings)

        dataset_annotation_score, dataset_warnings = self.validate_dataset_annotations(dataset_path)
        warnings.extend(dataset_warnings)

        evidence_monotonicity_score = 1.0 if not any("certainty cannot increase" in v for v in violations) else 0.0
        residual_preservation_score = 1.0 if not any("residual" in v.lower() for v in violations) else 0.0

        governance_score = round(
            (
                morphism_score
                + operator_law_score
                + fold_stability_score
                + jami_score
                + mani_score
                + dataset_annotation_score
                + evidence_monotonicity_score
                + residual_preservation_score
                + (1.0 if unit_ok else 0.0)
            )
            / 9,
            4,
        )

        passed = governance_score >= self.TARGET and len(violations) == 0
        return MathematicalGovernanceReport(
            passed=passed,
            governance_score=governance_score,
            morphism_score=morphism_score,
            operator_law_score=operator_law_score,
            fold_stability_score=fold_stability_score,
            jami_score=jami_score,
            mani_score=mani_score,
            dataset_annotation_score=dataset_annotation_score,
            evidence_monotonicity_score=evidence_monotonicity_score,
            residual_preservation_score=residual_preservation_score,
            violations=violations,
            warnings=warnings,
        )
