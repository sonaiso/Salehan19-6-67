"""Arabic Semantic Transform A(x) — converts Arabic text into a CognitiveFractalUnit.

Coordinate system: دلالة / علاقة / تركيب
A(x) answers: "What is the dalalah, nasba, 'amil, and hukm of this utterance?"

The transform uses:
  - mcd.murab (I'rab / syntactic case)
  - mcd.mabni (logical operators: ma, man, in, la, condition, qasr …)
  - mcd.morphosemantics (root/pattern folded graph)

It sets coordinate_type = "arabic" and populates:
  C.linguistic_force from irab / mabni operators
  R.role and R.edges from syntactic analysis
  O.logical_function from mabni operators
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
# Lightweight helpers (avoid hard dependency on full morphosemantics data)
# ---------------------------------------------------------------------------

_ARABIC_EMPHASIS_MARKERS = {"إنّ", "إن", "أن", "لام", "ل", "قد", "لقد", "إنما", "بل"}
_ARABIC_NEGATION_MARKERS = {"لا", "ما", "لم", "لن", "لات", "ليس", "ليست"}
_ARABIC_CONDITION_MARKERS = {"إن", "إذا", "لو", "لولا", "متى", "أينما", "كلما"}
_ARABIC_RESTRICTION_MARKERS = {"إلا", "غير", "سوى", "حاشا", "عدا", "خلا"}
_ARABIC_UNIVERSAL_MARKERS = {"كل", "جميع", "كافة", "سائر"}


def _detect_linguistic_force(tokens: list[str]) -> str:
    token_set = set(tokens)
    if token_set & _ARABIC_NEGATION_MARKERS:
        return "negation"
    if token_set & _ARABIC_EMPHASIS_MARKERS:
        return "emphasis"
    if token_set & _ARABIC_CONDITION_MARKERS:
        return "condition"
    if token_set & _ARABIC_RESTRICTION_MARKERS:
        return "restriction"
    if token_set & _ARABIC_UNIVERSAL_MARKERS:
        return "universal"
    return "neutral"


def _detect_operator(tokens: list[str]) -> tuple[str, str]:
    """Return (logical_function, operator_effect)."""
    token_set = set(tokens)
    if token_set & _ARABIC_NEGATION_MARKERS:
        return "negation_operator", "judgment_polarity_change"
    if token_set & _ARABIC_CONDITION_MARKERS:
        return "condition_operator", "hypothesis_creation"
    if token_set & _ARABIC_RESTRICTION_MARKERS:
        return "restriction_operator", "scope_narrowing"
    if token_set & _ARABIC_UNIVERSAL_MARKERS:
        return "universal_quantifier", "generalization_claim"
    if token_set & _ARABIC_EMPHASIS_MARKERS:
        return "emphasis_operator", "assertion_strengthening"
    return "predication", "assertion"


def _syntactic_role_from_murab(irab_case: str) -> str:
    mapping = {
        "nominative":   "subject_or_predicate",
        "accusative":   "object_or_circumstance",
        "genitive":     "possessor_or_governed",
        "jussive":      "verb_jussive",
        "indeclinable_local": "indeclinable",
        "unknown":      "unknown",
    }
    return mapping.get(irab_case, "unknown")


# ---------------------------------------------------------------------------
# Main Transform
# ---------------------------------------------------------------------------

class ArabicSemanticTransform:
    """Applies transform A: Arabic text → CognitiveFractalUnit (Arabic coordinates)."""

    def transform(self, text: str) -> KernelProjection:
        tokens = text.split()

        # --- try murab analysis ---
        murab_units: list[Any] = []
        murab_fallback = False
        murab_fallback_reason = ""
        try:
            from mcd.murab.murab_analyzer import MurabAnalyzer
            analyzer = MurabAnalyzer()
            murab_units = analyzer.analyze(text)
        except Exception as exc:
            murab_fallback = True
            murab_fallback_reason = str(exc) or "murab_unavailable"

        # --- try mabni analysis ---
        mabni_result: dict[str, Any] = {}
        mabni_fallback = False
        mabni_fallback_reason = ""
        try:
            from mcd.mabni.mabni_unfolder import MabniUnfolder
            unfolder = MabniUnfolder()
            res = unfolder.unfold(text)
            mabni_result = res.to_dict() if hasattr(res, "to_dict") else {}
        except Exception as exc:
            mabni_fallback = True
            mabni_fallback_reason = str(exc) or "mabni_unavailable"

        # Build linguistic_force and operator info
        linguistic_force = _detect_linguistic_force(tokens)
        logical_function, operator_effect = _detect_operator(tokens)

        # Override with mabni if available
        if mabni_result:
            speech_act = mabni_result.get("speech_act", {}).get("speech_act", "")
            if speech_act in ("negation", "condition", "restriction"):
                linguistic_force = speech_act
                logical_function = f"{speech_act}_operator"

        # Build edges from murab units
        edges: list[dict[str, str]] = []
        syntactic_role = "predication"
        for mu in murab_units:
            role = _syntactic_role_from_murab(getattr(mu, "irab_case", "unknown"))
            edges.append({
                "from": getattr(mu, "surface", ""),
                "type": role,
                "to": "sentence",
            })
        if murab_units:
            primary = murab_units[0]
            syntactic_role = _syntactic_role_from_murab(getattr(primary, "irab_case", "unknown"))

        # Linguistic force score (0–1)
        force_score_map = {
            "emphasis":    0.85,
            "negation":    0.80,
            "condition":   0.70,
            "restriction": 0.75,
            "universal":   0.72,
            "neutral":     0.55,
        }
        ling_score = force_score_map.get(linguistic_force, 0.55)

        # Cap comparable_score when fallback was used
        _fallback_used = murab_fallback or mabni_fallback
        _FALLBACK_SCORE_CAP = 0.55
        if _fallback_used:
            ling_score = min(ling_score, _FALLBACK_SCORE_CAP)

        # Syntactic certainty from murab
        syn_certainty = "probable_syntactic"
        if murab_units:
            cp = getattr(murab_units[0], "certainty_policy", "unknown")
            if cp == "certain_syntactic":
                syn_certainty = "certain_syntactic"

        uid = f"CFU-A-{uuid.uuid4().hex[:8]}"

        n = NodeInfo(
            node_id=uid,
            level="sentence",
            surface=text[:80],
            unit_type="claim",
            language_origin="arabic",
        )
        v = VectorInfo(
            statistical_weight=0.0,
            semantic_weight=ling_score,
            epistemic_weight=0.0,
        )
        r = RelationsInfo(
            edges=edges,
            role=syntactic_role,
        )
        o = OperatorsInfo(
            active_operators=[linguistic_force],
            logical_function=logical_function,
            operator_effect=operator_effect,
        )
        e = EvidenceInfo(
            evidence_state="missing",   # A(x) does not supply evidence
            source_trust=0.0,
        )
        c = CertaintyInfo(
            statistical_confidence=0.0,
            linguistic_force=linguistic_force,
            epistemic_certainty=0.0,   # A cannot set epistemic certainty
            certainty_level="hypothesis",
            coordinate_type=CoordinateType.ARABIC.value,
        )
        p = ProofInfo(
            produces_proof=False,
            proof_type="linguistic",
            proof_strength=ling_score * 0.4,   # linguistic force is partial proof signal
        )
        t = TraceInfo(
            origin_level="sentence",
            reverse_path=["arabic_text", "murab_analysis"],
        )
        z = ResidualInfo(
            residual_type="arabic_semantic_proposal",
            learning_signal="none",
        )

        unit = CognitiveFractalUnit(
            unit_id=uid,
            surface=text[:80],
            source_text=text,
            N=n, V=v, R=r, O=o, E=e, C=c, P=p, T=t, Z=z,
            metadata={
                "linguistic_force": linguistic_force,
                "syntactic_certainty": syn_certainty,
                "murab_units_count": len(murab_units),
                "mabni_speech_act": mabni_result.get("speech_act", {}).get("speech_act", ""),
                "murab_fallback": murab_fallback,
                "mabni_fallback": mabni_fallback,
            },
        )

        notes: list[str] = [
            "A(x): arabic semantic coordinate",
            f"linguistic_force={linguistic_force}",
            f"logical_function={logical_function}",
        ]
        if murab_units:
            notes.append(f"murab_units={len(murab_units)}")
        if murab_fallback:
            notes.append(f"transform_note=murab_unavailable_fallback_used ({murab_fallback_reason})")
        if mabni_fallback:
            notes.append(f"transform_note=mabni_unavailable_fallback_used ({mabni_fallback_reason})")
        if _fallback_used:
            notes.append(f"comparable_score_capped_at={_FALLBACK_SCORE_CAP} (fallback active)")

        return KernelProjection(
            projection_id=f"KP-A-{uuid.uuid4().hex[:8]}",
            coordinate_type=CoordinateType.ARABIC.value,
            unit=unit,
            comparable_score=ling_score,
            judgment=JudgmentStatus.HYPOTHESIS.value,
            transform_notes=notes,
        )
