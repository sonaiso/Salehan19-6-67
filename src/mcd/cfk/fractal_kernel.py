"""Fractal Kernel K — the unifying kernel that maps all three coordinate systems
to a comparable space.

The three transforms produce projections in different coordinates:
    S(x) → statistical_coordinate    (احتمالي)
    A(x) → arabic_coordinate         (دلالي)
    E(x) → epistemic_coordinate      (برهاني)

The kernel K makes them comparable:
    K(S(x)) ~ K(A(x)) ~ K(E(x))

The kernel does NOT collapse the three into one number — it produces a
KernelResult that contains all three projections alongside a unified judgment
and a cognitive residual score.

Key law:
    statistical_confidence alone ≠ epistemic_certainty
    K enforces: if E.evidence_state == "missing", final judgment ≤ Hypothesis
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from mcd.cfk.cfk_schema import (
    KernelProjection,
    JudgmentStatus,
    CoordinateType,
)


# ---------------------------------------------------------------------------
# Kernel Result
# ---------------------------------------------------------------------------

@dataclass
class KernelResult:
    """The output of applying kernel K to three projections."""

    result_id: str
    text: str

    statistical: KernelProjection
    arabic: KernelProjection
    epistemic: KernelProjection

    # Unified judgment derived by the kernel
    kernel_judgment: str = JudgmentStatus.HYPOTHESIS.value
    kernel_score: float = 0.0     # weighted combination

    # Per-dimension comparable scores (K(system(x)))
    k_statistical: float = 0.0
    k_arabic: float = 0.0
    k_epistemic: float = 0.0

    # Cognitive residual from the kernel (statistical – epistemic gap)
    cognitive_residual: float = 0.0
    residual_type: str = "none"

    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "result_id": self.result_id,
            "text": self.text,
            "statistical": self.statistical.to_dict(),
            "arabic": self.arabic.to_dict(),
            "epistemic": self.epistemic.to_dict(),
            "kernel_judgment": self.kernel_judgment,
            "kernel_score": round(self.kernel_score, 4),
            "k_statistical": round(self.k_statistical, 4),
            "k_arabic": round(self.k_arabic, 4),
            "k_epistemic": round(self.k_epistemic, 4),
            "cognitive_residual": round(self.cognitive_residual, 4),
            "residual_type": self.residual_type,
            "notes": self.notes,
        }


# ---------------------------------------------------------------------------
# Kernel weights (can be adjusted)
# ---------------------------------------------------------------------------

_WEIGHTS = {
    CoordinateType.STATISTICAL.value: 0.25,
    CoordinateType.ARABIC.value:      0.30,
    CoordinateType.EPISTEMIC.value:   0.45,
}


class FractalKernel:
    """Applies kernel K to three projections and produces a KernelResult.

    The kernel enforces conservation laws:
    1. If epistemic evidence is missing: cap judgment at Hypothesis.
    2. If statistical confidence is high but evidence is absent: mark as unsupported_generalization.
    3. Emphasis ≠ Evidence (emphasis_operator cannot raise epistemic certainty).
    """

    def apply(
        self,
        text: str,
        statistical: KernelProjection,
        arabic: KernelProjection,
        epistemic: KernelProjection,
    ) -> KernelResult:

        ks = statistical.comparable_score * _WEIGHTS[CoordinateType.STATISTICAL.value]
        ka = arabic.comparable_score     * _WEIGHTS[CoordinateType.ARABIC.value]
        ke = epistemic.comparable_score  * _WEIGHTS[CoordinateType.EPISTEMIC.value]

        kernel_score = ks + ka + ke

        # Extract key signals
        evidence_state   = epistemic.unit.E.evidence_state
        epistemic_score  = epistemic.comparable_score
        stat_score       = statistical.comparable_score
        ling_force       = arabic.unit.C.linguistic_force
        logical_function = arabic.unit.O.logical_function

        # Cognitive residual = gap between statistical plausibility and epistemic support
        cognitive_residual = max(0.0, stat_score - epistemic_score)

        # --- Kernel judgment rules (enforce conservation laws) ---
        notes: list[str] = []

        # Rule 1: evidence gate — missing evidence caps at Hypothesis / Suspend
        if evidence_state == "missing":
            if stat_score >= 0.7:
                notes.append(
                    "high_statistical_confidence_without_evidence → unsupported_generalization"
                )
                residual_type = "unsupported_generalization_residual"
                kernel_judgment = JudgmentStatus.SUSPEND.value
            else:
                residual_type = "evidence_gap_residual"
                kernel_judgment = JudgmentStatus.HYPOTHESIS.value

        elif evidence_state == "partial":
            residual_type = "partial_evidence_residual"
            if epistemic_score >= 0.60:
                kernel_judgment = JudgmentStatus.HYPOTHESIS.value
            else:
                kernel_judgment = JudgmentStatus.SUSPEND.value

        else:
            # evidence present
            residual_type = "none"
            if epistemic_score >= 0.75:
                kernel_judgment = JudgmentStatus.CERTIFICATE.value
            elif epistemic_score >= 0.55:
                kernel_judgment = JudgmentStatus.HYPOTHESIS.value
            else:
                kernel_judgment = JudgmentStatus.SUSPEND.value

        # Rule 2: emphasis ≠ proof
        if ling_force == "emphasis" and kernel_judgment == JudgmentStatus.CERTIFICATE.value:
            kernel_judgment = JudgmentStatus.HYPOTHESIS.value
            notes.append("emphasis_operator ≠ evidence — certificate downgraded to hypothesis")

        # Rule 3: universal quantifier without evidence
        if logical_function == "universal_quantifier" and evidence_state == "missing":
            kernel_judgment = JudgmentStatus.SUSPEND.value
            residual_type = "unsupported_generalization_residual"
            notes.append("universal_quantifier + no_evidence → suspend")

        # Rule 4: fake evidence or zero judgment
        if epistemic.judgment == JudgmentStatus.ZERO.value:
            kernel_judgment = JudgmentStatus.ZERO.value
            residual_type = "fake_evidence_residual"
            notes.append("fake_evidence_detected → kernel_judgment=zero")

        notes.append(
            f"K: stat={round(stat_score, 2)} arabic={round(arabic.comparable_score, 2)} "
            f"epistemic={round(epistemic_score, 2)} → {kernel_judgment}"
        )

        return KernelResult(
            result_id=f"KR-{uuid.uuid4().hex[:10]}",
            text=text,
            statistical=statistical,
            arabic=arabic,
            epistemic=epistemic,
            kernel_judgment=kernel_judgment,
            kernel_score=kernel_score,
            k_statistical=ks,
            k_arabic=ka,
            k_epistemic=ke,
            cognitive_residual=cognitive_residual,
            residual_type=residual_type,
            notes=notes,
        )
