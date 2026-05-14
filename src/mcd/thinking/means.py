"""Thinking means models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

MeansType = Literal["llm", "database", "source_text", "experiment", "calculator", "code", "human_input", "external_tool"]


@dataclass
class ThinkingMeans:
    means_id: str
    means_type: MeansType
    can_create_evidence: bool = False
    can_issue_judgment: bool = False
    constraints: list[str] | None = None
