"""Epistemic Cognitive Decoder — main orchestrator.

This module implements the ``EpistemicCognitiveDecoder`` class which
orchestrates the seven pipeline units into a single cognitive decision
emulator that sits *above* a language model.

The decoder enforces the epistemic chain:

    واقع → حس/مصدر → معلومات → ربط → فكر → مطابقة → دليل → درجة يقين → جواب

No answer is produced without passing through every stage.

Usage::

    from bayani.epistemic_decoder.decoder import EpistemicCognitiveDecoder

    decoder = EpistemicCognitiveDecoder()
    output = decoder.decode("ما الفرق بين العلم والثقافة؟")
    print(output.final_answer)
    print(output.certainty_level)
    print(output.answer_score)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from bayani.epistemic_decoder.contracts import (
    DecoderInput,
    DecoderOutput,
    VerifiedThought,
)
from bayani.epistemic_decoder.units import (
    AnswerDecoder,
    CertaintyScorer,
    EvidenceRetriever,
    InputAnalyzer,
    RealityExtractor,
    RelationGraphBuilder,
    SemioticParser,
)


_KNOWLEDGE_THRESHOLD = 0.60


class EpistemicCognitiveDecoder:
    """Epistemic Cognitive Decoder — a knowledge-epistemic supervisor over LLMs.

    This class does **not** replace the language model's weights or
    architecture.  It acts as a *cognitive gate* that:

    1. Analyzes the input to identify task type, domain, and hallucination risk.
    2. Extracts the واقع (reality) the question addresses.
    3. Parses the signifiers (دال) and signified (مدلول).
    4. Builds the semantic-relational graph.
    5. Retrieves supporting evidence.
    6. Generates and scores candidate thoughts.
    7. Composes a final answer only from verified, sufficiently certain thoughts.

    Parameters
    ----------
    evidence_retriever:
        Optional custom :class:`~bayani.epistemic_decoder.units.EvidenceRetriever`.
        Pass a subclass to integrate real data sources (files, web, vector DB).
    knowledge_threshold:
        Minimum ``answer_score`` required for a candidate thought to be
        accepted as verified knowledge.  Default: 0.60.
    """

    def __init__(
        self,
        evidence_retriever: Optional[EvidenceRetriever] = None,
        knowledge_threshold: float = _KNOWLEDGE_THRESHOLD,
    ) -> None:
        self._analyze_input = InputAnalyzer()
        self._extract_reality = RealityExtractor()
        self._parse_signifiers = SemioticParser()
        self._build_relations = RelationGraphBuilder()
        self._retrieve_evidence = evidence_retriever or EvidenceRetriever()
        self._score_certainty = CertaintyScorer()
        self._decode_answer = AnswerDecoder()
        self.knowledge_threshold = knowledge_threshold

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def decode(
        self,
        user_query: str,
        context: str = "",
        reasoning_effort: str = "high",
    ) -> DecoderOutput:
        """Run the full epistemic pipeline for *user_query*.

        Parameters
        ----------
        user_query:
            The raw question or instruction from the user.
        context:
            Optional extra context (e.g. retrieved documents, conversation
            history) that enriches reality extraction and evidence retrieval.
        reasoning_effort:
            Maps to GPT-5.5 ``reasoning_effort`` levels.
            ``"low"`` | ``"medium"`` | ``"high"`` (default) | ``"xhigh"``.

        Returns
        -------
        DecoderOutput
            Full structured pipeline output including the final answer,
            certainty level, and score.
        """
        decoder_input = DecoderInput(
            query=user_query,
            context=context,
            reasoning_effort=reasoning_effort,
        )
        ctx: Dict[str, Any] = {}

        # ── Unit 1: Input Analyzer ─────────────────────────────────────
        task = self._analyze_input(decoder_input, ctx)
        ctx["task"] = task

        # ── Unit 2: Reality Extractor ──────────────────────────────────
        reality = self._extract_reality(task, decoder_input, ctx)
        ctx["reality"] = reality

        # ── Unit 3: Semiotic Parser ────────────────────────────────────
        semiotic_map = self._parse_signifiers(decoder_input, reality, ctx)
        ctx["semiotic_map"] = semiotic_map

        # ── Unit 4: Relation Graph Builder ─────────────────────────────
        relation_graph = self._build_relations(semiotic_map, reality, ctx)
        ctx["relation_graph"] = relation_graph

        # ── Unit 5: Evidence Retriever ─────────────────────────────────
        evidence = self._retrieve_evidence(reality, relation_graph, ctx)
        ctx["evidence"] = evidence

        # ── Unit 6: Certainty Scorer — for each candidate thought ──────
        candidate_thoughts = self._generate_candidate_thoughts(
            task=task,
            relation_graph=relation_graph,
            evidence=evidence,
        )

        verified_thoughts: List[VerifiedThought] = []
        for thought in candidate_thoughts:
            score = self._score_certainty(
                thought=thought,
                evidence=evidence,
                reality=reality,
                relation_graph=relation_graph,
                context=ctx,
            )
            if score.passes_threshold(self.knowledge_threshold):
                verified_thoughts.append(VerifiedThought(claim=thought, score=score))

        # ── Unit 7: Answer Decoder ─────────────────────────────────────
        output = self._decode_answer(
            verified_thoughts=verified_thoughts,
            task=task,
            reality=reality,
            evidence=evidence,
            uncertainty_policy="state_limits_clearly",
        )

        # Attach intermediate results for introspection / traceability
        output.task = task
        output.reality = reality
        output.semiotic_map = semiotic_map
        output.relation_graph = relation_graph
        output.evidence = evidence

        return output

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _generate_candidate_thoughts(
        self, task, relation_graph, evidence
    ) -> List[str]:
        """Generate candidate thoughts from the relation graph and evidence.

        In this reference implementation, candidate thoughts are derived
        from the relation graph edges and evidence items.  Override this
        method to integrate a real LLM generation step.
        """
        thoughts: List[str] = []

        # Derive a thought from each relation edge
        for edge in relation_graph.relations[:5]:
            thought = f"{edge.from_node} {edge.relation} {edge.to_node}"
            if thought not in thoughts:
                thoughts.append(thought)

        # Derive a thought from each evidence item
        for item in evidence.items[:3]:
            if item.content and item.content not in thoughts:
                thoughts.append(item.content)

        # Fallback: generate one generic thought from the task type
        if not thoughts:
            thoughts.append(
                f"السؤال من نوع '{task.task_type}' في مجال '{task.domain}'."
            )

        return thoughts
