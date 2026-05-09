"""UsuliTarjih — conflict resolution engine using usul al-fiqh principles."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ConflictType(str, Enum):
    DAL = "dal"
    MADLUL = "madlul"
    REALITY = "reality"
    EVIDENCE = "evidence"
    RULE = "rule"
    VALUE = "value"
    SHARI = "shari"


class ResolutionStrategy(str, Enum):
    COMBINE = "combine"
    SPECIFY = "specify"
    RESTRICT = "restrict"
    PREFER = "prefer"
    SUSPEND = "suspend"


@dataclass
class TarjihResult:
    conflict_type: ConflictType
    claims: list[dict]
    resolution_strategy: ResolutionStrategy
    preferred_claim: Optional[dict]
    suspended_claims: list[dict]
    explanation: str
    certainty: float


class UsuliTarjihEngine:
    """Resolve conflicts between claims using usul al-fiqh tarjih rules."""

    def resolve(self, conflict_type: ConflictType, claims: list[dict]) -> TarjihResult:
        if len(claims) < 2:
            return TarjihResult(
                conflict_type=conflict_type,
                claims=claims,
                resolution_strategy=ResolutionStrategy.SUSPEND,
                preferred_claim=claims[0] if claims else None,
                suspended_claims=[],
                explanation="لا يوجد تعارض مع مطالبة واحدة فقط",
                certainty=0.5,
            )

        # Apply fake_evidence filter first
        valid_claims = [c for c in claims if not c.get("fake_evidence", False)]
        invalid_claims = [c for c in claims if c.get("fake_evidence", False)]

        # Lower certainty for claims with no source
        adjusted_claims = []
        for c in valid_claims:
            c2 = dict(c)
            if not c2.get("source"):
                c2["certainty"] = c2.get("certainty", 0.5) * 0.6
                c2["_no_source"] = True
            adjusted_claims.append(c2)

        # Check if claims are compatible (combine)
        if self._are_compatible(adjusted_claims):
            return TarjihResult(
                conflict_type=conflict_type,
                claims=claims,
                resolution_strategy=ResolutionStrategy.COMBINE,
                preferred_claim=None,
                suspended_claims=[],
                explanation="المطالبات متوافقة ويمكن الجمع بينها",
                certainty=0.75,
            )

        # General vs specific (specify)
        general, specific = self._find_general_specific(adjusted_claims)
        if general is not None and specific is not None:
            return TarjihResult(
                conflict_type=conflict_type,
                claims=claims,
                resolution_strategy=ResolutionStrategy.SPECIFY,
                preferred_claim=specific,
                suspended_claims=[general],
                explanation="تخصيص العام بالخاص — يُقدَّم الخاص",
                certainty=0.70,
            )

        # Absolute vs restricted (restrict)
        absolute_c, restricted_c = self._find_absolute_restricted(adjusted_claims)
        if absolute_c is not None and restricted_c is not None:
            return TarjihResult(
                conflict_type=conflict_type,
                claims=claims,
                resolution_strategy=ResolutionStrategy.RESTRICT,
                preferred_claim=restricted_c,
                suspended_claims=[absolute_c],
                explanation="تقييد المطلق بالمقيد — يُقدَّم المقيد",
                certainty=0.68,
            )

        # Prefer claim with higher certainty (if significant difference)
        sorted_claims = sorted(adjusted_claims, key=lambda c: c.get("certainty", 0.5), reverse=True)
        top = sorted_claims[0]
        rest = sorted_claims[1:]

        if top.get("certainty", 0.5) - sorted_claims[-1].get("certainty", 0.5) >= 0.2:
            return TarjihResult(
                conflict_type=conflict_type,
                claims=claims,
                resolution_strategy=ResolutionStrategy.PREFER,
                preferred_claim=top,
                suspended_claims=rest + invalid_claims,
                explanation="يُرجَّح الدليل الأقوى يقيناً",
                certainty=top.get("certainty", 0.5),
            )

        # No clear winner — suspend
        return TarjihResult(
            conflict_type=conflict_type,
            claims=claims,
            resolution_strategy=ResolutionStrategy.SUSPEND,
            preferred_claim=None,
            suspended_claims=adjusted_claims + invalid_claims,
            explanation="لا يوجد مُرجِّح واضح — التوقف عن الترجيح",
            certainty=0.3,
        )

    def _are_compatible(self, claims: list[dict]) -> bool:
        """Claims are compatible if they address different aspects (no negation)."""
        # Check if any claim explicitly negates another
        for c in claims:
            if c.get("negates"):
                return False

        # General vs specific — not compatible (handled by SPECIFY strategy)
        scopes = [c.get("scope", "") for c in claims]
        if set(scopes) == {"general", "specific"}:
            return False

        # Absolute vs restricted — not compatible (handled by RESTRICT strategy)
        has_absolute = any(c.get("is_absolute", False) for c in claims)
        has_restricted = any(c.get("is_restricted", False) for c in claims)
        if has_absolute and has_restricted:
            return False

        # Claims with is_compatible flag
        if all(c.get("is_compatible", False) for c in claims):
            return True

        # If all claims have completely different non-conflicting scopes, they can be combined
        if len(set(scopes)) == len(scopes) and all(scopes) and not {"general", "specific"} & set(scopes):
            return True

        return False

    def _find_general_specific(self, claims: list[dict]) -> tuple[Optional[dict], Optional[dict]]:
        general = None
        specific = None
        for c in claims:
            scope = c.get("scope", "")
            if scope == "general" or c.get("is_general", False):
                general = c
            elif scope == "specific" or c.get("is_specific", False):
                specific = c
        if general and specific:
            return general, specific
        return None, None

    def _find_absolute_restricted(self, claims: list[dict]) -> tuple[Optional[dict], Optional[dict]]:
        absolute_c = None
        restricted_c = None
        for c in claims:
            if c.get("is_absolute", False):
                absolute_c = c
            elif c.get("is_restricted", False):
                restricted_c = c
        if absolute_c and restricted_c:
            return absolute_c, restricted_c
        return None, None
