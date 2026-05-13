"""Phase 8 — Cognitive Fractal Kernel (CFK) core schemas.

The central dataclass is CognitiveFractalUnit (CFU) with nine dimensions:

    F(U) = ⟨N, V, R, O, E, C, P, T, Z⟩

where
    N  = Node        — ما هذه الوحدة؟
    V  = Vector      — ما أبعادها؟
    R  = Relations   — بماذا ترتبط؟
    O  = Operators   — ما الذي يشغّلها؟
    E  = Evidence    — ما دليلها؟
    C  = Certainty   — ما درجة ثبوتها؟
    P  = Proof       — هل تنتج برهانًا؟
    T  = Trace       — كيف نرجع إلى أصلها؟
    Z  = Residual    — ما الفرق بينها وبين العقد الرياضي؟

These nine dimensions are shared across all three coordinate systems:
    Statistical  (GPT / probability)
    Arabic       (semantic-relational)
    Epistemic    (evidence-based certainty)

A KernelProjection captures one unit after applying the unifying kernel K
so that all three can be compared in the same space.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from mcd.core.public_judgment import is_public_final_judgment

# ---------------------------------------------------------------------------
# Judgment vocabulary
# ---------------------------------------------------------------------------

class JudgmentStatus(str, Enum):
    CERTIFICATE = "certificate"       # دليل مكتمل — يقين
    HYPOTHESIS  = "hypothesis"        # دعوى محتملة — انتظار
    SUSPENDED   = "suspended"         # حالة إجرائية داخلية فقط (ليست حكمًا نهائيًا عامًا)
    SUSPEND     = "suspended"         # deprecated alias; prefer SUSPENDED/internal_state + public three-state judgment
    ZERO        = "zero"              # باقٍ معرفي — خطأ بنيوي


PUBLIC_FINAL_JUDGMENTS: tuple[str, str, str] = (
    JudgmentStatus.ZERO.value,
    JudgmentStatus.HYPOTHESIS.value,
    JudgmentStatus.CERTIFICATE.value,
)


def coerce_public_judgment(judgment: str | None) -> str:
    """Map any internal/non-public state into the public final judgment contract.

    CFK preserves explicit upstream public judgments (including explicit "zero"),
    collapses suspend/suspended to "hypothesis", and defaults unknown labels to
    "hypothesis" rather than exposing non-contract values.
    """
    normalized = (judgment or "").strip().lower()
    if is_public_final_judgment(normalized):
        return normalized
    if normalized in {"suspend", "suspended"}:
        return JudgmentStatus.HYPOTHESIS.value
    return JudgmentStatus.HYPOTHESIS.value


class CoordinateType(str, Enum):
    STATISTICAL = "statistical"   # إحصائي / احتمالي
    ARABIC      = "arabic"        # دلالي / علائقي
    EPISTEMIC   = "epistemic"     # برهاني / يقيني


# ---------------------------------------------------------------------------
# Nine dimensions of a CognitiveFractalUnit
# ---------------------------------------------------------------------------

@dataclass
class NodeInfo:
    """N — ما هذه الوحدة؟"""
    node_id: str
    level: str           # unicode|letter|root|pattern|word|phrase|sentence|claim|judgment
    surface: str
    unit_type: str       # character|word|claim|operator|judgment
    language_origin: str = "arabic"  # arabic|statistical|epistemic

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "level": self.level,
            "surface": self.surface,
            "unit_type": self.unit_type,
            "language_origin": self.language_origin,
        }


@dataclass
class VectorInfo:
    """V — ما أبعادها؟"""
    embedding: dict[str, float] = field(default_factory=dict)
    statistical_weight: float = 0.5
    semantic_weight: float = 0.5
    epistemic_weight: float = 0.5

    def to_dict(self) -> dict:
        return {
            "embedding": self.embedding,
            "statistical_weight": round(self.statistical_weight, 4),
            "semantic_weight": round(self.semantic_weight, 4),
            "epistemic_weight": round(self.epistemic_weight, 4),
        }


@dataclass
class RelationsInfo:
    """R — بماذا ترتبط؟"""
    edges: list[dict[str, str]] = field(default_factory=list)   # {from, type, to}
    role: str = "unknown"            # agent|patient|predicate|subject|…
    dependency_head: str | None = None

    def to_dict(self) -> dict:
        return {
            "edges": self.edges,
            "role": self.role,
            "dependency_head": self.dependency_head,
        }


@dataclass
class OperatorsInfo:
    """O — ما الذي يشغّلها؟"""
    active_operators: list[str] = field(default_factory=list)
    logical_function: str = "unknown"   # negation|emphasis|condition|restriction|…
    operator_effect: str = "none"

    def to_dict(self) -> dict:
        return {
            "active_operators": self.active_operators,
            "logical_function": self.logical_function,
            "operator_effect": self.operator_effect,
        }


@dataclass
class EvidenceInfo:
    """E — ما دليلها؟"""
    evidence_state: str = "missing"      # present|partial|missing
    evidence_refs: list[str] = field(default_factory=list)
    evidence_types: list[str] = field(default_factory=list)
    source_trust: float = 0.0

    def to_dict(self) -> dict:
        return {
            "evidence_state": self.evidence_state,
            "evidence_refs": self.evidence_refs,
            "evidence_types": self.evidence_types,
            "source_trust": round(self.source_trust, 4),
        }


@dataclass
class CertaintyInfo:
    """C — ما درجة ثبوتها؟"""
    statistical_confidence: float = 0.5
    linguistic_force: str = "neutral"      # neutral|emphasis|negation|condition|…
    epistemic_certainty: float = 0.0       # 0 = unknown, 1 = near_certainty
    certainty_level: str = "hypothesis"    # from core.certainty levels
    coordinate_type: str = CoordinateType.EPISTEMIC.value

    def to_dict(self) -> dict:
        return {
            "statistical_confidence": round(self.statistical_confidence, 4),
            "linguistic_force": self.linguistic_force,
            "epistemic_certainty": round(self.epistemic_certainty, 4),
            "certainty_level": self.certainty_level,
            "coordinate_type": self.coordinate_type,
        }


@dataclass
class ProofInfo:
    """P — هل تنتج برهانًا؟"""
    produces_proof: bool = False
    proof_type: str = "none"        # deductive|inductive|linguistic|empirical|none
    proof_strength: float = 0.0

    def to_dict(self) -> dict:
        return {
            "produces_proof": self.produces_proof,
            "proof_type": self.proof_type,
            "proof_strength": round(self.proof_strength, 4),
        }


@dataclass
class TraceInfo:
    """T — كيف نرجع إلى أصلها؟"""
    trace_ids: list[str] = field(default_factory=list)
    token_span: tuple[int, int] = (0, 0)
    origin_level: str = "word"
    reverse_path: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "trace_ids": self.trace_ids,
            "token_span": list(self.token_span),
            "origin_level": self.origin_level,
            "reverse_path": self.reverse_path,
        }


@dataclass
class ResidualInfo:
    """Z — ما الفرق بينها وبين العقد الرياضي؟"""
    residual_score: float = 0.0
    residual_type: str = "none"
    missing_components: list[str] = field(default_factory=list)
    learning_signal: str = "none"    # reinforce|correct|ignore

    def to_dict(self) -> dict:
        return {
            "residual_score": round(self.residual_score, 4),
            "residual_type": self.residual_type,
            "missing_components": self.missing_components,
            "learning_signal": self.learning_signal,
        }


# ---------------------------------------------------------------------------
# Main CognitiveFractalUnit
# ---------------------------------------------------------------------------

@dataclass
class CognitiveFractalUnit:
    """A unit that has been mapped through F(U) = ⟨N, V, R, O, E, C, P, T, Z⟩."""

    unit_id: str
    surface: str
    source_text: str = ""

    N: NodeInfo      = field(default_factory=lambda: NodeInfo("", "word", "", "word"))
    V: VectorInfo    = field(default_factory=VectorInfo)
    R: RelationsInfo = field(default_factory=RelationsInfo)
    O: OperatorsInfo = field(default_factory=OperatorsInfo)
    E: EvidenceInfo  = field(default_factory=EvidenceInfo)
    C: CertaintyInfo = field(default_factory=CertaintyInfo)
    P: ProofInfo     = field(default_factory=ProofInfo)
    T: TraceInfo     = field(default_factory=TraceInfo)
    Z: ResidualInfo  = field(default_factory=ResidualInfo)

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "unit_id": self.unit_id,
            "surface": self.surface,
            "source_text": self.source_text,
            "N": self.N.to_dict(),
            "V": self.V.to_dict(),
            "R": self.R.to_dict(),
            "O": self.O.to_dict(),
            "E": self.E.to_dict(),
            "C": self.C.to_dict(),
            "P": self.P.to_dict(),
            "T": self.T.to_dict(),
            "Z": self.Z.to_dict(),
            "metadata": self.metadata,
        }

    @classmethod
    def make(cls, surface: str, source_text: str = "") -> "CognitiveFractalUnit":
        uid = f"CFU-{uuid.uuid4().hex[:10]}"
        n = NodeInfo(node_id=uid, level="word", surface=surface, unit_type="word")
        return cls(unit_id=uid, surface=surface, source_text=source_text, N=n)


# ---------------------------------------------------------------------------
# KernelProjection — result of applying K to one coordinate system
# ---------------------------------------------------------------------------

@dataclass
class KernelProjection:
    """Projection of one coordinate system into the unified fractal kernel K."""

    projection_id: str
    coordinate_type: str              # statistical|arabic|epistemic
    unit: CognitiveFractalUnit
    comparable_score: float = 0.0     # K(system(x)) — scalar for comparison
    judgment: str = JudgmentStatus.HYPOTHESIS.value
    transform_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "projection_id": self.projection_id,
            "coordinate_type": self.coordinate_type,
            "unit": self.unit.to_dict(),
            "comparable_score": round(self.comparable_score, 4),
            "judgment": self.judgment,
            "transform_notes": self.transform_notes,
        }
