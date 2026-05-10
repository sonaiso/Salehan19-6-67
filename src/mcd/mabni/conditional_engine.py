"""ConditionalEngine — analyzes Arabic conditional structures."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ConditionalResult:
    condition_type: str
    particle: str
    protasis: str
    apodosis: str
    judgment_suspended: bool
    certainty_policy: str
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "condition_type": self.condition_type,
            "particle": self.particle,
            "protasis": self.protasis,
            "apodosis": self.apodosis,
            "judgment_suspended": self.judgment_suspended,
            "certainty_policy": self.certainty_policy,
            "warnings": self.warnings,
        }


# Conditional particles and their types
_CONDITIONAL_PARTICLES: dict[str, tuple[str, str]] = {
    "إن": ("real_condition", "conditional_certainty"),
    "إذا": ("possible_condition", "conditional_certainty"),
    "لو": ("counterfactual", "conditional_only"),
    "لولا": ("impossible", "conditional_only"),
    "لوما": ("impossible", "conditional_only"),
    "كلما": ("habitual", "habitual_certainty"),
    "من": ("real_condition", "conditional_certainty"),
    "ما": ("real_condition", "conditional_certainty"),
    "مهما": ("real_condition", "conditional_certainty"),
    "أينما": ("habitual", "habitual_certainty"),
    "حيثما": ("habitual", "habitual_certainty"),
}


class ConditionalEngine:
    """Analyzes Arabic conditional structures.

    Critical rule: A conditional does NOT assert that its protasis occurred
    or its apodosis will occur. Judgment is always suspended.
    """

    def analyze(self, text: str) -> ConditionalResult:
        text_stripped = text.strip()
        tokens = text_stripped.split()
        warnings: list[str] = []

        detected_particle = ""
        condition_type = "real_condition"
        certainty_policy = "conditional_certainty"

        # Detect conditional particle
        for token in tokens:
            clean = _strip_diacritics(token)
            if clean in _CONDITIONAL_PARTICLES:
                detected_particle = clean
                condition_type, certainty_policy = _CONDITIONAL_PARTICLES[clean]
                break

        if not detected_particle:
            warnings.append("no conditional particle detected; check if this is truly a conditional")
            return ConditionalResult(
                condition_type="unknown",
                particle="",
                protasis=text_stripped,
                apodosis="",
                judgment_suspended=True,
                certainty_policy="suspend",
                warnings=warnings,
            )

        # Split on particle to find protasis / apodosis
        parts = text_stripped.split(detected_particle, 1)
        if len(parts) == 2:
            before = parts[0].strip()
            after = parts[1].strip()
            # The protasis is after the particle up to the first verb clause break
            # Apodosis is the remainder — heuristic split on لـ or تـ
            protasis_end = _find_apodosis_start(after)
            protasis = after[:protasis_end].strip() if protasis_end else after
            apodosis = after[protasis_end:].strip() if protasis_end else ""
        else:
            protasis = text_stripped
            apodosis = ""

        warnings.append(
            "conditional_not_assertion: the conditional structure does not assert "
            "that the protasis occurred or the apodosis will occur"
        )

        return ConditionalResult(
            condition_type=condition_type,
            particle=detected_particle,
            protasis=protasis,
            apodosis=apodosis,
            judgment_suspended=True,
            certainty_policy=certainty_policy,
            warnings=warnings,
        )


def _find_apodosis_start(after: str) -> int:
    """Heuristic: find where apodosis begins (after first complete verb phrase)."""
    tokens = after.split()
    for i, tok in enumerate(tokens[1:], start=1):
        # Apodosis usually starts with ل (lam), or a new verb starting with ي/ت
        clean = _strip_diacritics(tok)
        if clean.startswith("ل") and len(clean) > 2:
            return len(" ".join(tokens[:i])) + 1
        if i >= 2 and (clean.startswith("ي") or clean.startswith("ت")):
            return len(" ".join(tokens[:i])) + 1
    return 0


def _strip_diacritics(text: str) -> str:
    diacritics = "\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670"
    return "".join(c for c in text if c not in diacritics)
