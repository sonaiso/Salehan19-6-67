# Meta-Control Layer (MCL)

## Purpose

MCL is a governance layer فوق التحليل الصوتي/الصرفي/النحوي/الدلالي.
It does not ask *"what is this mark absolutely?"*; it asks:

- ما وظيفة هذه العلامة داخل هذا المسار؟
- ما القيود التي نجحت/فشلت؟
- ما الدليل؟
- ما المسارات المنافسة؟
- ما البقايا التي يجب حفظها؟

## Core Contract

```text
Meaning(unit) = Role(unit | path, layer, context, evidence)
```

No unit-level absolute function is allowed.

## Path Governance

```text
P0 = GenerateCandidates(input)
P1 = FilterImpossible(P0)
P2 = RankLikely(P1)
P3 = KeepTopK(P2)
Output = Fold(P3 + Residuals)
```

The layer always:

1. removes impossible paths,
2. ranks viable paths,
3. preserves residual competing paths.

## Rank Law

```text
GateRank(p) = meet(phonetic, morphological, syntactic, semantic, context, evidence)
Support(p) = aggregate(independent_evidence)
FinalRank(p) = meet(GateRank(p), Support(p))
```

## Zero and Certificate Semantics

Path-level status may use:

- `zero_in_path`
- `possibility`
- `hypothesis`
- `likely`
- `strong`
- `certificate`

But **public final judgment remains triadic only**:

- `zero`
- `hypothesis`
- `certificate`

`zero_in_path` means failure **inside this path**, not absolute non-existence.

## Capsule Contract

MCL emits a foldable capsule containing:

- selected path
- top-k paths
- rejected paths
- role assignments
- transformations
- constraints
- evidence
- rank
- public judgment
- residuals
- trace
- fold hash
- unfold recipe

This guarantees explainability: not only *what* was selected, but *why*.
