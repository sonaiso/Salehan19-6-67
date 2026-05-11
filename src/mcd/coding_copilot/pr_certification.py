"""PR certification contract for merge governance."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

_BLOCKING_CERTIFICATE_RESIDUALS = {
    "ci_pending",
    "failing_checks",
    "missing_check_evidence",
    "merge_with_pending_checks",
    "merge_without_required_checks",
    "merge_without_pr_certification",
    "branch_protection_not_configured",
}


@dataclass
class PRCertification:
    pr_number: int
    certified_by: str
    judgment: str
    checks_summary: dict[str, Any]
    residuals: list[str] = field(default_factory=list)
    reverse_trace_complete: bool = False
    certificate_allowed: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        self.residuals = [str(item).strip() for item in self.residuals if str(item).strip()]
        self.judgment = (self.judgment or "").strip().upper()
        self.certificate_allowed = self.is_merge_certificate()

    def is_merge_certificate(self) -> bool:
        if self.judgment != "CERTIFICATE":
            return False
        if not self.reverse_trace_complete:
            return False
        return not any(item in _BLOCKING_CERTIFICATE_RESIDUALS for item in self.residuals)
