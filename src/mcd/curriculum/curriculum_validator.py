"""CurriculumValidator — validates CognitiveUnit collections."""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from .cognitive_unit import CognitiveUnit
from .curriculum_schema import (
    VALID_LEVELS, VALID_TARGET_LAYERS,
    VALID_CERTAINTY_POLICIES, VALID_DIFFICULTIES,
    LEVEL_PRIMARY_LAYERS,
)


@dataclass
class ValidationError:
    unit_id: str
    field: str
    message: str

    def to_dict(self) -> dict:
        return {"unit_id": self.unit_id, "field": self.field, "message": self.message}


@dataclass
class CurriculumValidationReport:
    total_units: int = 0
    valid_units: int = 0
    invalid_units: int = 0
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    status: str = "unknown"

    def to_dict(self) -> dict:
        return {
            "total_units": self.total_units,
            "valid_units": self.valid_units,
            "invalid_units": self.invalid_units,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": self.warnings,
            "status": self.status,
        }


class CurriculumValidator:
    """Validates a list of CognitiveUnit objects."""

    def validate(self, units: list[CognitiveUnit]) -> CurriculumValidationReport:
        report = CurriculumValidationReport(total_units=len(units))
        seen_ids: set[str] = set()
        invalid_set: set[str] = set()

        def err(uid: str, field_name: str, msg: str) -> None:
            report.errors.append(ValidationError(uid, field_name, msg))
            invalid_set.add(uid)

        for unit in units:
            uid = unit.unit_id or "<missing>"

            if uid in seen_ids:
                err(uid, "unit_id", "Duplicate unit_id")
            seen_ids.add(uid)

            if not unit.input_text or not unit.input_text.strip():
                err(uid, "input_text", "input_text is empty")

            if unit.level not in VALID_LEVELS:
                err(uid, "level", f"Invalid level {unit.level}")

            if unit.target_layer not in VALID_TARGET_LAYERS:
                err(uid, "target_layer", f"Invalid target_layer {unit.target_layer!r}")

            if unit.expected_frame is None:
                err(uid, "expected_frame", "expected_frame is None")
            else:
                frame = unit.expected_frame
                primary = LEVEL_PRIMARY_LAYERS.get(unit.level, [])
                layer_fields = {
                    "thing": frame.things,
                    "property": frame.properties,
                    "action": frame.actions,
                    "relation": frame.relations,
                    "cause": frame.causes,
                    "effect": frame.effects,
                    "instrument": frame.instruments,
                    "time": frame.times,
                    "place": frame.places,
                    "evidence": frame.evidence_need,
                    "certainty": frame.certainty_policy,
                    "mixed_reasoning": None,
                }
                for pl in primary:
                    val = layer_fields.get(pl)
                    if val is not None and not val:
                        report.warnings.append(
                            f"{uid}: expected_frame.{pl} is empty for primary layer {pl!r}"
                        )

            if unit.target_layer in ("evidence", "certainty") and not unit.evidence_need:
                err(uid, "evidence_need", "evidence/certainty unit must have evidence_need")

            if unit.certainty_policy not in VALID_CERTAINTY_POLICIES:
                err(uid, "certainty_policy", f"Invalid certainty_policy {unit.certainty_policy!r}")

            if unit.target_layer == "mixed_reasoning" and unit.certainty_policy == "near_certainty":
                err(uid, "certainty_policy", "mixed_reasoning unit must not be near_certainty")

            if unit.target_layer in ("cause", "effect"):
                frame = unit.expected_frame
                if not frame.causes and not frame.effects:
                    err(uid, "expected_frame", "cause/effect unit must have causes or effects in frame")

            if unit.difficulty == "adversarial" and not unit.forbidden_confusions:
                err(uid, "forbidden_confusions", "adversarial unit must have forbidden_confusions")

            try:
                json.dumps(unit.to_dict(), ensure_ascii=False)
            except (TypeError, ValueError) as ex:
                err(uid, "serialization", f"Not JSON serializable: {ex}")

        report.invalid_units = len(invalid_set)
        report.valid_units = report.total_units - report.invalid_units
        report.status = "valid" if report.invalid_units == 0 else "invalid"
        return report
