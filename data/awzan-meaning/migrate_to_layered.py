# -*- coding: utf-8 -*-
"""
migrate_to_layered.py — هجرة pattern_operator_registry.json إلى البنية الطبقية الثلاثية

يحوّل كل وزن من النموذج الحالي (12 بُعداً) إلى النموذج الطبقي:
  Φ_E  existential_signature   (يُستنتَج آلياً من pattern_form)
  Φ_D  operator_vector         (الـ12 الحالية + stative_attribute=0 + subtypes=null)
  Φ_O  functional_operators    (يُستنتَج آلياً جزئياً)

المخرجات:
  1. pattern_operator_registry_v2.json   — الملف الجديد بالبنية الطبقية
  2. subtypes_to_fill.csv                — تقرير بالأوزان التي تحتاج subtype يدوياً
  3. migration_report.md                 — تقرير شامل بما تم آلياً وما يحتاج يداً
"""

import json
import csv
import os
import re
from pathlib import Path

# =============== ثوابت ===============

INPUT_PATH = "/home/claude/pattern_operator_registry.json"
OUTPUT_DIR = "/home/claude"
OUTPUT_V2 = os.path.join(OUTPUT_DIR, "pattern_operator_registry_v2.json")
OUTPUT_SUBTYPES = os.path.join(OUTPUT_DIR, "subtypes_to_fill.csv")
OUTPUT_REPORT = os.path.join(OUTPUT_DIR, "migration_report.md")

# الأبعاد الـ12 الحالية
DIMENSIONS_12 = [
    "agency", "patienthood", "causation", "place", "time", "instrument",
    "nisba", "comparison", "multiplication", "transformation", "masdar", "jamid"
]

# التشكيل
FATHA = "\u064E"
DAMMA = "\u064F"
KASRA = "\u0650"
SUKUN = "\u0652"
SHADDA = "\u0651"
DIACRITICS = "\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652"

# حروف الزيادة العشرة (سألتمونيها)
AUGMENT_LETTERS = set("سألتمونيها")

# الحروف الأصلية في الميزان الصرفي
FA_AIN_LAM = {"ف", "ع", "ل"}

# =============== استنتاج Φ_E آلياً ===============


def strip_diacritics(s):
    """إزالة التشكيل من النص."""
    return ''.join(c for c in s if c not in DIACRITICS)


def get_letters(wazn):
    """استخراج الحروف فقط من الوزن (بلا تشكيل)."""
    return [c for c in wazn if c not in DIACRITICS]


def detect_root_arity(pattern_form):
    """
    تحديد عدد أحرف الجذر من الوزن.
    نعدّ مواضع ف/ع/ل في الميزان:
      - 3 حروف (ف، ع، ل) → ثلاثي
      - 4 حروف (ف، ع، ل، ل) → رباعي (الميزان لـ فَعْلَل وأخواته)
      - 5 حروف → خماسي
    """
    letters = get_letters(pattern_form)
    fa_ain_lam_count = sum(1 for c in letters if c in FA_AIN_LAM)

    if fa_ain_lam_count == 3:
        return "ثلاثي"
    elif fa_ain_lam_count == 4:
        return "رباعي"
    elif fa_ain_lam_count == 5:
        return "خماسي"
    elif fa_ain_lam_count == 2:
        # حالة خاصة: قد يكون مضعّفاً (فَعّ، مَدّ) — نعتبره ثلاثياً
        return "ثلاثي"
    else:
        return "غير_محدد"


def detect_augmentation(pattern_form):
    """
    تحديد حالة الزيادة:
      - إن لم تحتوِ على حروف غير ف/ع/ل → مجرد
      - وإلا → مزيد، مع تحديد الأحرف المزيدة
    """
    letters = get_letters(pattern_form)
    augment_letters = []

    for letter in letters:
        if letter not in FA_AIN_LAM:
            # أي حرف غير ف/ع/ل في الميزان يُعتبر زائداً
            augment_letters.append(letter)

    status = "مجرد" if not augment_letters else "مزيد"
    return status, augment_letters


def detect_final_letter_type(pattern_form):
    """
    تحديد نوع آخر حرف:
      - منقوص: ينتهي بياء قبلها كسرة في موضع اللام
      - مقصور: ينتهي بألف (ا أو ى) في موضع اللام
      - ممدود: ينتهي بهمزة (ء) قبلها ألف
      - صحيح: غير ذلك
    """
    # نزيل التشكيل ونحلل آخر الكلمة
    bare = strip_diacritics(pattern_form)

    if bare.endswith("اء") or bare.endswith("آء"):
        return "ممدود"
    if bare.endswith("ى"):
        return "مقصور"
    if bare.endswith("ا") and len(bare) >= 2:
        return "مقصور"
    # المنقوص نادر في الأوزان (ياء + لام محذوفة)
    # نتحقق من النمط ـِي في الآخر
    if bare.endswith("ي"):
        # نفحص ما قبل الياء في الوزن المشكول
        # إن كان قبل الياء كسرة وكانت الياء آخر حرف → منقوص
        for i, c in enumerate(pattern_form):
            if c == "ي" and i == len(pattern_form) - 1:
                # نفحص ما قبل الياء
                if i >= 2 and pattern_form[i-1] == KASRA:
                    return "منقوص"
                # أو إذا كانت ياء النسبة (مشدّدة) فهي صحيح
                if i >= 1 and pattern_form[i-1] == SHADDA:
                    return "صحيح"
    return "صحيح"


def detect_gender_marker(pattern_form):
    """
    تحديد علامة الجنس:
      - مؤنث بالتاء: ينتهي بـ ة
      - مؤنث بألف التأنيث: ينتهي بـ ـاء أو ـى
      - مذكر: غير ذلك
    """
    bare = strip_diacritics(pattern_form)
    if bare.endswith("ة"):
        return "مؤنث_بالتاء"
    if bare.endswith("اء") or bare.endswith("آء"):
        return "مؤنث_بألف_التأنيث"
    if bare.endswith("ى"):
        return "مؤنث_بألف_التأنيث"
    return "مذكر"


def detect_number_marker(family, pattern_form):
    """
    تحديد علامة العدد من العائلة (family) وشكل الوزن.
    """
    if "plural" in family:
        if "broken" in family:
            return "جمع_تكسير"
        return "جمع"
    return "مفرد"


def detect_is_jamid(pattern_form, ov):
    """تحديد ما إذا كان الوزن جامداً من قيمة jamid في operator_vector."""
    jamid_val = ov.get("jamid", 0.0)
    return jamid_val >= 0.5


def build_existential_signature(pattern):
    """بناء التوقيع الوجودي Φ_E من بيانات الوزن."""
    pf = pattern["pattern_form"]
    family = pattern.get("family", "")
    ov = pattern.get("operator_vector", {})

    arity = detect_root_arity(pf)
    aug_status, aug_letters = detect_augmentation(pf)
    final_type = detect_final_letter_type(pf)
    gender = detect_gender_marker(pf)
    number = detect_number_marker(family, pf)
    is_jamid = detect_is_jamid(pf, ov)

    return {
        "root_arity": arity,
        "augmentation_status": aug_status,
        "augmentation_letters": aug_letters,
        "final_letter_type_default": final_type,
        "gender_marker": gender,
        "number_marker": number,
        "is_jamid": is_jamid
    }


# =============== استنتاج Φ_D ===============

def build_operator_vector(pattern):
    """نقل الـ12 + إضافة stative_attribute + subtypes=null."""
    ov_old = pattern.get("operator_vector", {})

    ov_new = {dim: ov_old.get(dim, 0.0) for dim in DIMENSIONS_12}
    ov_new["stative_attribute"] = 0.0  # سيُملأ يدوياً
    ov_new["subtypes"] = {
        "masdar": None,
        "multiplication": None,
        "comparison": None
    }
    return ov_new


# =============== استنتاج Φ_O آلياً ===============

def detect_voice(pattern_form, family):
    """
    تحديد voice (معلوم/مجهول) من الوزن والعائلة.
    """
    family_lower = family.lower()
    if "passive" in family_lower or "patient" in family_lower:
        return "مجهول"
    return "معلوم"


def detect_tense_marker(pattern_form, family):
    """
    تحديد الزمن من الوزن والعائلة. الأولوية للعائلة:
      - present/mudari في العائلة → مضارع
      - past/madi في العائلة → ماضٍ
      - imperative/amr → أمر
      - أوزان الأفعال الماضية المعروفة → ماضٍ
      - الأوزان الأخرى التي تبدأ بـ ي/ت/ن (وليس بعائلة فعل ماضٍ) → مضارع
      - الأسماء → null
    """
    pf_bare = strip_diacritics(pattern_form)
    family_lower = family.lower()

    # 1. الأولوية للعائلة الصريحة
    if "present" in family_lower or "mudari" in family_lower:
        return "مضارع"
    if "past" in family_lower or "madi" in family_lower:
        return "ماضٍ"
    if "imperative" in family_lower or "amr" in family_lower:
        return "أمر"

    # 2. عائلات الأفعال الماضية المعروفة (قبل الفحص الشكلي)
    past_verb_families = [
        "base_verb", "stative_verb", "quality_verb",
        "causative_verb", "intensive_verb", "derived_verb",
        "form3_verb", "form5_verb", "form6_verb",
        "form7_verb", "form8_verb", "form10_verb",
        "quadriliteral_verb"
    ]
    if any(vf in family_lower for vf in past_verb_families):
        return "ماضٍ"

    # 3. الأوزان التي تبدأ بحرف مضارعة (ي/ت/ن) في أول الوزن
    #    ملاحظة: لا نعدّ الهمزة (أ) دليلاً وحدها، لأنها قد تكون في وزن ماضٍ مثل أَفْعَل
    if pf_bare and pf_bare[0] in "يتن":
        # هذه أوزان مضارع للغائب/المخاطب/المتكلمين
        return "مضارع"

    # 4. الباقي: أسماء، لا زمن
    return None


def detect_mood(family):
    """تحديد صيغة الطلب."""
    family_lower = family.lower()
    if "imperative" in family_lower:
        return "أمر"
    return "خبر"


def detect_derivation_form(pattern_form, ex_sig):
    """
    تحديد درجة الاشتقاق من حالة الزيادة وعدد الأحرف المزيدة.
    """
    arity = ex_sig["root_arity"]
    aug_status = ex_sig["augmentation_status"]
    aug_count = len(ex_sig["augmentation_letters"])

    if arity == "ثلاثي":
        if aug_status == "مجرد":
            return "ثلاثي_مجرد"
        if aug_count == 1:
            return "ثلاثي_مزيد_بحرف"
        if aug_count == 2:
            return "ثلاثي_مزيد_بحرفين"
        if aug_count == 3:
            return "ثلاثي_مزيد_بثلاثة"
        if aug_count >= 4:
            return "ثلاثي_مزيد_بأربعة"

    if arity == "رباعي":
        if aug_status == "مجرد":
            return "رباعي_مجرد"
        return "رباعي_مزيد"

    return "غير_محدد"


def build_functional_operators(pattern, ex_sig):
    """بناء التوقيع الوظيفي Φ_O."""
    pf = pattern["pattern_form"]
    family = pattern.get("family", "")

    voice = detect_voice(pf, family)
    tense = detect_tense_marker(pf, family)
    mood = detect_mood(family)
    deriv_form = detect_derivation_form(pf, ex_sig)

    return {
        "voice": voice,
        "mood": mood,
        "tense_marker": tense,
        "phonological_processes": {
            "has_ialal": None,    # يحتاج تحليل سياقي للكلمة الفعلية
            "has_ibdaal": None,
            "has_idgham": None,
            "has_qalb": None,
            "has_hadhf": None
        },
        "derivation_form": deriv_form
    }


# =============== كشف الحاجة لـ subtypes ===============

def needs_subtype(pattern, ov_new):
    """
    تحديد ما إذا كان الوزن يحتاج subtype في أحد الأبعاد.
    نُرجع dict بالأبعاد التي تحتاج subtype.
    """
    needs = {}
    ov_old = pattern.get("operator_vector", {})

    # masdar: إذا كانت قيمة المصدر > 0.3
    if ov_old.get("masdar", 0) > 0.3:
        needs["masdar"] = {
            "current_value": ov_old["masdar"],
            "options": ["صريح", "ميمي", "صناعي", "مرة", "هيئة"]
        }

    # multiplication: إذا كانت > 0.3
    if ov_old.get("multiplication", 0) > 0.3:
        needs["multiplication"] = {
            "current_value": ov_old["multiplication"],
            "options": ["تكسير", "مذكر_سالم", "مؤنث_سالم", "مثنى", "اسم_جنس", "اسم_جمع"]
        }

    # comparison: إذا كانت > 0.3
    if ov_old.get("comparison", 0) > 0.3:
        needs["comparison"] = {
            "current_value": ov_old["comparison"],
            "options": ["مبالغة", "تفضيل", "تصغير"]
        }

    return needs


# =============== التحقق من stative_attribute ===============

def needs_stative_review(pattern):
    """
    أوزان قد تحتاج مراجعة لـ stative_attribute:
      - الصفات المشبهة (فَعِيل، فَعْلَان، أَفْعَل اللون)
      - بعض الأوزان التي قيمها agency/comparison مختلطة
    """
    family = pattern.get("family", "").lower()
    pf = pattern["pattern_form"]
    ov = pattern.get("operator_vector", {})

    candidates_families = [
        "attributive_adj", "intensive_state", "fem_color",
        "attributive_fem", "stative_verb"
    ]

    if any(c in family for c in candidates_families):
        return True

    # أوزان معروفة بأنها صفات مشبهة
    stative_patterns = ["فَعْلَان", "فَعْلَاء", "أَفْعَل"]
    pf_clean = strip_diacritics(pf)
    for sp in stative_patterns:
        if pf_clean == strip_diacritics(sp):
            return True

    return False


# =============== المعالجة الرئيسية ===============

def migrate_pattern(pattern):
    """تحويل وزن واحد إلى البنية الطبقية."""
    new_pattern = {
        "pattern_id": pattern["pattern_id"],
        "pattern_form": pattern["pattern_form"],
        "family": pattern.get("family", ""),
        "description": pattern.get("description", "")
    }

    # Φ_E
    ex_sig = build_existential_signature(pattern)
    new_pattern["existential_signature"] = ex_sig

    # Φ_D
    new_pattern["operator_vector"] = build_operator_vector(pattern)

    # Φ_O
    new_pattern["functional_operators"] = build_functional_operators(pattern, ex_sig)

    # metadata
    new_pattern["examples"] = pattern.get("examples", [])
    new_pattern["certainty_policy"] = pattern.get("certainty_policy", "medium")
    new_pattern["notes"] = pattern.get("notes", "")

    return new_pattern


def main():
    print(f"قراءة الملف: {INPUT_PATH}")
    with open(INPUT_PATH, encoding="utf-8") as f:
        data = json.load(f)

    patterns = data["patterns"]
    print(f"عدد الأوزان: {len(patterns)}")

    # تحويل كل الأوزان
    migrated = []
    subtypes_needed = []
    stative_review = []

    for p in patterns:
        new_p = migrate_pattern(p)
        migrated.append(new_p)

        # تتبع الأوزان التي تحتاج subtypes
        subtypes = needs_subtype(p, new_p["operator_vector"])
        if subtypes:
            subtypes_needed.append({
                "pattern_id": p["pattern_id"],
                "pattern_form": p["pattern_form"],
                "family": p.get("family", ""),
                "examples": " | ".join(p.get("examples", [])[:3]),
                "needs": subtypes
            })

        # تتبع الأوزان التي تحتاج مراجعة stative_attribute
        if needs_stative_review(p):
            stative_review.append({
                "pattern_id": p["pattern_id"],
                "pattern_form": p["pattern_form"],
                "family": p.get("family", ""),
                "examples": " | ".join(p.get("examples", [])[:3])
            })

    # كتابة pattern_operator_registry_v2.json
    output_data = {
        "_meta": {
            "version": "2.0",
            "schema": "layered_architecture",
            "description_ar": "البنية الطبقية الثلاثية: Φ_E (وجودية) + Φ_D (تحويلية) + Φ_O (وظيفية)",
            "layers": {
                "existential_signature": "Φ_E — ماهية الكلمة كصيغة صرفية",
                "operator_vector": "Φ_D — الدلالة التحويلية (الـ12 الأصلية + stative_attribute + subtypes)",
                "functional_operators": "Φ_O — العمليات الصرفية المطبّقة"
            },
            "migration_notes_ar": [
                "Φ_E مستنتجة آلياً من pattern_form",
                "Φ_D محفوظة من النموذج السابق + stative_attribute=0 + subtypes=null للمراجعة اليدوية",
                "Φ_O مستنتجة جزئياً (voice, mood, tense, derivation_form). الـ phonological_processes تحتاج سياق كلمة فعلية."
            ]
        },
        "patterns": migrated
    }

    with open(OUTPUT_V2, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"\n✓ كُتب: {OUTPUT_V2}")

    # كتابة subtypes_to_fill.csv
    with open(OUTPUT_SUBTYPES, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "pattern_id", "pattern_form", "family", "examples",
            "dimension_needing_subtype", "current_value", "subtype_options",
            "suggested_subtype", "notes"
        ])
        for item in subtypes_needed:
            for dim, info in item["needs"].items():
                writer.writerow([
                    item["pattern_id"],
                    item["pattern_form"],
                    item["family"],
                    item["examples"],
                    dim,
                    info["current_value"],
                    " | ".join(info["options"]),
                    "",  # للمراجعة اليدوية
                    ""
                ])
    print(f"✓ كُتب: {OUTPUT_SUBTYPES} ({sum(len(x['needs']) for x in subtypes_needed)} صف)")

    # تقرير الهجرة
    report = []
    report.append("# تقرير هجرة pattern_operator_registry إلى البنية الطبقية\n")
    report.append(f"## ملخص\n")
    report.append(f"- **عدد الأوزان المهاجرة**: {len(migrated)}\n")
    report.append(f"- **يحتاج subtype يدوي**: {len(subtypes_needed)} وزن، بإجمالي {sum(len(x['needs']) for x in subtypes_needed)} حقل\n")
    report.append(f"- **يحتاج مراجعة stative_attribute**: {len(stative_review)} وزن\n")

    # إحصائيات Φ_E
    arities = {}
    aug_dist = {}
    final_types = {}
    genders = {}
    for p in migrated:
        es = p["existential_signature"]
        arities[es["root_arity"]] = arities.get(es["root_arity"], 0) + 1
        aug_dist[es["augmentation_status"]] = aug_dist.get(es["augmentation_status"], 0) + 1
        final_types[es["final_letter_type_default"]] = final_types.get(es["final_letter_type_default"], 0) + 1
        genders[es["gender_marker"]] = genders.get(es["gender_marker"], 0) + 1

    report.append("\n## إحصائيات Φ_E (الطبقة الوجودية)\n")
    report.append("\n### توزيع root_arity\n")
    for k, v in sorted(arities.items(), key=lambda x: -x[1]):
        report.append(f"- {k}: {v}\n")

    report.append("\n### توزيع augmentation_status\n")
    for k, v in sorted(aug_dist.items(), key=lambda x: -x[1]):
        report.append(f"- {k}: {v}\n")

    report.append("\n### توزيع final_letter_type\n")
    for k, v in sorted(final_types.items(), key=lambda x: -x[1]):
        report.append(f"- {k}: {v}\n")

    report.append("\n### توزيع gender_marker\n")
    for k, v in sorted(genders.items(), key=lambda x: -x[1]):
        report.append(f"- {k}: {v}\n")

    # إحصائيات Φ_O
    voices = {}
    tenses = {}
    deriv_forms = {}
    for p in migrated:
        fo = p["functional_operators"]
        voices[fo["voice"]] = voices.get(fo["voice"], 0) + 1
        t = fo["tense_marker"] or "null"
        tenses[t] = tenses.get(t, 0) + 1
        deriv_forms[fo["derivation_form"]] = deriv_forms.get(fo["derivation_form"], 0) + 1

    report.append("\n## إحصائيات Φ_O (الطبقة الوظيفية)\n")
    report.append("\n### توزيع voice\n")
    for k, v in sorted(voices.items(), key=lambda x: -x[1]):
        report.append(f"- {k}: {v}\n")

    report.append("\n### توزيع tense_marker\n")
    for k, v in sorted(tenses.items(), key=lambda x: -x[1]):
        report.append(f"- {k}: {v}\n")

    report.append("\n### توزيع derivation_form\n")
    for k, v in sorted(deriv_forms.items(), key=lambda x: -x[1]):
        report.append(f"- {k}: {v}\n")

    # قائمة الأوزان التي تحتاج subtypes
    report.append("\n## الأوزان التي تحتاج subtypes (يدوي)\n")
    report.append("\nيُرجى ملء عمود `suggested_subtype` في ملف `subtypes_to_fill.csv` لهذه الأوزان:\n")
    report.append(f"\n**عدد الأوزان**: {len(subtypes_needed)}\n\n")

    for item in subtypes_needed[:20]:
        report.append(f"\n### {item['pattern_form']} (`{item['pattern_id']}`)\n")
        for dim, info in item["needs"].items():
            report.append(f"- **{dim}** (قيمته {info['current_value']}) → اختر من: {', '.join(info['options'])}\n")
    if len(subtypes_needed) > 20:
        report.append(f"\n*... و {len(subtypes_needed) - 20} وزن آخر في ملف CSV*\n")

    # قائمة الأوزان التي تحتاج مراجعة stative
    report.append("\n## الأوزان المرشحة لمراجعة stative_attribute\n")
    report.append(f"\n**عدد الأوزان**: {len(stative_review)}\n\n")
    for item in stative_review:
        report.append(f"- {item['pattern_form']} (`{item['pattern_id']}`) — أمثلة: {item['examples']}\n")

    # القيود
    report.append("\n## ملاحظات وقيود\n")
    report.append("\n1. **`phonological_processes`** كلها مضبوطة على `null` لأنها تحتاج تحليل كلمة فعلية، لا وزناً مجرداً. ستُملأ ديناميكياً في `analyze_word.py` عند تحليل كلمة.\n")
    report.append("\n2. **`stative_attribute`** كلها مضبوطة على 0.0. الأوزان المرشحة للمراجعة محدّدة أعلاه.\n")
    report.append("\n3. **`subtypes`** كلها مضبوطة على null. الأوزان التي تحتاج subtype محدّدة في `subtypes_to_fill.csv`.\n")
    report.append("\n4. الـ `pattern_form` لم تتغيّر إطلاقاً (لا تطبيع للتشكيل).\n")
    report.append("\n5. الملف الأصلي `pattern_operator_registry.json` بقي كما هو، الإخراج إلى `_v2`.\n")

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.writelines(report)
    print(f"✓ كُتب: {OUTPUT_REPORT}")

    # عرض ملخص
    print("\n" + "=" * 70)
    print("ملخص الهجرة:")
    print("=" * 70)
    print(f"  ✓ {len(migrated)} وزن تمت هجرته بالكامل")
    print(f"  ⚠ {len(subtypes_needed)} وزن يحتاج subtype يدوي")
    print(f"  ⚠ {len(stative_review)} وزن يحتاج مراجعة stative_attribute")
    print(f"\nالملفات المُنتَجة:")
    print(f"  1. {OUTPUT_V2}")
    print(f"  2. {OUTPUT_SUBTYPES}")
    print(f"  3. {OUTPUT_REPORT}")


if __name__ == "__main__":
    main()
