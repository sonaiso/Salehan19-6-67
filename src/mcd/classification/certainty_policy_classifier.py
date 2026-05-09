"""CertaintyPolicyClassifier — determines the certainty policy before answering."""
from __future__ import annotations

from dataclasses import dataclass, field

from mcd.classification.taxonomy import CertaintyPolicy, EvidenceNeed, JudgmentType


@dataclass(frozen=True)
class CertaintyPolicyDecision:
    """Structured certainty policy decision."""

    policy: str
    reason: str
    required_before_upgrade: list[str] = field(default_factory=list)


_SHARI_SUSPEND_REASON = (
    "حكم شرعي بلا دليل شرعي مقدَّم: يُعلَّق الحكم حتى يتبيَّن الدليل."
)
_AMBIGUOUS_REASON = (
    "النص غامض أو السياق غير كافٍ: يُعلَّق الحكم حتى يُوضَح السياق."
)
_SHARI_EVIDENCE_SUSPEND_REASON = (
    "الحكم الشرعي يحتاج دليلًا قطعيًا من الكتاب أو السنة أو الإجماع."
)


class CertaintyPolicyClassifier:
    """Decide the certainty policy for a prompt given its classification."""

    def classify(
        self,
        judgment_types: dict[str, float],
        evidence_needs: dict[str, float],
        knowledge_categories: dict[str, float],
        has_shari_evidence: bool = False,
        context_provided: bool = True,
    ) -> CertaintyPolicyDecision:
        """Return a CertaintyPolicyDecision.

        Rules (in priority order):
        1. SHARI judgment without shari evidence → SUSPEND
        2. Ambiguous / no context (e.g. single common word, no category) → SUSPEND
        3. Technical / practical judgment → STRONG_KNOWLEDGE
        4. Philosophical / civilisation / wide culture question → HYPOTHESIS
        5. Scientific / sensory / experimental → NEAR_CERTAINTY or STRONG_KNOWLEDGE
        6. Value/epistemic with context → STRONG_KNOWLEDGE
        """
        shari_score = judgment_types.get(JudgmentType.SHARI, 0.0)
        technical_score = judgment_types.get(JudgmentType.TECHNICAL, 0.0)
        practical_score = judgment_types.get(JudgmentType.PRACTICAL, 0.0)
        epistemic_score = judgment_types.get(JudgmentType.EPISTEMIC, 0.0)
        value_score = judgment_types.get(JudgmentType.VALUE, 0.0)

        has_sensory = evidence_needs.get(EvidenceNeed.SENSORY, 0.0) >= 0.35
        has_experimental = evidence_needs.get(EvidenceNeed.EXPERIMENTAL, 0.0) >= 0.35
        has_shari_need = evidence_needs.get(EvidenceNeed.SHARI, 0.0) >= 0.50

        # 1. Shari without evidence → suspend
        if shari_score >= 0.70 or has_shari_need:
            if not has_shari_evidence:
                return CertaintyPolicyDecision(
                    policy=CertaintyPolicy.SUSPEND,
                    reason=_SHARI_SUSPEND_REASON,
                    required_before_upgrade=[EvidenceNeed.SHARI, EvidenceNeed.TEXTUAL],
                )

        # 2. Ambiguous / no context
        if not context_provided:
            return CertaintyPolicyDecision(
                policy=CertaintyPolicy.SUSPEND,
                reason=_AMBIGUOUS_REASON,
                required_before_upgrade=["context"],
            )

        # Check categories
        civ_score = knowledge_categories.get("civilization", 0.0)
        culture_score = knowledge_categories.get("culture", 0.0)
        science_score = knowledge_categories.get("science", 0.0)
        tech_score = knowledge_categories.get("technology", 0.0)
        lang_score = knowledge_categories.get("language", 0.0)
        method_score = knowledge_categories.get("method", 0.0)

        # Also use root_domain as a signal
        universe_score = judgment_types.get("universe", 0.0)  # not a jt, but via evidence
        has_universe = has_sensory or has_experimental

        # 3. Technical / practical → strong_knowledge
        if technical_score >= 0.55 or practical_score >= 0.55:
            return CertaintyPolicyDecision(
                policy=CertaintyPolicy.STRONG_KNOWLEDGE,
                reason="السؤال تقني أو عملي؛ الإجابة ممكنة لكن ليست يقينًا معرفيًا مطلقًا.",
                required_before_upgrade=[],
            )

        # 4. Science with sensory/experimental → near_certainty or strong_knowledge
        if science_score >= 0.30 and has_universe:
            if science_score >= 0.65:
                return CertaintyPolicyDecision(
                    policy=CertaintyPolicy.NEAR_CERTAINTY,
                    reason="المجال علمي تجريبي واضح بدليل حسي أو تجريبي.",
                    required_before_upgrade=[],
                )
            return CertaintyPolicyDecision(
                policy=CertaintyPolicy.STRONG_KNOWLEDGE,
                reason="المجال علمي أو طبيعي مع دليل حسي أو تجريبي.",
                required_before_upgrade=[],
            )

        # 5. Wide civilisation / culture / linguistic → hypothesis or suspend
        if civ_score >= 0.55 or (culture_score >= 0.60 and epistemic_score < 0.40):
            return CertaintyPolicyDecision(
                policy=CertaintyPolicy.HYPOTHESIS,
                reason="السؤال حضاري أو ثقافي واسع؛ يقتصر على فرضية معرفية.",
                required_before_upgrade=["historical_evidence", "textual_sources"],
            )

        # 6. Short language queries without sufficient context → suspend
        if lang_score >= 0.50 and context_provided:
            # e.g. "ما معنى علم؟" — single ambiguous word with no specifier
            # Suspend when the intent is "define" and concept count is very low
            return CertaintyPolicyDecision(
                policy=CertaintyPolicy.SUSPEND,
                reason="سؤال لغوي عن معنى مفهوم غامض؛ يُعلَّق الحكم حتى يُحدَّد السياق.",
                required_before_upgrade=["context", "linguistic_evidence"],
            )

        # 7. Epistemic / value → strong_knowledge
        if epistemic_score >= 0.30 or value_score >= 0.30:
            return CertaintyPolicyDecision(
                policy=CertaintyPolicy.STRONG_KNOWLEDGE,
                reason="سؤال معرفي أو قيمي مع سياق.",
                required_before_upgrade=[],
            )

        # Default
        return CertaintyPolicyDecision(
            policy=CertaintyPolicy.HYPOTHESIS,
            reason="السياق غير كافٍ لتحديد سياسة يقين أعلى.",
            required_before_upgrade=["more_context"],
        )
