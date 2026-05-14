"""Governed Answer Birth / Thinking Algebra package."""
from __future__ import annotations

from mcd.thinking.answer_birth import (
    AnswerBirthContract,
    AnswerBirthEvaluationResult,
    evaluate_answer_birth_contract,
)
from mcd.thinking.forbidden_transitions import THINKING_FORBIDDEN_TRANSITIONS, find_forbidden_transitions
from mcd.thinking.intent import UserIntentFrame
from mcd.thinking.means import ThinkingMeans
from mcd.thinking.mentality import ControlledConsciousnessFrame, MentalityFrame
from mcd.thinking.methods import ThinkingMethod
from mcd.thinking.styles import ThinkingStyle
from mcd.thinking.trace import ThoughtBirthTrace

__all__ = [
    "AnswerBirthContract",
    "AnswerBirthEvaluationResult",
    "THINKING_FORBIDDEN_TRANSITIONS",
    "find_forbidden_transitions",
    "UserIntentFrame",
    "ControlledConsciousnessFrame",
    "MentalityFrame",
    "ThinkingMethod",
    "ThinkingStyle",
    "ThinkingMeans",
    "ThoughtBirthTrace",
    "evaluate_answer_birth_contract",
]
