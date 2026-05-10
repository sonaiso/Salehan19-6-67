"""Serializers for Phase 8.3 concept geometry layer."""
from __future__ import annotations

import json

from mcd.concept_geometry.jamid_schema import JamidEssence
from mcd.concept_geometry.mushtaq_schema import MushtaqUnit
from mcd.concept_geometry.concept_center import ConceptCenter


def jamid_to_json(je: JamidEssence) -> str:
    return json.dumps(je.to_dict(), ensure_ascii=False, indent=2)


def mushtaq_to_json(mu: MushtaqUnit) -> str:
    return json.dumps(mu.to_dict(), ensure_ascii=False, indent=2)


def concept_center_to_json(cc: ConceptCenter) -> str:
    return json.dumps(cc.to_dict(), ensure_ascii=False, indent=2)


def jamid_from_json(s: str) -> JamidEssence:
    return JamidEssence.from_dict(json.loads(s))


def mushtaq_from_json(s: str) -> MushtaqUnit:
    return MushtaqUnit.from_dict(json.loads(s))
