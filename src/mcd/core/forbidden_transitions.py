"""Forbidden transition checks for formal epistemic flow."""
from __future__ import annotations


class ForbiddenTransition(ValueError):
    """Raised when an illegal epistemic transition is requested."""


FORBIDDEN: list[tuple[str, str]] = [
    ("ZERO", "CERTIFICATE"),
    ("HYPOTHESIS", "FINAL_JUDGMENT"),
    ("INTERPRETATION", "CERTIFICATE"),
    ("ROOT_OR_PATTERN", "FACTUAL_PROOF"),
    ("DERIVATIVE", "PROOF"),
    ("IRAB", "FACTUAL_CERTAINTY"),
    ("EMPHASIS", "EVIDENCE"),
    ("METAPHOR", "LITERAL_CERTIFICATE"),
    ("MEMORY", "EXTERNAL_EVIDENCE"),
    ("MODEL_OUTPUT", "EVIDENCE"),
    ("TOOL_OUTPUT", "CERTIFICATE_WITHOUT_GOVERNANCE"),
    ("RESIDUAL", "ERASURE"),
    ("LEVEL", "SILENT_SKIP"),
    ("CERTIFICATE", "WITHOUT_PROOF_OBJECT"),
    ("CERTIFICATE", "WITHOUT_GOVERNANCE_GATE"),
    ("CERTIFICATE", "WITHOUT_REVERSE_TRACE"),
]


def validate_transition(src: str, dst: str) -> None:
    src_normalized = (src or "").strip().upper()
    dst_normalized = (dst or "").strip().upper()
    if not src_normalized or not dst_normalized:
        raise ValueError("src and dst are required non-empty transition labels")
    pair = (src_normalized, dst_normalized)
    if pair in FORBIDDEN:
        raise ForbiddenTransition(f"forbidden transition: {pair[0]} -> {pair[1]}")
