from __future__ import annotations

from dataclasses import dataclass

from mcd.math_governance.level_schema import ALL_LEVELS
from mcd.morphosemantics.pattern_operator_registry import PatternOperatorRegistry
from mcd.patterns.core import MinimumCompletion, MorphologicalPattern, Pattern
from mcd.patterns.pattern_registry import (
    ClosureDefinition,
    ClosureRegistry,
    LayerPatternBinding,
    LayerPatternRegistry,
    MinimumCompletionRegistry,
    PatternRegistry,
)
from mcd.qualification.layer_sovereignty_registry import LayerSovereigntyRegistry

_ARABIC_DIACRITICS = {"َ", "ُ", "ِ", "ْ", "ّ"}


@dataclass(frozen=True)
class LayerDefinition:
    level: str
    allowed_patterns: tuple[str, ...]
    closure_functions: tuple[str, ...]
    minimum_completion: str
    allowed_bridges: tuple[str, ...]
    residual_rules: tuple[str, ...]
    governor: str


def wrap_pattern_operator_as_morphological_pattern(pattern_id: str) -> MorphologicalPattern | None:
    operator = PatternOperatorRegistry().get(pattern_id)
    if operator is None:
        return None
    return MorphologicalPattern(
        pattern_id=f"morph.{operator.pattern_id}",
        layer="morphology",
        family=operator.family,
        form_slots=("root", "weight"),
        role_slots=("operator_vector", "certainty"),
        binding_relation="form_role_tensor",
        governor="governor.morphology",
        required_evidence_rank="HYPOTHESIS",
        closure_function="chi_morphology",
        minimum_completion="MC_morphology",
        residual_policy=("preserve", "no_silent_drop", "no_residual_erasure"),
        fatal_barriers=("residual_erasure",),
        allowed_bridges=("morphology_to_phrase",),
        forbidden_bridges=("morphology_to_final_judgment",),
        trace_policy="replayable",
        pattern_form=operator.pattern_form,
        root_slots=("f", "a", "l"),
        added_letters=tuple(),
        vowel_schema=tuple(symbol for symbol in operator.pattern_form if symbol in _ARABIC_DIACRITICS),
        operator_vector=dict(operator.operator_vector),
        certainty_policy=operator.certainty_policy,
    )


def build_layered_pattern_pipeline() -> tuple[LayerDefinition, ...]:
    sovereignty = LayerSovereigntyRegistry()
    layers: list[LayerDefinition] = []
    for level in ALL_LEVELS:
        entry = sovereignty.get(level.name)
        if entry is None:
            continue
        layers.append(
            LayerDefinition(
                level=level.name,
                allowed_patterns=(f"pattern.{level.name}",),
                closure_functions=(entry.closure_function,),
                minimum_completion=entry.minimum_completion,
                allowed_bridges=tuple(f"{level.name}_to_{next_layer}" for next_layer in entry.allowed_ascent),
                residual_rules=tuple(entry.residual_rules),
                governor=entry.governor,
            )
        )
    return tuple(layers)


def build_pattern_registries() -> tuple[
    LayerPatternRegistry,
    PatternRegistry,
    ClosureRegistry,
    MinimumCompletionRegistry,
]:
    layer_registry = LayerPatternRegistry()
    pattern_registry = PatternRegistry()
    closure_registry = ClosureRegistry()
    minimum_registry = MinimumCompletionRegistry()

    for layer in build_layered_pattern_pipeline():
        pattern_id = layer.allowed_patterns[0]
        mc_id = layer.minimum_completion
        closure_id = layer.closure_functions[0]
        pattern_registry.register(
            Pattern(
                pattern_id=pattern_id,
                layer=layer.level,
                family="layer_default",
                form_slots=("symbols",),
                role_slots=("features",),
                binding_relation="form_role_tensor",
                governor=layer.governor,
                required_evidence_rank="HYPOTHESIS",
                closure_function=closure_id,
                minimum_completion=mc_id,
                residual_policy=layer.residual_rules,
                fatal_barriers=("residual_erasure",),
                allowed_bridges=layer.allowed_bridges,
                forbidden_bridges=tuple(),
                trace_policy="replayable",
            )
        )
        minimum_registry.register(
            MinimumCompletion(
                mc_id=mc_id,
                layer=layer.level,
                required_form_fields=("symbols",),
                required_role_fields=("features",),
                required_dependencies=tuple(),
                required_evidence_rank="HYPOTHESIS",
                residual_policy=layer.residual_rules,
                fatal_barriers=("residual_erasure",),
            )
        )
        closure_registry.register(
            ClosureDefinition(
                closure_id=closure_id,
                layer=layer.level,
                closure_function=closure_id,
                minimum_completion_id=mc_id,
            )
        )
        layer_registry.register(
            LayerPatternBinding(
                layer=layer.level,
                governor=layer.governor,
                closure_id=closure_id,
                minimum_completion_id=mc_id,
                pattern_ids=(pattern_id,),
                bridge_ids=layer.allowed_bridges,
            )
        )

    return layer_registry, pattern_registry, closure_registry, minimum_registry
