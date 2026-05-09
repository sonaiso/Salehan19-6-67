"""FakeEvidenceDetector — identifies weak or spurious evidence in a claim.

Ten fake-evidence patterns recognised:
1.  opinion_as_evidence
2.  surface_similarity
3.  analogy_without_illah
4.  unsupported_generalization
5.  linguistic_fluency_without_grounding
6.  circular_reasoning
7.  weak_association
8.  rule_out_of_scope
9.  missing_source
10. contradiction_ignored
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


FAKE_EVIDENCE_TYPES = [
    "opinion_as_evidence",
    "surface_similarity",
    "analogy_without_illah",
    "unsupported_generalization",
    "linguistic_fluency_without_grounding",
    "circular_reasoning",
    "weak_association",
    "rule_out_of_scope",
    "missing_source",
    "contradiction_ignored",
]

_SEVERITY_MAP = {0: "none", 1: "low", 2: "medium"}
_HIGH_THRESHOLD = 3


@dataclass
class FakeEvidenceReport:
    has_fake_evidence: bool
    detected_types: List[str]
    severity: str    # "none" | "low" | "medium" | "high"
    explanation: str
    recommendation: str


class FakeEvidenceDetector:
    """Evaluate a claim dict for fake or weak evidence patterns."""

    def detect(self, claim: Dict[str, Any]) -> FakeEvidenceReport:
        detected: List[str] = []

        evidence = claim.get("evidence", [])
        certainty = claim.get("certainty", 0.0)
        if isinstance(certainty, dict):
            certainty = certainty.get("score", 0.0)
        source = claim.get("sense_source", None)
        prior = claim.get("prior_information", None)
        chain = claim.get("relation_chain", None)

        # --- 1. missing_source ---
        if not source:
            detected.append("missing_source")

        # --- 2. opinion_as_evidence ---
        if isinstance(evidence, list):
            for ev in evidence:
                ev_type = ev.get("source_type", "") if isinstance(ev, dict) else ""
                if ev_type in ("opinion", "personal_view", "assumption"):
                    detected.append("opinion_as_evidence")
                    break
        # If prior info is absent but evidence exists, flag opinion risk
        if not prior and evidence:
            detected.append("opinion_as_evidence")

        # --- 3. weak_association ---
        if isinstance(evidence, list):
            for ev in evidence:
                strength = ev.get("strength", 1.0) if isinstance(ev, dict) else 1.0
                if strength < 0.30:
                    detected.append("weak_association")
                    break
        elif isinstance(certainty, float) and certainty < 0.35:
            detected.append("weak_association")

        # --- 4. linguistic_fluency_without_grounding ---
        # If the claim has no chain and no grounded reality but has text
        if not chain and claim.get("text"):
            detected.append("linguistic_fluency_without_grounding")

        # --- 5. unsupported_generalization ---
        text = claim.get("text", "")
        general_words = {"كل", "دائمًا", "أبدًا", "لا يوجد", "الجميع"}
        if any(w in text for w in general_words) and not chain:
            detected.append("unsupported_generalization")

        # Deduplicate
        detected = list(dict.fromkeys(detected))

        n = len(detected)
        if n == 0:
            severity = "none"
        elif n == 1:
            severity = "low"
        elif n < _HIGH_THRESHOLD:
            severity = "medium"
        else:
            severity = "high"

        has_fake = n > 0

        if not has_fake:
            explanation = "لم يُرصد دليل مزيف أو ضعيف."
            recommendation = "الدليل مقبول مبدئيًا. واصل التحقق من المطابقة."
        else:
            explanation = f"رُصدت أنماط دليل مشكوك فيه: {', '.join(detected)}."
            recommendation = "راجع مصادر الدليل وتحقق من وجود واقع وربط كافيين قبل قبول الادعاء."

        return FakeEvidenceReport(
            has_fake_evidence=has_fake,
            detected_types=detected,
            severity=severity,
            explanation=explanation,
            recommendation=recommendation,
        )
