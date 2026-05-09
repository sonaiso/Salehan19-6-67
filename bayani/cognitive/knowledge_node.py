"""KnowledgeNode — universal epistemic node model.

Every unit of knowledge in the Cognitive Reasoning Mind is represented as a
``KnowledgeNode``, regardless of its linguistic level.  A letter, a diacritic,
a root, a word, a sentence, a concept, and a judgment are all nodes — only
their ``level`` field differs.

This matches the Nabhani epistemological principle: the same four-element
cognitive process (reality, sensation, brain, prior information) operates at
every scale of linguistic analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Node level taxonomy
# ---------------------------------------------------------------------------

class NodeLevel(str, Enum):
    """Ordered epistemic levels from atomic symbol up to verified certainty."""
    ATOM = "atom"             # single Unicode code-point (letter, diacritic, digit)
    SYLLABLE = "syllable"     # phonological syllable
    ROOT = "root"             # Arabic tri/quadri-literal root (جذر)
    PATTERN = "pattern"       # morphological weight/pattern (وزن)
    WORD = "word"             # fully inflected word form
    PHRASE = "phrase"         # noun phrase, verb phrase
    SENTENCE = "sentence"     # full clause / جملة
    CONCEPT = "concept"       # مفهوم — meaning grounded in reality
    CLAIM = "claim"           # حكم — proposition awaiting evidence
    EVIDENCE = "evidence"     # دليل — supporting / refuting datum
    CERTAINTY = "certainty"   # يقين — verified knowledge


# ---------------------------------------------------------------------------
# Certainty sub-model
# ---------------------------------------------------------------------------

@dataclass
class CertaintyInfo:
    """Epistemic certainty attached to a node."""

    score: float = 0.0
    """Composite certainty score in [0, 1]."""

    evidence_type: str = "unknown"
    """Nature of the evidence backing this score.

    One of: orthographic | phonological | morphological | syntactic |
    semantic | empirical | textual | inferential | unknown.
    """

    status: str = "unknown"
    """Human-readable epistemic status.

    Scale: unknown → possible → probable → verified → certain.
    """

    dimensional_scores: Dict[str, float] = field(default_factory=dict)
    """Per-dimension breakdown of the composite score (see CertaintyScorer)."""

    def __post_init__(self) -> None:
        self.score = round(float(self.score), 4)

    @property
    def label(self) -> str:
        """Map the numeric score to a Nabhani-scale Arabic label."""
        s = self.score
        if s < 0.15:
            return "لفظ بلا واقع"
        if s < 0.30:
            return "إحساس بلا تفسير"
        if s < 0.45:
            return "معلومة بلا تحقق"
        if s < 0.55:
            return "ربط أولي"
        if s < 0.65:
            return "فكر محتمل"
        if s < 0.75:
            return "معرفة راجحة"
        if s < 0.85:
            return "معرفة صحيحة"
        if s < 0.93:
            return "يقين"
        if s < 0.98:
            return "يقين صار مقياسًا"
        return "مقياس صار سلوكًا"


# ---------------------------------------------------------------------------
# Relation record
# ---------------------------------------------------------------------------

@dataclass
class NodeRelation:
    """A directed semantic relation between two KnowledgeNodes."""
    relation_type: str
    """e.g. is_part_of, is_root_of, has_pattern, denotes, agent_of …"""

    target_id: str
    """node_id of the target node."""

    certainty: float = 0.0
    evidence: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Universal KnowledgeNode
# ---------------------------------------------------------------------------

@dataclass
class KnowledgeNode:
    """Universal epistemic node usable at every linguistic level.

    Parameters
    ----------
    node_id:
        Unique identifier for this node (auto-generated if not supplied).
    level:
        :class:`NodeLevel` enum value describing the linguistic/epistemic tier.
    surface:
        The raw surface form (character, morpheme, word, sentence …).
    features:
        Atomic feature dictionary (phonetic, orthographic, morphological …).
    role_vector:
        Dictionary of role probabilities inferred from context.
    relations:
        List of :class:`NodeRelation` edges departing from this node.
    evidence:
        List of evidence strings / source labels that support this node.
    certainty:
        :class:`CertaintyInfo` summarising the epistemic status.
    metadata:
        Arbitrary extra data (e.g. Unicode code-point, source offset).
    """

    node_id: str = ""
    level: NodeLevel = NodeLevel.ATOM
    surface: str = ""
    features: Dict[str, Any] = field(default_factory=dict)
    role_vector: Dict[str, float] = field(default_factory=dict)
    relations: List[NodeRelation] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    certainty: CertaintyInfo = field(default_factory=CertaintyInfo)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def add_relation(
        self,
        relation_type: str,
        target_id: str,
        certainty: float = 0.0,
        evidence: Optional[List[str]] = None,
    ) -> None:
        """Append a :class:`NodeRelation` to this node."""
        self.relations.append(
            NodeRelation(
                relation_type=relation_type,
                target_id=target_id,
                certainty=round(float(certainty), 4),
                evidence=evidence or [],
            )
        )

    def top_role(self) -> Optional[str]:
        """Return the role with the highest probability, or None."""
        if not self.role_vector:
            return None
        return max(self.role_vector, key=lambda k: self.role_vector[k])

    def is_verified(self, threshold: float = 0.60) -> bool:
        """Return True if certainty score meets *threshold*."""
        return self.certainty.score >= threshold

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a plain dict (JSON-compatible)."""
        return {
            "node_id": self.node_id,
            "level": self.level.value,
            "surface": self.surface,
            "features": self.features,
            "role_vector": self.role_vector,
            "relations": [
                {
                    "relation_type": r.relation_type,
                    "target_id": r.target_id,
                    "certainty": r.certainty,
                    "evidence": r.evidence,
                }
                for r in self.relations
            ],
            "evidence": self.evidence,
            "certainty": {
                "score": self.certainty.score,
                "label": self.certainty.label,
                "status": self.certainty.status,
                "evidence_type": self.certainty.evidence_type,
                "dimensional_scores": self.certainty.dimensional_scores,
            },
            "metadata": self.metadata,
        }
