from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class JamiManiDefinition:
    concept_id: str
    positive_cases: list[str] = field(default_factory=list)
    negative_cases: list[str] = field(default_factory=list)
    required_features: list[str] = field(default_factory=list)
    forbidden_features: list[str] = field(default_factory=list)
    boundary_conditions: list[str] = field(default_factory=list)


@dataclass
class JamiManiReport:
    concept_id: str
    jami_score: float
    mani_score: float
    concept_tightness: float
    false_inclusions: list[str] = field(default_factory=list)
    false_exclusions: list[str] = field(default_factory=list)
    boundary_warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "concept_id": self.concept_id,
            "jami_score": self.jami_score,
            "mani_score": self.mani_score,
            "concept_tightness": self.concept_tightness,
            "false_inclusions": self.false_inclusions,
            "false_exclusions": self.false_exclusions,
            "boundary_warnings": self.boundary_warnings,
        }


class JamiManiCalculator:
    @staticmethod
    def harmonic_mean(a: float, b: float) -> float:
        if a <= 0 or b <= 0:
            return 0.0
        return 2.0 * a * b / (a + b)

    def calculate(
        self,
        definition: JamiManiDefinition,
        observed_positive: list[str],
        observed_negative: list[str],
    ) -> JamiManiReport:
        total_pos = len(definition.positive_cases)
        total_neg = len(definition.negative_cases)

        covered_positive = [c for c in observed_positive if c in definition.positive_cases]
        excluded_negative = [c for c in definition.negative_cases if c in observed_negative]

        jami_score = (len(covered_positive) / total_pos) if total_pos else 1.0
        mani_score = (len(excluded_negative) / total_neg) if total_neg else 1.0
        concept_tightness = self.harmonic_mean(jami_score, mani_score)

        false_inclusions = [c for c in observed_negative if c not in definition.negative_cases]
        false_exclusions = [c for c in definition.positive_cases if c not in observed_positive]

        boundary_warnings = []
        if false_inclusions:
            boundary_warnings.append("Concept boundary leaked into forbidden space")
        if false_exclusions:
            boundary_warnings.append("Concept boundary missed required positive cases")

        return JamiManiReport(
            concept_id=definition.concept_id,
            jami_score=round(jami_score, 4),
            mani_score=round(mani_score, 4),
            concept_tightness=round(concept_tightness, 4),
            false_inclusions=false_inclusions,
            false_exclusions=false_exclusions,
            boundary_warnings=boundary_warnings,
        )

    def calculate_for_concept(self, concept: str) -> JamiManiReport:
        templates = {
            "evidence": JamiManiDefinition(
                concept_id="evidence",
                positive_cases=["verified_source", "traceable_observation"],
                negative_cases=["emphasis", "tool_output", "memory"],
                boundary_conditions=["operator_non_proof"],
            ),
            "harmful_vs_haram": JamiManiDefinition(
                concept_id="harmful_vs_haram",
                positive_cases=["harmful"],
                negative_cases=["haram_without_proof"],
                boundary_conditions=["requires_textual_or_legal_evidence"],
            ),
        }
        definition = templates.get(concept)
        if definition is None:
            definition = JamiManiDefinition(concept_id=concept)
        return self.calculate(definition, definition.positive_cases, definition.negative_cases)
