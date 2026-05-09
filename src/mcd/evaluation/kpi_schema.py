"""KPI Schema — 20 measurable industrial performance indicators."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class KPICategory(str, Enum):
    EPISTEMIC_QUALITY = "epistemic_quality"
    PROMPT_CLASSIFICATION = "prompt_classification"
    REASONING = "reasoning"
    INDUSTRIAL = "industrial"


class KPIStatus(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


@dataclass
class KPI:
    kpi_id: str
    name: str
    category: str
    definition: str
    formula: str
    target_value: float
    current_value: float | None
    status: str  # green | yellow | red
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "kpi_id": self.kpi_id,
            "name": self.name,
            "category": self.category,
            "definition": self.definition,
            "formula": self.formula,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "status": self.status,
            "notes": self.notes,
        }


def build_kpi_registry() -> list[KPI]:
    """Return all 20 KPIs with definitions, formulas and current estimates."""
    return [
        # A. Epistemic Quality KPIs
        KPI(
            kpi_id="EQ-01",
            name="Grounding Rate",
            category=KPICategory.EPISTEMIC_QUALITY.value,
            definition="Fraction of outputs that reference reality, prior knowledge, or evidence.",
            formula="grounded_outputs / total_outputs",
            target_value=0.85,
            current_value=None,
            status=KPIStatus.YELLOW.value,
            notes="Not yet measured on a calibrated dataset.",
        ),
        KPI(
            kpi_id="EQ-02",
            name="Evidence Attachment Rate",
            category=KPICategory.EPISTEMIC_QUALITY.value,
            definition="Fraction of claims that carry attached evidence.",
            formula="claims_with_evidence / total_claims",
            target_value=0.80,
            current_value=None,
            status=KPIStatus.YELLOW.value,
            notes="Requires benchmark dataset evaluation.",
        ),
        KPI(
            kpi_id="EQ-03",
            name="Certainty Calibration Error",
            category=KPICategory.EPISTEMIC_QUALITY.value,
            definition="Mean absolute difference between predicted certainty and reference certainty.",
            formula="mean(|predicted_certainty - reference_certainty|)",
            target_value=0.10,
            current_value=None,
            status=KPIStatus.YELLOW.value,
            notes="Requires gold-labeled calibration dataset.",
        ),
        KPI(
            kpi_id="EQ-04",
            name="Suspension Correctness Rate",
            category=KPICategory.EPISTEMIC_QUALITY.value,
            definition="Rate at which judgment is correctly suspended when evidence is insufficient.",
            formula="correct_suspensions / total_suspension_cases",
            target_value=0.90,
            current_value=None,
            status=KPIStatus.YELLOW.value,
            notes="Core epistemic discipline metric.",
        ),
        KPI(
            kpi_id="EQ-05",
            name="Domain Separation Accuracy",
            category=KPICategory.EPISTEMIC_QUALITY.value,
            definition="Accuracy in separating epistemic, technical, value, shari, and practical domains.",
            formula="correct_domain_labels / total_examples",
            target_value=0.85,
            current_value=None,
            status=KPIStatus.YELLOW.value,
            notes="Key differentiator from generic LLMs.",
        ),
        KPI(
            kpi_id="EQ-06",
            name="Harm-vs-Haram Separation Accuracy",
            category=KPICategory.EPISTEMIC_QUALITY.value,
            definition="Accuracy in distinguishing harmful (epistemic/empirical) from haram (shari).",
            formula="correct_harm_haram_separations / total_examples",
            target_value=0.90,
            current_value=None,
            status=KPIStatus.YELLOW.value,
            notes="Critical for Islamic epistemic correctness.",
        ),
        # B. Prompt Classification KPIs
        KPI(
            kpi_id="PC-01",
            name="Root Domain Accuracy",
            category=KPICategory.PROMPT_CLASSIFICATION.value,
            definition="Accuracy in classifying root domain (universe/human/life).",
            formula="correct_root_domain / total_examples",
            target_value=0.80,
            current_value=None,
            status=KPIStatus.YELLOW.value,
            notes="FPCL primary classification target.",
        ),
        KPI(
            kpi_id="PC-02",
            name="Judgment Type Accuracy",
            category=KPICategory.PROMPT_CLASSIFICATION.value,
            definition="Accuracy in classifying judgment type (epistemic/shari/value/practical).",
            formula="correct_judgment_type / total_examples",
            target_value=0.80,
            current_value=None,
            status=KPIStatus.YELLOW.value,
            notes="Directly measurable with benchmark dataset.",
        ),
        KPI(
            kpi_id="PC-03",
            name="Evidence Need Accuracy",
            category=KPICategory.PROMPT_CLASSIFICATION.value,
            definition="Accuracy in determining what type of evidence is needed for a prompt.",
            formula="correct_evidence_need / total_examples",
            target_value=0.80,
            current_value=None,
            status=KPIStatus.YELLOW.value,
            notes="Tied to EQ-02.",
        ),
        KPI(
            kpi_id="PC-04",
            name="Certainty Policy Accuracy",
            category=KPICategory.PROMPT_CLASSIFICATION.value,
            definition="Accuracy in assigning the correct certainty policy for a prompt.",
            formula="correct_certainty_policy / total_examples",
            target_value=0.80,
            current_value=None,
            status=KPIStatus.YELLOW.value,
            notes="Policy accuracy vs. calibration error are complementary.",
        ),
        # C. Reasoning KPIs
        KPI(
            kpi_id="RQ-01",
            name="False Certainty Rate",
            category=KPICategory.REASONING.value,
            definition="Rate at which system expresses certainty without sufficient evidence (hallucination proxy).",
            formula="false_certainty_cases / total_outputs",
            target_value=0.05,
            current_value=None,
            status=KPIStatus.YELLOW.value,
            notes="Lower is better. Critical safety metric.",
        ),
        KPI(
            kpi_id="RQ-02",
            name="Fake Evidence Detection Rate",
            category=KPICategory.REASONING.value,
            definition="Rate at which fake/unsupported evidence is correctly flagged.",
            formula="detected_fake_evidence / total_fake_evidence_cases",
            target_value=0.85,
            current_value=None,
            status=KPIStatus.YELLOW.value,
            notes="NERL fake_evidence_detector is the relevant component.",
        ),
        KPI(
            kpi_id="RQ-03",
            name="Conflict Suspension Rate",
            category=KPICategory.REASONING.value,
            definition="Rate at which conflicting evidence correctly leads to judgment suspension.",
            formula="correct_conflict_suspensions / total_conflict_cases",
            target_value=0.90,
            current_value=None,
            status=KPIStatus.YELLOW.value,
            notes="NERL conflict_resolver is the relevant component.",
        ),
        KPI(
            kpi_id="RQ-04",
            name="Manat Applicability Accuracy",
            category=KPICategory.REASONING.value,
            definition="Accuracy of manat (analogy basis) detection in grounding layer.",
            formula="correct_manat_applications / total_analogy_cases",
            target_value=0.75,
            current_value=None,
            status=KPIStatus.YELLOW.value,
            notes="Requires GLCFL manat_engine calibration.",
        ),
        # D. Industrial KPIs
        KPI(
            kpi_id="IN-01",
            name="Test Pass Rate",
            category=KPICategory.INDUSTRIAL.value,
            definition="Percentage of automated tests passing.",
            formula="passed_tests / total_tests * 100",
            target_value=100.0,
            current_value=100.0,
            status=KPIStatus.GREEN.value,
            notes="All tests pass as of last run.",
        ),
        KPI(
            kpi_id="IN-02",
            name="CLI Success Rate",
            category=KPICategory.INDUSTRIAL.value,
            definition="Percentage of CLI command smoke tests that succeed.",
            formula="successful_cli_calls / total_cli_calls * 100",
            target_value=100.0,
            current_value=None,
            status=KPIStatus.YELLOW.value,
            notes="Measured by CLI smoke tests.",
        ),
        KPI(
            kpi_id="IN-03",
            name="Average Latency (ms)",
            category=KPICategory.INDUSTRIAL.value,
            definition="Average time to process a prompt through the full pipeline in milliseconds.",
            formula="sum(latency_ms) / total_requests",
            target_value=200.0,
            current_value=None,
            status=KPIStatus.YELLOW.value,
            notes="Not yet measured. No REST API yet.",
        ),
        KPI(
            kpi_id="IN-04",
            name="Error Rate",
            category=KPICategory.INDUSTRIAL.value,
            definition="Percentage of requests that result in an unhandled exception.",
            formula="errors / total_requests * 100",
            target_value=0.1,
            current_value=None,
            status=KPIStatus.YELLOW.value,
            notes="Requires production observability.",
        ),
        KPI(
            kpi_id="IN-05",
            name="JSON Schema Stability",
            category=KPICategory.INDUSTRIAL.value,
            definition="Fraction of outputs that match the expected JSON schema.",
            formula="schema_valid_outputs / total_outputs",
            target_value=1.0,
            current_value=None,
            status=KPIStatus.YELLOW.value,
            notes="JSON serializers exist; schema validation not yet enforced.",
        ),
        KPI(
            kpi_id="IN-06",
            name="Regression Failure Rate",
            category=KPICategory.INDUSTRIAL.value,
            definition="Fraction of previously passing tests that fail after a change.",
            formula="new_failures / total_tests",
            target_value=0.0,
            current_value=0.0,
            status=KPIStatus.GREEN.value,
            notes="CI enforces no regressions.",
        ),
    ]
