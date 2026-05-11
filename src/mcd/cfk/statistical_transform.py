"""Statistical Transform S(x) — converts a GPTProposal into a CognitiveFractalUnit.

Coordinate system: احتمال / ترجيح
S(x) answers: "What is the most statistically probable continuation in context?"

The transform does NOT raise epistemic certainty.
It sets coordinate_type = "statistical" and populates
C.statistical_confidence from the proposal's certainty metadata.
"""
from __future__ import annotations

import uuid
from typing import Any

from mcd.cfk.cfk_schema import (
    CognitiveFractalUnit,
    NodeInfo,
    VectorInfo,
    RelationsInfo,
    OperatorsInfo,
    EvidenceInfo,
    CertaintyInfo,
    ProofInfo,
    TraceInfo,
    ResidualInfo,
    CoordinateType,
    JudgmentStatus,
    KernelProjection,
)


# Maps claimed_certainty strings (from GPTProposal) to a float score
_CONFIDENCE_MAP: dict[str, float] = {
    "near_certainty":     0.92,
    "strong_knowledge":   0.82,
    "probable_knowledge": 0.68,
    "hypothesis":         0.52,
    "weak_or_unverified": 0.25,
    "unknown":            0.50,
}


class StatisticalTransform:
    """Applies transform S: GPTProposal → CognitiveFractalUnit (statistical coordinates)."""

    def transform(self, proposal_dict: dict[str, Any]) -> KernelProjection:
        """Convert a GPTProposal dict to a KernelProjection in statistical coordinates."""

        text = proposal_dict.get("gpt_output", "")
        claimed = proposal_dict.get("claimed_certainty") or "unknown"
        evidence_refs = proposal_dict.get("claimed_evidence", [])
        proposal_id = proposal_dict.get("proposal_id", str(uuid.uuid4()))
        proposal_type = proposal_dict.get("proposal_type", "answer")

        stat_confidence = _CONFIDENCE_MAP.get(claimed, 0.50)

        # Evidence state
        evidence_state = "present" if evidence_refs else "missing"

        uid = f"CFU-S-{uuid.uuid4().hex[:8]}"

        n = NodeInfo(
            node_id=uid,
            level="claim",
            surface=text[:80],
            unit_type="claim",
            language_origin="statistical",
        )
        v = VectorInfo(
            statistical_weight=stat_confidence,
            semantic_weight=0.0,   # not evaluated by this transform
            epistemic_weight=0.0,  # not evaluated by this transform
        )
        r = RelationsInfo(
            role="proposal",
        )
        o = OperatorsInfo(
            logical_function="probability_distribution",
            operator_effect="statistical_weighting",
        )
        e = EvidenceInfo(
            evidence_state=evidence_state,
            evidence_refs=evidence_refs,
            source_trust=0.3 if not evidence_refs else 0.5,
        )
        c = CertaintyInfo(
            statistical_confidence=stat_confidence,
            linguistic_force="neutral",
            epistemic_certainty=0.0,   # S cannot set epistemic certainty
            certainty_level=claimed if claimed in _CONFIDENCE_MAP else "hypothesis",
            coordinate_type=CoordinateType.STATISTICAL.value,
        )
        p = ProofInfo(
            produces_proof=False,
            proof_type="none",
            proof_strength=0.0,
        )
        t = TraceInfo(
            origin_level="claim",
            reverse_path=[proposal_id, "gpt_output"],
        )
        z = ResidualInfo(
            residual_type="statistical_proposal",
            learning_signal="none",
        )

        unit = CognitiveFractalUnit(
            unit_id=uid,
            surface=text[:80],
            source_text=text,
            N=n, V=v, R=r, O=o, E=e, C=c, P=p, T=t, Z=z,
            metadata={
                "proposal_id": proposal_id,
                "proposal_type": proposal_type,
            },
        )

        # Comparable score for kernel = statistical_confidence
        # (Evidence absent → cap at 0.6 even if high confidence)
        comparable_score = stat_confidence if evidence_refs else min(stat_confidence, 0.6)

        notes: list[str] = ["S(x): statistical coordinate"]
        if not evidence_refs:
            notes.append("no_evidence_refs — comparable_score capped at 0.60")

        return KernelProjection(
            projection_id=f"KP-S-{uuid.uuid4().hex[:8]}",
            coordinate_type=CoordinateType.STATISTICAL.value,
            unit=unit,
            comparable_score=comparable_score,
            judgment=JudgmentStatus.HYPOTHESIS.value,
            transform_notes=notes,
        )
