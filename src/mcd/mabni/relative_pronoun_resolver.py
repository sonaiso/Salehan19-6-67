"""RelativePronounResolver — resolves Arabic relative pronouns."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RelativePronounResult:
    surface: str
    antecedent_type: str
    gender: str
    number: str
    opens_reference_node: bool
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "surface": self.surface,
            "antecedent_type": self.antecedent_type,
            "gender": self.gender,
            "number": self.number,
            "opens_reference_node": self.opens_reference_node,
            "warnings": self.warnings,
        }


_RELATIVE_PRONOUNS: dict[str, tuple[str, str, str]] = {
    "الذي": ("definite_masculine_noun", "masculine", "singular"),
    "التي": ("definite_feminine_noun", "feminine", "singular"),
    "اللذان": ("definite_masculine_noun", "masculine", "dual"),
    "اللتان": ("definite_feminine_noun", "feminine", "dual"),
    "الذين": ("definite_plural_noun", "masculine", "plural"),
    "اللواتي": ("definite_feminine_noun", "feminine", "plural"),
    "اللاتي": ("definite_feminine_noun", "feminine", "plural"),
    "اللائي": ("definite_feminine_noun", "feminine", "plural"),
}

_RELATIVE_INDETERMINATE = {"ما", "من"}


class RelativePronounResolver:
    """Resolves Arabic relative pronouns. All relative pronouns open reference nodes."""

    def resolve(self, text: str) -> RelativePronounResult:
        text_stripped = text.strip()
        tokens = text_stripped.split()
        warnings: list[str] = []

        for token in tokens:
            clean = _strip_diacritics(token)
            if clean in _RELATIVE_PRONOUNS:
                antecedent_type, gender, number = _RELATIVE_PRONOUNS[clean]
                return RelativePronounResult(
                    surface=clean,
                    antecedent_type=antecedent_type,
                    gender=gender,
                    number=number,
                    opens_reference_node=True,
                    warnings=warnings,
                )
            if clean in _RELATIVE_INDETERMINATE:
                return RelativePronounResult(
                    surface=clean,
                    antecedent_type="indeterminate",
                    gender="common",
                    number="common",
                    opens_reference_node=True,
                    warnings=["indeterminate relative; antecedent requires context"],
                )

        warnings.append("no relative pronoun found in text")
        return RelativePronounResult(
            surface="",
            antecedent_type="none",
            gender="unknown",
            number="unknown",
            opens_reference_node=False,
            warnings=warnings,
        )


def _strip_diacritics(text: str) -> str:
    diacritics = "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670"
    return "".join(c for c in text if c not in diacritics)
