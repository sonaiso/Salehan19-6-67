"""ProofObject — the final output of the Cognitive Fractal Kernel pipeline.

A ProofObject is one of four types:
  Certificate   — دليل مكتمل — يقين (evidence present, certainty ≥ 0.75)
  Hypothesis    — دعوى محتملة — انتظار (partial evidence or moderate certainty)
  Suspend       — دليل ناقص — تعليق (evidence missing, or rule violated)
  Zero          — باقٍ معرفي — خطأ بنيوي (fake evidence, conservation law broken)

The ProofObject carries:
  - the three projections (statistical, arabic, epistemic)
  - the kernel judgment
  - conservation check results
  - the cognitive residual (learning signal)
  - a full reverse trace
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from mcd.cfk.cfk_schema import JudgmentStatus
from mcd.cfk.fractal_kernel import KernelResult
from mcd.cfk.conservation_law import ConservationCheckResult


@dataclass
class ProofObject:
    """The formal output of the CFK pipeline for a single claim."""

    proof_id: str
    text: str

    # Final judgment
    judgment: str   # certificate|hypothesis|suspend|zero

    # Scores from each coordinate system
    statistical_confidence: float
    linguistic_force: str
    epistemic_certainty: float

    # Evidence
    evidence_state: str   # present|partial|missing

    # Conservation
    conservation: ConservationCheckResult

    # Residual
    cognitive_residual: float
    residual_type: str
    learning_signal: str  # reinforce|correct|suspend|ignore

    # Trace
    reverse_trace: list[str] = field(default_factory=list)

    # Full kernel result (optional — for detailed output)
    kernel_result: KernelResult | None = None

    def to_dict(self) -> dict:
        d: dict = {
            "proof_id": self.proof_id,
            "text": self.text,
            "judgment": self.judgment,
            "statistical_confidence": round(self.statistical_confidence, 4),
            "linguistic_force": self.linguistic_force,
            "epistemic_certainty": round(self.epistemic_certainty, 4),
            "evidence_state": self.evidence_state,
            "conservation": self.conservation.to_dict(),
            "cognitive_residual": round(self.cognitive_residual, 4),
            "residual_type": self.residual_type,
            "learning_signal": self.learning_signal,
            "reverse_trace": self.reverse_trace,
        }
        if self.kernel_result is not None:
            d["kernel_result"] = self.kernel_result.to_dict()
        return d


class ProofObjectBuilder:
    """Builds a ProofObject from a KernelResult and ConservationCheckResults."""

    def build(
        self,
        kernel_result: KernelResult,
        conservation_results: list[ConservationCheckResult],
    ) -> ProofObject:

        # Choose the primary conservation check (epistemic is most critical)
        primary_conservation = self._merge_conservation(conservation_results)

        # Determine final judgment
        judgment = kernel_result.kernel_judgment

        # Override: if any conservation law is blocking → Zero
        blocking = any(
            v.severity == "blocking"
            for v in primary_conservation.violations
        )
        if blocking:
            judgment = JudgmentStatus.ZERO.value

        # Learning signal
        signal_map = {
            JudgmentStatus.CERTIFICATE.value: "reinforce",
            JudgmentStatus.HYPOTHESIS.value:  "correct",
            JudgmentStatus.SUSPEND.value:     "suspend",
            JudgmentStatus.ZERO.value:        "ignore",
        }
        learning_signal = signal_map.get(judgment, "suspend")

        # Reverse trace
        reverse_trace: list[str] = []
        for proj in (kernel_result.statistical, kernel_result.arabic, kernel_result.epistemic):
            reverse_trace.extend(proj.unit.T.reverse_path)
        reverse_trace = list(dict.fromkeys(reverse_trace))  # deduplicate, preserve order

        epistemic_unit = kernel_result.epistemic.unit
        arabic_unit = kernel_result.arabic.unit

        return ProofObject(
            proof_id=f"PO-{uuid.uuid4().hex[:10]}",
            text=kernel_result.text,
            judgment=judgment,
            statistical_confidence=kernel_result.statistical.comparable_score,
            linguistic_force=arabic_unit.C.linguistic_force,
            epistemic_certainty=epistemic_unit.C.epistemic_certainty,
            evidence_state=epistemic_unit.E.evidence_state,
            conservation=primary_conservation,
            cognitive_residual=kernel_result.cognitive_residual,
            residual_type=kernel_result.residual_type,
            learning_signal=learning_signal,
            reverse_trace=reverse_trace,
            kernel_result=kernel_result,
        )

    @staticmethod
    def _merge_conservation(results: list[ConservationCheckResult]) -> ConservationCheckResult:
        if not results:
            return ConservationCheckResult(unit_id="merged", passed=True)

        all_violations = []
        for r in results:
            all_violations.extend(r.violations)

        penalty = sum(
            {"low": 0.02, "medium": 0.05, "high": 0.10, "blocking": 0.30}.get(v.severity, 0.05)
            for v in all_violations
        )
        score = max(0.0, 1.0 - penalty)

        return ConservationCheckResult(
            unit_id="merged",
            passed=len(all_violations) == 0,
            violations=all_violations,
            conservation_score=score,
        )
