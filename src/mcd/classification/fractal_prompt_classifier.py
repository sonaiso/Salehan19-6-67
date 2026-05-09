"""FractalPromptClassifier — full 9-step FPCL pipeline.

Pipeline:
  input
  → normalize
  → extract concepts
  → classify each concept
  → detect intent
  → compose vectors
  → classify judgment
  → determine evidence needs
  → determine certainty policy
  → route
  → PromptFrame
"""
from __future__ import annotations

import re
from typing import Any

from mcd.classification.certainty_policy_classifier import CertaintyPolicyClassifier
from mcd.classification.concept_classifier import ConceptClassifier
from mcd.classification.concept_extractor import ConceptExtractor, _normalize
from mcd.classification.evidence_need_classifier import EvidenceNeedClassifier
from mcd.classification.judgment_classifier import JudgmentClassifier
from mcd.classification.prompt_frame import PromptFrame
from mcd.classification.router import Router
from mcd.classification.vector_composer import VectorComposer


# ---------------------------------------------------------------------------
# Intent detection
# ---------------------------------------------------------------------------

_JUDGE_PATTERNS = re.compile(
    r"هل|هل\s+|هل_|هل[_ ]|(^|\s)(صحيح|خاطئ|يصح|هل\s)"
)
_BUILD_PATTERNS = re.compile(
    r"(^|\s)(كيف\s+نبني|كيف\s+نبنى|ابن|انشئ|أنشئ|اصنع|طور|طوّر|نفذ|نفّذ)"
)
_DEFINE_PATTERNS = re.compile(
    r"(^|\s)(ما\s+معنى|ما\s+هو|ما\s+هي|ما\s+هم|عرّف|عرف|اشرح|اذكر)"
)
_EXPLAIN_PATTERNS = re.compile(
    r"(^|\s)(كيف\s+يعمل|كيف\s+يتم|كيف\s+نعرف|لماذا|ما\s+السبب)"
)
_PLAN_PATTERNS = re.compile(
    r"(^|\s)(ما\s+خطوات|ما\s+الخطوات|ما\s+الخطة|ما\s+الخطه|ما\s+اللازم|ماذا\s+نفعل)"
)


def _detect_intent(text: str) -> str:
    if _BUILD_PATTERNS.search(text):
        return "build"
    if _PLAN_PATTERNS.search(text):
        return "plan"
    if _DEFINE_PATTERNS.search(text):
        return "define"
    if _JUDGE_PATTERNS.search(text):
        return "judge"
    if _EXPLAIN_PATTERNS.search(text):
        return "explain"
    return "general"


# ---------------------------------------------------------------------------
# FractalPromptClassifier
# ---------------------------------------------------------------------------

class FractalPromptClassifier:
    """Classify any Arabic prompt into a structured PromptFrame.

    Never raises on ambiguous input; returns PromptFrame with warnings.
    """

    def __init__(self) -> None:
        self._extractor = ConceptExtractor()
        self._classifier = ConceptClassifier()
        self._vector_composer = VectorComposer()
        self._judgment_clf = JudgmentClassifier()
        self._evidence_clf = EvidenceNeedClassifier()
        self._certainty_clf = CertaintyPolicyClassifier()
        self._router = Router()

    def classify(self, text: str, include_debug: bool = False) -> PromptFrame:
        warnings: list[str] = []
        debug: dict[str, Any] = {}

        # --- Step 1: Normalize ---
        normalized = _normalize(text)

        # --- Step 2: Extract concepts ---
        raw_concepts = self._extractor.extract(text)

        # --- Step 3: Classify each concept ---
        classified_concepts = self._classifier.classify_all(raw_concepts)

        # --- Step 4: Detect intent ---
        intent = _detect_intent(normalized)

        # --- Step 5: Compose vectors ---
        composed = self._vector_composer.compose(classified_concepts, intent=intent)

        root_domain = composed.get("root_domain", {})
        concept_types = composed.get("concept_types", {})
        knowledge_categories = composed.get("knowledge_categories", {})

        # --- Step 6: Classify judgment types ---
        # Aggregate judgment hints from composed + text scan
        composed_judgment_hints = composed.get("judgment_types", {})
        judgment_types = self._judgment_clf.classify(normalized, composed_judgment_hints)

        # --- Step 7: Determine evidence needs ---
        # Aggregate evidence hints from composed
        concept_evidence_hints = composed.get("evidence_needs", {})
        evidence_needs = self._evidence_clf.classify(
            judgment_types=judgment_types,
            knowledge_categories=knowledge_categories,
            concept_evidence_hints=concept_evidence_hints,
        )

        # --- Step 8: Determine certainty policy ---
        context_provided = self._has_sufficient_context(normalized, classified_concepts)

        policy_decision = self._certainty_clf.classify(
            judgment_types=judgment_types,
            evidence_needs=evidence_needs,
            knowledge_categories=knowledge_categories,
            has_shari_evidence=False,  # no external evidence in this layer
            context_provided=context_provided,
        )

        # --- Step 9: Route ---
        routing = self._router.route(
            judgment_types=judgment_types,
            knowledge_categories=knowledge_categories,
            evidence_needs=evidence_needs,
            certainty_policy=policy_decision.policy,
        )

        # --- Warnings ---
        if routing.should_suspend:
            if "shari" in evidence_needs:
                warnings.append("shari judgment requires shari evidence")
            else:
                warnings.append("ambiguous prompt or insufficient context — judgment suspended")

        if not context_provided:
            warnings.append("prompt may be ambiguous without additional context")

        if policy_decision.required_before_upgrade:
            warnings.append(
                "to upgrade certainty provide: "
                + ", ".join(policy_decision.required_before_upgrade)
            )

        # --- Debug info ---
        if include_debug:
            debug = {
                "concept_vectors": [c.to_dict() for c in classified_concepts],
                "composed_vectors": composed,
                "intent": intent,
                "certainty_reason": policy_decision.reason,
                "routing_reason": routing.reason,
                "context_provided": context_provided,
            }

        return PromptFrame(
            raw_text=text,
            normalized_text=normalized,
            intent=intent,
            concepts=classified_concepts,
            root_domain=root_domain,
            concept_types=concept_types,
            knowledge_categories=knowledge_categories,
            judgment_types=judgment_types,
            evidence_needs=evidence_needs,
            certainty_policy=policy_decision.policy,
            certainty_reason=policy_decision.reason,
            routing_engine=routing.primary_engine,
            sub_engines=list(routing.sub_engines),
            warnings=warnings,
            debug=debug,
        )

    # ------------------------------------------------------------------

    def _has_sufficient_context(self, text: str, concepts: list) -> bool:
        """Return True if the prompt has enough context to reason about."""
        words = text.split()
        # Very short prompts (1-2 words) may lack context
        if len(words) <= 2 and len(concepts) <= 1:
            return False
        # All-question-word prompt with no noun
        if len(words) <= 3:
            question_words = {"هل", "ما", "من", "أين", "متى", "كيف", "لماذا", "ماذا"}
            if all(w in question_words for w in words):
                return False
        return True
