"""Thought birth tracing contract."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ThoughtBirthTrace:
    trace_id: str
    intent_ref: str = ""
    consciousness_ref: str = ""
    mentality_ref: str = ""
    method_ref: str = ""
    style_ref: str = ""
    means_ref: str = ""
    language_ref: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    residuals: list[str] = field(default_factory=list)
    path_complete: bool = False
    evidence_complete: bool = False
    certificate_complete: bool = False
    complete: bool = False

    def assess_completeness(self) -> None:
        """Update path/evidence/certificate completeness flags.

        `complete` is retained as a compatibility alias for certificate completeness.
        """
        self.path_complete = all(
            [
                self.intent_ref,
                self.consciousness_ref,
                self.mentality_ref,
                self.method_ref,
                self.style_ref,
                self.means_ref,
                self.language_ref,
            ]
        )
        self.evidence_complete = bool(self.evidence_refs)
        self.certificate_complete = self.path_complete and self.evidence_complete
        self.complete = self.certificate_complete
