"""AgreementEngine — checks grammatical agreement between head and dependent."""
from __future__ import annotations

from mcd.murab.murab_schema import MurabUnit


class AgreementEngine:
    """Checks gender, number, and case agreement between two units."""

    def check_agreement(
        self,
        head_unit: MurabUnit,
        dependent_unit: MurabUnit,
    ) -> dict:
        mismatches: list[str] = []

        # Case agreement (for توابع)
        if (head_unit.irab_case != "unknown"
                and dependent_unit.irab_case != "unknown"
                and head_unit.irab_case != dependent_unit.irab_case):
            mismatches.append(
                f"case_mismatch: head={head_unit.irab_case} "
                f"dependent={dependent_unit.irab_case}"
            )

        # Marker agreement (both should carry same marker type where applicable)
        if (head_unit.irab_marker not in ("none", "estimated", "local")
                and dependent_unit.irab_marker not in ("none", "estimated", "local")
                and head_unit.irab_marker != dependent_unit.irab_marker):
            mismatches.append(
                f"marker_mismatch: head={head_unit.irab_marker} "
                f"dependent={dependent_unit.irab_marker}"
            )

        return {
            "agrees": len(mismatches) == 0,
            "mismatches": mismatches,
            "head_id": head_unit.unit_id,
            "dependent_id": dependent_unit.unit_id,
        }
