"""Forbidden transition checks for formal epistemic flow."""
from __future__ import annotations


class ForbiddenTransition(ValueError):
    """Raised when an illegal epistemic transition is requested."""


FORBIDDEN: list[tuple[str, str]] = [
    ("ZERO", "CERTIFICATE"),
    ("HYPOTHESIS", "FINAL_JUDGMENT"),
    ("INTERPRETATION", "CERTIFICATE"),
]


def validate_transition(src: str, dst: str) -> None:
    pair = ((src or "").strip().upper(), (dst or "").strip().upper())
    if pair in FORBIDDEN:
        raise ForbiddenTransition(f"forbidden transition: {pair[0]} -> {pair[1]}")
