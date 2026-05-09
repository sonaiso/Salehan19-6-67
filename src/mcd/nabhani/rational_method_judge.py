"""RationalMethodJudge — validates claims through the Nabhani rational method (الطريقة العقلية).

The method requires:
  واقع (reality) + حس/مصدر (sense/source) + معلومات سابقة (prior info)
  + ربط (linking) + مطابقة (correspondence) + دليل (evidence)
  + يقين (certainty score)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RationalJudgment:
    accepted: bool
    status: str          # "accepted" | "suspended" | "rejected"
    missing_requirements: List[str]
    violated_axioms: List[str]
    explanation: str
    certainty_hint: str


_ACCEPTANCE_CERTAINTY_THRESHOLD = 0.60   # minimum to move from suspended → accepted


class RationalMethodJudge:
    """Evaluate a claim dict against the rational method requirements."""

    # Required keys and the axiom violated if they are absent
    _REALITY_KEY = "target_reality"
    _SOURCE_KEY = "sense_source"
    _PRIOR_KEY = "prior_information"
    _CHAIN_KEY = "relation_chain"
    _CORR_KEY = "correspondence_test"
    _EVIDENCE_KEY = "evidence"
    _CERTAINTY_KEY = "certainty"

    def judge(self, claim: Dict[str, Any]) -> RationalJudgment:
        missing: List[str] = []
        violated: List[str] = []

        # --- Check 1: Reality (HARD — rejection if absent) ---
        reality = claim.get(self._REALITY_KEY)
        if not reality:
            missing.append(self._REALITY_KEY)
            violated.append("no_knowledge_without_reality")
            return RationalJudgment(
                accepted=False,
                status="rejected",
                missing_requirements=missing,
                violated_axioms=violated,
                explanation="الادعاء مرفوض: لا يوجد واقع (target_reality). لا معرفة بلا واقع.",
                certainty_hint="none",
            )

        # --- Check 2: Evidence (SOFT — suspension if absent) ---
        evidence = claim.get(self._EVIDENCE_KEY)
        evidence_ok = bool(evidence) and (
            (isinstance(evidence, list) and len(evidence) > 0) or
            (isinstance(evidence, dict) and evidence)
        )
        if not evidence_ok:
            missing.append(self._EVIDENCE_KEY)
            violated.append("no_knowledge_without_evidence")

        # --- Check 3: Source / Sense ---
        sense_source = claim.get(self._SOURCE_KEY)
        if not sense_source:
            missing.append(self._SOURCE_KEY)
            violated.append("no_thought_without_sense_or_source")

        # --- Check 4: Prior information ---
        prior = claim.get(self._PRIOR_KEY)
        if not prior:
            missing.append(self._PRIOR_KEY)
            violated.append("no_understanding_without_prior")

        # --- Check 5: Relation chain ---
        chain = claim.get(self._CHAIN_KEY)
        chain_ok = bool(chain) and (
            (isinstance(chain, list) and len(chain) > 0) or
            (isinstance(chain, dict) and chain)
        )
        if not chain_ok:
            missing.append(self._CHAIN_KEY)
            violated.append("thought_from_linking")

        # --- Check 6: Correspondence ---
        corr = claim.get(self._CORR_KEY)
        if not corr:
            missing.append(self._CORR_KEY)
            violated.append("thought_validity_by_correspondence")

        # --- Check 7: Certainty score ---
        certainty_score: float = 0.0
        raw_cert = claim.get(self._CERTAINTY_KEY, 0.0)
        if isinstance(raw_cert, (int, float)):
            certainty_score = float(raw_cert)
        elif isinstance(raw_cert, dict):
            certainty_score = float(raw_cert.get("score", 0.0))

        if certainty_score < _ACCEPTANCE_CERTAINTY_THRESHOLD:
            missing.append("certainty_above_threshold")
            violated.append("certainty_is_degree")

        # --- Determine status ---
        if missing:
            explanation_parts = ["الادعاء معلَّق لنقص المتطلبات التالية: " + "، ".join(missing)]
            if violated:
                explanation_parts.append("الأصول المنتهكة: " + "، ".join(violated))
            return RationalJudgment(
                accepted=False,
                status="suspended",
                missing_requirements=missing,
                violated_axioms=violated,
                explanation=" | ".join(explanation_parts),
                certainty_hint=_certainty_hint(certainty_score),
            )

        return RationalJudgment(
            accepted=True,
            status="accepted",
            missing_requirements=[],
            violated_axioms=[],
            explanation="الادعاء مقبول معرفيًا: تحقق الواقع والمصدر والمعلومات السابقة والربط والمطابقة والدليل واليقين.",
            certainty_hint=_certainty_hint(certainty_score),
        )


def _certainty_hint(score: float) -> str:
    if score >= 0.90:
        return "near_certainty"
    if score >= 0.75:
        return "strong_knowledge"
    if score >= 0.60:
        return "probable_knowledge"
    if score >= 0.40:
        return "hypothesis"
    return "weak_or_unverified"
