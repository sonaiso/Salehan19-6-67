from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FoldRecord:
    fold_id: str
    input_unit_ids: list[str]
    folded_unit_id: str
    preserved_relations: list[str] = field(default_factory=list)
    preserved_trace_refs: list[str] = field(default_factory=list)
    preserved_evidence_needs: list[str] = field(default_factory=list)
    preserved_certainty_caps: list[str] = field(default_factory=list)
    lost_details: list[str] = field(default_factory=list)
    residuals: list[str] = field(default_factory=list)


@dataclass
class UnfoldRecord:
    unfold_id: str
    folded_unit_id: str
    output_unit_ids: list[str]
    restored_relations: list[str] = field(default_factory=list)
    restored_trace_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class RefoldLawResult:
    passed: bool
    stability_score: float
    lost_trace: list[str] = field(default_factory=list)
    lost_evidence_need: list[str] = field(default_factory=list)
    lost_residuals: list[str] = field(default_factory=list)
    certainty_increased: bool = False
    violations: list[str] = field(default_factory=list)


class FoldUnfoldRefoldLaws:
    TARGET_STABILITY = 0.95

    @classmethod
    def evaluate(
        cls,
        original: FoldRecord,
        unfolded: UnfoldRecord,
        refolded: FoldRecord,
        *,
        certainty_before: float,
        certainty_after: float,
    ) -> RefoldLawResult:
        lost_trace = [t for t in original.preserved_trace_refs if t not in refolded.preserved_trace_refs]
        lost_evidence_need = [
            e for e in original.preserved_evidence_needs if e not in refolded.preserved_evidence_needs
        ]
        lost_residuals = [r for r in original.residuals if r not in refolded.residuals]
        certainty_increased = certainty_after > certainty_before

        violations: list[str] = []
        if certainty_increased:
            violations.append("Fold does not increase certainty")
        if lost_evidence_need:
            violations.append("Fold must preserve evidence_need")
        if lost_residuals:
            violations.append("Fold must preserve residuals")

        for rel in original.preserved_relations:
            if rel not in unfolded.restored_relations:
                violations.append("Unfold must restore key relations")
                break

        total_checks = 5
        failed_checks = int(bool(lost_trace)) + int(bool(lost_evidence_need)) + int(bool(lost_residuals)) + int(certainty_increased) + int(any("restore" in v.lower() for v in violations))
        stability = max(0.0, 1.0 - (failed_checks / total_checks))

        passed = stability >= cls.TARGET_STABILITY and len(violations) == 0
        return RefoldLawResult(
            passed=passed,
            stability_score=round(stability, 4),
            lost_trace=lost_trace,
            lost_evidence_need=lost_evidence_need,
            lost_residuals=lost_residuals,
            certainty_increased=certainty_increased,
            violations=violations,
        )
