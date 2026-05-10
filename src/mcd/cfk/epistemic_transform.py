"""Epistemic Transform E(x) — converts a claim into epistemic coordinates.

Coordinate system: دليل / يقين / حكم
E(x) answers:
  هل هو مطابق للواقع؟  وما دليله؟  وما درجة يقينه؟

The transform uses:
  - mcd.nabhani (epistemic axioms, fake-evidence detection, rational method)
  - evidence_refs and evidence_state to gate certainty
  - The key law:
      C_epistemic = G(C_statistical, E, R, T)
    i.e. epistemic certainty requires evidence, not just probability.

Key rule encoded here:
  statistical_confidence + no_evidence → C_epistemic stays low
  emphasis_operator + no_evidence      → C_epistemic stays low
  (emphasis ≠ proof)
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


# ---------------------------------------------------------------------------
# Certainty formula: C_epistemic = G(C_stat, E, R, T)
# ---------------------------------------------------------------------------

def compute_epistemic_certainty(
    statistical_confidence: float,
    evidence_state: str,
    relation_complexity: int,
    has_reverse_trace: bool,
) -> float:
    """
    C_epistemic = G(C_statistical, E, R, T)

    Rules:
    - If evidence is missing: epistemic certainty ≤ 0.40 (hypothesis ceiling)
    - If evidence is partial: epistemic certainty ≤ 0.65
    - If evidence is present: computed from all four inputs
    - Relation complexity and trace availability contribute small boosts
    """
    if evidence_state == "missing":
        return min(statistical_confidence * 0.3, 0.40)

    if evidence_state == "partial":
        base = statistical_confidence * 0.55
        base += 0.05 if has_reverse_trace else 0.0
        return min(base, 0.65)

    # evidence_state == "present"
    base = statistical_confidence * 0.75
    base += min(relation_complexity * 0.02, 0.10)
    base += 0.05 if has_reverse_trace else 0.0
    return min(base, 0.98)


def _certainty_level(score: float) -> str:
    if score < 0.40:
        return "weak_or_unverified"
    if score < 0.60:
        return "hypothesis"
    if score < 0.75:
        return "probable_knowledge"
    if score < 0.90:
        return "strong_knowledge"
    return "near_certainty"


# ---------------------------------------------------------------------------
# Main Transform
# ---------------------------------------------------------------------------

class EpistemicTransform:
    """Applies transform E: claim + evidence → CognitiveFractalUnit (epistemic coordinates)."""

    def transform(
        self,
        text: str,
        statistical_confidence: float = 0.5,
        evidence_refs: list[str] | None = None,
        evidence_types: list[str] | None = None,
        linguistic_force: str = "neutral",
        source_text: str = "",
    ) -> KernelProjection:
        evidence_refs = evidence_refs or []
        evidence_types = evidence_types or []

        evidence_state = (
            "present" if len(evidence_refs) >= 2
            else ("partial" if len(evidence_refs) == 1 else "missing")
        )

        has_trace = bool(source_text)
        relation_complexity = len(text.split())

        epistemic_certainty = compute_epistemic_certainty(
            statistical_confidence,
            evidence_state,
            relation_complexity,
            has_trace,
        )

        certainty_level = _certainty_level(epistemic_certainty)

        # Nabhani fake-evidence detection (optional)
        fake_evidence_detected = False
        fake_evidence_notes: list[str] = []
        try:
            from mcd.nabhani.fake_evidence_detector import FakeEvidenceDetector
            detector = FakeEvidenceDetector()
            fe_result = detector.detect(text)
            fake_evidence_detected = fe_result.get("fake_detected", False)
            if fake_evidence_detected:
                fake_evidence_notes.append("fake_evidence_detected")
                epistemic_certainty = min(epistemic_certainty, 0.30)
                certainty_level = "weak_or_unverified"
        except Exception:
            pass

        # Determine judgment
        if certainty_level in ("strong_knowledge", "near_certainty") and not fake_evidence_detected:
            judgment = JudgmentStatus.CERTIFICATE.value
        elif certainty_level in ("probable_knowledge",) and not fake_evidence_detected:
            judgment = JudgmentStatus.HYPOTHESIS.value
        elif evidence_state == "missing":
            judgment = JudgmentStatus.SUSPEND.value
        else:
            judgment = JudgmentStatus.HYPOTHESIS.value

        if fake_evidence_detected:
            judgment = JudgmentStatus.ZERO.value

        uid = f"CFU-E-{uuid.uuid4().hex[:8]}"

        n = NodeInfo(
            node_id=uid,
            level="claim",
            surface=text[:80],
            unit_type="claim",
            language_origin="epistemic",
        )
        v = VectorInfo(
            statistical_weight=statistical_confidence,
            semantic_weight=0.0,
            epistemic_weight=epistemic_certainty,
        )
        r = RelationsInfo(role="epistemic_judgment")
        o = OperatorsInfo(
            logical_function="epistemic_evaluation",
            operator_effect="certainty_assignment",
        )
        e = EvidenceInfo(
            evidence_state=evidence_state,
            evidence_refs=evidence_refs,
            evidence_types=evidence_types,
            source_trust=0.8 if evidence_state == "present" else 0.3,
        )
        c = CertaintyInfo(
            statistical_confidence=statistical_confidence,
            linguistic_force=linguistic_force,
            epistemic_certainty=epistemic_certainty,
            certainty_level=certainty_level,
            coordinate_type=CoordinateType.EPISTEMIC.value,
        )
        p = ProofInfo(
            produces_proof=judgment == JudgmentStatus.CERTIFICATE.value,
            proof_type="epistemic" if judgment == JudgmentStatus.CERTIFICATE.value else "none",
            proof_strength=epistemic_certainty,
        )
        t = TraceInfo(
            origin_level="claim",
            reverse_path=["source_text", "evidence_refs", "epistemic_transform"],
        )
        z = ResidualInfo(
            residual_score=max(0.0, statistical_confidence - epistemic_certainty),
            residual_type=(
                "evidence_gap" if evidence_state == "missing"
                else ("fake_evidence" if fake_evidence_detected else "none")
            ),
            missing_components=(
                ["evidence_refs"] if evidence_state == "missing" else []
            ) + (["valid_evidence"] if fake_evidence_detected else []),
            learning_signal="correct" if judgment == JudgmentStatus.CERTIFICATE.value else "suspend",
        )

        unit = CognitiveFractalUnit(
            unit_id=uid,
            surface=text[:80],
            source_text=source_text or text,
            N=n, V=v, R=r, O=o, E=e, C=c, P=p, T=t, Z=z,
            metadata={
                "evidence_state": evidence_state,
                "judgment": judgment,
                "fake_evidence_detected": fake_evidence_detected,
            },
        )

        notes: list[str] = [
            "E(x): epistemic coordinate",
            f"evidence_state={evidence_state}",
            f"epistemic_certainty={round(epistemic_certainty, 3)}",
            f"judgment={judgment}",
        ] + fake_evidence_notes

        return KernelProjection(
            projection_id=f"KP-E-{uuid.uuid4().hex[:8]}",
            coordinate_type=CoordinateType.EPISTEMIC.value,
            unit=unit,
            comparable_score=epistemic_certainty,
            judgment=judgment,
            transform_notes=notes,
        )
