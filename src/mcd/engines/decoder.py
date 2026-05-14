"""MinimalCognitiveDecoder — main pipeline entry point."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from mcd.engines.normalizer import ArabicNormalizer, NormalizationMode
from mcd.engines.unicode_vectorizer import UnicodeVectorizer
from mcd.engines.role_inferer import RoleInferer
from mcd.engines.pattern_matcher import PatternMatcher
from mcd.engines.fractal_composer import FractalComposer
from mcd.engines.relation_builder import RelationBuilder
from mcd.engines.evidence_gate import EvidenceGate
from mcd.engines.certainty_scorer import CertaintyScorer
from mcd.engines.reasoning_engine import ReasoningEngine, Claim
from mcd.engines.learning_engine import LearningEngine
from mcd.core.nodes import KnowledgeNode
from mcd.core.certainty import Certainty
from mcd.core.evidence import Evidence, EvidenceType


@dataclass
class DecoderOutput:
    input: str
    normalized: str
    unicode_vectors: list[dict]
    role_vectors: list[dict]
    nodes: list[dict]
    relations: list[dict]
    claims: list[dict]
    certainty: dict
    learning_actions: list[dict]
    answer: str


class MinimalCognitiveDecoder:

    def __init__(
        self,
        store=None,
        llm_adapter=None,
        allow_learning: bool = False,
    ) -> None:
        self._store = store
        self._llm = llm_adapter
        self._allow_learning = allow_learning

        self._normalizer = ArabicNormalizer()
        self._vectorizer = UnicodeVectorizer()
        self._role_inferer = RoleInferer()
        self._pattern_matcher = PatternMatcher()
        self._composer = FractalComposer()
        self._rel_builder = RelationBuilder(store=store)
        self._gate = EvidenceGate()
        self._scorer = CertaintyScorer()
        self._reasoner = ReasoningEngine(store=store)
        self._learner = LearningEngine(store=store)

    def decode(self, text: str, mode: str = "knower") -> DecoderOutput:
        # Step 1: Normalize
        normalized = self._normalizer.normalize(text, NormalizationMode.LIGHT)

        # Step 2: Vectorize Unicode
        char_vectors = self._vectorizer.vectorize_text(text)
        unicode_vectors = [{"char": c, **v.to_dict()} for c, v in char_vectors]

        # Step 3: Infer roles
        words = normalized.split()
        role_vectors_out = []
        for word in words:
            roles = self._role_inferer.infer_roles(word)
            for ch, rv in roles:
                role_vectors_out.append({"char": ch, "word": word, "roles": rv.to_dict(), "top_role": rv.top_role()})

        # Step 4: Pattern matching + build word nodes
        from mcd.knowledge.mishkat_root_lookup import lookup_root
        word_nodes: list[KnowledgeNode] = []
        for word in words:
            # Strip article before PatternMatcher so ال doesn't bleed into root
            pm_word = word[2:] if word.startswith('ال') and len(word) > 2 else word
            best = self._pattern_matcher.best_match(pm_word)
            features: dict = {}
            # Only trust PatternMatcher when certainty is meaningful (>= 0.65).
            # Below that threshold false positives outweigh true matches
            # (e.g. borrowed words accidentally matching افتعل structure).
            if best and best.get("certainty", 0) >= 0.65:
                features["pattern"] = best["pattern"]
                features["role"] = best["role"]
                features["semantic_hint"] = best["semantic_hint"]
                root = best.get("root", "")
                # ة is never a root letter — apply hollow inference same as lookup_root
                if root.endswith("ة"):
                    root = root[:-1]
                    if len(root) == 2:
                        root = root[0] + "و" + root[1]
                features["root"] = root
                cert_score = best["certainty"]
            else:
                # Four-layer root extractor (mishkat → audited → pattern → skeleton)
                mishkat_root = lookup_root(word)
                if mishkat_root:
                    features["root"] = mishkat_root
                    cert_score = 0.80
                else:
                    # Last resort: bare stem
                    stem = word
                    if stem.startswith('ال') and len(stem) > 2:
                        stem = stem[2:]
                    if stem.endswith('ة') and len(stem) > 1:
                        stem = stem[:-1]
                    features["root"] = stem
                    cert_score = 0.5

            # Check if word/stem is in prior store → boost certainty
            prior_boost = 0.0
            if self._store:
                for query in [word, word.replace('ال', '').strip(), features.get("root", "")]:
                    if query and self._store.query_things_by_name(query):
                        prior_boost = 0.30
                        break
                # Check facts
                if not prior_boost:
                    for q in [word, text]:
                        if self._store.facts.find_by_claim(q):
                            prior_boost = 0.25
                            break

            final_cert = min(1.0, cert_score + prior_boost)

            node = KnowledgeNode(
                node_id=f"word_{word}_{uuid.uuid4().hex[:6]}",
                level="word",
                surface=word,
                features=features,
                certainty=Certainty.from_score(final_cert, "morphological"),
            )
            word_nodes.append(node)

        # Step 5: Build relations
        relations = self._rel_builder.build_relations(text, word_nodes)

        # Step 6: Gate evidence
        # Build evidence from the text itself (linguistic evidence)
        text_evidence = [
            Evidence(
                source_id="text_input",
                source_type=EvidenceType.LINGUISTIC.value,
                description=f"Input text: {text}",
                strength=0.70,
                reliability=0.70,
            )
        ]
        # Add strong evidence if we find matching things in store
        if self._store:
            for word in words:
                for q in [word, word.replace('ال', '').strip()]:
                    things = self._store.query_things_by_name(q)
                    if things:
                        for thing in things:
                            text_evidence.extend(thing.evidence)
                        break

        gate_result = self._gate.evaluate(text, text_evidence)

        # Step 7: Score certainty
        prior_relevance = 0.85 if any(
            self._store and self._store.query_things_by_name(w.replace('ال', '').strip())
            for w in words
        ) else 0.30

        cert_result = self._scorer.score(
            reality_match=0.75 if gate_result.accepted else 0.30,
            evidence_strength=gate_result.evidence_strength,
            semantic_fit=0.65,
            relation_validity=0.65 if relations else 0.30,
            prior_relevance=prior_relevance,
            context_fit=0.60,
        )

        # Step 8: Reason
        claims: list[Claim] = self._reasoner.reason(word_nodes, relations, context=text)

        # Boost claim certainty when prior knowledge matches
        if self._store:
            for claim in claims:
                if claim.prior_information:
                    if claim.certainty.score < 0.75:
                        claim.certainty = Certainty.from_score(
                            min(1.0, claim.certainty.score + 0.25),
                            claim.certainty.evidence_type,
                            claim.certainty.explanation + " [prior boost]",
                        )

        # Step 9: Learn (only in learner mode or if allow_learning)
        learning_actions = []
        if mode == "learner" or self._allow_learning:
            learning_actions = self._learner.learn(claims)

        # Step 10: Produce output
        overall_cert = cert_result.score
        if claims:
            overall_cert = max(overall_cert, max(c.certainty.score for c in claims))

        answer = self._generate_answer(text, normalized, claims, cert_result, words)

        return DecoderOutput(
            input=text,
            normalized=normalized,
            unicode_vectors=unicode_vectors,
            role_vectors=role_vectors_out,
            nodes=[n.to_dict() for n in word_nodes],
            relations=[r.to_dict() for r in relations],
            claims=[c.to_dict() for c in claims],
            certainty={
                "score": overall_cert,
                "level": cert_result.level,
                "dimensions": cert_result.dimensions,
                "explanation": cert_result.explanation,
            },
            learning_actions=[a.to_dict() for a in learning_actions],
            answer=answer,
        )

    def _generate_answer(self, text, normalized, claims, cert_result, words) -> str:
        parts = [f"المدخل: {text}"]
        if normalized != text:
            parts.append(f"المُعيَّر: {normalized}")
        if claims:
            best = max(claims, key=lambda c: c.certainty.score)
            parts.append(f"الادعاء الرئيسي: {best.text} (يقين: {best.certainty.score:.2f})")
            if best.prior_information:
                parts.append(f"المعرفة السابقة: {best.prior_information[0]}")
        parts.append(f"مستوى اليقين الكلي: {cert_result.level} ({cert_result.score:.2f})")
        return " | ".join(parts)
