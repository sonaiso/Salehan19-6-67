"""CI checks governance for coding PR epistemic judgment."""
from __future__ import annotations

from dataclasses import dataclass

from mcd.coding_copilot.coding_residual import CodingResidual


@dataclass
class ChecksGovernance:
    checks_total: int
    checks_passed: int
    checks_failed: int
    checks_pending: int

    def has_pending(self) -> bool:
        return self.checks_pending > 0

    def has_failures(self) -> bool:
        return self.checks_failed > 0

    def all_green(self) -> bool:
        return (
            self.checks_total > 0
            and self.checks_pending == 0
            and self.checks_failed == 0
            and self.checks_passed == self.checks_total
        )

    def residuals(self) -> list[CodingResidual]:
        residuals: list[CodingResidual] = []
        if self.checks_total == 0:
            residuals.append(
                CodingResidual(
                    residual_type="missing_check_evidence",
                    severity="blocking",
                    message="No check evidence available for this PR.",
                )
            )
        if self.has_pending():
            residuals.append(
                CodingResidual(
                    residual_type="ci_pending",
                    severity="blocking",
                    message="One or more required checks are still pending.",
                )
            )
        if self.has_failures():
            residuals.append(
                CodingResidual(
                    residual_type="failing_checks",
                    severity="blocking",
                    message="One or more checks failed.",
                )
            )
        return residuals
