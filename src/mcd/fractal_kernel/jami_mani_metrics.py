from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class JamiManiReport:
    jami_score: float = 0.0
    mani_score: float = 0.0
    coverage_score: float = 0.0
    exclusion_score: float = 0.0
    overgeneration_rate: float = 0.0
    undergeneration_rate: float = 0.0
    false_acceptance_rate: float = 0.0
    false_rejection_rate: float = 0.0
    blocking_invariant_coverage: float = 0.0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "jami_score": self.jami_score,
            "mani_score": self.mani_score,
            "coverage_score": self.coverage_score,
            "exclusion_score": self.exclusion_score,
            "overgeneration_rate": self.overgeneration_rate,
            "undergeneration_rate": self.undergeneration_rate,
            "false_acceptance_rate": self.false_acceptance_rate,
            "false_rejection_rate": self.false_rejection_rate,
            "blocking_invariant_coverage": self.blocking_invariant_coverage,
            "notes": self.notes,
        }


class JamiManiCalculator:
    """Calculate Jami (coverage) and Mani (exclusion) scores for a layer."""

    def calculate(self,
                  required_cases: list[str],
                  covered_cases: list[str],
                  forbidden_cases: list[str],
                  rejected_cases: list[str],
                  false_acceptances: int = 0,
                  false_rejections: int = 0,
                  blocking_invariants: list[str] = None,
                  covered_invariants: list[str] = None) -> JamiManiReport:
        blocking_invariants = blocking_invariants or []
        covered_invariants = covered_invariants or []

        n_required = len(required_cases)
        n_covered = len([c for c in covered_cases if c in required_cases])
        n_forbidden = len(forbidden_cases)
        n_rejected = len([c for c in rejected_cases if c in forbidden_cases])
        n_inv = len(blocking_invariants)
        n_inv_covered = len([i for i in covered_invariants if i in blocking_invariants])

        jami_score = n_covered / n_required if n_required > 0 else 1.0
        mani_score = n_rejected / n_forbidden if n_forbidden > 0 else 1.0
        coverage_score = jami_score
        exclusion_score = mani_score
        total_cases = n_required + n_forbidden
        overgeneration_rate = false_acceptances / total_cases if total_cases > 0 else 0.0
        undergeneration_rate = false_rejections / total_cases if total_cases > 0 else 0.0
        false_acceptance_rate = false_acceptances / n_forbidden if n_forbidden > 0 else 0.0
        false_rejection_rate = false_rejections / n_required if n_required > 0 else 0.0
        blocking_inv_coverage = n_inv_covered / n_inv if n_inv > 0 else 1.0

        notes = []
        if jami_score < 0.9:
            notes.append(f"Low jami score ({jami_score:.2f}): many required cases not covered")
        if mani_score < 0.9:
            notes.append(f"Low mani score ({mani_score:.2f}): many forbidden cases not blocked")

        return JamiManiReport(
            jami_score=round(jami_score, 4),
            mani_score=round(mani_score, 4),
            coverage_score=round(coverage_score, 4),
            exclusion_score=round(exclusion_score, 4),
            overgeneration_rate=round(overgeneration_rate, 4),
            undergeneration_rate=round(undergeneration_rate, 4),
            false_acceptance_rate=round(false_acceptance_rate, 4),
            false_rejection_rate=round(false_rejection_rate, 4),
            blocking_invariant_coverage=round(blocking_inv_coverage, 4),
            notes=notes,
        )
