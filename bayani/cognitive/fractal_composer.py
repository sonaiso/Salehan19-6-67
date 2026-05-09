"""FractalComposer — multi-level composition engine.

Implements the fractal composition principle:

    N_{level+1} = Compose(N_level[1..n], Relation, Context, Evidence)

Each call to :meth:`FractalComposer.compose` elevates a list of lower-level
:class:`~bayani.cognitive.knowledge_node.KnowledgeNode` objects to a single
higher-level node.  The same function signature applies at every level:

    atoms       → syllables
    syllables   → roots / patterns
    roots       → words
    words       → phrases
    phrases     → sentences
    sentences   → concepts

The composer does not produce semantic meaning — it produces structural
nodes with certainty scores that reflect how confident the system is in
each composition step.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from bayani.cognitive.arabic_morphology import ArabicMorphologyAnalyzer
from bayani.cognitive.certainty import MultiDimensionalCertaintyScorer
from bayani.cognitive.knowledge_node import (
    CertaintyInfo,
    KnowledgeNode,
    NodeLevel,
    NodeRelation,
)


_morphology = ArabicMorphologyAnalyzer()
_scorer = MultiDimensionalCertaintyScorer()


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


class FractalComposer:
    """Compose lower-level KnowledgeNodes into higher-level nodes.

    Usage::

        composer = FractalComposer()
        levels = composer.compose_all(atoms, context="كتب الطالب الدرس")
    """

    # ------------------------------------------------------------------
    # Level-1: atoms → syllables
    # ------------------------------------------------------------------

    def compose_syllables(
        self, atoms: List[KnowledgeNode], context: str = ""
    ) -> List[KnowledgeNode]:
        """Group atom nodes into syllable-level nodes.

        A syllable is formed by grouping consonant atoms with their
        immediately following vowel (diacritic or long vowel).
        """
        syllables: List[KnowledgeNode] = []
        current_letters: List[KnowledgeNode] = []

        for atom in atoms:
            sym_class = atom.features.get("class", "other")
            current_letters.append(atom)

            # A consonant followed by nothing more, or a long vowel, closes a syllable
            if sym_class in ("consonant", "long_vowel"):
                # Peek-ahead for diacritics
                syllable_node = self._make_syllable(current_letters)
                syllables.append(syllable_node)
                current_letters = []

        # Flush remaining atoms
        if current_letters:
            syllables.append(self._make_syllable(current_letters))

        return syllables

    # ------------------------------------------------------------------
    # Level-2: syllables (or atoms) → roots + patterns
    # ------------------------------------------------------------------

    def compose_roots(
        self, word_surface: str, context: str = ""
    ) -> List[KnowledgeNode]:
        """Extract root-level nodes from a word surface form."""
        analysis = _morphology.analyze(word_surface)
        nodes: List[KnowledgeNode] = []

        for rc in analysis.root_candidates:
            cert_result = _scorer.score_morphological_claim(
                claim=f"root:{rc.root}",
                root_cert=rc.certainty,
                pattern_cert=analysis.pattern_matches[0].certainty
                if analysis.pattern_matches else 0.40,
                context_evidence=0.50,
            )
            node = KnowledgeNode(
                node_id=_new_id("root"),
                level=NodeLevel.ROOT,
                surface=rc.root,
                features={
                    "letters": rc.letters,
                    "notes": rc.notes,
                },
                certainty=CertaintyInfo(
                    score=cert_result.final_certainty,
                    evidence_type="morphological",
                    status=cert_result.status,
                    dimensional_scores=cert_result.to_dict()["scores"],
                ),
                metadata={"word_source": word_surface},
            )
            nodes.append(node)

        return nodes

    def compose_patterns(
        self, word_surface: str, context: str = ""
    ) -> List[KnowledgeNode]:
        """Extract morphological pattern (وزن) nodes from a word surface form."""
        analysis = _morphology.analyze(word_surface)
        nodes: List[KnowledgeNode] = []

        for pm in analysis.pattern_matches:
            node = KnowledgeNode(
                node_id=_new_id("pattern"),
                level=NodeLevel.PATTERN,
                surface=pm.pattern_label,
                features={"description": pm.description},
                certainty=CertaintyInfo(
                    score=pm.certainty,
                    evidence_type="morphological",
                    status="probable" if pm.certainty < 0.85 else "verified",
                ),
                metadata={"word_source": word_surface},
            )
            nodes.append(node)

        return nodes

    # ------------------------------------------------------------------
    # Level-3: roots + patterns → word
    # ------------------------------------------------------------------

    def compose_word(
        self,
        word_surface: str,
        root_nodes: List[KnowledgeNode],
        pattern_nodes: List[KnowledgeNode],
        context: str = "",
    ) -> KnowledgeNode:
        """Compose a word-level node from root and pattern nodes."""
        analysis = _morphology.analyze(word_surface)

        root_cert = root_nodes[0].certainty.score if root_nodes else 0.40
        pattern_cert = pattern_nodes[0].certainty.score if pattern_nodes else 0.40

        cert_result = _scorer.score(
            claim=f"word:{word_surface}",
            unicode_integrity=1.0,
            morphological_fit=(root_cert + pattern_cert) / 2,
            syntactic_fit=0.60,   # placeholder — would need sentence context
            semantic_fit=root_cert * 0.6,
            context_fit=0.50,
            evidence_strength=pattern_cert,
            reality_match=0.50,
            ambiguity_penalty=max(0.0, 0.5 - root_cert),
            contradiction_penalty=0.0,
        )

        node = KnowledgeNode(
            node_id=_new_id("word"),
            level=NodeLevel.WORD,
            surface=word_surface,
            features={
                "normalized": analysis.normalized,
                "best_root": analysis.best_root,
                "best_pattern": analysis.best_pattern,
                "segmentation": {
                    "prefix": analysis.segmentation.prefix if analysis.segmentation else "",
                    "stem": analysis.segmentation.stem if analysis.segmentation else word_surface,
                    "suffix": analysis.segmentation.suffix if analysis.segmentation else "",
                },
            },
            certainty=CertaintyInfo(
                score=cert_result.final_certainty,
                evidence_type="morphological",
                status=cert_result.status,
                dimensional_scores=cert_result.to_dict()["scores"],
            ),
        )

        # Link to root and pattern nodes
        for rn in root_nodes:
            node.add_relation("has_root", rn.node_id, rn.certainty.score)
        for pn in pattern_nodes:
            node.add_relation("has_pattern", pn.node_id, pn.certainty.score)

        return node

    # ------------------------------------------------------------------
    # Level-4: words → phrase
    # ------------------------------------------------------------------

    def compose_phrase(
        self,
        words: List[KnowledgeNode],
        phrase_type: str = "unknown",
        context: str = "",
    ) -> KnowledgeNode:
        """Compose a phrase-level node from word nodes."""
        surface = " ".join(w.surface for w in words)
        avg_cert = sum(w.certainty.score for w in words) / max(len(words), 1)

        cert_result = _scorer.score(
            claim=f"phrase:{surface}",
            unicode_integrity=1.0,
            morphological_fit=avg_cert,
            syntactic_fit=avg_cert * 0.9,
            semantic_fit=avg_cert * 0.7,
            context_fit=0.55,
            evidence_strength=avg_cert * 0.8,
            reality_match=avg_cert * 0.6,
            ambiguity_penalty=0.10,
            contradiction_penalty=0.0,
        )

        node = KnowledgeNode(
            node_id=_new_id("phrase"),
            level=NodeLevel.PHRASE,
            surface=surface,
            features={"phrase_type": phrase_type, "word_count": len(words)},
            certainty=CertaintyInfo(
                score=cert_result.final_certainty,
                evidence_type="syntactic",
                status=cert_result.status,
            ),
        )
        for w in words:
            node.add_relation("contains_word", w.node_id, w.certainty.score)

        return node

    # ------------------------------------------------------------------
    # Level-5: phrases → sentence
    # ------------------------------------------------------------------

    def compose_sentence(
        self,
        phrases: List[KnowledgeNode],
        sentence_surface: str = "",
        context: str = "",
    ) -> KnowledgeNode:
        """Compose a sentence-level node from phrase nodes."""
        surface = sentence_surface or " ".join(p.surface for p in phrases)
        avg_cert = sum(p.certainty.score for p in phrases) / max(len(phrases), 1)

        cert_result = _scorer.score(
            claim=f"sentence:{surface[:40]}",
            unicode_integrity=1.0,
            morphological_fit=avg_cert,
            syntactic_fit=avg_cert * 0.95,
            semantic_fit=avg_cert * 0.75,
            context_fit=0.60,
            evidence_strength=avg_cert * 0.85,
            reality_match=avg_cert * 0.65,
            ambiguity_penalty=0.08,
            contradiction_penalty=0.0,
        )

        node = KnowledgeNode(
            node_id=_new_id("sentence"),
            level=NodeLevel.SENTENCE,
            surface=surface,
            features={"phrase_count": len(phrases)},
            certainty=CertaintyInfo(
                score=cert_result.final_certainty,
                evidence_type="syntactic",
                status=cert_result.status,
            ),
        )
        for ph in phrases:
            node.add_relation("contains_phrase", ph.node_id, ph.certainty.score)

        return node

    # ------------------------------------------------------------------
    # Level-6: sentences → concept
    # ------------------------------------------------------------------

    def compose_concept(
        self,
        sentences: List[KnowledgeNode],
        external_evidence: Optional[List[str]] = None,
        context: str = "",
    ) -> KnowledgeNode:
        """Compose a concept-level node from sentence nodes."""
        evidence = external_evidence or []
        avg_cert = sum(s.certainty.score for s in sentences) / max(len(sentences), 1)
        ev_strength = min(1.0, avg_cert + 0.05 * len(evidence))

        cert_result = _scorer.score(
            claim=f"concept from {len(sentences)} sentences",
            unicode_integrity=1.0,
            morphological_fit=avg_cert,
            syntactic_fit=avg_cert,
            semantic_fit=avg_cert * 0.85,
            context_fit=0.65,
            evidence_strength=ev_strength,
            reality_match=avg_cert * 0.75,
            ambiguity_penalty=0.05,
            contradiction_penalty=0.0,
        )

        surface = "; ".join(s.surface[:30] for s in sentences[:3])
        node = KnowledgeNode(
            node_id=_new_id("concept"),
            level=NodeLevel.CONCEPT,
            surface=surface,
            features={"sentence_count": len(sentences)},
            evidence=evidence,
            certainty=CertaintyInfo(
                score=cert_result.final_certainty,
                evidence_type="semantic",
                status=cert_result.status,
            ),
        )
        for s in sentences:
            node.add_relation("derives_from", s.node_id, s.certainty.score)

        return node

    # ------------------------------------------------------------------
    # Full pipeline convenience method
    # ------------------------------------------------------------------

    def compose_all(
        self,
        atoms: List[KnowledgeNode],
        context: str = "",
        external_evidence: Optional[List[str]] = None,
    ) -> Dict[str, List[KnowledgeNode]]:
        """Run the full fractal composition pipeline on atom nodes.

        Returns a dict keyed by level name.
        """
        levels: Dict[str, List[KnowledgeNode]] = {"atoms": list(atoms)}

        # Syllables from atoms
        levels["syllables"] = self.compose_syllables(atoms, context)

        # Words: group atoms by word (split by spaces in context)
        words_surfaces = context.split() if context else []
        word_nodes: List[KnowledgeNode] = []
        for ws in words_surfaces:
            roots = self.compose_roots(ws, context)
            patterns = self.compose_patterns(ws, context)
            w_node = self.compose_word(ws, roots, patterns, context)
            word_nodes.append(w_node)

        levels["words"] = word_nodes

        # One phrase per pair of words (simplified)
        phrase_nodes: List[KnowledgeNode] = []
        for i in range(0, len(word_nodes), 2):
            chunk = word_nodes[i: i + 2]
            phrase_nodes.append(self.compose_phrase(chunk, context=context))
        levels["phrases"] = phrase_nodes

        # One sentence node
        if phrase_nodes:
            sent_node = self.compose_sentence(phrase_nodes, context, context)
            levels["sentences"] = [sent_node]
        else:
            levels["sentences"] = []

        # One concept node
        if levels["sentences"]:
            concept_node = self.compose_concept(
                levels["sentences"], external_evidence, context
            )
            levels["concepts"] = [concept_node]
        else:
            levels["concepts"] = []

        return levels

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _make_syllable(self, atoms: List[KnowledgeNode]) -> KnowledgeNode:
        surface = "".join(a.surface for a in atoms)
        avg_cert = sum(a.certainty.score for a in atoms) / max(len(atoms), 1)
        node = KnowledgeNode(
            node_id=_new_id("syl"),
            level=NodeLevel.SYLLABLE,
            surface=surface,
            features={"atom_count": len(atoms)},
            certainty=CertaintyInfo(
                score=round(avg_cert, 4),
                evidence_type="phonological",
                status="verified" if avg_cert >= 0.85 else "probable",
            ),
        )
        for a in atoms:
            node.add_relation("contains_atom", a.node_id, a.certainty.score)
        return node
