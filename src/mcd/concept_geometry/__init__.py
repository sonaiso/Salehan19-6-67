"""Phase 8.3 — Jamid/Mushtaq Concept Geometry Layer.

Jamid (الجامد) = Essence Geometry: fixes the center of a concept (genus, species, differentia).
Mushtaq (المشتق) = Derivational Relation Geometry: opens the folded event/attribute relation.

Neither creates evidence or issues a Certificate. Both feed KernelProjection in CFK.
"""
from __future__ import annotations

from mcd.concept_geometry.jamid_schema import JamidEssence, EssenceType
from mcd.concept_geometry.mushtaq_schema import MushtaqUnit, DerivationType, ProjectedRelation
from mcd.concept_geometry.concept_center import ConceptCenter, build_concept_center
from mcd.concept_geometry.concept_geometry_projection import ConceptGeometryProjection, CONCEPT_GEOMETRY_CONTRACT

__all__ = [
    "JamidEssence", "EssenceType",
    "MushtaqUnit", "DerivationType", "ProjectedRelation",
    "ConceptCenter", "build_concept_center",
    "ConceptGeometryProjection", "CONCEPT_GEOMETRY_CONTRACT",
]
