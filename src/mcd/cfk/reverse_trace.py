"""Phase 8.1 — ReverseTrace for ProofObject.

A ReverseTrace links the final judgment all the way back to the original
projections, evidence references, and conservation checks that produced it.

A Certificate requires:
  - reverse_trace.complete = True
  - evidence_refs non-empty
  - no blocking conservation violation

A Hypothesis is allowed without a complete ReverseTrace.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass
class ReverseTrace:
    """Full backward-traceability record for one ProofObject.

    Attributes
    ----------
    reverse_trace_id:
        Unique ID for this trace record.
    final_judgment:
        The judgment this trace is attached to (certificate|hypothesis|zero).
    proof_id:
        ID of the ProofObject that owns this trace.
    statistical_projection_id:
        projection_id from the StatisticalTransform KernelProjection.
    arabic_projection_id:
        projection_id from the ArabicSemanticTransform KernelProjection.
    epistemic_projection_id:
        projection_id from the EpistemicTransform KernelProjection.
    evidence_refs:
        Evidence references collected from the EpistemicTransform.
    conservation_refs:
        IDs/summaries of ConservationCheckResult instances that were passed.
    residual_refs:
        Residual notes (e.g. "evidence_gap_residual").
    complete:
        True if and only if all mandatory fields are populated and no
        blocking violation was recorded.  Only a complete ReverseTrace
        allows a Certificate to be issued.
    blocking_violations:
        List of blocking violation descriptions found during the build.
    """

    reverse_trace_id: str
    final_judgment: str
    proof_id: str

    statistical_projection_id: str = ""
    arabic_projection_id: str = ""
    epistemic_projection_id: str = ""

    evidence_refs: list[str] = field(default_factory=list)
    conservation_refs: list[str] = field(default_factory=list)
    residual_refs: list[str] = field(default_factory=list)

    blocking_violations: list[str] = field(default_factory=list)
    complete: bool = False

    def to_dict(self) -> dict:
        return {
            "reverse_trace_id": self.reverse_trace_id,
            "final_judgment": self.final_judgment,
            "proof_id": self.proof_id,
            "statistical_projection_id": self.statistical_projection_id,
            "arabic_projection_id": self.arabic_projection_id,
            "epistemic_projection_id": self.epistemic_projection_id,
            "evidence_refs": self.evidence_refs,
            "conservation_refs": self.conservation_refs,
            "residual_refs": self.residual_refs,
            "blocking_violations": self.blocking_violations,
            "complete": self.complete,
        }


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

class ReverseTraceBuilder:
    """Constructs a ReverseTrace from the artefacts of a CFK pipeline run."""

    def build(
        self,
        proof_id: str,
        final_judgment: str,
        statistical_projection,   # KernelProjection
        arabic_projection,        # KernelProjection
        epistemic_projection,     # KernelProjection
        conservation_results,     # list[ConservationCheckResult]
        cross_layer_report=None,  # CrossLayerConservationReport | None
    ) -> ReverseTrace:
        """Build a ReverseTrace.

        Completeness rules:
        - All three projection IDs must be present.
        - evidence_refs must be non-empty for a Certificate.
        - No blocking conservation violation may exist.
        """
        rid = f"RT-{uuid.uuid4().hex[:16]}"

        evidence_refs = list(epistemic_projection.unit.E.evidence_refs)

        # Collect conservation refs
        conservation_refs: list[str] = [
            cr.unit_id for cr in conservation_results
        ]

        # Collect residual refs
        residual_refs: list[str] = []
        for proj in (statistical_projection, arabic_projection, epistemic_projection):
            rt = proj.unit.Z.residual_type
            if rt and rt != "none":
                residual_refs.append(rt)
        residual_refs = list(dict.fromkeys(residual_refs))  # deduplicate

        # Check for blocking violations
        blocking_violations: list[str] = []
        for cr in conservation_results:
            for v in cr.violations:
                if v.severity == "blocking":
                    blocking_violations.append(
                        f"{cr.unit_id}: {v.law} — {v.description}"
                    )
        if cross_layer_report is not None:
            for v in cross_layer_report.violations:
                if v.severity == "blocking":
                    blocking_violations.append(
                        f"cross_layer: {v.check_name} — {v.description}"
                    )

        # Completeness check
        has_all_projections = bool(
            statistical_projection.projection_id
            and arabic_projection.projection_id
            and epistemic_projection.projection_id
        )
        complete = (
            has_all_projections
            and bool(evidence_refs)
            and len(blocking_violations) == 0
        )

        return ReverseTrace(
            reverse_trace_id=rid,
            final_judgment=final_judgment,
            proof_id=proof_id,
            statistical_projection_id=statistical_projection.projection_id,
            arabic_projection_id=arabic_projection.projection_id,
            epistemic_projection_id=epistemic_projection.projection_id,
            evidence_refs=evidence_refs,
            conservation_refs=conservation_refs,
            residual_refs=residual_refs,
            blocking_violations=blocking_violations,
            complete=complete,
        )
