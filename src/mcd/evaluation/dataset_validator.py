"""Dataset Validator — validates BenchmarkExample objects for consistency."""
from __future__ import annotations
from dataclasses import dataclass, field
from mcd.evaluation.dataset_schema import BenchmarkExample

VALID_CERTAINTY_POLICIES = {"near_certainty", "strong_knowledge", "probable_knowledge", "hypothesis", "suspend"}
VALID_DIFFICULTIES = {"easy", "medium", "hard", "adversarial"}
VALID_EPISTEMIC_STATUSES = {"verified", "probable", "hypothesis", "suspended", "rejected", "requires_context"}


@dataclass
class ValidationError:
    example_id: str
    field: str
    message: str


@dataclass
class DatasetValidationReport:
    total: int
    valid: int
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    @property
    def error_count(self) -> int:
        return len(self.errors)

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "valid": self.valid,
            "is_valid": self.is_valid,
            "error_count": self.error_count,
            "errors": [{"example_id": e.example_id, "field": e.field, "message": e.message} for e in self.errors],
            "warnings": self.warnings,
        }


def validate_dataset(examples: list[BenchmarkExample]) -> DatasetValidationReport:
    """Validate a list of BenchmarkExample objects."""
    errors: list[ValidationError] = []
    warnings: list[str] = []
    seen_ids: set[str] = set()

    for ex in examples:
        if ex.example_id in seen_ids:
            errors.append(ValidationError(ex.example_id, "example_id", f"Duplicate ID: {ex.example_id}"))
        seen_ids.add(ex.example_id)

        if not ex.input_text.strip():
            errors.append(ValidationError(ex.example_id, "input_text", "Empty input_text"))

        if not ex.expected_judgment_types:
            warnings.append(f"{ex.example_id}: empty expected_judgment_types")

        if ex.expected_certainty_policy not in VALID_CERTAINTY_POLICIES:
            errors.append(ValidationError(ex.example_id, "expected_certainty_policy",
                f"Invalid policy: {ex.expected_certainty_policy}"))

        if ex.difficulty not in VALID_DIFFICULTIES:
            errors.append(ValidationError(ex.example_id, "difficulty",
                f"Invalid difficulty: {ex.difficulty}"))

        if ex.expected_epistemic_status not in VALID_EPISTEMIC_STATUSES:
            errors.append(ValidationError(ex.example_id, "expected_epistemic_status",
                f"Invalid status: {ex.expected_epistemic_status}"))

        tags = [t.lower() for t in ex.tags]
        jt_keys = set(ex.expected_judgment_types.keys())
        if "shari" in jt_keys or "shari" in tags:
            if "shari_evidence_required" not in ex.required_warnings:
                warnings.append(f"{ex.example_id}: shari example missing 'shari_evidence_required' warning")

        if "ambiguous" in jt_keys or ex.source_type == "ambiguity":
            if ex.expected_certainty_policy != "suspend":
                errors.append(ValidationError(ex.example_id, "expected_certainty_policy",
                    "Ambiguous examples must have expected_certainty_policy='suspend'"))
            if ex.expected_epistemic_status != "requires_context":
                warnings.append(f"{ex.example_id}: ambiguous example should have expected_epistemic_status='requires_context'")

        if "analogy" in tags and "missing_illah" not in ex.required_warnings:
            if not ex.metadata.get("has_illah", True):
                warnings.append(f"{ex.example_id}: analogy example without illah should have 'missing_illah' warning")

        if "harm_vs_haram" in tags or "harm_haram" in tags:
            if "harm_vs_haram" not in ex.required_separations:
                warnings.append(f"{ex.example_id}: harm_vs_haram example missing required_separations")

        for k, v in ex.expected_judgment_types.items():
            if not (0.0 <= v <= 1.0):
                errors.append(ValidationError(ex.example_id, "expected_judgment_types",
                    f"Score out of range for {k}: {v}"))

        if not ex.tags:
            warnings.append(f"{ex.example_id}: empty tags")

    total = len(examples)
    error_ids = {e.example_id for e in errors}
    valid = total - len(error_ids)

    return DatasetValidationReport(total=total, valid=valid, errors=errors, warnings=warnings)
