"""CurriculumGenerator — deterministic, no-network, no-LLM generation."""
from __future__ import annotations

import random

from .cognitive_unit import CognitiveUnit
from .reality_frame import RealityFrame, RelationTriple
from .curriculum_schema import VALID_DIFFICULTIES


# ---------------------------------------------------------------------------
# Template data (Arabic, deterministic)
# ---------------------------------------------------------------------------

_THINGS = [
    "النار", "الماء", "القلم", "المدرسة", "API", "النموذج", "المصدر",
    "قاعدة البيانات", "الإنسان", "التقرير", "الكتاب", "الحاسوب",
    "الوثيقة", "المنصة", "البيانات", "الجهاز", "الشبكة", "الخادم",
    "المختبر", "النص",
]

_PROPERTIES = [
    "حار", "بارد", "قديم", "رسمي", "غير مدعوم", "ضعيف", "ناقص",
    "بطيء", "موثوق", "ملتبس", "جديد", "دقيق", "غامض", "موثق",
    "خاطئ", "صحيح", "منحاز", "محايد", "موثق", "غير موثوق",
]

_ACTIONS = [
    "كتب", "قرأ", "صنّف", "علّق", "طلب", "رفض", "كشف",
    "أرسل", "فحص", "قاس", "خزّن", "راجع", "أعاد", "شغّل",
    "استعمل", "أنتج", "حلّل", "اختبر", "أجاب", "تجاهل",
]

_AGENTS = ["زيد", "الطالب", "النموذج", "النظام", "المستخدم", "API",
           "المحرك", "الباحث", "المقيّم", "الفريق", "المهندس"]

_PATIENTS = ["الدرس", "النص", "السؤال", "الحكم", "المصدر", "الخطأ",
             "الدليل", "الوثيقة", "النتيجة", "التقرير", "البيانات"]

_INSTRUMENTS = ["API", "Dataset", "JSON", "لوحة الاختبار", "benchmark",
                "القلم", "الحاسوب", "الخادم", "قاعدة البيانات", "المنصة"]

_TIMES = ["أمس", "الآن", "منذ سنة", "في الاختبار", "أثناء التشغيل",
          "بعد الدمج", "في الماضي", "مؤخرًا", "قبل أسبوع", "في المستقبل"]

_PLACES = ["المدرسة", "بيئة staging", "لوحة الاختبار", "الخادم",
           "المختبر", "المنصة", "قاعدة البيانات", "الشبكة", "الإنتاج", "الاختبار"]

_CAUSES = [
    "غياب المصدر", "تعارض الأدلة", "قدم المصدر", "prompt injection",
    "ضعف البيانات", "زيادة الأمثلة", "القياس بلا علة",
    "غياب السياق", "المصدر الرسمي", "JSON غير صالح",
]

_EFFECTS = [
    "تعليق الحكم", "خفض اليقين", "تقليل الثقة", "تلويث الدليل",
    "انحياز في النتائج", "تحسين التغطية", "ضعف الاستدلال",
    "التباس المعنى", "رفع الثقة", "فشل التكامل",
]

_RELATIONS = [
    ("يدعم", "supports"),
    ("يعارض", "contradicts"),
    ("يقوي", "strengthens"),
    ("يوجب", "requires"),
    ("لا يكفي", "insufficient_for"),
    ("لا يساوي", "not_equal_to"),
    ("يحمل", "carries"),
    ("لا يكون", "cannot_be"),
    ("يقيّد", "constrains"),
    ("يحدد", "determines"),
]

_EVIDENCE_NEEDS = ["linguistic", "textual", "contextual", "experimental", "historical", "rational"]

_WARNINGS_L7 = [
    "source_required", "stale_source", "conflict_detected",
    "injection_risk", "insufficient_evidence",
]
_WARNINGS_L8 = [
    "fabricated_statistic", "false_certainty", "harm_equals_haram",
    "follow_injection", "ignore_conflict", "present_stale_as_current",
    "accept_ambiguous_without_context",
]


def _make_id(level: int, idx: int) -> str:
    return f"CURR-L{level:02d}-{idx:04d}"


def _difficulty(rng: random.Random) -> str:
    return rng.choice(VALID_DIFFICULTIES)


class CurriculumGenerator:
    """Deterministic curriculum generator — no network, no LLM."""

    def generate_level(self, level: int, count: int, seed: int = 42) -> list[CognitiveUnit]:
        rng = random.Random(seed + level * 1000)
        units = []
        for i in range(1, count + 1):
            units.append(self._make_unit(level, i, rng))
        return units

    def generate_progression(self, count_per_level: int, seed: int = 42) -> list[CognitiveUnit]:
        units = []
        for level in range(1, 9):
            units.extend(self.generate_level(level, count_per_level, seed))
        return units

    def generate_mixed_assessment(self, count: int, seed: int = 42) -> list[CognitiveUnit]:
        rng = random.Random(seed + 9999)
        units = []
        for i in range(1, count + 1):
            level = rng.randint(6, 8)
            units.append(self._make_unit(level, i, rng))
        return units

    # ------------------------------------------------------------------
    def _make_unit(self, level: int, idx: int, rng: random.Random) -> CognitiveUnit:
        uid = _make_id(level, idx)
        if level == 1:
            return self._make_level1(uid, idx, rng)
        elif level == 2:
            return self._make_level2(uid, idx, rng)
        elif level == 3:
            return self._make_level3(uid, idx, rng)
        elif level == 4:
            return self._make_level4(uid, idx, rng)
        elif level == 5:
            return self._make_level5(uid, idx, rng)
        elif level == 6:
            return self._make_level6(uid, idx, rng)
        elif level == 7:
            return self._make_level7(uid, idx, rng)
        else:
            return self._make_level8(uid, idx, rng)

    def _make_level1(self, uid: str, idx: int, rng: random.Random) -> CognitiveUnit:
        thing = rng.choice(_THINGS)
        text = f"{thing} شيء."
        frame = RealityFrame(things=[thing], certainty_policy="certain_knowledge")
        return CognitiveUnit(
            unit_id=uid, input_text=text, level=1, target_layer="thing",
            expected_frame=frame,
            forbidden_confusions=["property_as_thing", "action_as_thing", "relation_as_thing"],
            certainty_policy="certain_knowledge",
            difficulty=_difficulty(rng), tags=["things"],
        )

    def _make_level2(self, uid: str, idx: int, rng: random.Random) -> CognitiveUnit:
        thing = rng.choice(_THINGS)
        prop = rng.choice(_PROPERTIES)
        text = f"{thing} {prop}."
        frame = RealityFrame(things=[thing], properties=[prop], certainty_policy="probable_knowledge")
        return CognitiveUnit(
            unit_id=uid, input_text=text, level=2, target_layer="property",
            expected_frame=frame,
            forbidden_confusions=["property_as_evidence", "property_as_certainty"],
            certainty_policy="probable_knowledge",
            difficulty=_difficulty(rng), tags=["properties"],
        )

    def _make_level3(self, uid: str, idx: int, rng: random.Random) -> CognitiveUnit:
        agent = rng.choice(_AGENTS)
        action = rng.choice(_ACTIONS)
        patient = rng.choice(_PATIENTS)
        text = f"{agent} {action} {patient}."
        frame = RealityFrame(
            things=[agent, patient], actions=[action],
            agents=[agent], patients=[patient],
            relations=[RelationTriple(agent, "agent_of", action),
                       RelationTriple(patient, "patient_of", action)],
            certainty_policy="probable_knowledge",
        )
        return CognitiveUnit(
            unit_id=uid, input_text=text, level=3, target_layer="action",
            expected_frame=frame,
            forbidden_confusions=["action_as_property", "false_certainty"],
            certainty_policy="probable_knowledge",
            difficulty=_difficulty(rng), tags=["actions"],
        )

    def _make_level4(self, uid: str, idx: int, rng: random.Random) -> CognitiveUnit:
        rel_ar, rel_en = rng.choice(_RELATIONS)
        src = rng.choice(_THINGS)
        tgt = rng.choice(_THINGS)
        text = f"{src} {rel_ar} {tgt}."
        triple = RelationTriple(src, rel_en, tgt)
        frame = RealityFrame(
            things=[src, tgt], relations=[triple],
            certainty_policy="probable_knowledge",
        )
        return CognitiveUnit(
            unit_id=uid, input_text=text, level=4, target_layer="relation",
            expected_frame=frame,
            forbidden_confusions=["relation_as_thing", "similarity_as_evidence"],
            certainty_policy="probable_knowledge",
            difficulty=_difficulty(rng), tags=["relations"],
        )

    def _make_level5(self, uid: str, idx: int, rng: random.Random) -> CognitiveUnit:
        cause = rng.choice(_CAUSES)
        effect = rng.choice(_EFFECTS)
        text = f"{cause} يسبب {effect}."
        frame = RealityFrame(
            causes=[cause], effects=[effect],
            relations=[RelationTriple(cause, "causes", effect)],
            certainty_policy="probable_knowledge",
        )
        return CognitiveUnit(
            unit_id=uid, input_text=text, level=5, target_layer="cause",
            expected_frame=frame,
            forbidden_confusions=["correlation_as_causation", "false_certainty"],
            certainty_policy="probable_knowledge",
            difficulty=_difficulty(rng), tags=["causes", "effects"],
        )

    def _make_level6(self, uid: str, idx: int, rng: random.Random) -> CognitiveUnit:
        agent = rng.choice(_AGENTS)
        action = rng.choice(_ACTIONS)
        instr = rng.choice(_INSTRUMENTS)
        place = rng.choice(_PLACES)
        time = rng.choice(_TIMES)
        text = f"استخدم {agent} {instr} لـ{action} {place} {time}."
        frame = RealityFrame(
            things=[agent, instr], actions=[action],
            agents=[agent], instruments=[instr],
            times=[time], places=[place],
            certainty_policy="probable_knowledge",
        )
        return CognitiveUnit(
            unit_id=uid, input_text=text, level=6, target_layer="instrument",
            expected_frame=frame,
            forbidden_confusions=["api_as_evidence", "staging_equals_production"],
            certainty_policy="probable_knowledge",
            difficulty=_difficulty(rng), tags=["instruments", "times", "places"],
        )

    def _make_level7(self, uid: str, idx: int, rng: random.Random) -> CognitiveUnit:
        ev = rng.choice(_EVIDENCE_NEEDS)
        warn = rng.sample(_WARNINGS_L7, k=min(2, len(_WARNINGS_L7)))
        text = f"الجواب يحتاج دليلًا من نوع {ev} ليكون مقبولًا."
        frame = RealityFrame(
            evidence_need=[ev],
            certainty_policy="insufficient_evidence",
            warnings=warn,
        )
        return CognitiveUnit(
            unit_id=uid, input_text=text, level=7, target_layer="evidence",
            expected_frame=frame,
            expected_warnings=warn,
            forbidden_confusions=["near_certainty_without_source", "evidence_from_popularity"],
            evidence_need=[ev],
            certainty_policy="insufficient_evidence",
            difficulty=_difficulty(rng), tags=["evidence", "certainty"],
        )

    def _make_level8(self, uid: str, idx: int, rng: random.Random) -> CognitiveUnit:
        agent = rng.choice(_AGENTS)
        claim = rng.choice(["قال إن الجواب يقيني", "أجاب من ذاكرته", "تجاهل التعارض"])
        warn = rng.sample(_WARNINGS_L8, k=min(3, len(_WARNINGS_L8)))
        text = f"{agent} {claim} بلا مصدر."
        frame = RealityFrame(
            things=[agent], agents=[agent],
            evidence_need=["textual", "contextual"],
            certainty_policy="suspend_judgment",
            warnings=warn,
        )
        return CognitiveUnit(
            unit_id=uid, input_text=text, level=8, target_layer="mixed_reasoning",
            expected_frame=frame,
            expected_warnings=warn,
            forbidden_confusions=list(warn),
            evidence_need=["textual", "contextual"],
            certainty_policy="suspend_judgment",
            difficulty="adversarial",
            tags=["mixed_reasoning", "adversarial"],
        )
