"""SpeechActResolver — classifies Arabic speech acts."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SpeechActResult:
    speech_act: str
    is_assertion: bool
    is_inshaa: bool
    establishes_reality: bool
    certainty_policy: str
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "speech_act": self.speech_act,
            "is_assertion": self.is_assertion,
            "is_inshaa": self.is_inshaa,
            "establishes_reality": self.establishes_reality,
            "certainty_policy": self.certainty_policy,
            "warnings": self.warnings,
        }


# Only unambiguously interrogative markers — excludes "من" and "ما" which are
# frequently used as prepositions/relative pronouns in non-interrogative contexts.
# Position-independent interrogative adverbs and particles (؟ is checked separately).
_QUESTION_MARKERS = {"هل", "أليس", "أَلَيْسَ", "أين", "متى", "كيف", "لماذا", "لِمَ"}
_PROHIBITION_STARTERS = {"لا تـ", "لا ت"}
_WISH_MARKERS = {"ليت", "لعل", "عسى", "لو"}
_WARNING_MARKERS = {"إياك", "إياكم", "حذار", "انتبه"}
_OATH_MARKERS = {"والله", "وتالله", "تالله", "بالله", "أقسم", "أحلف"}
_VOCATIVE_MARKERS = {"يا", "أيا", "هيا", "أي"}
_WONDER_MARKERS = {"ما أجمل", "ما أحسن", "ما أكرم", "ما أعظم", "كم"}


class SpeechActResolver:
    """Classifies Arabic utterances by speech act type.

    Key rule: إنشاء (non-assertion) ≠ khabar (assertion).
    Tamanni/Taraji do not establish reality.
    Questions do not create assertions.
    """

    def resolve(self, text: str) -> SpeechActResult:
        text_stripped = text.strip()
        tokens = set(text_stripped.split())
        warnings: list[str] = []

        # Question (Istifham): triggered by explicit question mark or unambiguous
        # interrogative markers (هل, أليس, أين, متى, كيف, لماذا).
        # Also triggered by "أ" or "همزة" only when it is the FIRST token (not mid-sentence).
        first_token = text_stripped.split()[0] if text_stripped.split() else ""
        is_question = (
            "؟" in text_stripped
            or bool(tokens.intersection(_QUESTION_MARKERS))
            or (first_token in {"أ", "أَ"})
        )
        if is_question:
            warnings.append("question_not_assertion: istifham does not create an assertion")
            return SpeechActResult(
                speech_act="istifham",
                is_assertion=False,
                is_inshaa=True,
                establishes_reality=False,
                certainty_policy="request_evidence",
                warnings=warnings,
            )

        # Oath (Qasam) — qasam is an assertion (khabar) with emphasis; it is NOT inshaa.
        # Emphasis/oath does not constitute external evidence.
        if tokens.intersection(_OATH_MARKERS):
            warnings.append("oath_not_external_evidence: qasam is emphasis, not external evidence")
            return SpeechActResult(
                speech_act="qasam",
                is_assertion=True,
                is_inshaa=False,
                establishes_reality=False,
                certainty_policy="emphasis_only",
                warnings=warnings,
            )

        # Prohibition (Nahy)
        if "لا ت" in text_stripped or any(t.startswith("لا") for t in text_stripped.split()):
            next_after_la = _get_token_after(text_stripped, "لا")
            if next_after_la and (next_after_la.startswith("ت") or next_after_la.startswith("ي")):
                return SpeechActResult(
                    speech_act="nahy",
                    is_assertion=False,
                    is_inshaa=True,
                    establishes_reality=False,
                    certainty_policy="directive",
                    warnings=warnings,
                )

        # Command (Amr)
        # Imperative verbs: often start without prefix or with اِ
        if _is_imperative(text_stripped):
            return SpeechActResult(
                speech_act="amr",
                is_assertion=False,
                is_inshaa=True,
                establishes_reality=False,
                certainty_policy="directive",
                warnings=warnings,
            )

        # Warning (Tahdhir)
        if tokens.intersection(_WARNING_MARKERS):
            return SpeechActResult(
                speech_act="tahdhir",
                is_assertion=False,
                is_inshaa=True,
                establishes_reality=False,
                certainty_policy="directive",
                warnings=warnings,
            )

        # Wish/Tamanni
        if "ليت" in tokens:
            warnings.append("tamanni_not_reality: لَيت expresses unattainable wish, does not establish reality")
            return SpeechActResult(
                speech_act="tamanni",
                is_assertion=False,
                is_inshaa=True,
                establishes_reality=False,
                certainty_policy="suspend",
                warnings=warnings,
            )

        # Hope/Taraji
        if "لعل" in tokens or "عسى" in tokens:
            warnings.append("taraji_not_reality: لَعَل/عَسَى expresses hope, does not establish reality")
            return SpeechActResult(
                speech_act="taraji",
                is_assertion=False,
                is_inshaa=True,
                establishes_reality=False,
                certainty_policy="suspend",
                warnings=warnings,
            )

        # Vocative (Nida)
        if tokens.intersection(_VOCATIVE_MARKERS):
            return SpeechActResult(
                speech_act="nida",
                is_assertion=False,
                is_inshaa=True,
                establishes_reality=False,
                certainty_policy="directive",
                warnings=warnings,
            )

        # Wonder (Ta'ajjub)
        for marker in _WONDER_MARKERS:
            if text_stripped.startswith(marker):
                warnings.append("ta_ajjub_not_evidence: wonder expression is pragmatic, not evidential")
                return SpeechActResult(
                    speech_act="ta_ajjub",
                    is_assertion=False,
                    is_inshaa=True,
                    establishes_reality=False,
                    certainty_policy="emphasis_only",
                    warnings=warnings,
                )

        # Default: Khabar (assertion)
        return SpeechActResult(
            speech_act="khabar",
            is_assertion=True,
            is_inshaa=False,
            establishes_reality=True,
            certainty_policy="standard",
            warnings=warnings,
        )


def _get_token_after(text: str, token: str) -> str:
    tokens = text.split()
    for i, t in enumerate(tokens):
        if t == token and i + 1 < len(tokens):
            return tokens[i + 1]
    return ""


def _is_imperative(text: str) -> bool:
    """Heuristic: check if text starts with a plausible imperative form.

    Excludes:
    - Words starting with the definite article "ال" (e.g., "الكتاب", "البيت").
    - Words of length < 3 that begin with "ا" (too short to be an imperative stem).
    """
    tokens = text.split()
    if not tokens:
        return False
    first = tokens[0]
    # Definite article prefix — definitely NOT an imperative
    if first.startswith("ال"):
        return False
    # Common explicit imperatives (highest confidence)
    common_imps = {"اذهب", "تعال", "قل", "اقرأ", "اكتب", "افعل", "قم", "اجلس", "انظر", "خذ"}
    if first in common_imps:
        return True
    # Arabic imperatives of Form I often start with اِ followed by at least 2 more chars;
    # require length >= 4 to avoid false positives from short words beginning with "ا".
    if (first.startswith("اِ") or first.startswith("ا")) and len(first) >= 4:
        return True
    return False
