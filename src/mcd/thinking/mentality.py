"""Controlled consciousness and mentality governance frames."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

OutputKind = Literal[
    "descriptive",
    "empirical",
    "formal",
    "linguistic",
    "normative",
    "legal",
    "shari",
    "worldview",
    "systemic",
]


@dataclass
class ControlledConsciousnessFrame:
    frame_id: str
    source_request_ref: str
    awareness_object: str = ""
    attention_state: str = ""
    distinction_state: str = ""
    reality_refs: list[str] = field(default_factory=list)
    prior_information_refs: list[str] = field(default_factory=list)
    residuals: list[str] = field(default_factory=list)
    trace_refs: list[str] = field(default_factory=list)


@dataclass
class MentalityFrame:
    mentality_id: str
    base_orientation: str
    worldview_assumptions: list[str] = field(default_factory=list)
    domain: str = ""
    output_kind: OutputKind = "descriptive"
    allowed_methods: list[str] = field(default_factory=list)
    forbidden_outputs: list[str] = field(default_factory=list)
    residuals: list[str] = field(default_factory=list)
    trace_refs: list[str] = field(default_factory=list)
