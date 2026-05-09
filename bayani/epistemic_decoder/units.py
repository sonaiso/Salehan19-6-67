"""Seven pipeline units of the Epistemic Cognitive Decoder.

Each unit is a pure callable class with a single ``__call__`` method that
accepts a :class:`DecoderInput` plus optional accumulated context, and returns
its specific output dataclass.

The units implement the theoretical model from the Epistemic Cognitive Decoder
specification:

1. **InputAnalyzer**      — classify the query (task type, domain, risk)
2. **RealityExtractor**   — identify the واقع (reality) behind the question
3. **SemioticParser**     — decompose the دال (signifier) and المدلول (signified)
4. **RelationGraphBuilder** — build the semantic-relational graph
5. **EvidenceRetriever**  — gather supporting evidence and sources
6. **CertaintyScorer**    — compute the epistemic certainty score
7. **AnswerDecoder**      — compose the final constrained answer
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from bayani.epistemic_decoder.contracts import (
    CertaintyScore,
    DecoderInput,
    DecoderOutput,
    EvidenceBundle,
    EvidenceItem,
    RelationEdge,
    RelationGraph,
    RealityExtractionResult,
    SemioticMap,
    SignifierEntry,
    TaskAnalysis,
    VerifiedThought,
)


# ---------------------------------------------------------------------------
# Minimum certainty level for a thought to be accepted
# ---------------------------------------------------------------------------

_KNOWLEDGE_LEVELS = {
    "معرفة راجحة",
    "معرفة صحيحة",
    "يقين",
    "يقين صار مقياسًا",
    "مقياس صار سلوكًا",
    "probable_knowledge",
    "correct_knowledge",
    "certainty",
    "strong_knowledge",
    "yaqeen",
}

_ANSWER_THRESHOLD = 0.60


# ---------------------------------------------------------------------------
# Unit 1 — Input Analyzer
# ---------------------------------------------------------------------------

class InputAnalyzer:
    """Classify the query to determine task type, domain, and risk."""

    # Simple keyword-based domain heuristics
    _DOMAIN_HINTS: Dict[str, List[str]] = {
        "epistemology_language_reasoning": [
            "مفهوم", "يقين", "دال", "مدلول", "عقل", "معرفة", "إدراك",
            "concept", "epistem", "cognit", "logic",
        ],
        "islamic_jurisprudence": [
            "حكم", "فقه", "علة", "قياس", "مناط", "واجب", "حرام", "مباح",
            "fiqh", "hukm", "illah", "manat", "qiyas",
        ],
        "linguistic_analysis": [
            "لفظ", "كلمة", "جملة", "نحو", "صرف", "بلاغة", "عام", "خاص",
            "grammar", "syntax", "semantic", "rhetoric",
        ],
        "factual_inquiry": [
            "ما", "من", "متى", "أين", "كيف", "what", "who", "when", "where", "how",
        ],
        "general": [],
    }

    _RISK_MAP = {
        "epistemology_language_reasoning": "high",
        "islamic_jurisprudence": "high",
        "linguistic_analysis": "medium",
        "factual_inquiry": "medium",
        "general": "medium",
    }

    def __call__(
        self, decoder_input: DecoderInput, context: Optional[Dict[str, Any]] = None
    ) -> TaskAnalysis:
        query_lower = decoder_input.query.lower()

        domain = "general"
        for candidate_domain, hints in self._DOMAIN_HINTS.items():
            if any(hint in query_lower for hint in hints):
                domain = candidate_domain
                break

        # Complexity from reasoning_effort
        effort_complexity = {
            "low": "simple",
            "medium": "medium",
            "high": "complex",
            "xhigh": "deep",
        }
        complexity = effort_complexity.get(decoder_input.reasoning_effort, "medium")

        # Task type heuristics
        task_type = "factual_query"
        if any(kw in query_lower for kw in ["فرق", "difference", "compare", "مقارنة"]):
            task_type = "comparative_analysis"
        elif any(kw in query_lower for kw in ["اشرح", "explain", "ما هو", "what is"]):
            task_type = "conceptual_modeling"
        elif any(kw in query_lower for kw in ["طبّق", "apply", "حكم على", "rule on"]):
            task_type = "application"

        return TaskAnalysis(
            task_type=task_type,
            domain=domain,
            requires_sources=domain in ("islamic_jurisprudence", "epistemology_language_reasoning"),
            requires_reality_grounding=True,
            risk_of_hallucination=self._RISK_MAP.get(domain, "medium"),
            complexity=complexity,
        )


# ---------------------------------------------------------------------------
# Unit 2 — Reality Extractor
# ---------------------------------------------------------------------------

class RealityExtractor:
    """Identify the واقع (reality) that the question refers to."""

    _REALITY_TYPE_HINTS = {
        "conceptual_human_cognition": ["عقل", "معرفة", "إدراك", "ذهن", "فكر", "مفهوم"],
        "material_sensory": ["جسم", "مادة", "دواء", "طعام", "شيء"],
        "textual": ["نص", "آية", "حديث", "كتاب", "وثيقة", "قرآن"],
        "social_behavioral": ["حضارة", "ثقافة", "مجتمع", "سلوك", "علم"],
        "normative_juridical": ["حكم", "واجب", "حرام", "فرض", "مباح", "علة"],
        "relational": ["علاقة", "نسبة", "ربط", "ترابط"],
    }

    def __call__(
        self,
        task: TaskAnalysis,
        decoder_input: DecoderInput,
        context: Optional[Dict[str, Any]] = None,
    ) -> RealityExtractionResult:
        query = decoder_input.query

        # Extract noun-like fragments as reality objects (simplified heuristic)
        words = [w.strip("؟!,.،") for w in query.split() if len(w) > 2]
        reality_objects = [w for w in words if w and not w.startswith("ال")][:6]

        # Determine reality type
        reality_type = "unknown"
        query_lower = query.lower()
        for rtype, hints in self._REALITY_TYPE_HINTS.items():
            if any(hint in query_lower for hint in hints):
                reality_type = rtype
                break

        # Sensory access
        sensory_access = "indirect"
        if reality_type == "material_sensory":
            sensory_access = "direct"
        elif reality_type in ("textual", "normative_juridical"):
            sensory_access = "textual"

        # Evidence needed
        evidence_needed: List[str] = ["نصوص"]
        if task.requires_sources:
            evidence_needed.append("مصادر موثوقة")
        if task.domain == "islamic_jurisprudence":
            evidence_needed.extend(["نصوص شرعية", "أدلة أصولية"])

        return RealityExtractionResult(
            reality_objects=reality_objects,
            reality_type=reality_type,
            sensory_access=sensory_access,
            evidence_needed=evidence_needed,
        )


# ---------------------------------------------------------------------------
# Unit 3 — Semiotic Parser
# ---------------------------------------------------------------------------

class SemioticParser:
    """Decompose the دال (signifier) and المدلول (signified)."""

    _ONTOLOGICAL_KEYWORDS = {
        "صفة معرفية": ["يقين", "ظن", "شك", "علم"],
        "فعل": ["قال", "فعل", "أكل", "كتب", "ذهب"],
        "مفهوم مجرد": ["حضارة", "ثقافة", "عدالة", "حرية", "قيمة"],
        "حالة إنسانية": ["معرفة", "إدراك", "تفكير", "فهم"],
        "اسم جنس": ["إنسان", "حيوان", "نبات", "معدن"],
    }

    def __call__(
        self,
        decoder_input: DecoderInput,
        reality: RealityExtractionResult,
        context: Optional[Dict[str, Any]] = None,
    ) -> SemioticMap:
        words = decoder_input.query.split()
        signifiers: List[SignifierEntry] = []

        for word in words:
            clean = word.strip("؟!,.،\"'")
            if len(clean) < 2:
                continue

            # Determine ontological type
            ont_type = "لفظ عام"
            for label, keywords in self._ONTOLOGICAL_KEYWORDS.items():
                if clean in keywords:
                    ont_type = label
                    break

            # Determine semantic modes (default: مطابقة always present)
            modes = ["مطابقة"]
            if ont_type in ("مفهوم مجرد", "حالة إنسانية"):
                modes.append("التزام")
            if len(clean) > 4:
                modes.append("تضمن")

            signifiers.append(
                SignifierEntry(
                    text=clean,
                    dal_type="لفظ مفرد",
                    madlul_type=ont_type,
                    semantic_mode=modes,
                    ontological_type=ont_type,
                    lexical_category="haqiqa",
                )
            )

        return SemioticMap(signifiers=signifiers)


# ---------------------------------------------------------------------------
# Unit 4 — Relation Graph Builder
# ---------------------------------------------------------------------------

class RelationGraphBuilder:
    """Build the semantic-relational graph among sentence components."""

    _DEFAULT_RELATIONS = [
        RelationEdge(
            from_node="واقع",
            relation="ينقل عبر",
            to_node="حس",
            relation_type="sababiyya",
            carrier_operator="cognitive_process",
        ),
        RelationEdge(
            from_node="حس",
            relation="يفسر بواسطة",
            to_node="معلومات سابقة",
            relation_type="isnad",
            carrier_operator="nominal_sentence",
        ),
        RelationEdge(
            from_node="ربط",
            relation="ينتج",
            to_node="فكر",
            relation_type="sababiyya",
            carrier_operator="cause_tool",
        ),
        RelationEdge(
            from_node="فكر مطابق للواقع عن دليل قطعي",
            relation="ينتج",
            to_node="يقين",
            relation_type="sababiyya",
            carrier_operator="cause_tool",
        ),
    ]

    def __call__(
        self,
        semiotic_map: SemioticMap,
        reality: RealityExtractionResult,
        context: Optional[Dict[str, Any]] = None,
    ) -> RelationGraph:
        # Start with the cognitive-pipeline default relations
        relations = list(self._DEFAULT_RELATIONS)

        # Add subject→predicate pairs from signifiers (simplified)
        prev: Optional[str] = None
        for entry in semiotic_map.signifiers:
            if prev is not None:
                relations.append(
                    RelationEdge(
                        from_node=prev,
                        relation="مرتبط بـ",
                        to_node=entry.text,
                        relation_type="isnad",
                        carrier_operator="nominal_sentence",
                        certainty_rank="zanni",
                    )
                )
            prev = entry.text

        # Add reality objects as root nodes
        for obj in reality.reality_objects[:3]:
            relations.append(
                RelationEdge(
                    from_node=obj,
                    relation="ينتمي إلى واقع",
                    to_node=reality.reality_type,
                    relation_type="isnad",
                    carrier_operator="nominal_sentence",
                    certainty_rank="zanni",
                )
            )

        return RelationGraph(relations=relations, unresolved=[])


# ---------------------------------------------------------------------------
# Unit 5 — Evidence Retriever
# ---------------------------------------------------------------------------

class EvidenceRetriever:
    """Gather evidence for the claim from available knowledge sources.

    In this reference implementation the retriever is a structured stub.
    Override :meth:`_retrieve_from_backend` to integrate real data sources
    (files, web, vector stores, etc.).
    """

    def __call__(
        self,
        reality: RealityExtractionResult,
        relation_graph: RelationGraph,
        context: Optional[Dict[str, Any]] = None,
    ) -> EvidenceBundle:
        items: List[EvidenceItem] = []

        # Add a stub evidence item for each reality object (at least one call)
        objects = reality.reality_objects[:3] or [reality.reality_type or "general"]
        for obj in objects:
            retrieved = self._retrieve_from_backend(obj, reality.reality_type)
            items.extend(retrieved)

        # Always include a policy-based item for epistemic framing
        items.append(
            EvidenceItem(
                source="decoder_policy.md",
                content="القاعدة الحاكمة: لا فكر بلا واقع، ولا يقين بلا دليل.",
                strength="high",
                source_type="text",
            )
        )

        return EvidenceBundle(items=items)

    def _retrieve_from_backend(
        self, entity: str, reality_type: str
    ) -> List[EvidenceItem]:
        """Stub: return a placeholder evidence item.

        Override this method to integrate real retrieval backends.
        """
        return [
            EvidenceItem(
                source=f"knowledge_base:{entity}",
                content=f"معلومة مسترجعة عن: {entity} (نوع الواقع: {reality_type})",
                strength="medium",
                source_type="database",
            )
        ]


# ---------------------------------------------------------------------------
# Unit 6 — Certainty Scorer
# ---------------------------------------------------------------------------

class CertaintyScorer:
    """Assign an epistemic certainty score to each candidate thought."""

    _LEVEL_LABELS = [
        (7, "يقين"),
        (6, "معرفة صحيحة"),
        (5, "معرفة راجحة"),
        (4, "فكر محتمل"),
        (3, "ربط أولي"),
        (2, "معلومة بلا تحقق"),
        (1, "إحساس بلا تفسير"),
        (0, "لفظ بلا واقع"),
    ]

    def __call__(
        self,
        thought: str,
        evidence: EvidenceBundle,
        reality: RealityExtractionResult,
        relation_graph: RelationGraph,
        context: Optional[Dict[str, Any]] = None,
    ) -> CertaintyScore:
        score = CertaintyScore(claim=thought)

        # Reality grounded?
        score.reality_grounded = reality.reality_type not in ("unknown", "")

        # Evidence present?
        high_evidence = [e for e in evidence.items if e.strength == "high"]
        score.evidence_present = len(high_evidence) > 0

        # Compute factor scores
        linguistic_coherence = 0.8
        reality_match = 0.85 if score.reality_grounded else 0.3
        evidence_strength = min(1.0, len(high_evidence) * 0.4 + len(evidence.items) * 0.1)
        semantic_validity = 0.9 if score.reality_grounded else 0.5
        inference_validity = 0.85 if len(relation_graph.relations) >= 2 else 0.4
        certainty_clarity = 0.8 if score.reality_grounded and score.evidence_present else 0.4
        hallucination_risk = 0.1 if score.reality_grounded and score.evidence_present else 0.6

        score.semantic_clarity = round(semantic_validity, 4)
        score.inference_validity = round(inference_validity, 4)
        score.hallucination_risk = round(hallucination_risk, 4)

        score.compute_score(
            linguistic_coherence=linguistic_coherence,
            reality_match=reality_match,
            evidence_strength=evidence_strength,
            semantic_validity=semantic_validity,
            inference_validity=inference_validity,
            certainty_clarity=certainty_clarity,
            hallucination_risk=hallucination_risk,
        )

        # Map to level
        level_number = 0
        label = "لفظ بلا واقع"
        for threshold, lbl in self._LEVEL_LABELS:
            if score.answer_score >= threshold * 0.1:
                level_number = threshold
                label = lbl
                break

        score.certainty_level = label
        score.level_number = level_number

        return score


# ---------------------------------------------------------------------------
# Unit 7 — Answer Decoder
# ---------------------------------------------------------------------------

class AnswerDecoder:
    """Compose the final constrained answer from verified thoughts.

    Answers only what is known with sufficient certainty, explicitly
    states limits, and refuses to output hallucinated content.
    """

    def __call__(
        self,
        verified_thoughts: List[VerifiedThought],
        task: TaskAnalysis,
        reality: RealityExtractionResult,
        evidence: EvidenceBundle,
        uncertainty_policy: str = "state_limits_clearly",
    ) -> DecoderOutput:
        output = DecoderOutput(verified_thoughts=verified_thoughts)

        if not verified_thoughts:
            output.blocked = True
            output.block_reason = (
                "لا يوجد فكر محقق يتجاوز عتبة اليقين المطلوبة. "
                "الجواب مرفوض لعدم توفر دليل كافٍ."
            )
            output.final_answer = (
                "[الديكودر المعرفي] لا يمكن إصدار جواب: "
                + output.block_reason
            )
            return output

        # Aggregate results
        best = max(verified_thoughts, key=lambda vt: vt.score.answer_score)
        output.certainty_level = best.score.certainty_level
        output.answer_score = best.score.answer_score

        output.known = [vt.claim for vt in verified_thoughts]
        output.uncertain = []
        output.needs_verification = []

        # Build the final answer text
        lines = [
            f"[الديكودر المعرفي] النتيجة المعرفية:",
            f"",
            f"• نوع الواقع: {reality.reality_type}",
            f"• درجة اليقين: {output.certainty_level}",
            f"• نقاط الثقة: {output.answer_score:.2f} / 1.00",
            f"",
            "ما يُعرف بثقة:",
        ]
        for claim in output.known:
            lines.append(f"  ✓ {claim}")

        if output.uncertain:
            lines.append("\nما يحتاج مزيداً من التحقق:")
            for u in output.uncertain:
                lines.append(f"  ? {u}")

        output.final_answer = "\n".join(lines)
        return output
