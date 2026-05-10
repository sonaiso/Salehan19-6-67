"""JamidEssenceOntology — ontology of primitive Arabic nouns as essence nodes."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from mcd.concept_geometry.jamid_schema import JamidEssence, EssenceType

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "concept_geometry"

_BUILTIN: list[dict] = [
    {"essence_id": "JE-insan", "surface": "إنسان", "normalized": "إنسان",
     "essence_type": "species", "genus": "حيوان", "species": "إنسان",
     "differentia": ["ناطق", "عاقل", "مدرك"],
     "intrinsic_properties": ["حياة", "إدراك", "إرادة", "نطق"],
     "accidental_properties": ["طول", "لون", "وزن"],
     "part_whole_relations": ["جسم", "عقل", "روح"],
     "ownership_relations": [],
     "plural_forms": ["بشر", "أناس", "ناس"],
     "diminutive_forms": ["أنيسان"],
     "nisba_forms": ["إنساني"],
     "essence_vector": {"living": 1.0, "rational": 1.0, "social": 0.9},
     "domain_vector": {"human": 1.0, "biology": 0.6, "epistemology": 0.7},
     "trace_refs": [], "evidence_state": "missing", "certainty_policy": "grounding_required"},
    {"essence_id": "JE-hajar", "surface": "حجر", "normalized": "حجر",
     "essence_type": "natural_object", "genus": "جماد", "species": "صخرة",
     "differentia": ["صلب", "غير حي"],
     "intrinsic_properties": ["صلابة", "امتداد", "مادية"],
     "accidental_properties": ["حجم", "لون"],
     "part_whole_relations": [], "ownership_relations": [],
     "plural_forms": ["أحجار", "حجارة"], "diminutive_forms": ["حجير"],
     "nisba_forms": ["حجري"],
     "essence_vector": {"material": 1.0, "solid": 1.0},
     "domain_vector": {"universe": 0.9, "material": 1.0},
     "trace_refs": [], "evidence_state": "missing", "certainty_policy": "grounding_required"},
    {"essence_id": "JE-maa", "surface": "ماء", "normalized": "ماء",
     "essence_type": "material", "genus": "مادة", "species": "سائل",
     "differentia": ["H2O", "شفاف", "حيوي"],
     "intrinsic_properties": ["سيولة", "شفافية", "حيوية"],
     "accidental_properties": ["حرارة", "ملوحة"],
     "part_whole_relations": ["بحر", "نهر", "بئر"], "ownership_relations": [],
     "plural_forms": ["مياه"], "diminutive_forms": [],
     "nisba_forms": ["مائي"],
     "essence_vector": {"material": 1.0, "liquid": 1.0},
     "domain_vector": {"universe": 0.9, "material": 1.0, "life": 0.8},
     "trace_refs": [], "evidence_state": "missing", "certainty_policy": "grounding_required"},
    {"essence_id": "JE-nar", "surface": "نار", "normalized": "نار",
     "essence_type": "natural_object", "genus": "طاقة", "species": "حرارة",
     "differentia": ["محرقة", "مضيئة"],
     "intrinsic_properties": ["حرارة", "إضاءة", "احتراق"],
     "accidental_properties": ["لون", "حجم"],
     "part_whole_relations": ["لهب", "جمر", "دخان"], "ownership_relations": [],
     "plural_forms": ["نيران"], "diminutive_forms": [],
     "nisba_forms": ["ناري"],
     "essence_vector": {"energy": 1.0, "heat": 1.0},
     "domain_vector": {"universe": 0.9, "material": 0.8},
     "trace_refs": [], "evidence_state": "missing", "certainty_policy": "grounding_required"},
    {"essence_id": "JE-shajara", "surface": "شجرة", "normalized": "شجرة",
     "essence_type": "living_being", "genus": "نبات", "species": "شجرة",
     "differentia": ["ذات جذع", "مثمرة"],
     "intrinsic_properties": ["نمو", "تمثيل ضوئي", "تكاثر"],
     "accidental_properties": ["ارتفاع", "نوع الثمر"],
     "part_whole_relations": ["جذر", "جذع", "غصن", "ورقة", "ثمرة"],
     "ownership_relations": [],
     "plural_forms": ["أشجار", "شجر"], "diminutive_forms": ["شجيرة"],
     "nisba_forms": ["شجري"],
     "essence_vector": {"living": 1.0, "plant": 1.0},
     "domain_vector": {"biology": 0.9, "agriculture": 0.7},
     "trace_refs": [], "evidence_state": "missing", "certainty_policy": "grounding_required"},
    {"essence_id": "JE-kitab", "surface": "كتاب", "normalized": "كتاب",
     "essence_type": "artifact", "genus": "وعاء", "species": "وعاء معرفي",
     "differentia": ["مكتوب", "مجلد"],
     "intrinsic_properties": ["يحمل معرفة", "منظم", "قابل للقراءة"],
     "accidental_properties": ["حجم", "لون", "موضوع"],
     "part_whole_relations": ["صفحة", "غلاف", "فصل"],
     "ownership_relations": [],
     "plural_forms": ["كتب", "أكتاب"], "diminutive_forms": ["كتيب"],
     "nisba_forms": ["كتابي"],
     "essence_vector": {"artifact": 1.0, "knowledge_vessel": 0.9},
     "domain_vector": {"knowledge": 1.0, "culture": 0.8},
     "trace_refs": [], "evidence_state": "missing", "certainty_policy": "grounding_required"},
    {"essence_id": "JE-qalam", "surface": "قلم", "normalized": "قلم",
     "essence_type": "tool", "genus": "أداة", "species": "أداة كتابة",
     "differentia": ["يُكتب به"],
     "intrinsic_properties": ["حبر", "يكتب", "أداة"],
     "accidental_properties": ["حجم", "لون"],
     "part_whole_relations": ["رأس", "جسم"], "ownership_relations": [],
     "plural_forms": ["أقلام"], "diminutive_forms": ["قليم"],
     "nisba_forms": ["قلمي"],
     "essence_vector": {"tool": 1.0, "writing": 0.9},
     "domain_vector": {"knowledge": 0.8, "culture": 0.7},
     "trace_refs": [], "evidence_state": "missing", "certainty_policy": "grounding_required"},
    {"essence_id": "JE-bayt", "surface": "بيت", "normalized": "بيت",
     "essence_type": "artifact", "genus": "مكان", "species": "مسكن",
     "differentia": ["للإنسان", "مبني"],
     "intrinsic_properties": ["يؤوي", "مبني", "خاص"],
     "accidental_properties": ["حجم", "موقع"],
     "part_whole_relations": ["غرفة", "باب", "نافذة", "سقف"],
     "ownership_relations": [],
     "plural_forms": ["بيوت", "أبيات"], "diminutive_forms": ["بييت"],
     "nisba_forms": ["بيتي"],
     "essence_vector": {"place": 0.9, "artifact": 1.0},
     "domain_vector": {"human": 0.9, "society": 0.8},
     "trace_refs": [], "evidence_state": "missing", "certainty_policy": "grounding_required"},
    {"essence_id": "JE-madrasa", "surface": "مدرسة", "normalized": "مدرسة",
     "essence_type": "institution", "genus": "مؤسسة", "species": "مؤسسة تعليمية",
     "differentia": ["للتعليم"],
     "intrinsic_properties": ["تعليم", "منهج", "معلمون"],
     "accidental_properties": ["حجم", "موقع"],
     "part_whole_relations": ["فصل", "ملعب", "مكتبة"],
     "ownership_relations": [],
     "plural_forms": ["مدارس"], "diminutive_forms": [],
     "nisba_forms": ["مدرسي"],
     "essence_vector": {"institution": 1.0, "education": 1.0},
     "domain_vector": {"education": 1.0, "society": 0.8},
     "trace_refs": [], "evidence_state": "missing", "certainty_policy": "grounding_required"},
    {"essence_id": "JE-ilm", "surface": "علم", "normalized": "علم",
     "essence_type": "abstract_concept", "genus": "معرفة", "species": "معرفة منهجية",
     "differentia": ["يقين", "دليل"],
     "intrinsic_properties": ["إدراك", "يقين", "دليل"],
     "accidental_properties": ["موضوع", "مجال"],
     "part_whole_relations": [], "ownership_relations": [],
     "plural_forms": ["علوم"], "diminutive_forms": [],
     "nisba_forms": ["علمي"],
     "essence_vector": {"abstract": 1.0, "knowledge": 1.0},
     "domain_vector": {"epistemology": 1.0, "knowledge": 1.0},
     "trace_refs": [], "evidence_state": "missing", "certainty_policy": "context_required"},
    {"essence_id": "JE-adl", "surface": "عدل", "normalized": "عدل",
     "essence_type": "abstract_concept", "genus": "قيمة", "species": "قيمة أخلاقية",
     "differentia": ["إنصاف", "مساواة"],
     "intrinsic_properties": ["إنصاف", "مساواة", "ميزان"],
     "accidental_properties": ["تطبيق", "نطاق"],
     "part_whole_relations": [], "ownership_relations": [],
     "plural_forms": [], "diminutive_forms": [],
     "nisba_forms": ["عدلي"],
     "essence_vector": {"abstract": 1.0, "value": 1.0},
     "domain_vector": {"ethics": 1.0, "society": 0.9},
     "trace_refs": [], "evidence_state": "missing", "certainty_policy": "context_required"},
    {"essence_id": "JE-haqq", "surface": "حق", "normalized": "حق",
     "essence_type": "abstract_concept", "genus": "قيمة", "species": "قيمة قانونية",
     "differentia": ["ثابت", "مشروع"],
     "intrinsic_properties": ["ثبوت", "مشروعية", "استحقاق"],
     "accidental_properties": ["نوع", "نطاق"],
     "part_whole_relations": [], "ownership_relations": [],
     "plural_forms": ["حقوق"], "diminutive_forms": [],
     "nisba_forms": ["حقي", "حقوقي"],
     "essence_vector": {"abstract": 1.0, "right": 1.0},
     "domain_vector": {"law": 1.0, "ethics": 0.9},
     "trace_refs": [], "evidence_state": "missing", "certainty_policy": "context_required"},
]


class JamidEssenceOntology:
    """Ontology of Jamid essences: load, add, classify, project."""

    def __init__(self) -> None:
        self._essences: dict[str, JamidEssence] = {}
        self._load_builtin()
        self._load_seed()

    def _load_builtin(self) -> None:
        for d in _BUILTIN:
            e = JamidEssence.from_dict(d)
            self._essences[e.surface] = e

    def _load_seed(self) -> None:
        path = _DATA_DIR / "jamid_essence_seed_ar.jsonl"
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        d = json.loads(line)
                        e = JamidEssence.from_dict(d)
                        if e.surface not in self._essences:
                            self._essences[e.surface] = e
        except (FileNotFoundError, json.JSONDecodeError, TypeError):
            pass

    def add_essence(self, essence: JamidEssence) -> None:
        self._essences[essence.surface] = essence

    def get_by_surface(self, surface: str) -> Optional[JamidEssence]:
        return self._essences.get(surface)

    def all_essences(self) -> list[JamidEssence]:
        return list(self._essences.values())

    def classify_jamid(self, word: str) -> Optional[EssenceType]:
        e = self.get_by_surface(word)
        return e.essence_type if e else None

    def infer_essence_vector(self, word: str) -> dict[str, float]:
        e = self.get_by_surface(word)
        return e.essence_vector if e else {}

    def to_projection(self, word: str) -> dict:
        """Convert Jamid to a CFK-compatible projection dict (no Certificate)."""
        e = self.get_by_surface(word)
        if e is None:
            return {
                "source_layer": "concept_geometry",
                "projection_type": "concept_formation",
                "surface": word,
                "found": False,
                "can_create_evidence": False,
                "can_issue_certificate": False,
                "certainty_policy": "context_required",
            }
        return {
            "source_layer": "concept_geometry",
            "projection_type": "concept_formation",
            "surface": word,
            "found": True,
            "essence_type": e.essence_type.value if isinstance(e.essence_type, EssenceType) else e.essence_type,
            "genus": e.genus,
            "species": e.species,
            "differentia": e.differentia,
            "intrinsic_properties": e.intrinsic_properties,
            "domain_vector": e.domain_vector,
            "essence_vector": e.essence_vector,
            "can_create_evidence": False,
            "can_issue_certificate": False,
            "certainty_policy": e.certainty_policy,
        }
