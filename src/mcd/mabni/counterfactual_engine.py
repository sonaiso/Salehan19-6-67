"""CounterfactualEngine — analyzes لو/لولا/لوما counterfactual conditions."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CounterfactualResult:
    is_counterfactual: bool
    particle: str
    protasis: str
    apodosis: str
    prevented_by: str
    certainty_policy: str
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "is_counterfactual": self.is_counterfactual,
            "particle": self.particle,
            "protasis": self.protasis,
            "apodosis": self.apodosis,
            "prevented_by": self.prevented_by,
            "certainty_policy": self.certainty_policy,
            "warnings": self.warnings,
        }


_COUNTERFACTUAL_PARTICLES = {"لو", "لولا", "لوما"}


class CounterfactualEngine:
    """Analyzes counterfactual conditionals (لو / لولا / لوما).

    Critical rule: A counterfactual does NOT assert that the condition occurred.
    لو implies the condition did NOT occur (contrary-to-fact).
    لولا implies the preventing condition IS present.
    certainty_policy is always 'conditional_only'.
    """

    def analyze(self, text: str) -> CounterfactualResult:
        text_stripped = text.strip()
        tokens = text_stripped.split()
        warnings: list[str] = []

        detected_particle = ""
        for tok in tokens:
            clean = _strip_diacritics(tok)
            if clean in _COUNTERFACTUAL_PARTICLES:
                detected_particle = clean
                break

        if not detected_particle:
            return CounterfactualResult(
                is_counterfactual=False,
                particle="",
                protasis=text_stripped,
                apodosis="",
                prevented_by="",
                certainty_policy="standard",
                warnings=["no counterfactual particle detected"],
            )

        # Split into protasis and apodosis
        parts = text_stripped.split(detected_particle, 1)
        after = parts[1].strip() if len(parts) > 1 else text_stripped

        # For لولا: subject (prevented_by) is the noun after the particle
        prevented_by = ""
        if detected_particle == "لولا":
            after_tokens = after.split()
            if after_tokens:
                prevented_by = after_tokens[0]

        # Heuristic apodosis split: look for لـ + verb or second verb phrase
        protasis_toks = after.split()
        apodosis_start = 0
        for i, tok in enumerate(protasis_toks[1:], 1):
            clean = _strip_diacritics(tok)
            if clean.startswith("ل") and len(clean) > 2:
                apodosis_start = i
                break

        if apodosis_start:
            protasis = " ".join(protasis_toks[:apodosis_start]).strip()
            apodosis = " ".join(protasis_toks[apodosis_start:]).strip()
        else:
            protasis = after
            apodosis = ""

        warnings.append(
            "counterfactual_not_assertion: لو/لولا/لوما does not assert the condition occurred. "
            "The protasis is counterfactual; certainty_policy=conditional_only"
        )

        return CounterfactualResult(
            is_counterfactual=True,
            particle=detected_particle,
            protasis=protasis,
            apodosis=apodosis,
            prevented_by=prevented_by,
            certainty_policy="conditional_only",
            warnings=warnings,
        )


def _strip_diacritics(text: str) -> str:
    diacritics = "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670"
    return "".join(c for c in text if c not in diacritics)
