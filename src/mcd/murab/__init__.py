"""Phase 7.5 — Arabic Mu'rab / I'rab Relational Engineering Layer."""
from __future__ import annotations
from mcd.murab.murab_schema import MurabUnit
from mcd.murab.irab_case import IrabCase, load_irab_case_registry
from mcd.murab.irab_marker import IrabMarker, load_irab_marker_registry
from mcd.murab.governing_factor import GoverningFactor, load_governing_factors
from mcd.murab.case_resolver import CaseResolver

__all__ = [
    "MurabUnit", "IrabCase", "load_irab_case_registry",
    "IrabMarker", "load_irab_marker_registry",
    "GoverningFactor", "load_governing_factors",
    "CaseResolver",
]
