"""ExceptionIrabEngine — handles Arabic مستثنى (exception) with إلا، غير، سوى."""
from __future__ import annotations
from dataclasses import dataclass

EXCEPTION_MARKERS = {"إلّا", "إلا", "غير", "سوى", "خلا", "عدا", "حاشا"}


@dataclass
class ExceptionResult:
    surface: str
    marker: str  # إلا|غير|سوى
    exception_type: str  # positive_sentence|negative_sentence|exception_marker
    irab_case: str  # accusative (positive), same_as_preceding (negative)
    syntactic_role: str
    certainty: float

    def to_dict(self) -> dict:
        return {
            "surface": self.surface,
            "marker": self.marker,
            "exception_type": self.exception_type,
            "irab_case": self.irab_case,
            "syntactic_role": self.syntactic_role,
            "certainty": self.certainty,
        }


class ExceptionIrabEngine:
    """Handles مستثنى I'rab with إلا، غير، سوى."""

    def detect_exceptions(self, tokens: list) -> list:
        """Detect exception constructs in token list."""
        results = []

        for i, tok in enumerate(tokens):
            stripped = self._strip_diacritics(tok)

            if stripped in EXCEPTION_MARKERS or tok in EXCEPTION_MARKERS:
                if i + 1 < len(tokens):
                    exception_tok = tokens[i + 1]

                    has_negation = any(
                        self._strip_diacritics(t) in {"لا", "لم", "لن", "ما", "لات"}
                        for t in tokens[:i]
                    )

                    if has_negation:
                        irab_case = "same_as_preceding"
                        exception_type = "negative_sentence"
                    else:
                        irab_case = "accusative"
                        exception_type = "positive_sentence"

                    results.append(ExceptionResult(
                        surface=exception_tok,
                        marker=tok,
                        exception_type=exception_type,
                        irab_case=irab_case,
                        syntactic_role="exception",
                        certainty=0.85,
                    ))

        return results

    def _strip_diacritics(self, text: str) -> str:
        diacritics = set('\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652')
        return ''.join(c for c in text if c not in diacritics)
