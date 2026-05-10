"""MushtaqDerivationEngine — infers root, pattern, derivation type, and projected relation."""
from __future__ import annotations

import uuid
from typing import Optional

from mcd.concept_geometry.mushtaq_schema import MushtaqUnit, DerivationType, ProjectedRelation


# ── Pattern → DerivationType ─────────────────────────────────────────────────

_PATTERN_TO_TYPE: dict[str, DerivationType] = {
    "فاعل": DerivationType.ISM_FAAIL,
    "فعّال": DerivationType.SIGHAT_MUBALAGHAH,
    "فعول": DerivationType.SIGHAT_MUBALAGHAH,
    "فعيل": DerivationType.SIFAH_MUSHABBAHAH,
    "مفعول": DerivationType.ISM_MAFOOL,
    "مفعل": DerivationType.ISM_MAKAN,
    "مفعلة": DerivationType.ISM_MAKAN,
    "فعلة": DerivationType.MASDAR,
    "فعال": DerivationType.MASDAR,
    "فعل": DerivationType.MASDAR,
    "تفعيل": DerivationType.MASDAR,
    "استفعال": DerivationType.MASDAR,
    "مفاعلة": DerivationType.MASDAR,
    "أفعل": DerivationType.ISM_TAFDIL,
    "فعليّ": DerivationType.NISBA,
    "فعّالة": DerivationType.ISM_ALAH,
    "مفعال": DerivationType.ISM_ALAH,
}

# ── DerivationType → ProjectedRelation ───────────────────────────────────────

_TYPE_TO_RELATION: dict[DerivationType, ProjectedRelation] = {
    DerivationType.ISM_FAAIL: ProjectedRelation.AGENT_OF,
    DerivationType.ISM_MAFOOL: ProjectedRelation.PATIENT_OF,
    DerivationType.SIFAH_MUSHABBAHAH: ProjectedRelation.HAS_PROPERTY,
    DerivationType.MASDAR: ProjectedRelation.HAS_PROPERTY,
    DerivationType.MASDAR_MIMI: ProjectedRelation.HAS_PROPERTY,
    DerivationType.ISM_ALAH: ProjectedRelation.INSTRUMENT_OF,
    DerivationType.ISM_ZAMAN: ProjectedRelation.TIME_OF,
    DerivationType.ISM_MAKAN: ProjectedRelation.PLACE_OF,
    DerivationType.SIGHAT_MUBALAGHAH: ProjectedRelation.INTENSIFIED_PROPERTY,
    DerivationType.ISM_TAFDIL: ProjectedRelation.COMPARATIVE_PROPERTY,
    DerivationType.NISBA: ProjectedRelation.ATTRIBUTED_TO,
    DerivationType.INDUSTRIAL_MASDAR: ProjectedRelation.HAS_PROPERTY,
    DerivationType.DIMINUTIVE: ProjectedRelation.HAS_PROPERTY,
    DerivationType.BROKEN_PLURAL: ProjectedRelation.HAS_PROPERTY,
}

# ── Known word database ───────────────────────────────────────────────────────

_KNOWN: dict[str, dict] = {
    "كاتب": {"root": "ك ت ب", "pattern": "فاعل", "derivation_type": DerivationType.ISM_FAAIL,
              "folded_event": "كتابة", "projected_relation": ProjectedRelation.AGENT_OF,
              "role_vector": {"agent": 0.95, "event_bound": 0.85},
              "certainty_policy": "pattern_confirmed"},
    "مكتوب": {"root": "ك ت ب", "pattern": "مفعول", "derivation_type": DerivationType.ISM_MAFOOL,
               "folded_event": "كتابة", "projected_relation": ProjectedRelation.PATIENT_OF,
               "role_vector": {"patient": 0.95, "affected_entity": 0.8},
               "certainty_policy": "pattern_confirmed"},
    "مكتب": {"root": "ك ت ب", "pattern": "مفعل", "derivation_type": DerivationType.ISM_MAKAN,
              "folded_event": "كتابة",
              "projected_relation": ProjectedRelation.UNKNOWN,
              "candidate_relations": ["place_of", "instrument_of", "institution_of"],
              "role_vector": {"place": 0.6, "instrument": 0.4},
              "certainty_policy": "context_required"},
    "كتابة": {"root": "ك ت ب", "pattern": "فعالة", "derivation_type": DerivationType.MASDAR,
               "folded_event": "كتابة", "projected_relation": ProjectedRelation.HAS_PROPERTY,
               "role_vector": {"event": 1.0}, "certainty_policy": "pattern_confirmed"},
    "مكتبة": {"root": "ك ت ب", "pattern": "مفعلة", "derivation_type": DerivationType.ISM_MAKAN,
               "folded_event": "كتابة", "projected_relation": ProjectedRelation.PLACE_OF,
               "role_vector": {"place": 0.9}, "certainty_policy": "pattern_confirmed"},
    "كتابي": {"root": "ك ت ب", "pattern": "فعالي", "derivation_type": DerivationType.NISBA,
               "folded_event": "كتابة", "projected_relation": ProjectedRelation.ATTRIBUTED_TO,
               "role_vector": {"domain": 0.9}, "certainty_policy": "context_required"},
    "عالم": {"root": "ع ل م", "pattern": "فاعل", "derivation_type": DerivationType.ISM_FAAIL,
              "folded_event": "علم", "projected_relation": ProjectedRelation.AGENT_OF,
              "role_vector": {"agent": 0.9}, "certainty_policy": "pattern_confirmed"},
    "معلوم": {"root": "ع ل م", "pattern": "مفعول", "derivation_type": DerivationType.ISM_MAFOOL,
               "folded_event": "علم", "projected_relation": ProjectedRelation.PATIENT_OF,
               "role_vector": {"patient": 0.9}, "certainty_policy": "pattern_confirmed"},
    "تعليم": {"root": "ع ل م", "pattern": "تفعيل", "derivation_type": DerivationType.MASDAR,
               "folded_event": "تعليم", "projected_relation": ProjectedRelation.HAS_PROPERTY,
               "role_vector": {"event": 1.0}, "certainty_policy": "pattern_confirmed"},
    "متعلم": {"root": "ع ل م", "pattern": "متفعل", "derivation_type": DerivationType.ISM_MAFOOL,
               "folded_event": "تعلم", "projected_relation": ProjectedRelation.PATIENT_OF,
               "role_vector": {"patient": 0.85}, "certainty_policy": "pattern_confirmed"},
    "زارع": {"root": "ز ر ع", "pattern": "فاعل", "derivation_type": DerivationType.ISM_FAAIL,
              "folded_event": "زراعة", "projected_relation": ProjectedRelation.AGENT_OF,
              "role_vector": {"agent": 0.9}, "certainty_policy": "pattern_confirmed"},
    "مزروع": {"root": "ز ر ع", "pattern": "مفعول", "derivation_type": DerivationType.ISM_MAFOOL,
               "folded_event": "زراعة", "projected_relation": ProjectedRelation.PATIENT_OF,
               "role_vector": {"patient": 0.9}, "certainty_policy": "pattern_confirmed"},
    "زراعة": {"root": "ز ر ع", "pattern": "فعالة", "derivation_type": DerivationType.MASDAR,
               "folded_event": "زراعة", "projected_relation": ProjectedRelation.HAS_PROPERTY,
               "role_vector": {"event": 1.0}, "certainty_policy": "pattern_confirmed"},
    "مزرعة": {"root": "ز ر ع", "pattern": "مفعلة", "derivation_type": DerivationType.ISM_MAKAN,
               "folded_event": "زراعة", "projected_relation": ProjectedRelation.PLACE_OF,
               "role_vector": {"place": 0.9}, "certainty_policy": "pattern_confirmed"},
    "زراعي": {"root": "ز ر ع", "pattern": "فعالي", "derivation_type": DerivationType.NISBA,
               "folded_event": "زراعة", "projected_relation": ProjectedRelation.ATTRIBUTED_TO,
               "role_vector": {"domain": 0.9}, "certainty_policy": "context_required"},
}


class MushtaqDerivationEngine:
    """Analyze Arabic words to build MushtaqUnit objects."""

    def analyze(self, word: str) -> MushtaqUnit:
        if word in _KNOWN:
            k = _KNOWN[word]
            return MushtaqUnit(
                mushtaq_id=f"MU-{word}-{uuid.uuid4().hex[:6]}",
                surface=word,
                normalized=word,
                root=k["root"],
                pattern=k["pattern"],
                derivation_type=k["derivation_type"],
                folded_event=k.get("folded_event", ""),
                projected_relation=k.get("projected_relation", ProjectedRelation.UNKNOWN),
                candidate_relations=k.get("candidate_relations", []),
                role_vector=k.get("role_vector", {}),
                event_vector=k.get("event_vector", {"event": 1.0} if k.get("folded_event") else {}),
                context_requirements=k.get("context_requirements", []),
                certainty_policy=k.get("certainty_policy", "context_required"),
            )
        # Unknown word — return unknown with context_required
        return MushtaqUnit(
            mushtaq_id=f"MU-{word}-{uuid.uuid4().hex[:6]}",
            surface=word,
            normalized=word,
            root="",
            pattern="",
            derivation_type=DerivationType.UNKNOWN,
            projected_relation=ProjectedRelation.UNKNOWN,
            certainty_policy="context_required",
            context_requirements=["root_identification", "pattern_matching"],
        )

    def build_mushtaq_unit(self, surface: str, root: str, pattern: str,
                           derivation_type: DerivationType,
                           folded_event: str = "",
                           projected_relation: Optional[ProjectedRelation] = None) -> MushtaqUnit:
        if projected_relation is None:
            projected_relation = _TYPE_TO_RELATION.get(derivation_type, ProjectedRelation.UNKNOWN)
        return MushtaqUnit.make(
            surface=surface, root=root, pattern=pattern,
            derivation_type=derivation_type,
            folded_event=folded_event,
            projected_relation=projected_relation,
        )
