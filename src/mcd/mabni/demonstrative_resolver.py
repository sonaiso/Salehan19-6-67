"""DemonstrativeResolver — resolves Arabic demonstrative pronouns."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DemonstrativeResult:
    surface: str
    deixis: str
    gender: str
    number: str
    reference_node: str
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "surface": self.surface,
            "deixis": self.deixis,
            "gender": self.gender,
            "number": self.number,
            "reference_node": self.reference_node,
            "warnings": self.warnings,
        }


_DEMONSTRATIVES: dict[str, tuple[str, str, str]] = {
    "هذا": ("proximal", "masculine", "singular"),
    "هذه": ("proximal", "feminine", "singular"),
    "هذان": ("proximal", "masculine", "dual"),
    "هاتان": ("proximal", "feminine", "dual"),
    "هؤلاء": ("proximal", "common", "plural"),
    "ذلك": ("distal", "masculine", "singular"),
    "تلك": ("distal", "feminine", "singular"),
    "ذانك": ("distal", "masculine", "dual"),
    "تانك": ("distal", "feminine", "dual"),
    "أولئك": ("distal", "common", "plural"),
}


class DemonstrativeResolver:
    """Resolves Arabic demonstrative pronouns."""

    def resolve(self, text: str) -> DemonstrativeResult:
        text_stripped = text.strip()
        tokens = text_stripped.split()
        warnings: list[str] = []

        for token in tokens:
            clean = _strip_diacritics(token)
            if clean in _DEMONSTRATIVES:
                deixis, gender, number = _DEMONSTRATIVES[clean]
                return DemonstrativeResult(
                    surface=clean,
                    deixis=deixis,
                    gender=gender,
                    number=number,
                    reference_node=f"DEM_{clean}_{deixis.upper()}",
                    warnings=warnings,
                )

        warnings.append("no demonstrative found in text")
        return DemonstrativeResult(
            surface="",
            deixis="unknown",
            gender="unknown",
            number="unknown",
            reference_node="",
            warnings=warnings,
        )


def _strip_diacritics(text: str) -> str:
    diacritics = "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670"
    return "".join(c for c in text if c not in diacritics)
