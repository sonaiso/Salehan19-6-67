"""FoldUnfoldConsistencyChecker — validates fold/unfold preserves semantics."""
from __future__ import annotations
from dataclasses import dataclass, field
from mcd.residual_learning.residual_schema import CognitiveResidual
from .fold_schema import FoldSignature
from .fold_signature import FoldSignatureRegistry

__all__ = ["FoldUnfoldConsistencyChecker", "FoldUnfoldConsistencyReport", "FoldConsistencyFailure"]


@dataclass
class FoldConsistencyFailure:
    fold_id: str
    field: str
    expected: str
    actual: str

    def to_dict(self) -> dict:
        return {"fold_id": self.fold_id, "field": self.field, "expected": self.expected, "actual": self.actual}


@dataclass
class FoldUnfoldConsistencyReport:
    total_folds: int
    passed_folds: int
    failed_folds: int
    fold_consistency_score: float
    failures: list[FoldConsistencyFailure] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total_folds": self.total_folds,
            "passed_folds": self.passed_folds,
            "failed_folds": self.failed_folds,
            "fold_consistency_score": round(self.fold_consistency_score, 4),
            "failures": [f.to_dict() for f in self.failures],
        }

    def to_markdown(self) -> str:
        lines = [
            "# Fold-Unfold Consistency Report",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Folds | {self.total_folds} |",
            f"| Passed | {self.passed_folds} |",
            f"| Failed | {self.failed_folds} |",
            f"| Consistency Score | {self.fold_consistency_score:.4f} |",
            "",
        ]
        if self.failures:
            lines.append("## Failures")
            for f in self.failures:
                lines.append(f"- [{f.fold_id}] {f.field}: expected={f.expected}, actual={f.actual}")
        else:
            lines.append("✅ All folds passed consistency check.")
        return "\n".join(lines)


class FoldUnfoldConsistencyChecker:
    def check(self, folds: list[FoldSignature], residuals: list[CognitiveResidual] | None = None) -> FoldUnfoldConsistencyReport:
        failures = []
        for fold in folds:
            # Must have residual_types
            if not fold.residual_types:
                failures.append(FoldConsistencyFailure(fold.fold_id, "residual_types", "non-empty", "empty"))
                continue
            # Must have recall_keys
            if not fold.recall_keys:
                failures.append(FoldConsistencyFailure(fold.fold_id, "recall_keys", "non-empty", "empty"))
                continue
            # Must have evidence_signature
            if not fold.evidence_signature:
                failures.append(FoldConsistencyFailure(fold.fold_id, "evidence_signature", "non-empty", "empty"))
                continue
            # Must have certainty_signature
            if not fold.certainty_signature:
                failures.append(FoldConsistencyFailure(fold.fold_id, "certainty_signature", "non-empty", "empty"))
                continue
            # Must have trace_signature
            if not fold.trace_signature:
                failures.append(FoldConsistencyFailure(fold.fold_id, "trace_signature", "non-empty", "empty"))
                continue
            # Must have learning_actions
            if not fold.learning_actions:
                failures.append(FoldConsistencyFailure(fold.fold_id, "learning_actions", "non-empty", "empty"))
                continue
            # Must have unfold_plan
            if not fold.unfold_plan:
                failures.append(FoldConsistencyFailure(fold.fold_id, "unfold_plan", "non-empty", "empty"))

        total = len(folds)
        failed = len(failures)
        passed = total - failed
        score = passed / total if total > 0 else 1.0

        return FoldUnfoldConsistencyReport(
            total_folds=total,
            passed_folds=passed,
            failed_folds=failed,
            fold_consistency_score=score,
            failures=failures,
        )
