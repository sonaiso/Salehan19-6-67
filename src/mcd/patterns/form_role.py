from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FormState:
    form_id: str
    layer: str
    symbols: tuple[str, ...]
    invariants: tuple[str, ...]
    source_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class RoleState:
    role_id: str
    layer: str
    role_type: str
    features: dict[str, object]
    rank: str
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class FormRoleHypothesis:
    layer: str
    form: FormState
    role: RoleState
    pattern_id: str
    scope: str
    residuals: tuple[str, ...]
    trace_refs: tuple[str, ...]


def compose_form_role(form: FormState, role: RoleState, pattern: object) -> FormRoleHypothesis:
    layer = getattr(pattern, "layer", form.layer)
    pattern_id = getattr(pattern, "pattern_id", "pattern.unknown")
    scope = getattr(pattern, "family", layer)
    residuals: tuple[str, ...] = tuple()
    trace_refs = tuple(dict.fromkeys((*form.source_refs, *role.evidence_refs)))
    if form.layer != role.layer:
        residuals = ("cross_layer_form_role",)
    return FormRoleHypothesis(
        layer=layer,
        form=form,
        role=role,
        pattern_id=pattern_id,
        scope=scope,
        residuals=residuals,
        trace_refs=trace_refs,
    )
