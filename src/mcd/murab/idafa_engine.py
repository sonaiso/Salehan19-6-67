"""IdafaEngine — classifies the type of an Idafa (إضافة) construction."""
from __future__ import annotations

from mcd.murab.murab_schema import MurabUnit


# Rule: إضافة لا تعني ملكية دائمًا — idafa does not always mean ownership
_OWNERSHIP_MARKERS = {"بيت", "كتاب", "سيارة", "قلم", "مال", "دار"}
_PART_WHOLE_MARKERS = {"باب", "نهاية", "بداية", "رأس", "قلب", "يد", "قدم"}
_MASDAR_MARKERS = {"قراءة", "كتابة", "فهم", "علم", "ضرب", "نصر"}


class IdafaEngine:
    """Classifies the semantic type of an إضافة construction.

    idafa_types:
        ownership | specification | part_whole | bayan |
        masdar_to_agent | masdar_to_patient | lafziyya | manawiyya
    """

    def resolve(
        self,
        mudaf: MurabUnit,
        mudaf_ilayh: MurabUnit,
    ) -> dict:
        warnings: list[str] = []
        import re
        _H = re.compile(r"[\u064b-\u065f]")
        mudaf_bare = _H.sub("", mudaf.surface)
        mudaf_ilayh_bare = _H.sub("", mudaf_ilayh.surface)

        idafa_type = self._classify(mudaf_bare, mudaf_ilayh_bare)

        if idafa_type == "ownership":
            warnings.append("idafa_not_always_ownership_verify_context")

        return {
            "idafa_type": idafa_type,
            "mudaf_id": mudaf.unit_id,
            "mudaf_ilayh_id": mudaf_ilayh.unit_id,
            "certainty_policy": "probable_syntactic",
            "warnings": warnings,
        }

    def _classify(self, mudaf: str, mudaf_ilayh: str) -> str:
        if any(m in mudaf for m in _MASDAR_MARKERS):
            return "masdar_to_agent"
        if any(m in mudaf for m in _PART_WHOLE_MARKERS):
            return "part_whole"
        if any(m in mudaf for m in _OWNERSHIP_MARKERS):
            return "ownership"
        # Default: specification (الإضافة المعنوية)
        return "specification"
