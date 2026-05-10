"""MushtaqUnit — Derivational Relation Geometry for Arabic derived words.

المشتق = مفهوم مطوي يحمل علاقة بين ذات وحدث أو صفة:
  جذر + وزن + operator = علاقة مطوية (فاعلية، مفعولية، آلة، مكان، نسبة…)
  لا يثبت وقوع الحدث. لا ينشئ دليلاً.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class DerivationType(str, Enum):
    ISM_FAAIL = "ism_faail"          # اسم فاعل
    ISM_MAFOOL = "ism_mafool"        # اسم مفعول
    SIFAH_MUSHABBAHAH = "sifah_mushabbahah"  # صفة مشبهة
    MASDAR = "masdar"                # مصدر
    MASDAR_MIMI = "masdar_mimi"      # مصدر ميمي
    ISM_ALAH = "ism_alah"            # اسم آلة
    ISM_ZAMAN = "ism_zaman"          # اسم زمان
    ISM_MAKAN = "ism_makan"          # اسم مكان
    SIGHAT_MUBALAGHAH = "sighat_mubalaghah"  # صيغة مبالغة
    ISM_TAFDIL = "ism_tafdil"        # اسم تفضيل
    NISBA = "nisba"                  # نسبة
    INDUSTRIAL_MASDAR = "industrial_masdar"  # مصدر صناعي
    DIMINUTIVE = "diminutive"        # تصغير
    BROKEN_PLURAL = "broken_plural"  # جمع تكسير
    UNKNOWN = "unknown"


class ProjectedRelation(str, Enum):
    AGENT_OF = "agent_of"
    PATIENT_OF = "patient_of"
    HAS_PROPERTY = "has_property"
    INSTRUMENT_OF = "instrument_of"
    TIME_OF = "time_of"
    PLACE_OF = "place_of"
    ATTRIBUTED_TO = "attributed_to"
    INTENSIFIED_PROPERTY = "intensified_property"
    COMPARATIVE_PROPERTY = "comparative_property"
    TRANSFORMED_STATE = "transformed_state"
    UNKNOWN = "unknown"


@dataclass
class MushtaqUnit:
    """Full Mushtaq Unit schema with CFK-compatible fields."""
    mushtaq_id: str
    surface: str
    normalized: str
    root: str                           # e.g. "ك ت ب"
    pattern: str                        # e.g. "فاعل"
    derivation_type: DerivationType
    folded_event: str = ""              # the event folded inside (e.g. "كتابة")
    projected_relation: ProjectedRelation = ProjectedRelation.UNKNOWN
    candidate_relations: list[str] = field(default_factory=list)
    operator_vector: dict[str, float] = field(default_factory=dict)
    role_vector: dict[str, float] = field(default_factory=dict)
    event_vector: dict[str, float] = field(default_factory=dict)
    context_requirements: list[str] = field(default_factory=list)
    certainty_policy: str = "context_required"
    trace_refs: list[str] = field(default_factory=list)

    # ── Hard rules ──────────────────────────────────────────────────────────
    can_create_evidence: bool = False
    can_issue_certificate: bool = False
    can_prove_event_occurred: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "can_create_evidence", False)
        object.__setattr__(self, "can_issue_certificate", False)
        object.__setattr__(self, "can_prove_event_occurred", False)

    def to_dict(self) -> dict:
        return {
            "mushtaq_id": self.mushtaq_id,
            "surface": self.surface,
            "normalized": self.normalized,
            "root": self.root,
            "pattern": self.pattern,
            "derivation_type": self.derivation_type.value if isinstance(self.derivation_type, DerivationType) else self.derivation_type,
            "folded_event": self.folded_event,
            "projected_relation": self.projected_relation.value if isinstance(self.projected_relation, ProjectedRelation) else self.projected_relation,
            "candidate_relations": self.candidate_relations,
            "operator_vector": self.operator_vector,
            "role_vector": self.role_vector,
            "event_vector": self.event_vector,
            "context_requirements": self.context_requirements,
            "certainty_policy": self.certainty_policy,
            "trace_refs": self.trace_refs,
            "can_create_evidence": False,
            "can_issue_certificate": False,
            "can_prove_event_occurred": False,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "MushtaqUnit":
        d = dict(d)
        d.pop("can_create_evidence", None)
        d.pop("can_issue_certificate", None)
        d.pop("can_prove_event_occurred", None)
        dt = d.get("derivation_type", "unknown")
        try:
            d["derivation_type"] = DerivationType(dt)
        except ValueError:
            d["derivation_type"] = DerivationType.UNKNOWN
        pr = d.get("projected_relation", "unknown")
        try:
            d["projected_relation"] = ProjectedRelation(pr)
        except ValueError:
            d["projected_relation"] = ProjectedRelation.UNKNOWN
        return cls(**d)

    @classmethod
    def make(cls, surface: str, root: str, pattern: str, derivation_type: DerivationType,
             folded_event: str = "", projected_relation: ProjectedRelation = ProjectedRelation.UNKNOWN,
             **kwargs) -> "MushtaqUnit":
        return cls(
            mushtaq_id=f"MU-{uuid.uuid4().hex[:10]}",
            surface=surface,
            normalized=surface,
            root=root,
            pattern=pattern,
            derivation_type=derivation_type,
            folded_event=folded_event,
            projected_relation=projected_relation,
            **kwargs,
        )
