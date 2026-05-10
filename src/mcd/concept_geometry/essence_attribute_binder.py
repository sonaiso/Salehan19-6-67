"""EssenceAttributeBinder — binds JamidEssence to MushtaqUnit attributes."""
from __future__ import annotations

from mcd.concept_geometry.jamid_schema import JamidEssence
from mcd.concept_geometry.mushtaq_schema import MushtaqUnit


class EssenceAttributeBinding:
    """Result of binding an essence to an attribute."""
    def __init__(self, essence: JamidEssence, attribute: MushtaqUnit) -> None:
        self.essence = essence
        self.attribute = attribute
        self.binding_type = self._infer_binding()

    def _infer_binding(self) -> str:
        rel = self.attribute.projected_relation.value if hasattr(self.attribute.projected_relation, "value") else str(self.attribute.projected_relation)
        if rel == "agent_of":
            return "essence_is_agent"
        elif rel == "patient_of":
            return "essence_is_patient"
        elif rel == "has_property":
            return "essence_has_property"
        elif rel == "instrument_of":
            return "essence_is_instrument"
        elif rel == "place_of":
            return "essence_is_place"
        elif rel == "attributed_to":
            return "essence_in_domain"
        return "essence_with_attribute"

    def to_dict(self) -> dict:
        return {
            "essence_surface": self.essence.surface,
            "attribute_surface": self.attribute.surface,
            "binding_type": self.binding_type,
            "folded_event": self.attribute.folded_event,
            "projected_relation": (
                self.attribute.projected_relation.value
                if hasattr(self.attribute.projected_relation, "value")
                else str(self.attribute.projected_relation)
            ),
            "can_create_evidence": False,
            "can_issue_certificate": False,
        }


class EssenceAttributeBinder:
    """Binds JamidEssence nodes to MushtaqUnit attribute nodes."""

    def bind(self, essence: JamidEssence, attribute: MushtaqUnit) -> EssenceAttributeBinding:
        return EssenceAttributeBinding(essence, attribute)

    def describe(self, essence: JamidEssence, attribute: MushtaqUnit) -> str:
        b = self.bind(essence, attribute)
        return f"{essence.surface} ({essence.essence_type.value}) → {b.binding_type} → {attribute.surface}"
