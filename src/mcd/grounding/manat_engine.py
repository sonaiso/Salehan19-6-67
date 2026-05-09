"""ManatEngine — checks applicability of a rule to a given reality."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ManatStatus(str, Enum):
    APPLICABLE = "applicable"
    PARTIALLY_APPLICABLE = "partially_applicable"
    NOT_APPLICABLE = "not_applicable"
    SUSPENDED = "suspended"


@dataclass
class ManatResult:
    rule_id: str
    target_reality: str
    applicability_conditions: list[str]
    matched_conditions: list[str]
    missing_conditions: list[str]
    applicability_score: float
    status: ManatStatus
    explanation: str


# Threshold values for applicability scoring
_APPLICABLE_THRESHOLD = 0.8
_PARTIALLY_APPLICABLE_THRESHOLD = 0.4


class ManatApplicabilityEngine:
    """Checks whether a rule's conditions match a given reality."""

    def check(
        self,
        rule_id: str,
        rule_text: str,
        conditions: list[str],
        target_reality: str,
        target_properties: list[str],
    ) -> ManatResult:
        if not conditions:
            return ManatResult(
                rule_id=rule_id,
                target_reality=target_reality,
                applicability_conditions=[],
                matched_conditions=[],
                missing_conditions=[],
                applicability_score=0.0,
                status=ManatStatus.SUSPENDED,
                explanation="لا توجد شروط تطبيق محددة — الحكم موقوف",
            )

        matched: list[str] = []
        missing: list[str] = []

        for cond in conditions:
            # Check if condition is satisfied by any target property
            if any(cond in prop or prop in cond for prop in target_properties):
                matched.append(cond)
            else:
                missing.append(cond)

        score = len(matched) / len(conditions)

        if score >= _APPLICABLE_THRESHOLD:
            status = ManatStatus.APPLICABLE
            explanation = f"تحققت {len(matched)} من {len(conditions)} شروط — الحكم منطبق"
        elif score >= _PARTIALLY_APPLICABLE_THRESHOLD:
            status = ManatStatus.PARTIALLY_APPLICABLE
            explanation = f"تحققت {len(matched)} من {len(conditions)} شروط — الانطباق جزئي"
        else:
            status = ManatStatus.NOT_APPLICABLE
            explanation = f"تحققت {len(matched)} من {len(conditions)} شروط فقط — الحكم غير منطبق"

        return ManatResult(
            rule_id=rule_id,
            target_reality=target_reality,
            applicability_conditions=conditions,
            matched_conditions=matched,
            missing_conditions=missing,
            applicability_score=score,
            status=status,
            explanation=explanation,
        )
