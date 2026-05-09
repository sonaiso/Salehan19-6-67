"""CognitiveReasoningMind — العقل المعرفي المستدل.

This module implements the top-level cognitive system described in the
Nabhani-grounded epistemological specification.  It integrates all sub-systems:

    Unicode Seed Encoder       (Φ function)
    Role Vectorizer            (Ρ function)
    Arabic Morphology Analyzer
    Fractal Composer           (N_{level+1} = Compose(...))
    Three-Layer Memory         (Atomic / Relational / Conceptual)
    Multi-Dimensional Certainty Scorer (9-dimension formula)

The system operates in two modes:

**Knower mode** (``allow_learning=False``, default)
    Uses existing memory to reason from verified knowledge.  No memory
    updates are performed.

**Learner mode** (``allow_learning=True``)
    Reasons as above, then updates relation weights and concept certainties
    when new evidence supports a change.  New concepts are promoted to
    Conceptual Memory when they pass the knowledge threshold.

The full pipeline is:

    Input Text / Reality Signal
    ↓  perceive()      → Unicode normalisation + atom encoding + role vectors
    ↓  compose()       → fractal composition (atoms → concepts)
    ↓  reason()        → evidence gate + certainty scoring → verified nodes
    ↓  learn()         → memory update (learner mode only)
    ↓  answer()        → structured output
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from bayani.cognitive.arabic_morphology import ArabicMorphologyAnalyzer, strip_diacritics
from bayani.cognitive.certainty import CertaintyResult, MultiDimensionalCertaintyScorer
from bayani.cognitive.fractal_composer import FractalComposer
from bayani.cognitive.knowledge_node import CertaintyInfo, KnowledgeNode, NodeLevel
from bayani.cognitive.memory import ThreeLayerMemory
from bayani.cognitive.role_vectorizer import RoleVectorizer
from bayani.cognitive.unicode_encoder import UnicodeAtomicEncoder


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

_KNOWLEDGE_THRESHOLD = 0.60    # minimum score to accept as knowledge
_LEARNING_THRESHOLD = 0.75     # minimum score to store as verified relation
_WEAK_THRESHOLD = 0.40         # below this → mark as weak / suspend

# Maximum number of word-level nodes appended to higher-level candidates.
# Prevents the candidate list from growing unboundedly on long sentences while
# still surfacing the most important morphological claims.
_MAX_WORD_CANDIDATES = 6


# ---------------------------------------------------------------------------
# Output dataclass
# ---------------------------------------------------------------------------

@dataclass
class MindOutput:
    """Structured output of one :meth:`CognitiveReasoningMind.reason` call."""

    raw_input: str
    mode: str                               # "knower" | "learner"

    # Pipeline intermediate results
    atom_nodes: List[KnowledgeNode] = field(default_factory=list)
    levels: Dict[str, List[KnowledgeNode]] = field(default_factory=dict)
    certainty_results: List[CertaintyResult] = field(default_factory=list)

    # Epistemic outputs
    verified: List[KnowledgeNode] = field(default_factory=list)
    suspended: List[KnowledgeNode] = field(default_factory=list)
    learned: List[str] = field(default_factory=list)    # entry_ids added/updated

    # Final answer
    answer: str = ""
    overall_certainty: float = 0.0
    certainty_label: str = ""

    # Memory snapshot (optional, filled on request)
    memory_snapshot: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class CognitiveReasoningMind:
    """The Cognitive Reasoning Mind — simulated epistemic agent.

    Parameters
    ----------
    knowledge_threshold:
        Minimum certainty score for a node to be accepted as knowledge.
        Default: 0.60.
    learning_threshold:
        Minimum score for a node to be stored back to memory in learner mode.
        Default: 0.75.
    memory:
        Optional pre-populated :class:`~bayani.cognitive.memory.ThreeLayerMemory`.
        If not supplied, a fresh empty memory is created.

    Usage::

        mind = CognitiveReasoningMind()

        # Knower mode (default)
        output = mind.reason("كتب الطالب الدرس")
        print(output.answer)
        print(output.overall_certainty)

        # Learner mode
        output = mind.reason(
            "شبكة الحاسوب مترابطة",
            external_evidence=["repeated_digital_contexts"],
            allow_learning=True,
        )
        print(output.learned)
    """

    def __init__(
        self,
        knowledge_threshold: float = _KNOWLEDGE_THRESHOLD,
        learning_threshold: float = _LEARNING_THRESHOLD,
        memory: Optional[ThreeLayerMemory] = None,
    ) -> None:
        self._encoder = UnicodeAtomicEncoder()
        self._role_vectorizer = RoleVectorizer()
        self._morphology = ArabicMorphologyAnalyzer()
        self._composer = FractalComposer()
        self._scorer = MultiDimensionalCertaintyScorer()
        self.memory = memory or ThreeLayerMemory()
        self.knowledge_threshold = knowledge_threshold
        self.learning_threshold = learning_threshold

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reason(
        self,
        raw_input: str,
        external_evidence: Optional[List[str]] = None,
        allow_learning: bool = False,
    ) -> MindOutput:
        """Run the full cognitive pipeline on *raw_input*.

        Parameters
        ----------
        raw_input:
            Arabic (or mixed) text to process.
        external_evidence:
            Optional list of evidence strings / source labels from outside
            the current session (e.g. repeated corpus contexts, document refs).
        allow_learning:
            When True, the mind operates in **learner mode** and updates its
            memory based on the verified results.

        Returns
        -------
        MindOutput
            Structured pipeline output including verified nodes, certainty
            scores, learned entries, and a natural-language answer.
        """
        mode = "learner" if allow_learning else "knower"

        # ---- Step 1: Perceive (Unicode → atoms with role vectors) ----
        atom_nodes = self._perceive(raw_input)

        # ---- Step 2: Fractal composition ----
        levels = self._composer.compose_all(
            atom_nodes, context=raw_input, external_evidence=external_evidence or []
        )

        # ---- Step 3: Build candidate claims from concept/sentence nodes ----
        candidates = self._build_candidates(levels, raw_input, external_evidence or [])

        # ---- Step 4: Evidence gate + certainty scoring ----
        verified: List[KnowledgeNode] = []
        suspended: List[KnowledgeNode] = []
        certainty_results: List[CertaintyResult] = []

        for node in candidates:
            cert_result = self._score_node(node, raw_input, external_evidence or [])
            certainty_results.append(cert_result)
            node.certainty = CertaintyInfo(
                score=cert_result.final_certainty,
                evidence_type=node.certainty.evidence_type,
                status=cert_result.status,
                dimensional_scores=cert_result.to_dict()["scores"],
            )
            if cert_result.passes_threshold(self.knowledge_threshold):
                verified.append(node)
            else:
                node.metadata["suspension_reason"] = (
                    f"score {cert_result.final_certainty:.3f} < threshold {self.knowledge_threshold}"
                )
                suspended.append(node)

        # ---- Step 5: Learn (update memory if in learner mode) ----
        learned: List[str] = []
        if allow_learning:
            learned = self._learn(verified, suspended, raw_input)

        # ---- Step 6: Compose answer ----
        answer, overall_cert = self._compose_answer(verified, suspended, raw_input)
        cert_node = CertaintyInfo(score=overall_cert)

        output = MindOutput(
            raw_input=raw_input,
            mode=mode,
            atom_nodes=atom_nodes,
            levels=levels,
            certainty_results=certainty_results,
            verified=verified,
            suspended=suspended,
            learned=learned,
            answer=answer,
            overall_certainty=overall_cert,
            certainty_label=cert_node.label,
        )
        return output

    # ------------------------------------------------------------------
    # Step 1 — Perceive
    # ------------------------------------------------------------------

    def _perceive(self, raw_input: str) -> List[KnowledgeNode]:
        """Encode every character in *raw_input* to an atom node with role vector."""
        atom_nodes: List[KnowledgeNode] = []
        words = raw_input.split()

        for word_idx, word in enumerate(words):
            stripped = strip_diacritics(word)
            word_atoms: List[KnowledgeNode] = []

            for char_idx, ch in enumerate(word):
                node_id = f"atom-{word_idx}-{char_idx}-{ord(ch):04X}"
                node = self._encoder.to_node(ch, node_id=node_id)
                node.metadata["word_index"] = word_idx
                node.metadata["char_index"] = char_idx
                node.metadata["word_surface"] = word

                # Cache atom in memory
                self.memory.store_atom(
                    ch,
                    features=node.features,
                    role_vector=node.role_vector,
                )
                word_atoms.append(node)

            # Assign role vectors to atoms within this word's context
            is_particle = len(stripped) == 1
            self._role_vectorizer.assign_roles(
                word_atoms,
                word_surface=stripped,
                position_in_sentence=word_idx,
                is_standalone_particle=is_particle,
            )
            atom_nodes.extend(word_atoms)

        return atom_nodes

    # ------------------------------------------------------------------
    # Step 3 — Build candidate claims
    # ------------------------------------------------------------------

    def _build_candidates(
        self,
        levels: Dict[str, List[KnowledgeNode]],
        raw_input: str,
        evidence: List[str],
    ) -> List[KnowledgeNode]:
        """Collect candidate nodes from the highest meaningful level."""
        # Prefer concept nodes, fall back to sentence, phrase, word
        for level_key in ("concepts", "sentences", "phrases", "words"):
            nodes = levels.get(level_key, [])
            if nodes:
                # Also include word-level morphological claims
                claims = list(nodes)
                if level_key != "words":
                    claims = list(nodes) + levels.get("words", [])[:_MAX_WORD_CANDIDATES]
                return claims
        return []

    # ------------------------------------------------------------------
    # Step 4 — Score a single candidate node
    # ------------------------------------------------------------------

    def _score_node(
        self,
        node: KnowledgeNode,
        context: str,
        evidence: List[str],
    ) -> CertaintyResult:
        """Compute a 9-dimension certainty score for *node*."""
        # Unicode integrity: always 1.0 (we encoded from real text)
        unicode_integrity = 1.0

        # Morphological fit: from existing certainty if morphological
        morph_fit = 0.0
        if node.level in (NodeLevel.WORD, NodeLevel.ROOT, NodeLevel.PATTERN):
            morph_fit = node.certainty.score
        elif node.level in (NodeLevel.PHRASE, NodeLevel.SENTENCE):
            morph_fit = node.certainty.score * 0.85

        # Syntactic fit: higher for sentence-level nodes
        syntactic_fit = {
            NodeLevel.ATOM: 0.30,
            NodeLevel.SYLLABLE: 0.40,
            NodeLevel.ROOT: 0.55,
            NodeLevel.PATTERN: 0.60,
            NodeLevel.WORD: 0.65,
            NodeLevel.PHRASE: 0.75,
            NodeLevel.SENTENCE: 0.85,
            NodeLevel.CONCEPT: 0.80,
            NodeLevel.CLAIM: 0.70,
        }.get(node.level, 0.50)

        # Semantic fit: from node's existing score (fractal composer set it)
        semantic_fit = node.certainty.score * 0.80

        # Context fit: simple keyword overlap
        context_fit = self._context_overlap(node.surface, context)

        # Evidence strength: from external evidence list
        evidence_strength = min(1.0, 0.50 + 0.10 * len(evidence))

        # Reality match: from node level (concept = real, atom = not yet)
        reality_match = {
            NodeLevel.ATOM: 0.10,
            NodeLevel.SYLLABLE: 0.20,
            NodeLevel.ROOT: 0.45,
            NodeLevel.PATTERN: 0.50,
            NodeLevel.WORD: 0.60,
            NodeLevel.PHRASE: 0.70,
            NodeLevel.SENTENCE: 0.80,
            NodeLevel.CONCEPT: 0.85,
        }.get(node.level, 0.50)

        # Ambiguity: higher if node has many relations suggesting multiple analyses
        ambiguity_penalty = min(0.40, 0.05 * len(node.relations))

        # Contradiction: 0 unless explicitly marked
        contradiction_penalty = 0.0

        return self._scorer.score(
            claim=f"{node.level.value}:{node.surface[:40]}",
            unicode_integrity=unicode_integrity,
            morphological_fit=morph_fit,
            syntactic_fit=syntactic_fit,
            semantic_fit=semantic_fit,
            context_fit=context_fit,
            evidence_strength=evidence_strength,
            reality_match=reality_match,
            ambiguity_penalty=ambiguity_penalty,
            contradiction_penalty=contradiction_penalty,
        )

    # ------------------------------------------------------------------
    # Step 5 — Learn
    # ------------------------------------------------------------------

    def _learn(
        self,
        verified: List[KnowledgeNode],
        suspended: List[KnowledgeNode],
        context: str,
    ) -> List[str]:
        """Update memory from verified (and weakly from suspended) nodes."""
        learned: List[str] = []

        for node in verified:
            if node.certainty.score >= self.learning_threshold:
                # Store root to relational memory
                if node.level == NodeLevel.ROOT:
                    entry_id = f"root:{node.surface}"
                    self.memory.store_relation(
                        entry_id,
                        "root",
                        node.surface,
                        certainty=node.certainty.score,
                        evidence=[context[:60]],
                    )
                    learned.append(entry_id)

                # Store concept to conceptual memory
                elif node.level in (NodeLevel.CONCEPT, NodeLevel.SENTENCE):
                    concept_id = f"concept:{node.surface[:30]}"
                    self.memory.store_concept(
                        concept_id,
                        node.surface[:30],
                        certainty=node.certainty.score,
                        evidence=[context[:60]],
                    )
                    learned.append(concept_id)

                # For word-level, update existing relations
                elif node.level == NodeLevel.WORD:
                    best_root = node.features.get("best_root")
                    if best_root:
                        entry_id = f"root:{best_root}"
                        existing = self.memory.get_relation(entry_id)
                        if existing:
                            self.memory.update_relation_certainty(
                                entry_id, delta=+0.02
                            )
                        else:
                            self.memory.store_relation(
                                entry_id,
                                "root",
                                best_root,
                                certainty=node.certainty.score * 0.85,
                                evidence=[context[:60]],
                            )
                        learned.append(entry_id)

        # Mark suspended nodes as weak in relational memory
        for node in suspended:
            if node.level == NodeLevel.ROOT:
                entry_id = f"root:{node.surface}"
                if self.memory.get_relation(entry_id):
                    self.memory.mark_relation_weak(entry_id)

        return list(set(learned))

    # ------------------------------------------------------------------
    # Step 6 — Compose answer
    # ------------------------------------------------------------------

    def _compose_answer(
        self,
        verified: List[KnowledgeNode],
        suspended: List[KnowledgeNode],
        raw_input: str,
    ) -> Tuple[str, float]:
        """Build a structured Arabic answer from verified nodes."""
        if not verified and not suspended:
            return "لم يتمكن النظام من معالجة المدخل.", 0.0

        parts: List[str] = []
        scores: List[float] = []

        # Verified concepts and sentences
        for node in verified:
            if node.level in (NodeLevel.CONCEPT, NodeLevel.SENTENCE):
                score = node.certainty.score
                label = node.certainty.label
                parts.append(
                    f"[{label} — {score:.0%}] {node.surface}"
                )
                scores.append(score)

        # Verified word-level morphological claims
        word_claims: List[str] = []
        for node in verified:
            if node.level == NodeLevel.WORD:
                root = node.features.get("best_root", "")
                pattern = node.features.get("best_pattern", "")
                score = node.certainty.score
                scores.append(score)
                if root or pattern:
                    word_claims.append(
                        f"  • «{node.surface}»"
                        + (f" جذره «{root}»" if root else "")
                        + (f" على وزن «{pattern}»" if pattern else "")
                        + f" (يقين {score:.0%})"
                    )

        if word_claims:
            parts.append("التحليل الصرفي:")
            parts.extend(word_claims)

        # Suspended
        if suspended:
            sus_labels = [n.surface[:20] for n in suspended[:3]]
            parts.append(
                "حالات مُعلَّقة (تحتاج دليلًا أقوى): "
                + "، ".join(sus_labels)
            )

        overall = sum(scores) / max(len(scores), 1) if scores else 0.0
        answer = "\n".join(parts) if parts else "النتائج غير كافية للحكم."
        return answer, round(overall, 4)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def _context_overlap(surface: str, context: str) -> float:
        """Simple word-overlap ratio between *surface* and *context*."""
        if not surface or not context:
            return 0.0
        surf_words = set(strip_diacritics(surface).split())
        ctx_words = set(strip_diacritics(context).split())
        if not surf_words:
            return 0.0
        overlap = surf_words & ctx_words
        return round(len(overlap) / len(surf_words), 4)

    def memory_snapshot(self) -> Dict[str, Any]:
        """Return a JSON-serialisable snapshot of the current memory state."""
        return self.memory.snapshot()
