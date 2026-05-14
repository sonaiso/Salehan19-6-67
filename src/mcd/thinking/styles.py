"""Thinking style models and contract checks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from mcd.thinking.methods import ThinkingMethod

StyleType = Literal[
    "analysis",
    "comparison",
    "definition",
    "deduction",
    "induction",
    "experiment",
    "modeling",
    "critique",
    "synthesis",
    "system_building",
]


@dataclass
class ThinkingStyle:
    style_id: str
    method_id: str
    style_type: StyleType
    required_method_type: str
    residual_policy: str = "preserve"


def style_belongs_to_method(style: ThinkingStyle, method: ThinkingMethod) -> bool:
    """A style can only operate within its method contract."""
    if style.method_id != method.method_id:
        return False
    return (style.required_method_type or "").strip().lower() == (method.method_type or "").strip().lower()
