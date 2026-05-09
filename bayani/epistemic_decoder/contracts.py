"""Typed data models for the Epistemic Cognitive Decoder.

All inputs, intermediate results, and final outputs are represented as
frozen dataclasses so that every unit can exchange structured,
type-checked data without requiring an external library such as Pydantic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

@dataclass
class DecoderInput:
    """Raw query submitted by the caller."""
    query: str
    context: str = ""
    reasoning_effort: str = "high"  # "low" | "medium" | "high" | "xhigh"


# ---------------------------------------------------------------------------
# Unit 1 — Input Analyzer
# ---------------------------------------------------------------------------

@dataclass
class TaskAnalysis:
    """Output of the Input Analyzer (Unit 1)."""
    task_type: str                        # e.g. "conceptual_modeling"
    domain: str                           # e.g. "epistemology_language_reasoning"
    requires_sources: bool = True
    requires_reality_grounding: bool = True
    risk_of_hallucination: str = "medium" # "low" | "medium" | "high"
    complexity: str = "medium"            # "simple" | "medium" | "complex" | "deep"


# ---------------------------------------------------------------------------
# Unit 2 — Reality Extractor
# ---------------------------------------------------------------------------

@dataclass
class RealityExtractionResult:
    """Output of the Reality Extractor (Unit 2)."""
    reality_objects: List[str] = field(default_factory=list)
    reality_type: str = "unknown"          # e.g. "conceptual_human_cognition"
    sensory_access: str = "unknown"        # "direct" | "indirect" | "none"
    evidence_needed: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Unit 3 — Semiotic Parser
# ---------------------------------------------------------------------------

@dataclass
class SignifierEntry:
    """One signifier extracted by the Semiotic Parser."""
    text: str
    dal_type: str = ""          # e.g. "لفظ مفرد"
    madlul_type: str = ""       # e.g. "حالة معرفية"
    semantic_mode: List[str] = field(default_factory=list)  # مطابقة / تضمن / التزام
    ontological_type: str = ""  # e.g. "صفة معرفية"
    lexical_category: str = "haqiqa"  # haqiqa | majaz | ishtiraq | taraduf | naql | istilah


@dataclass
class SemioticMap:
    """Output of the Semiotic Parser (Unit 3)."""
    signifiers: List[SignifierEntry] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Unit 4 — Relation Graph Builder
# ---------------------------------------------------------------------------

@dataclass
class RelationEdge:
    """One directed edge in the relation graph."""
    from_node: str
    relation: str
    to_node: str
    relation_type: str = ""     # isnad | sababiyya | shartiyya | etc.
    carrier_operator: str = ""  # verb_sentence | nominal_sentence | etc.
    certainty_rank: str = "zanni"  # "qat'i" | "zanni"


@dataclass
class RelationGraph:
    """Output of the Relation Graph Builder (Unit 4)."""
    relations: List[RelationEdge] = field(default_factory=list)
    unresolved: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Unit 5 — Evidence Retriever
# ---------------------------------------------------------------------------

@dataclass
class EvidenceItem:
    """One piece of evidence retrieved by the Evidence Retriever."""
    source: str
    content: str = ""
    strength: str = "medium"  # "high" | "medium" | "low"
    source_type: str = "text"  # "text" | "web" | "database" | "experience"


@dataclass
class EvidenceBundle:
    """Output of the Evidence Retriever (Unit 5)."""
    items: List[EvidenceItem] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Unit 6 — Certainty Scorer
# ---------------------------------------------------------------------------

@dataclass
class CertaintyScore:
    """Output of the Certainty Scorer (Unit 6) for one candidate thought."""
    claim: str
    reality_grounded: bool = False
    evidence_present: bool = False
    semantic_clarity: float = 0.0    # 0.0 – 1.0
    inference_validity: float = 0.0  # 0.0 – 1.0
    hallucination_risk: float = 0.5  # 0.0 – 1.0
    answer_score: float = 0.0        # composite score
    certainty_level: str = "unknown" # label from ontology certainty levels
    level_number: int = 0            # 0-9

    _LEVEL_MAP: Dict[str, int] = field(default_factory=lambda: {
        "لفظ بلا واقع": 0,
        "إحساس بلا تفسير": 1,
        "معلومة بلا تحقق": 2,
        "ربط أولي": 3,
        "فكر محتمل": 4,
        "معرفة راجحة": 5,
        "معرفة صحيحة": 6,
        "يقين": 7,
        "يقين صار مقياسًا": 8,
        "مقياس صار سلوكًا": 9,
        # English aliases
        "zero": 0,
        "sensation": 1,
        "unverified_information": 2,
        "initial_linking": 3,
        "probable_thought": 4,
        "probable_knowledge": 5,
        "correct_knowledge": 6,
        "certainty": 7,
        "strong_knowledge": 6,
        "yaqeen": 7,
    })

    def compute_score(
        self,
        linguistic_coherence: float,
        reality_match: float,
        evidence_strength: float,
        semantic_validity: float,
        inference_validity: float,
        certainty_clarity: float,
        hallucination_risk: float,
    ) -> float:
        """Compute answer score using the policy formula."""
        score = (
            0.20 * linguistic_coherence
            + 0.25 * reality_match
            + 0.20 * evidence_strength
            + 0.15 * semantic_validity
            + 0.10 * inference_validity
            + 0.10 * certainty_clarity
            - 0.30 * hallucination_risk
        )
        self.answer_score = round(max(0.0, score), 4)
        return self.answer_score

    def passes_threshold(self, threshold: float = 0.60) -> bool:
        return self.answer_score >= threshold


# ---------------------------------------------------------------------------
# Unit 7 — Answer Decoder
# ---------------------------------------------------------------------------

@dataclass
class VerifiedThought:
    """A candidate thought that passed the certainty gate."""
    claim: str
    score: CertaintyScore


@dataclass
class DecoderOutput:
    """Final structured output of the EpistemicCognitiveDecoder."""
    # Intermediate results
    task: Optional[TaskAnalysis] = None
    reality: Optional[RealityExtractionResult] = None
    semiotic_map: Optional[SemioticMap] = None
    relation_graph: Optional[RelationGraph] = None
    evidence: Optional[EvidenceBundle] = None
    verified_thoughts: List[VerifiedThought] = field(default_factory=list)

    # Final answer fields
    known: List[str] = field(default_factory=list)
    uncertain: List[str] = field(default_factory=list)
    needs_verification: List[str] = field(default_factory=list)
    certainty_level: str = "unknown"
    answer_score: float = 0.0
    final_answer: str = ""
    blocked: bool = False
    block_reason: str = ""
