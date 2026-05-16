from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

TRANSITION_JUDGMENTS = {"allowed", "blocked", "suspended"}
KNOWN_PASSED_BY_JUDGMENT: dict[str, tuple[int, int]] = {
    "suspended": (0, 0),
    "blocked": (1, 0),
    "allowed": (1, 1),
}


@dataclass(frozen=True)
class TransitionInput:
    U: str
    P: str
    L: str
    R: str
    G: str
    C: bool | None
    W: list[str] = field(default_factory=list)
    X: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TransitionOutput:
    U_prime: str
    judgment: str
    known: int
    passed: int
    residuals: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.judgment not in TRANSITION_JUDGMENTS:
            raise ValueError(f"judgment must be one of {sorted(TRANSITION_JUDGMENTS)}")
        if (self.known, self.passed) != KNOWN_PASSED_BY_JUDGMENT[self.judgment]:
            raise ValueError("known/passed bits do not match transition judgment")


def phi_transition(payload: TransitionInput) -> TransitionOutput:
    """
    Executable contract for Φ(U,P,L,R,G,C,W,X) = (U', J).

    - C is unknown  -> suspended (known=0, passed=0)
    - C is False    -> blocked   (known=1, passed=0)
    - C is True     -> allowed   (known=1, passed=1)
    """
    if payload.C is None:
        return TransitionOutput(
            U_prime=payload.U,
            judgment="suspended",
            known=0,
            passed=0,
            residuals=["transition_condition_unknown"],
        )
    if payload.C is False:
        return TransitionOutput(
            U_prime=payload.U,
            judgment="blocked",
            known=1,
            passed=0,
            residuals=["transition_condition_failed"],
        )
    return TransitionOutput(
        U_prime=f"{payload.U}@{payload.G}",
        judgment="allowed",
        known=1,
        passed=1,
        residuals=[],
    )
