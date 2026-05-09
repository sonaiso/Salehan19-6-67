"""Router — maps a PromptFrame to a routing decision.

Routing rules:
  shari  → domain_judge + nabhani_decoder (require shari evidence)
  epistemic → nabhani_decoder + rational_method_judge + evidence_gate
  technical → mcd + practical_output
  language  → dal_madlul_mapper + concept_grounder
  method    → nabhani_decoder + certainty_scorer
  technology → mcd + practical_output
  suspend   → suspended_response
"""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.classification.taxonomy import (
    CertaintyPolicy,
    EvidenceNeed,
    JudgmentType,
    KnowledgeCategory,
)


@dataclass(frozen=True)
class RoutingDecision:
    """Structured routing decision."""

    primary_engine: str
    sub_engines: list[str]
    reason: str
    requires_evidence: list[str]
    should_suspend: bool = False


class Router:
    """Route a classified prompt to the appropriate engine pipeline."""

    def route(
        self,
        judgment_types: dict[str, float],
        knowledge_categories: dict[str, float],
        evidence_needs: dict[str, float],
        certainty_policy: str,
    ) -> RoutingDecision:
        """Return a RoutingDecision based on classification vectors."""
        shari_score = judgment_types.get(JudgmentType.SHARI, 0.0)
        technical_score = judgment_types.get(JudgmentType.TECHNICAL, 0.0)
        epistemic_score = judgment_types.get(JudgmentType.EPISTEMIC, 0.0)
        practical_score = judgment_types.get(JudgmentType.PRACTICAL, 0.0)

        lang_score = knowledge_categories.get(KnowledgeCategory.LANGUAGE, 0.0)
        tech_score = knowledge_categories.get(KnowledgeCategory.TECHNOLOGY, 0.0)
        method_score = knowledge_categories.get(KnowledgeCategory.METHOD, 0.0)

        needs_shari = evidence_needs.get(EvidenceNeed.SHARI, 0.0) >= 0.50

        # 1. Suspension policy overrides
        if certainty_policy == CertaintyPolicy.SUSPEND:
            if shari_score >= 0.70 or needs_shari:
                return RoutingDecision(
                    primary_engine="nabhani_decoder",
                    sub_engines=["domain_judge", "evidence_gate", "certainty_scorer"],
                    reason="الحكم شرعي بدون دليل شرعي؛ يُعلَّق الجواب.",
                    requires_evidence=[EvidenceNeed.SHARI, EvidenceNeed.TEXTUAL],
                    should_suspend=True,
                )
            return RoutingDecision(
                primary_engine="nabhani_decoder",
                sub_engines=["rational_method_judge", "evidence_gate"],
                reason="السياسة: تعليق بسبب غموض أو سياق ناقص.",
                requires_evidence=list(evidence_needs.keys()),
                should_suspend=True,
            )

        # 2. Shari judgment with evidence present
        if shari_score >= 0.70 or needs_shari:
            return RoutingDecision(
                primary_engine="nabhani_decoder",
                sub_engines=["domain_judge", "evidence_gate", "certainty_scorer"],
                reason="حكم شرعي؛ يُوجَّه إلى NabhaniDecoder عبر DomainJudge.",
                requires_evidence=[EvidenceNeed.SHARI, EvidenceNeed.TEXTUAL],
                should_suspend=False,
            )

        # 3. Technical / practical
        if technical_score >= 0.55 or tech_score >= 0.60:
            return RoutingDecision(
                primary_engine="mcd",
                sub_engines=["practical_output"],
                reason="سؤال تقني أو عملي؛ يُوجَّه إلى MCD + practical_output.",
                requires_evidence=[EvidenceNeed.TECHNICAL, EvidenceNeed.TEXTUAL],
                should_suspend=False,
            )

        # 4. Language domain
        if lang_score >= 0.60:
            return RoutingDecision(
                primary_engine="nabhani_decoder",
                sub_engines=["dal_madlul_mapper", "concept_grounder"],
                reason="سؤال لغوي؛ يُوجَّه إلى DalMadlulMapper + ConceptGrounder.",
                requires_evidence=[EvidenceNeed.LINGUISTIC, EvidenceNeed.CONTEXTUAL],
                should_suspend=False,
            )

        # 5. Methodological
        if method_score >= 0.55:
            return RoutingDecision(
                primary_engine="nabhani_decoder",
                sub_engines=["certainty_scorer", "rational_method_judge"],
                reason="سؤال منهجي معرفي؛ يُوجَّه إلى NabhaniDecoder.",
                requires_evidence=list(evidence_needs.keys()),
                should_suspend=False,
            )

        # 6. Epistemic (default)
        return RoutingDecision(
            primary_engine="nabhani_decoder",
            sub_engines=["rational_method_judge", "evidence_gate", "certainty_scorer"],
            reason="حكم معرفي عقلي؛ يُوجَّه إلى NabhaniDecoder.",
            requires_evidence=list(evidence_needs.keys()),
            should_suspend=False,
        )
