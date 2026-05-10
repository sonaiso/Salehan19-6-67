"""ExceptionRestrictionEngine — analyzes Arabic exception (استثناء) structures."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExceptionResult:
    particle: str
    excepted_item: str
    scope_modified: bool
    certainty_note: str
    is_evidence: bool
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "particle": self.particle,
            "excepted_item": self.excepted_item,
            "scope_modified": self.scope_modified,
            "certainty_note": self.certainty_note,
            "is_evidence": self.is_evidence,
            "warnings": self.warnings,
        }


_EXCEPTION_PARTICLES = {"إلا", "غير", "سوى", "خلا", "عدا", "حاشا"}


class ExceptionRestrictionEngine:
    """Analyzes Arabic exception structures.

    Rule: Exception modifies scope, not evidence.
    is_evidence is always False.
    """

    def analyze(self, text: str) -> ExceptionResult:
        text_stripped = text.strip()
        tokens = text_stripped.split()
        warnings: list[str] = []

        detected_particle = ""
        particle_idx = -1
        for i, tok in enumerate(tokens):
            clean = _strip_diacritics(tok)
            if clean in _EXCEPTION_PARTICLES:
                detected_particle = clean
                particle_idx = i
                break

        if not detected_particle:
            warnings.append("no exception particle found in text")
            return ExceptionResult(
                particle="",
                excepted_item="",
                scope_modified=False,
                certainty_note="no exception detected",
                is_evidence=False,
                warnings=warnings,
            )

        # The excepted item is typically the word after the exception particle
        excepted_item = tokens[particle_idx + 1] if particle_idx + 1 < len(tokens) else ""

        return ExceptionResult(
            particle=detected_particle,
            excepted_item=excepted_item,
            scope_modified=True,
            certainty_note="exception modifies scope, not evidence",
            is_evidence=False,
            warnings=warnings,
        )


def _strip_diacritics(text: str) -> str:
    diacritics = "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670"
    return "".join(c for c in text if c not in diacritics)
