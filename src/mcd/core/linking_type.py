"""Formal linking taxonomy for governed epistemic transitions."""
from __future__ import annotations

from enum import Enum


class LinkingType(str, Enum):
    SYMBOLIC = "symbolic"
    SEMANTIC = "semantic"
    CONTEXTUAL = "contextual"
    CAUSAL = "causal"
    INTERPRETIVE = "interpretive"
    EVIDENTIARY = "evidentiary"
    GOVERNED_CERTIFICATION = "governed_certification"


class LinkingTypeError(ValueError):
    """Raised when linking type parsing fails."""


def parse_linking_type(linking_type: LinkingType | str) -> LinkingType:
    if isinstance(linking_type, LinkingType):
        return linking_type
    normalized = (linking_type or "").strip().upper()
    try:
        return LinkingType[normalized]
    except KeyError as exc:
        raise LinkingTypeError(f"invalid linking type: {linking_type}") from exc


def certificate_eligible(linking_type: LinkingType | str) -> bool:
    return parse_linking_type(linking_type) is LinkingType.GOVERNED_CERTIFICATION
