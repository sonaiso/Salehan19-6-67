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

# "ما" and "من" are treated as indeterminate relatives ONLY when there is a
# relative-clause context cue (a definite noun antecedent preceding them, or
# a verbal predicate immediately following without a question-mark in the text).
# Bare "من" / "ما" in prepositional or interrogative contexts are handled by
# man_resolver / ma_resolver and must NOT be marked as relative here.
_RELATIVE_INDETERMINATE = {"ما", "من"}

# Tokens that signal the text is NOT a relative-clause context for ما/من.
# If any of these appear, or if there is no preceding definite noun, skip indeterminate match.
_NON_RELATIVE_SIGNALS = {"؟", "في", "من", "على", "عن", "إلى", "بـ", "لـ", "هل", "أين", "متى"}


def _has_relative_clause_context(tokens: list[str], indeterminate_idx: int) -> bool:
    """Return True only if ما/من at tokens[indeterminate_idx] is plausibly a relative.

    Heuristic: a relative ما/من is typically preceded by a verbal complement
    (a definite antecedent with ال prefix) OR immediately followed by a verb
    (not another particle/preposition).  Interrogative context (؟) disqualifies it.
    """
    text = " ".join(tokens)
    if "؟" in text:
        return False
    # Preceding token ends with ال-prefixed noun → likely relative antecedent
    if indeterminate_idx > 0:
        prev = _strip_diacritics(tokens[indeterminate_idx - 1])
        if prev.startswith("ال") and len(prev) > 2:
            return True
    # Following token looks like a verb (no ال prefix, length ≥ 3)
    if indeterminate_idx + 1 < len(tokens):
        nxt = _strip_diacritics(tokens[indeterminate_idx + 1])
        if not nxt.startswith("ال") and len(nxt) >= 3 and nxt not in _NON_RELATIVE_SIGNALS:
            return True
    return False


class RelativePronounResolver:
    """Resolves Arabic relative pronouns. All relative pronouns open reference nodes."""

    def resolve(self, text: str) -> RelativePronounResult:
        text_stripped = text.strip()
        tokens = text_stripped.split()
        warnings: list[str] = []

        for idx, token in enumerate(tokens):
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
                # Only treat ما/من as relative when context supports a relative clause
                if _has_relative_clause_context(tokens, idx):
                    return RelativePronounResult(
                        surface=clean,
                        antecedent_type="indeterminate",
                        gender="common",
                        number="common",
                        opens_reference_node=True,
                        warnings=["indeterminate relative; antecedent requires context"],
                    )
                # Otherwise skip — handled by ma_resolver / man_resolver
                warnings.append(
                    f"{clean}: ambiguous (preposition/interrogative/relative); "
                    "resolved by dedicated resolver"
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
