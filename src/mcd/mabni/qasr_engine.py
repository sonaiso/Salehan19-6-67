"""QasrEngine — analyzes Arabic qasr (restriction/specification) structures."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class QasrResult:
    qasr_type: str
    particle: str
    restricted_predicate: str
    restricted_subject: str
    is_evidence: bool
    certainty_note: str
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "qasr_type": self.qasr_type,
            "particle": self.particle,
            "restricted_predicate": self.restricted_predicate,
            "restricted_subject": self.restricted_subject,
            "is_evidence": self.is_evidence,
            "certainty_note": self.certainty_note,
            "warnings": self.warnings,
        }


class QasrEngine:
    """Analyzes Arabic qasr (تخصيص/حصر) structures.

    Detected patterns:
    - إنما (innama qasr)
    - لا...إلا (negation + exception)
    - ما...إلا (negation + exception)
    - Fronting (تقديم ما حقه التأخير) — structural qasr

    Rule: Qasr restricts scope, not evidence. is_evidence is always False.
    """

    def analyze(self, text: str) -> QasrResult:
        text_stripped = text.strip()
        warnings: list[str] = []

        # إنما — explicit qasr particle
        if "إنما" in text_stripped:
            parts = text_stripped.split("إنما", 1)
            after = parts[1].strip() if len(parts) > 1 else ""
            toks = after.split()
            restricted_subject = toks[0] if toks else ""
            restricted_predicate = " ".join(toks[1:]) if len(toks) > 1 else ""
            return QasrResult(
                qasr_type="innama_qasr",
                particle="إنما",
                restricted_predicate=restricted_predicate,
                restricted_subject=restricted_subject,
                is_evidence=False,
                certainty_note="qasr restricts scope of predication, not evidence strength",
                warnings=warnings,
            )

        # لا...إلا or ما...إلا
        has_neg = "لا " in text_stripped or "ما " in text_stripped
        has_illa = "إلا" in text_stripped

        if has_neg and has_illa:
            neg_particle = "لا" if "لا " in text_stripped else "ما"
            # Find what's between negation and إلا
            parts = text_stripped.split("إلا", 1)
            before_illa = parts[0].strip()
            after_illa = parts[1].strip() if len(parts) > 1 else ""

            neg_toks = before_illa.split()
            neg_idx = next((i for i, t in enumerate(neg_toks) if _strip_diacritics(t) == neg_particle), -1)
            negated_part = " ".join(neg_toks[neg_idx + 1:]) if neg_idx >= 0 else before_illa

            restricted_subject = after_illa.split()[0] if after_illa.split() else ""
            restricted_predicate = negated_part

            return QasrResult(
                qasr_type=f"{neg_particle}_illa_qasr",
                particle=f"{neg_particle}...إلا",
                restricted_predicate=restricted_predicate,
                restricted_subject=restricted_subject,
                is_evidence=False,
                certainty_note="qasr restricts scope of predication, not evidence strength",
                warnings=warnings,
            )

        # Fronting heuristic — non-standard word order detected
        warnings.append("possible fronting qasr; manual analysis recommended")
        return QasrResult(
            qasr_type="fronting_qasr",
            particle="تقديم",
            restricted_predicate=text_stripped,
            restricted_subject="",
            is_evidence=False,
            certainty_note="qasr restricts scope of predication, not evidence strength",
            warnings=warnings,
        )


def _strip_diacritics(text: str) -> str:
    diacritics = "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670"
    return "".join(c for c in text if c not in diacritics)
