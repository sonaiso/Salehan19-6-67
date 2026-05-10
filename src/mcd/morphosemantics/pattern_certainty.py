"""PatternCertainty — certainty scoring for pattern assignments.

Certainty in Arabic morphological analysis depends on whether the pattern
is قياسي (qiyasi — rule-based, certain), سماعي (samai — attested by usage),
or شاذ (shadh — anomalous/irregular).  This module provides a unified
certainty score for any pattern/root combination.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PatternCertaintyResult:
    pattern_id: str
    root_id: str
    certainty_policy: str  # qiyasi|samai|shadh|unknown
    certainty_score: float  # 0.0-1.0
    rationale: str

    def to_dict(self) -> dict:
        return {
            "pattern_id": self.pattern_id,
            "root_id": self.root_id,
            "certainty_policy": self.certainty_policy,
            "certainty_score": self.certainty_score,
            "rationale": self.rationale,
        }


_POLICY_BASE_SCORE = {
    "qiyasi": 0.95,
    "samai": 0.80,
    "shadh": 0.50,
    "unknown": 0.40,
}

_QIYASI_PATTERNS = {
    "faail", "mafuul", "mafal_place", "mafala_place", "faaaal_intense",
    "istafala_verb", "tafaala_reflex", "faiil_attr", "fuayyil_dim",
    "nisba_yaa", "mustafl_patient", "mufaail_agent", "fiaala_masdar_craft",
    "afaal_plural",
}

_SAMAI_PATTERNS = {"fuuul_plural", "fiaal_plural", "fual_plural"}


class PatternCertaintyScorer:
    """Scores the certainty of a pattern assignment for a given root."""

    def score(
        self,
        pattern_id: str,
        root_id: str,
        override_policy: str = "",
    ) -> PatternCertaintyResult:
        if override_policy in _POLICY_BASE_SCORE:
            policy = override_policy
        elif pattern_id in _QIYASI_PATTERNS:
            policy = "qiyasi"
        elif pattern_id in _SAMAI_PATTERNS:
            policy = "samai"
        else:
            policy = "unknown"

        base = _POLICY_BASE_SCORE[policy]

        # Slight penalty for weak/hollow/hamzated roots — harder to apply patterns
        weak_roots = {"hollow", "weak", "defective", "hamzated"}
        penalty = 0.05 if any(w in root_id.lower() for w in weak_roots) else 0.0

        certainty = max(0.0, min(1.0, base - penalty))
        rationale = (
            f"Pattern '{pattern_id}' is {policy} "
            f"(base={base:.2f}, penalty={penalty:.2f})"
        )

        return PatternCertaintyResult(
            pattern_id=pattern_id,
            root_id=root_id,
            certainty_policy=policy,
            certainty_score=certainty,
            rationale=rationale,
        )
