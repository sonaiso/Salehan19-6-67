"""ConflictResolver — resolves conflicts between meanings, evidences, or relations.

Steps:
1. Identify where the conflict is: dal, madlul, reality, or evidence.
2. Is the conflict real or apparent?
3. Can claims be combined?
4. Is there specialisation/restriction (تخصيص / تقييد)?
5. Which evidence is stronger?
6. Suspend if unresolvable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ConflictResolution:
    conflict_type: str          # "dal" | "madlul" | "reality" | "evidence" | "none"
    resolution_strategy: str    # "combined" | "specialized" | "stronger_evidence" | "suspended" | "no_conflict"
    preferred_claim: Optional[str]
    suspended_claims: List[str]
    explanation: str


class ConflictResolver:
    """Resolve conflicts between a list of claim dicts."""

    def resolve(self, claims: List[Any]) -> ConflictResolution:
        if not claims or len(claims) < 2:
            return ConflictResolution(
                conflict_type="none",
                resolution_strategy="no_conflict",
                preferred_claim=None,
                suspended_claims=[],
                explanation="لا يوجد تعارض: عدد الادعاءات أقل من اثنين.",
            )

        # Normalise claims to dicts
        dicts: List[Dict[str, Any]] = []
        for c in claims:
            if isinstance(c, dict):
                dicts.append(c)
            elif hasattr(c, "to_dict"):
                dicts.append(c.to_dict())
            else:
                dicts.append({"text": str(c), "certainty": 0.0})

        # --- Detect conflict type ---
        conflict_type = self._detect_conflict_type(dicts)

        if conflict_type == "none":
            return ConflictResolution(
                conflict_type="none",
                resolution_strategy="no_conflict",
                preferred_claim=dicts[0].get("text", ""),
                suspended_claims=[],
                explanation="لا يوجد تعارض حقيقي بين الادعاءات.",
            )

        # --- Try to resolve ---
        # Strategy 1: Pick by evidence strength
        best, rest = self._pick_by_certainty(dicts)
        if best is not None:
            return ConflictResolution(
                conflict_type=conflict_type,
                resolution_strategy="stronger_evidence",
                preferred_claim=best.get("text", ""),
                suspended_claims=[d.get("text", "") for d in rest],
                explanation=f"تعارض في '{conflict_type}'. الادعاء الأرجح اختير بناءً على قوة الدليل.",
            )

        # Strategy 2: Suspend all
        suspended = [d.get("text", "") for d in dicts]
        return ConflictResolution(
            conflict_type=conflict_type,
            resolution_strategy="suspended",
            preferred_claim=None,
            suspended_claims=suspended,
            explanation=f"تعارض في '{conflict_type}' لم يُحسم. جميع الادعاءات مُعلَّقة حتى يتبيَّن الراجح.",
        )

    # ------------------------------------------------------------------

    def _detect_conflict_type(self, dicts: List[Dict[str, Any]]) -> str:
        texts = [d.get("text", "") for d in dicts]
        # Apparent contradiction: opposite certainty levels on same subject
        certs = [self._cert_score(d) for d in dicts]
        if max(certs) - min(certs) > 0.40:
            return "evidence"
        # If texts share words but different predicates, call it semantic/madlul
        words_sets = [set(t.split()) for t in texts if t]
        if len(words_sets) >= 2:
            shared = words_sets[0] & words_sets[1]
            if len(shared) > 0 and texts[0] != texts[1]:
                return "madlul"
        return "none"

    def _pick_by_certainty(
        self, dicts: List[Dict[str, Any]]
    ) -> tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        scored = sorted(dicts, key=lambda d: self._cert_score(d), reverse=True)
        best = scored[0]
        rest = scored[1:]
        # Only prefer if significantly higher certainty
        if rest and self._cert_score(best) - self._cert_score(rest[0]) > 0.15:
            return best, rest
        return None, dicts

    @staticmethod
    def _cert_score(d: Dict[str, Any]) -> float:
        cert = d.get("certainty", 0.0)
        if isinstance(cert, dict):
            return float(cert.get("score", 0.0))
        try:
            return float(cert)
        except (TypeError, ValueError):
            return 0.0
