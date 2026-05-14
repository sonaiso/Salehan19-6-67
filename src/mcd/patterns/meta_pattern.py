from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetaPattern:
    meta_id: str
    applies_to_layers: tuple[str, ...]
    form_kind: str
    role_kind: str
    composition_operator: str
    required_domain: str
    required_scope: str
    required_rank: str
    closure_schema: str
    minimum_completion_schema: str
    governor_schema: str
    residual_schema: str
    trace_schema: str
    allowed_bridge_schema: str
    forbidden_bridge_schema: str
