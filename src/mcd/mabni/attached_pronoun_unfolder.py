"""AttachedPronounUnfolder — detects and unfolds Arabic attached pronouns."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PronounUnfoldResult:
    pronoun_form: str
    base_word: str
    role: str
    person: str
    number: str
    gender: str
    referent_known: bool
    certainty_policy: str
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "pronoun_form": self.pronoun_form,
            "base_word": self.base_word,
            "role": self.role,
            "person": self.person,
            "number": self.number,
            "gender": self.gender,
            "referent_known": self.referent_known,
            "certainty_policy": self.certainty_policy,
            "warnings": self.warnings,
        }


# Suffix → (pronoun_form, person, number, gender, roles)
_PRONOUN_SUFFIXES: list[tuple[str, str, str, str, str, list[str]]] = [
    # (suffix, pronoun_form, person, number, gender, possible_roles)
    ("هم", "هم", "third", "plural", "masculine", ["possessor", "object", "prep_object"]),
    ("هن", "هن", "third", "plural", "feminine", ["possessor", "object", "prep_object"]),
    ("كم", "كم", "second", "plural", "masculine", ["possessor", "object", "prep_object"]),
    ("نا", "نا", "first", "plural", "common", ["possessor", "object", "subject_marker"]),
    ("ها", "ها", "third", "singular", "feminine", ["possessor", "object", "prep_object"]),
    ("ه", "ه", "third", "singular", "masculine", ["possessor", "object", "prep_object"]),
    ("ك", "ك", "second", "singular", "common", ["possessor", "object", "prep_object"]),
    ("ي", "ي", "first", "singular", "common", ["possessor", "indirect_object"]),
]


class AttachedPronounUnfolder:
    """Detects Arabic attached (suffixed) pronouns and unfolds their properties.

    Rule: referent_known defaults to False — pronouns require discourse context
    to establish reference. Unresolved pronouns lower certainty.
    """

    def unfold(self, text: str) -> list[PronounUnfoldResult]:
        results: list[PronounUnfoldResult] = []
        tokens = text.strip().split()

        for token in tokens:
            result = self._check_token(token)
            if result:
                results.append(result)

        return results

    def _check_token(self, token: str) -> PronounUnfoldResult | None:
        clean = _strip_diacritics(token)
        if len(clean) < 2:
            return None

        for suffix, pronoun_form, person, number, gender, roles in _PRONOUN_SUFFIXES:
            if clean.endswith(suffix) and len(clean) > len(suffix):
                base = clean[: -len(suffix)]
                # Avoid false positives on short bases
                if len(base) < 2:
                    continue

                # Determine role heuristically
                role = _infer_role(base, roles)
                warnings: list[str] = []
                warnings.append(
                    "pronoun_referent_unknown: attached pronoun requires discourse context "
                    "to establish reference; certainty lowered until referent resolved"
                )

                return PronounUnfoldResult(
                    pronoun_form=pronoun_form,
                    base_word=base,
                    role=role,
                    person=person,
                    number=number,
                    gender=gender,
                    referent_known=False,
                    certainty_policy="lower_until_resolved",
                    warnings=warnings,
                )

        return None


def _infer_role(base: str, possible_roles: list[str]) -> str:
    """Heuristic role inference from base word."""
    # If base looks like a noun (ends in ة or ي), likely possessor
    if base.endswith("ة") or base.endswith("ات"):
        return "possessor"
    # If base looks like a verb, likely object
    if base.startswith("ي") or base.startswith("ت") or base.startswith("ف"):
        return "object"
    # Default to first possible role
    return possible_roles[0] if possible_roles else "possessor"


def _strip_diacritics(text: str) -> str:
    diacritics = "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670"
    return "".join(c for c in text if c not in diacritics)
