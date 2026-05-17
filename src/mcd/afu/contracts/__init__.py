"""AFU contracts package — passive, frozen, governance-aware dataclasses.

These contracts are the *only* AFU surface introduced in PR 1. They
hold data, enforce the constitutional invariants at construction time,
and never execute theory. The Gate Registry, stages, and runner are
introduced in later PRs.
"""
from __future__ import annotations

from ._common import (
    AFUContractError,
    ALLOWED_PUBLIC_RANKS,
    EpistemicRank,
    LicensedOutput,
    TraceStep,
    normalize_rank,
)
from .answer_plan import AnswerPlan
from .licensed_response import LicensedResponse
from .linked_understanding import LinkedUnderstanding
from .obligations import Obligations
from .prior_filter import PriorInformationFilter
from .prompt_reality import PromptReality
from .response_audit import ResponseAudit
from .understanding_judgment import UnderstandingJudgment, UnderstandingPayload

__all__ = [
    "AFUContractError",
    "ALLOWED_PUBLIC_RANKS",
    "AnswerPlan",
    "EpistemicRank",
    "LicensedOutput",
    "LicensedResponse",
    "LinkedUnderstanding",
    "Obligations",
    "PriorInformationFilter",
    "PromptReality",
    "ResponseAudit",
    "TraceStep",
    "UnderstandingJudgment",
    "UnderstandingPayload",
    "normalize_rank",
]
