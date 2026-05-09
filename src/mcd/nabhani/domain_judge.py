"""DomainJudge — separates epistemic judgments from normative-shari judgments.

Key principle (Axiom AX-12, AX-13):
- Epistemic judgments (existence, harm, benefit, causality …) → reason can decide.
- Normative/Shari judgments (obligation, prohibition …) → require revelation evidence.
  Without revelation evidence: status = "no_shari_ruling_available"
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


# ---------------------------------------------------------------------------
# Domain definitions
# ---------------------------------------------------------------------------

EPISTEMIC_JUDGMENT_TYPES = frozenset({
    "existence", "identity", "property", "causality",
    "utility", "harm", "semantic", "correspondence",
    "evidence_strength", "certainty",
})

NORMATIVE_JUDGMENT_TYPES = frozenset({
    "obligation", "prohibition", "reward", "punishment",
    "praise_blame", "legal_validity",
})

# Arabic keyword → domain mapping
_HARM_KEYWORDS = frozenset({"ضار", "ضرر", "يضر", "مضر", "ضارة"})
_BENEFIT_KEYWORDS = frozenset({"نافع", "نفع", "مفيد", "يفيد", "نافعة"})
_PROHIBITION_KEYWORDS = frozenset({"حرام", "محرم", "يحرم", "حُرِّمَ", "لا يجوز"})
_OBLIGATION_KEYWORDS = frozenset({"واجب", "واجبة", "فريضة", "يجب", "فرض", "مفروض"})


@dataclass
class DomainJudgment:
    judgment_type: str               # "epistemic" | "normative_shari"
    domain: str                      # e.g. "harm", "prohibition"
    can_reason_without_revelation: bool
    status: str                      # "proceed_epistemic" | "no_shari_ruling_available" | "shari_judgment_with_evidence"
    explanation: str


class DomainJudge:
    """Classify a claim into its epistemic or normative-shari domain."""

    def classify(self, claim: Dict[str, Any]) -> DomainJudgment:
        domain = claim.get("domain", "")
        revelation_evidence = claim.get("revelation_evidence")

        if domain in EPISTEMIC_JUDGMENT_TYPES:
            return DomainJudgment(
                judgment_type="epistemic",
                domain=domain,
                can_reason_without_revelation=True,
                status="proceed_epistemic",
                explanation=f"الحكم في نطاق '{domain}' معرفيٌّ عقليٌّ؛ يمكن البتّ فيه بلا دليل شرعي.",
            )

        if domain in NORMATIVE_JUDGMENT_TYPES:
            if revelation_evidence:
                return DomainJudgment(
                    judgment_type="normative_shari",
                    domain=domain,
                    can_reason_without_revelation=False,
                    status="shari_judgment_with_evidence",
                    explanation=f"الحكم في نطاق '{domain}' شرعيٌّ وقد وُجد دليله.",
                )
            return DomainJudgment(
                judgment_type="normative_shari",
                domain=domain,
                can_reason_without_revelation=False,
                status="no_shari_ruling_available",
                explanation=f"الحكم في نطاق '{domain}' شرعيٌّ ولا يصدر عن العقل وحده؛ لا دليل شرعي متاح.",
            )

        # Unknown domain → default epistemic (conservative)
        return DomainJudgment(
            judgment_type="epistemic",
            domain=domain or "unknown",
            can_reason_without_revelation=True,
            status="proceed_epistemic",
            explanation="النطاق غير محدد؛ يُعامَل معاملةً معرفيةً بشكل افتراضي.",
        )

    # ------------------------------------------------------------------
    # Text-level helpers
    # ------------------------------------------------------------------

    def is_harm_claim(self, text: str) -> bool:
        """Return True if the text expresses a harm/benefit epistemic claim."""
        words = set(text.split())
        return bool(words & (_HARM_KEYWORDS | _BENEFIT_KEYWORDS))

    def is_prohibition_claim(self, text: str) -> bool:
        """Return True if the text expresses a normative prohibition/obligation."""
        words = set(text.split())
        return bool(words & (_PROHIBITION_KEYWORDS | _OBLIGATION_KEYWORDS))

    def classify_text(self, text: str) -> DomainJudgment:
        """Auto-classify an Arabic text string."""
        if self.is_prohibition_claim(text):
            return DomainJudgment(
                judgment_type="normative_shari",
                domain="prohibition",
                can_reason_without_revelation=False,
                status="no_shari_ruling_available",
                explanation="النص يتضمن حكمًا تكليفيًا شرعيًا (حرام/واجب). لا يصدر عن العقل وحده؛ يحتاج دليلًا شرعيًا.",
            )
        if self.is_harm_claim(text):
            return DomainJudgment(
                judgment_type="epistemic",
                domain="harm",
                can_reason_without_revelation=True,
                status="proceed_epistemic",
                explanation="النص يتضمن حكمًا معرفيًا بالنفع أو الضرر؛ يمكن للعقل أن يستدل فيه.",
            )
        # Generic epistemic
        return DomainJudgment(
            judgment_type="epistemic",
            domain="general",
            can_reason_without_revelation=True,
            status="proceed_epistemic",
            explanation="النص يُعامَل معاملةً معرفيةً عامة.",
        )
