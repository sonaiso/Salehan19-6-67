"""ProofObject — the final output of the Cognitive Fractal Kernel pipeline.

A ProofObject public judgment is one of three types:
  Certificate   — دليل مكتمل — يقين (evidence present, certainty ≥ 0.75)
  Hypothesis    — دعوى محتملة — انتظار (partial evidence or moderate certainty)
  Zero          — باقٍ معرفي — خطأ بنيوي (fake evidence, conservation law broken)

Internal procedural state may still be "suspended", but it must collapse into
public judgment="hypothesis" with residuals explaining blocked certification.

The ProofObject carries:
  - the three projections (statistical, arabic, epistemic)
  - the kernel judgment
  - conservation check results
  - the cognitive residual (learning signal)
  - a full reverse trace (Phase 8.1: ReverseTrace object)

Phase 8.1 hardening:
  Certificate requires ALL of:
    1. evidence_refs non-empty
    2. conservation passed (no blocking violation)
    3. reverse_trace.complete = True
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from mcd.cfk.cfk_schema import JudgmentStatus, coerce_public_judgment
from mcd.cfk.fractal_kernel import KernelResult
from mcd.cfk.conservation_law import ConservationCheckResult
from mcd.cfk.reverse_trace import ReverseTrace, ReverseTraceBuilder


@dataclass
class ProofObject:
    """The formal output of the CFK pipeline for a single claim."""

    proof_id: str
    text: str

    # Final judgment
    judgment: str   # certificate|hypothesis|zero (public contract only)

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
    learning_signal: str  # certificate->reinforce, hypothesis->correct, zero->ignore

    internal_state: str = "active"
    residuals: list[str] = field(default_factory=list)

    # Trace — Phase 8.1: structured ReverseTrace replaces plain list
    reverse_trace_obj: ReverseTrace | None = None
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
            "residuals": self.residuals,
            "learning_signal": self.learning_signal,
            "internal_state": self.internal_state,
            "reverse_trace": self.reverse_trace,
        }
        if self.reverse_trace_obj is not None:
            d["reverse_trace_obj"] = self.reverse_trace_obj.to_dict()
        if self.kernel_result is not None:
            d["kernel_result"] = self.kernel_result.to_dict()
        return d


class ProofObjectBuilder:
    """Builds a ProofObject from a KernelResult and ConservationCheckResults.

    Phase 8.1 gate: Certificate is ONLY issued when:
      - evidence_refs is non-empty
      - no blocking conservation violation exists
      - ReverseTrace.complete is True
    """

    def __init__(self) -> None:
        self._rt_builder = ReverseTraceBuilder()

    def build(
        self,
        kernel_result: KernelResult,
        conservation_results: list[ConservationCheckResult],
        cross_layer_report=None,  # CrossLayerConservationReport | None
    ) -> ProofObject:

        # Choose the primary conservation check (epistemic is most critical)
        primary_conservation = self._merge_conservation(conservation_results)

        # Determine final judgment
        judgment = coerce_public_judgment(kernel_result.kernel_judgment)
        internal_state = kernel_result.kernel_internal_state
        residuals: list[str] = []

        # Override: if any conservation law is blocking → Zero
        blocking = any(
            v.severity == "blocking"
            for v in primary_conservation.violations
        )
        if blocking:
            judgment = JudgmentStatus.ZERO.value
            internal_state = "active"
            residuals.append("certificate_blocked")

        # Generate a preliminary proof_id so ReverseTrace can reference it
        proof_id = f"PO-{uuid.uuid4().hex[:10]}"

        # Build ReverseTrace
        rt = self._rt_builder.build(
            proof_id=proof_id,
            final_judgment=judgment,
            statistical_projection=kernel_result.statistical,
            arabic_projection=kernel_result.arabic,
            epistemic_projection=kernel_result.epistemic,
            conservation_results=conservation_results,
            cross_layer_report=cross_layer_report,
        )

        # Phase 8.1 Certificate gate
        if judgment == JudgmentStatus.CERTIFICATE.value:
            if not rt.complete:
                # Downgrade to Hypothesis if reverse trace is incomplete
                judgment = JudgmentStatus.HYPOTHESIS.value
                rt.final_judgment = judgment
                residuals.append("certificate_blocked")
                if not rt.raw_text_units:
                    residuals.append("reverse_trace_missing_raw_text")
                residuals.append("reverse_trace_missing")

        if internal_state == JudgmentStatus.SUSPENDED.value:
            residuals.append("certificate_blocked")
            if not kernel_result.epistemic.unit.E.evidence_refs:
                residuals.append("insufficient_evidence")
            if not rt.complete:
                residuals.append("reverse_trace_missing")
            if not primary_conservation.passed:
                residuals.append("governance_incomplete")

        # The same residual may be appended by multiple governance checks; deduplicate in stable order.
        residuals = list(dict.fromkeys(residuals))

        # Learning signal
        signal_map = {
            JudgmentStatus.CERTIFICATE.value: "reinforce",
            JudgmentStatus.HYPOTHESIS.value:  "correct",
            JudgmentStatus.ZERO.value:        "ignore",
        }
        learning_signal = signal_map.get(judgment, "correct")

        # Reverse trace path (human-readable list, kept for backward compat)
        reverse_trace: list[str] = []
        for proj in (kernel_result.statistical, kernel_result.arabic, kernel_result.epistemic):
            reverse_trace.extend(proj.unit.T.reverse_path)
        reverse_trace = list(dict.fromkeys(reverse_trace))  # deduplicate, preserve order

        epistemic_unit = kernel_result.epistemic.unit
        arabic_unit = kernel_result.arabic.unit

        return ProofObject(
            proof_id=proof_id,
            text=kernel_result.text,
            judgment=judgment,
            statistical_confidence=kernel_result.statistical.comparable_score,
            linguistic_force=arabic_unit.C.linguistic_force,
            epistemic_certainty=epistemic_unit.C.epistemic_certainty,
            evidence_state=epistemic_unit.E.evidence_state,
            conservation=primary_conservation,
            cognitive_residual=kernel_result.cognitive_residual,
            residual_type=kernel_result.residual_type,
            residuals=residuals,
            learning_signal=learning_signal,
            internal_state=internal_state,
            reverse_trace_obj=rt,
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
