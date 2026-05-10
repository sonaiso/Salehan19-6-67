"""PatternOperatorLinker — maps patterns to operator types within concept geometry."""
from __future__ import annotations

from mcd.concept_geometry.mushtaq_schema import DerivationType, ProjectedRelation


class PatternOperatorLinker:
    """Links morphological patterns to their operator type and projected relation."""

    _PATTERN_OPS: dict[str, dict] = {
        "فاعل": {"derivation_type": DerivationType.ISM_FAAIL, "relation": ProjectedRelation.AGENT_OF, "certainty": 0.9},
        "مفعول": {"derivation_type": DerivationType.ISM_MAFOOL, "relation": ProjectedRelation.PATIENT_OF, "certainty": 0.9},
        "مفعل": {"derivation_type": DerivationType.ISM_MAKAN, "relation": ProjectedRelation.PLACE_OF, "certainty": 0.6},
        "مفعلة": {"derivation_type": DerivationType.ISM_MAKAN, "relation": ProjectedRelation.PLACE_OF, "certainty": 0.7},
        "فعالة": {"derivation_type": DerivationType.MASDAR, "relation": ProjectedRelation.HAS_PROPERTY, "certainty": 0.85},
        "فعيل": {"derivation_type": DerivationType.SIFAH_MUSHABBAHAH, "relation": ProjectedRelation.HAS_PROPERTY, "certainty": 0.75},
        "فعّال": {"derivation_type": DerivationType.SIGHAT_MUBALAGHAH, "relation": ProjectedRelation.INTENSIFIED_PROPERTY, "certainty": 0.8},
        "أفعل": {"derivation_type": DerivationType.ISM_TAFDIL, "relation": ProjectedRelation.COMPARATIVE_PROPERTY, "certainty": 0.85},
        "فعالي": {"derivation_type": DerivationType.NISBA, "relation": ProjectedRelation.ATTRIBUTED_TO, "certainty": 0.7},
        "مفعال": {"derivation_type": DerivationType.ISM_ALAH, "relation": ProjectedRelation.INSTRUMENT_OF, "certainty": 0.8},
    }

    def get_operator(self, pattern: str) -> dict:
        return self._PATTERN_OPS.get(pattern, {
            "derivation_type": DerivationType.UNKNOWN,
            "relation": ProjectedRelation.UNKNOWN,
            "certainty": 0.0,
        })

    def get_relation(self, pattern: str) -> ProjectedRelation:
        return self._PATTERN_OPS.get(pattern, {}).get("relation", ProjectedRelation.UNKNOWN)

    def get_certainty(self, pattern: str) -> float:
        return self._PATTERN_OPS.get(pattern, {}).get("certainty", 0.0)
