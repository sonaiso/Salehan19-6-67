"""CivilizationCivility — classifies items as civilization vs. civility."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CivilizationCivilityResult:
    item: str
    is_civilization: bool
    is_civility: bool
    civilizational_concept: Optional[str] = None
    technical_form: Optional[str] = None
    risk_of_value_transfer: float = 0.0
    evidence: list[str] = field(default_factory=list)
    certainty: float = 0.5
    explanation: str = ""


# Keywords indicating pure tools (civility / مدنية)
_TOOL_KEYWORDS = {
    "سيارة", "طائرة", "هاتف", "حاسوب", "آلة", "أداة", "تقنية", "جهاز",
    "مكيف", "مصنع", "كهرباء", "طب", "دواء",
}

# Keywords indicating concepts about life/values (civilization / حضارة)
_CIVILIZATION_KEYWORDS = {
    "الديمقراطية", "الحرية", "العدالة", "الدين", "الإسلام", "العلمانية",
    "الرأسمالية", "الاشتراكية", "الإنسانية", "الحقوق", "الأخلاق", "القيم",
    "النظام", "السلطة", "السيادة", "الدولة",
}

# AI-specific terms — hybrid (civility tool but potentially carries civilizational assumptions)
_AI_KEYWORDS = {
    "الذكاء", "الاصطناعي", "ذكاء", "اصطناعي",
    "خوارزمية", "نموذج", "بيانات", "تعلم",
}


class CivilizationCivilityDeepClassifier:
    """Classifies whether an item is civilization (حضارة) or civility (مدنية)."""

    def classify(self, item: str, context: str = "") -> CivilizationCivilityResult:
        text = f"{item} {context}".lower()
        words = text.split()

        is_civilization = False
        is_civility = False
        risk = 0.0
        civilizational_concept: Optional[str] = None
        technical_form: Optional[str] = None
        explanation_parts: list[str] = []

        # Check for AI terms first (special case)
        is_ai = any(kw in item for kw in _AI_KEYWORDS)

        if is_ai:
            is_civility = True
            technical_form = item
            risk = 0.6
            explanation_parts.append(
                "الذكاء الاصطناعي أداة تقنية (مدنية) لكنه قد يحمل افتراضات حضارية "
                "عن الإنسان والقرار والمعرفة والسلطة"
            )
            # Partial civilization if the context suggests value transfer
            if any(w in context for w in ["الإنسان", "القرار", "المعرفة", "السلطة", "القيم"]):
                is_civilization = True
                civilizational_concept = "مفهوم الإنسان والقرار والمعرفة"

        # Check for pure tools
        tool_match = any(kw in item for kw in _TOOL_KEYWORDS)
        if tool_match and not is_ai:
            is_civility = True
            technical_form = item
            explanation_parts.append(f"'{item}' أداة تقنية بحتة (مدنية) — لا تحمل مفهومًا حضاريًا بذاتها")

        # Check for civilization keywords
        civ_match = any(kw in item for kw in _CIVILIZATION_KEYWORDS)
        if civ_match:
            is_civilization = True
            civilizational_concept = item
            explanation_parts.append(f"'{item}' مفهوم حضاري يتعلق بالقيم والحياة")

        # Default: if neither matched, check by context
        if not is_civility and not is_civilization:
            # Heuristic: abstract nouns tend to be civilizational
            if len(item) > 3 and not any(char.isdigit() for char in item):
                is_civilization = True
                civilizational_concept = item
                explanation_parts.append(f"'{item}' يبدو مفهومًا مجردًا — يُصنَّف مبدئيًا حضاريًا")
            else:
                is_civility = True
                technical_form = item
                explanation_parts.append(f"'{item}' يبدو أداةً محددة — يُصنَّف مبدئيًا مدنيًا")

        return CivilizationCivilityResult(
            item=item,
            is_civilization=is_civilization,
            is_civility=is_civility,
            civilizational_concept=civilizational_concept,
            technical_form=technical_form,
            risk_of_value_transfer=risk,
            certainty=0.6,
            explanation=" | ".join(explanation_parts),
        )
