"""ExceptionIrabEngine — classify basic الاستثناء structures.

This module provides a lightweight structural classifier that keeps
exception handling explicit and traceable without changing public judgment
contracts. Arabic terminology is used because this module serves the
Arabic I'rab analysis track in the Mu'rab layer.
"""
from __future__ import annotations

from dataclasses import dataclass


_EXCEPTION_PARTICLES = {"إلا", "غير", "سوى", "عدا", "خلا", "حاشا"}


@dataclass(frozen=True)
class ExceptionIrabResult:
    has_exception: bool
    particle: str | None
    style: str
    certainty_policy: str
    warnings: tuple[str, ...]


class ExceptionIrabEngine:
    """Detects whether a token stream contains an exception construction."""

    def classify(self, tokens: list[str]) -> ExceptionIrabResult:
        particle = next((token for token in tokens if token in _EXCEPTION_PARTICLES), None)
        if particle is None:
            return ExceptionIrabResult(
                has_exception=False,
                particle=None,
                style="none",
                certainty_policy="hypothesis",
                warnings=(),
            )

        style = "explicit_illa" if particle == "إلا" else "general_exception_particle"
        return ExceptionIrabResult(
            has_exception=True,
            particle=particle,
            style=style,
            certainty_policy="hypothesis",
            warnings=(),
        )
