"""TawabiEngine — handles Arabic توابع (followers that inherit I'rab)."""
from __future__ import annotations
from dataclasses import dataclass
from mcd.murab.murab_schema import MurabUnit
from typing import Optional
from enum import Enum


class TabiType(str, Enum):
    NAAT = "naat"        # نعت
    ATF = "atf"          # عطف
    TAWKID = "tawkid"    # توكيد
    BADAL = "badal"      # بدل
    ATF_BAYAN = "atf_bayan"  # عطف بيان


@dataclass
class TabiRelation:
    matbu: str
    tabi: str
    tabi_type: TabiType
    inherited_case: str
    matbu_id: str
    tabi_id: str
    certainty: float

    def to_dict(self) -> dict:
        return {
            "matbu": self.matbu,
            "tabi": self.tabi,
            "tabi_type": self.tabi_type.value,
            "inherited_case": self.inherited_case,
            "matbu_id": self.matbu_id,
            "tabi_id": self.tabi_id,
            "certainty": self.certainty,
        }


ATF_CONJUNCTIONS = {"وَ", "فَ", "ثُمَّ", "أو", "أم", "بَل", "لَكِن", "لا", "وَلَكِن"}


class TawabiEngine:
    """Handles تابع / متبوع relations. Tabi' inherits I'rab of matbu'."""

    def detect_tawabi(self, units: list) -> list:
        """Detect tabi' relations from MurabUnit list."""
        relations = []

        for i in range(len(units) - 1):
            unit = units[i]
            next_unit = units[i + 1]

            tabi_type = self._classify_tabi(unit, next_unit)
            if tabi_type:
                relations.append(TabiRelation(
                    matbu=unit.surface,
                    tabi=next_unit.surface,
                    tabi_type=tabi_type,
                    inherited_case=unit.irab_case,
                    matbu_id=unit.unit_id,
                    tabi_id=next_unit.unit_id,
                    certainty=0.75,
                ))

        return relations

    def apply_inheritance(self, matbu: MurabUnit, tabi: MurabUnit) -> MurabUnit:
        """Apply case inheritance from matbu' to tabi'."""
        tabi.irab_case = matbu.irab_case
        tabi.irab_marker = matbu.irab_marker
        tabi.marker_visibility = matbu.marker_visibility
        return tabi

    def _classify_tabi(self, unit: MurabUnit, next_unit: MurabUnit) -> Optional[TabiType]:
        """Classify tabi type between adjacent units."""
        if unit.irab_case == next_unit.irab_case and unit.irab_case != "unknown":
            return TabiType.NAAT
        return None
