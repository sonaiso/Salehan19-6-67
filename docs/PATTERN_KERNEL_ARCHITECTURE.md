# Pattern Kernel Architecture

This module introduces a unified, layer-aware pattern kernel under `mcd.patterns` without replacing existing runtime systems.

## Core contract

- `FormState ⊗_L RoleState -> FormRoleHypothesis`
- `MC_L(h)` is evaluated by `satisfies_minimum_completion`
- `close_layer` emits only: `zero`, `hypothesis`, `certificate`
- `certificate` requires MC satisfaction and no fatal barrier
- bridge ascent is governed by `BridgePattern`

## Kernel units

- `FormState`, `RoleState`, `FormRoleHypothesis`
- `Pattern`, `MorphologicalPattern`, `MetaPattern`
- `MinimumCompletion`, `ClosureResult`, `BridgePattern`
- registries: layer/pattern/closure/bridge/meta/minimum-completion

## Integration adapters

- `build_layered_pattern_pipeline()` references `level_schema` + `LayerSovereigntyRegistry`
- `build_pattern_registries()` builds initial layer bindings from existing sovereignty declarations
- `wrap_pattern_operator_as_morphological_pattern()` maps `PatternOperatorRegistry` entries into `MorphologicalPattern`

## Governance alignment

- No new public judgment beyond `zero/hypothesis/certificate`
- Local certificate does not imply global certificate
- No cross-layer authority without an explicit bridge contract
- Residual-preserving policy remains explicit in pattern and bridge objects

## Scope of this PR

This is a kernel introduction and contract layer only. It does not claim full runtime migration or complete meaning-ascent formalization.
