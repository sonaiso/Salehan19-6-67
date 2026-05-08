"""Rule-based classifiers for the Bayani Mustadil Runtime Engine.

Two classifiers are implemented here:

1. ``prompt_type_classifier``   — maps a raw prompt to one of PT-01..PT-10.
2. ``mustadil_prompt_classifier`` — maps a raw prompt to an
   :class:`~bayani.runtime.contracts.IntentClassificationResult` that covers
   the eleven MPC layers (MPC-01..MPC-11).

Both classifiers are intentionally *rule-based* in v0.1 so that the runtime
has no external dependencies.  Each rule is expressed as a tuple of
``(pattern_keywords, type_id, type_name, matched_rule_description)``.
Rules are evaluated in order; the first match wins.  A catch-all fallback is
always returned when no rule matches.
"""

from __future__ import annotations

import re
from typing import List, Tuple

from bayani.runtime.contracts import IntentClassificationResult, PromptTypeResult


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _contains(text: str, *keywords: str) -> bool:
    """Return True if *any* keyword appears in *text* (case-insensitive)."""
    t = text.casefold()
    return any(kw.casefold() in t for kw in keywords)


def _contains_all(text: str, *keywords: str) -> bool:
    """Return True if *all* keywords appear in *text* (case-insensitive)."""
    t = text.casefold()
    return all(kw.casefold() in t for kw in keywords)


# ---------------------------------------------------------------------------
# Prompt-Type rules   (PT-01 .. PT-10)
# ---------------------------------------------------------------------------
# Each entry is:
#   (matcher_callable, type_id, type_name, matched_rule_description)

_PT_RULES: List[Tuple] = [
    # PT-01  Existence — is something present / does a text exist?
    (
        lambda t: _contains(t, "هل هذا موجود", "هل ورد", "هل وجد", "هل يوجد",
                             "هل النص موجود", "هل اللفظ", "هل ورد اللفظ",
                             "هل يوجد", "is it present", "does it exist")
                  or ("هل" in t and "موجود" in t),
        "PT-01", "Existence Prompt",
        "Prompt asks about existence of a text, token, or entity.",
    ),
    # PT-02  Definition — what does X mean / define X
    # Note: "ما مفهوم" is intentionally excluded here because it routes to PT-07.
    (
        lambda t: _contains(t, "ما معنى", "عرّف", "عرف ", "ما هو", "ما هي",
                             "ما تعريف", "define", "what is", "ما المراد"),
        "PT-02", "Definition Prompt",
        "Prompt requests a definition or meaning of a term or concept.",
    ),
    # PT-03  Attribute — what are the properties / attributes of X
    (
        lambda t: _contains(t, "ما صفات", "ما خصائص", "ما أوصاف", "ما سمات",
                             "what are the attributes", "what are the properties"),
        "PT-03", "Attribute Prompt",
        "Prompt inquires about the attributes or properties of an entity.",
    ),
    # PT-04  Relational — what is the relation between X and Y
    (
        lambda t: _contains(t, "ما العلاقة", "ما الفرق", "قارن", "ما الصلة",
                             "what is the relation", "compare", "distinguish"),
        "PT-04", "Relational Prompt",
        "Prompt asks about the relation between two or more concepts.",
    ),
    # PT-05  Linguistic/Syntactic — parse, irab, Arabic grammar
    (
        lambda t: _contains(t, "أعرب", "ما إعراب", "ما الإعراب", "حلّل",
                             "parse", "syntactic", "نحو", "صرف"),
        "PT-05", "Linguistic/Syntactic Prompt",
        "Prompt requests grammatical/syntactic analysis.",
    ),
    # PT-09  Illah/Qiyas — BEFORE PT-06/07 to avoid false mantuq/mafhoom match
    (
        lambda t: _contains(t, "هل الوصف علة", "هل العلة", "ما علة", "ما سبب التحريم",
                             "قياس", "علة التحريم", "علة الحكم",
                             "هل الإسكار", "يقاس", "illah", "qiyas"),
        "PT-09", "Illah/Qiyas Prompt",
        "Prompt asks about a causal juridical relation (illah/qiyas).",
    ),
    # PT-07  Mafhoom — implicit implication / mafhoom al-mukhalafa
    # (checked before PT-06 because "مفهوم" could overlap with definition queries)
    (
        lambda t: _contains(t, "مفهوم المخالفة", "مفهوم الموافقة",
                             "دلالة المفهوم", "implicit meaning", "mafhoom",
                             "ما مفهوم"),
        "PT-07", "Mafhoom Prompt",
        "Prompt asks about the implicit (mafhoom) meaning of a text.",
    ),
    # PT-06  Mantuq — explicit textual implication
    (
        lambda t: _contains(t, "منطوق", "دلالة النص", "ما دل عليه النص",
                             "explicit meaning", "mantuq"),
        "PT-06", "Mantuq Prompt",
        "Prompt asks about the explicit (mantuq) meaning of a text.",
    ),
    # PT-08  General/Specific — 'aam / khaas / qat'i
    (
        lambda t: _contains(t, "العام", "الخاص", "قطعي الدلالة", "هل العام قطعي",
                             "تخصيص", "general", "specific", "aam", "khaas"),
        "PT-08", "General/Specific Prompt",
        "Prompt asks about the generality or specificity of a ruling or text.",
    ),
    # PT-10  Application — apply a ruling to a specific case
    (
        lambda t: _contains(t, "طبّق", "نزّل", "تطبيق الحكم", "طبق الحكم",
                             "apply", "application", "implement ruling",
                             "تنزيل الحكم", "طبق هذا"),
        "PT-10", "Application Prompt",
        "Prompt requests application of a ruling to a concrete case.",
    ),
]

_PT_FALLBACK = ("PT-02", "Definition Prompt", "No specific rule matched; defaulting to definition/explanation type.")


def prompt_type_classifier(prompt_text: str) -> PromptTypeResult:
    """Classify *prompt_text* into one of PT-01..PT-10.

    Rules are evaluated in priority order; the first matching rule wins.
    """
    for matcher, type_id, type_name, rule_desc in _PT_RULES:
        try:
            if matcher(prompt_text):
                return PromptTypeResult(
                    type_id=type_id,
                    type_name=type_name,
                    confidence="high",
                    matched_rule=rule_desc,
                )
        except Exception:
            continue

    type_id, type_name, rule_desc = _PT_FALLBACK
    return PromptTypeResult(
        type_id=type_id,
        type_name=type_name,
        confidence="low",
        matched_rule=rule_desc,
    )


# ---------------------------------------------------------------------------
# Mustadil Prompt Classifier   (MPC-01 .. MPC-11)
# ---------------------------------------------------------------------------

def mustadil_prompt_classifier(prompt_text: str) -> IntentClassificationResult:
    """Classify the *intent* of *prompt_text* across the eleven MPC layers.

    Returns an :class:`IntentClassificationResult` covering:
    - MPC-01 Purpose Layer
    - MPC-02 Thinking Level Layer
    - MPC-03 Hukm Knowledge vs Istinbat Layer
    - MPC-04 Taqlid/Tarjih Layer
    - MPC-05 Evidence Authentication Layer
    - MPC-06 Usul vs Furu Evidence Rank Layer
    - MPC-07 Evidence Type Classification Layer
    - MPC-08 Conflict and Tarjih Layer
    - MPC-09 Manat vs Illah Layer
    - MPC-10 Construction Intent Layer
    - MPC-11 Malakah Building Layer
    """
    t = prompt_text

    # ---- MPC-01: Primary purpose ----------------------------------------
    primary_purpose = _detect_primary_purpose(t)
    secondary_purposes = _detect_secondary_purposes(t, primary_purpose)
    mpc_layers: list[str] = ["MPC-01"]

    # ---- MPC-02: Thinking level -----------------------------------------
    mpc_layers.append("MPC-02")
    thinking_level = "deep"
    if _contains(t, "باختصار", "بإيجاز", "briefly", "summarize", "اختصر"):
        thinking_level = "shallow"
    elif _contains(t, "اشرح", "وضّح", "بالتفصيل", "explain", "detail"):
        thinking_level = "standard"

    # ---- MPC-03: Hukm knowledge vs istinbat -----------------------------
    mpc_layers.append("MPC-03")
    hukm_mode = "knowledge"
    if _contains(t, "استنبط", "استخرج الحكم", "ما الحكم الفقهي", "istinbat",
                 "derive the ruling", "استنباط"):
        hukm_mode = "istinbat"

    # ---- MPC-04: Taqlid / tarjih ----------------------------------------
    mpc_layers.append("MPC-04")
    tarjih_required = _contains(t, "رجّح", "الراجح", "أيهما أقوى", "tarjih",
                                  "ترجيح", "الأرجح")

    # ---- MPC-05: Evidence authentication --------------------------------
    mpc_layers.append("MPC-05")
    evidence_required = _contains(t, "الدليل", "الحديث", "الآية", "evidence",
                                    "proof", "البرهان", "المصدر")

    # ---- MPC-06: Usul vs furu evidence rank -----------------------------
    mpc_layers.append("MPC-06")

    # ---- MPC-07: Evidence type classification ---------------------------
    mpc_layers.append("MPC-07")

    # ---- MPC-08: Conflict and tarjih ------------------------------------
    mpc_layers.append("MPC-08")

    # ---- MPC-09: Manat vs illah -----------------------------------------
    mpc_layers.append("MPC-09")
    tahqeeq_manat_required = _contains(t, "تحقيق المناط", "مناط", "manat",
                                         "tahqeeq", "تحقق من الواقعة",
                                         "طبّق", "نزّل", "تطبيق", "تنزيل")

    # ---- MPC-10: Construction intent ------------------------------------
    mpc_layers.append("MPC-10")
    construction_intent = _contains(t, "ابنِ", "أنشئ", "صمّم", "construct",
                                      "build schema", "اصنع", "schema")

    # ---- MPC-11: Malakah building ---------------------------------------
    mpc_layers.append("MPC-11")
    malakah_mode = _contains(t, "ملكة", "malakah", "تدريب", "training",
                               "تعلّم", "learning", "how to reason")

    return IntentClassificationResult(
        primary_purpose=primary_purpose,
        secondary_purposes=secondary_purposes,
        thinking_level=thinking_level,
        malakah_mode=malakah_mode,
        hukm_mode=hukm_mode,
        evidence_required=evidence_required,
        tarjih_required=tarjih_required,
        tahqeeq_manat_required=tahqeeq_manat_required,
        construction_intent=construction_intent,
        mpc_layers_activated=mpc_layers,
    )


# ---------------------------------------------------------------------------
# Internal helpers for MPC-01
# ---------------------------------------------------------------------------

_PURPOSE_RULES: List[Tuple[callable, str]] = [
    (lambda t: _contains(t, "طبّق", "نزّل", "طبق"), "tahqeeq_manat"),
    (lambda t: _contains(t, "استنبط", "استنباط", "istinbat", "استخرج الحكم"), "hukm_istinbat"),
    (lambda t: _contains(t, "رجّح", "ترجيح", "tarjih", "الراجح"), "tarjih"),
    (lambda t: _contains(t, "تحقيق المناط", "تحقق", "manat"), "tahqeeq_manat"),
    (lambda t: _contains(t, "ابنِ", "أنشئ", "schema", "construct"), "schema_construction"),
    (lambda t: _contains(t, "ملكة", "malakah", "تدريب"), "malakah_building"),
    (lambda t: _contains(t, "ما حكم", "ما الحكم", "حكم الشرع", "hukm"), "hukm_knowledge"),
    (lambda t: _contains(t, "اشرح", "وضّح", "explain", "describe"), "explanation"),
    (lambda t: _contains(t, "بناء البرومبت", "prompt construction"), "prompt_construction"),
]


def _detect_primary_purpose(text: str) -> str:
    for matcher, purpose in _PURPOSE_RULES:
        try:
            if matcher(text):
                return purpose
        except Exception:
            continue
    return "direct_answer"


def _detect_secondary_purposes(text: str, primary: str) -> List[str]:
    secondaries = []
    for matcher, purpose in _PURPOSE_RULES:
        if purpose == primary:
            continue
        try:
            if matcher(text) and purpose not in secondaries:
                secondaries.append(purpose)
        except Exception:
            continue
    return secondaries[:3]  # cap at three secondary purposes
