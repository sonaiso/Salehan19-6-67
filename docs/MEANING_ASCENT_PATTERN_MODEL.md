# Meaning-Ascent Pattern Model

The model treats a pattern as a layer closure law, not a static template.

## Layer law

For each layer `L`:

- hypothesis: `h_L = FormState ⊗_L RoleState`
- closure: `χ_L(h_L)`
- minimum completion: `MC_L(h_L)`

Decision contract:

- `certificate`: in-domain, MC satisfied, no fatal barrier
- `hypothesis`: in-domain, no fatal barrier, MC incomplete
- `zero`: domain failure or fatal barrier

## Meta-pattern law

`MetaPattern` defines how concrete patterns are built:

- form kind + role kind
- composition operator
- closure schema + minimum-completion schema
- governor + rank + residual + trace schema
- allowed/forbidden bridge schema

## Global certificate

Global certificate is separate from local closure.

Required:

1. all required local closures certified
2. all required bridges validated
3. no silent layer authority transfer

## Existing-system compatibility

The kernel is additive and references existing:

- `level_schema`
- `LayerSovereigntyRegistry`
- `PatternOperatorRegistry`

It keeps current certificate semantics and public judgment triad unchanged.
