"""HalTamyizEngine — distinguishes حال from تمييز (both accusative)."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class HalTamyizResult:
    surface: str
    result_type: str  # hal|tamyiz
    syntactic_role: str
    semantic_role: str
    certainty: float
    notes: str

    def to_dict(self) -> dict:
        return {
            "surface": self.surface,
            "result_type": self.result_type,
            "syntactic_role": self.syntactic_role,
            "semantic_role": self.semantic_role,
            "certainty": self.certainty,
            "notes": self.notes,
        }


class HalTamyizEngine:
    """Distinguishes حال (state) from تمييز (specification) — both are accusative."""

    TAMYIZ_WORDS = {"كيلوغراماً", "متراً", "عاماً", "رطلاً", "ليلةً", "ميلاً", "قدماً", "شبراً",
                    "نفساً", "عقلاً", "ساعةً", "يوماً", "شهراً"}

    HAL_PATTERNS = {"راكباً", "ماشياً", "فرحاً", "حزيناً", "ضاحكاً", "باكياً", "مسرعاً", "قائماً",
                    "قاعداً", "نائماً", "جالساً"}

    def classify(self, surface: str, context_tokens: list, position: int) -> HalTamyizResult:
        """Classify an accusative token as hal or tamyiz."""
        stripped = self._strip_diacritics(surface)

        if surface in self.TAMYIZ_WORDS or stripped in {self._strip_diacritics(w) for w in self.TAMYIZ_WORDS}:
            return HalTamyizResult(
                surface=surface,
                result_type="tamyiz",
                syntactic_role="tamyiz",
                semantic_role="specification",
                certainty=0.8,
                notes="unit of measure or specification",
            )

        if surface in self.HAL_PATTERNS or stripped in {self._strip_diacritics(w) for w in self.HAL_PATTERNS}:
            return HalTamyizResult(
                surface=surface,
                result_type="hal",
                syntactic_role="hal",
                semantic_role="state_description",
                certainty=0.8,
                notes="state description (حال)",
            )

        if position > 0:
            prev = self._strip_diacritics(context_tokens[position - 1])
            if self._is_number(prev):
                return HalTamyizResult(
                    surface=surface,
                    result_type="tamyiz",
                    syntactic_role="tamyiz",
                    semantic_role="specification",
                    certainty=0.85,
                    notes="follows a number",
                )

        return HalTamyizResult(
            surface=surface,
            result_type="hal",
            syntactic_role="hal",
            semantic_role="state_description",
            certainty=0.5,
            notes="uncertain hal/tamyiz",
        )

    def _strip_diacritics(self, text: str) -> str:
        diacritics = set('\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652')
        return ''.join(c for c in text if c not in diacritics)

    def _is_number(self, text: str) -> bool:
        arabic_numbers = {"واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة", "عشرة",
                          "عشرون", "ثلاثون", "مائة", "ألف"}
        return text.isdigit() or text in arabic_numbers
