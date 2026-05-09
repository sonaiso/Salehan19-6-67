"""CognitiveMeasure — promotes a verified claim to a reusable epistemic rule.

Axiom AX-10: اليقين إذا ثبت صار مقياسًا
When certainty is established (≥ 0.85), the knowledge becomes a cognitive measure
that can govern future reasoning.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


MEASURE_CERTAINTY_THRESHOLD = 0.85


@dataclass
class CognitiveMeasure:
    measure_id: str
    source_claim: str
    rule: str
    domain: str
    certainty: float
    applies_to: List[str]
    conditions: List[str]
    exceptions: List[str]
    version: int = 1


class CognitiveMeasureBuilder:
    """Build a CognitiveMeasure from a claim dict when conditions are met."""

    def build(self, claim: Dict[str, Any]) -> Optional[CognitiveMeasure]:
        """Return a CognitiveMeasure if the claim qualifies, else None.

        Qualifications:
        - certainty >= MEASURE_CERTAINTY_THRESHOLD (0.85)
        - evidence_strength >= 0.60
        - no strong conflict (has_conflict is False or not present)
        - domain is specified
        """
        certainty = self._extract_certainty(claim)
        evidence_strength = self._extract_evidence_strength(claim)
        has_conflict = bool(claim.get("has_conflict", False))
        domain = claim.get("domain", "")

        if certainty < MEASURE_CERTAINTY_THRESHOLD:
            return None
        if evidence_strength < 0.60:
            return None
        if has_conflict:
            return None
        if not domain:
            return None

        text = claim.get("text", "")
        rule = f"[{domain}] {text}" if text else f"[{domain}] rule"

        applies_to = claim.get("applies_to", [domain])
        if isinstance(applies_to, str):
            applies_to = [applies_to]

        conditions = claim.get("conditions", [])
        exceptions = claim.get("exceptions", [])

        return CognitiveMeasure(
            measure_id=f"measure_{uuid.uuid4().hex[:8]}",
            source_claim=text,
            rule=rule,
            domain=domain,
            certainty=round(certainty, 4),
            applies_to=list(applies_to),
            conditions=list(conditions),
            exceptions=list(exceptions),
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _extract_certainty(claim: Dict[str, Any]) -> float:
        cert = claim.get("certainty", 0.0)
        if isinstance(cert, dict):
            return float(cert.get("score", 0.0))
        try:
            return float(cert)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _extract_evidence_strength(claim: Dict[str, Any]) -> float:
        es = claim.get("evidence_strength", None)
        if es is not None:
            try:
                return float(es)
            except (TypeError, ValueError):
                pass
        # Fallback: use certainty as a proxy
        cert = claim.get("certainty", 0.0)
        if isinstance(cert, dict):
            return float(cert.get("score", 0.0))
        try:
            return float(cert)
        except (TypeError, ValueError):
            return 0.0
