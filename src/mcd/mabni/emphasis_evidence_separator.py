"""EmphasisEvidenceSeparator — distinguishes emphasis markers from evidence."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EmphasisAnalysisResult:
    has_emphasis: bool
    emphasis_markers: list[str]
    creates_evidence: bool
    certainty_increase: float
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "has_emphasis": self.has_emphasis,
            "emphasis_markers": self.emphasis_markers,
            "creates_evidence": self.creates_evidence,
            "certainty_increase": round(self.certainty_increase, 4),
            "warnings": self.warnings,
        }


_EMPHASIS_MARKERS: dict[str, str] = {
    "إنّ": "inna_emphasis",
    "إِنَّ": "inna_emphasis",
    "إن": "in_emphasis_mukhaffafa",
    "قد": "qad_emphasis",
    "لام": "lam_ibtida",
    "نون": "nun_tawkid",
    "والله": "qasam",
    "تالله": "qasam",
    "بالله": "qasam",
    "أقسم": "qasam",
    "كلّ": "shumuliyya",
    "كل": "shumuliyya",
    "أجمع": "shumuliyya",
    "جميع": "shumuliyya",
    "نفس": "tawkid_nafsi",
    "عين": "tawkid_ayni",
    "لقد": "lam_qad_compound",
    "إنما": "innama_emphasis_qasr",
}


class EmphasisEvidenceSeparator:
    """Separates emphasis markers from evidence.

    Critical rules:
    1. Emphasis increases discourse force, NOT evidence strength.
    2. creates_evidence is ALWAYS False.
    3. certainty_increase is ALWAYS 0.0 — emphasis alone cannot raise certainty.
    4. Issues warning when emphasis is present without external evidence.
    """

    def analyze(self, text: str) -> EmphasisAnalysisResult:
        text_stripped = text.strip()
        tokens = text_stripped.split()
        warnings: list[str] = []
        found_markers: list[str] = []

        for token in tokens:
            clean = _strip_diacritics(token)
            if clean in _EMPHASIS_MARKERS:
                found_markers.append(clean)
            elif token in _EMPHASIS_MARKERS:
                found_markers.append(token)
            # Check for compound لقد
            if clean == "لقد" or token == "لقد":
                if "لقد" not in found_markers:
                    found_markers.append("لقد")

        # Special: إنّ with shadda
        if "إنّ" in text_stripped:
            if "إنّ" not in found_markers:
                found_markers.append("إنّ")

        has_emphasis = len(found_markers) > 0

        if has_emphasis:
            warnings.append(
                "emphasis_not_evidence: emphasis markers increase discourse force only. "
                "They do NOT create or strengthen evidence. "
                "External evidence is required for certainty increase."
            )

        return EmphasisAnalysisResult(
            has_emphasis=has_emphasis,
            emphasis_markers=found_markers,
            creates_evidence=False,  # ALWAYS False
            certainty_increase=0.0,  # ALWAYS 0.0 — emphasis never raises certainty
            warnings=warnings,
        )


def _strip_diacritics(text: str) -> str:
    diacritics = "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670"
    return "".join(c for c in text if c not in diacritics)
