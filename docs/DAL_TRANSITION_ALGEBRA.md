# Dal Transition Algebra (DTA)

## Constitutional Position

The Dal Transition Algebra governs transitions within the **Dalalah** (دلالة) layer — the pre-meaning linguistic signification space that sits between raw text and semantic interpretation.

### Supreme Architecture Position

```
Reality
  → Cognitive Distinction
  → Linguistic Signification
  → [DAL LAYER ← You are here]
  → Conceptual Geometry
  → Direct Meaning
  → Licensed Implication
  → Claim
  → Evidence
  → Judgment
  → ReverseTrace
```

## Core Principle

**DAL produces NO meaning, NO ifadah (إفادة), NO hukm (حكم).**

DAL processes linguistic forms — carriers, patterns, weights — not semantic content.

## Transition States

DTA defines four progressive states:

1. **UNICODE_RAW** — Raw text input
2. **CARRIER** — Text with preserved orthographic identity
3. **ISOLATED_LAFZ** — Single lexical unit (LafzMufrad candidate)
4. **ROOT_STEM** — Morphological root extraction (still pre-meaning)

### Constitutional Rule: No Level Jumps

Transitions MUST be stepwise:

- ✅ UNICODE_RAW → CARRIER
- ✅ CARRIER → ISOLATED_LAFZ
- ✅ ISOLATED_LAFZ → ROOT_STEM
- ❌ CARRIER → ROOT_STEM (skips ISOLATED_LAFZ)
- ❌ UNICODE_RAW → ROOT_STEM (skips two levels)

## Transition Proof Requirements

Every transition requires a **DTATransitionProof** containing:

### 1. Qiyas Proof (Structural Analogy)

- **origin**: Reference case
- **branch**: New case being transitioned
- **shared_cause** (علة): Why they belong to same class
- **effective_description**: What property is preserved

Example: "كاتب" transitions like "ضارب" because both follow the فاعل pattern.

### 2. Identity Preservation

The orthographic form must be preserved through the transition.

### 3. Minimal Completeness

- All required carriers must be present
- All required identities must be present
- Origin must be traceable

### 4. License + Trace + Rank + Residuals

- **license**: Authorization tag for this transition
- **trace**: Evidence chain back to source
- **rank**: Epistemic status (ZERO/HYPOTHESIS/CERTIFICATE)
- **residuals**: Unresolved issues that block or warn

## Forbidden Outputs

The following outputs are **constitutionally forbidden** at the DAL layer:

- `meaning` / `ma'na` / `معنى`
- `ifadah` / `إفادة`
- `hukm` / `حكم`
- `judgment`

Any transition attempting to produce these outputs is **automatically rejected** with `DTARejectionKind.FORBIDDEN_OUTPUT`.

## LafzMufrad: NOT Meaning

`LafzMufrad` (لفظ مفرد) is the fundamental unit of the DAL layer.

### What LafzMufrad IS

A governed linguistic form with:

- Preserved **carriers** (orthographic components: ك، ا، ت، ب)
- Preserved **identities** (morphological markers: فاعل، مذكر، مفرد)
- Traceable **origin** (source text)
- Epistemic **rank** (certainty level)
- Documented **residuals** (unresolved issues)

### What LafzMufrad is NOT

- ❌ NOT semantic meaning ("كاتب" ≠ "writer")
- ❌ NOT ifadah (statement-making)
- ❌ NOT hukm (judgment)

### Example: "كاتب" as WeightCandidate

```python
proof = DTALafzMufradAcceptanceProof(
    lafz="كاتب",
    carriers=("ك", "ا", "ت", "ب"),
    identities=("فاعل_pattern", "fa3il_weight"),
    origin="raw:كاتب",
)
# ✅ Accepted as dal form
# ❌ NOT accepted as meaning "writer"
```

"كاتب" is a **weight candidate** (وزن) following the فاعل pattern. The meaning "writer" comes AFTER dal layer processing.

## Composite Forms

Some forms cannot be treated as simple LafzMufrad:

### Example: "فكتبوه"

This contains multiple components:

- **ف** — conjunction prefix
- **كتب** — verb root
- **و** — plural marker
- **ه** — attached pronoun

It must be accepted as **CompositeOrthographicLafz** with all parts preserved:

```python
proof = DTALafzMufradAcceptanceProof(
    lafz="فكتبوه",
    carriers=("ف", "كتب", "و", "ه"),  # All parts
    identities=(
        "conjunction_fa",
        "root_ktb",
        "plural_waw",
        "pronoun_hu",
    ),
    origin="raw:فكتبوه",
)
# ✅ Accepted with full decomposition
```

## Rejection Taxonomy

DTA defines eight rejection kinds:

1. **FORBIDDEN_OUTPUT** — Produces meaning/ifadah/hukm
2. **LEVEL_JUMP** — Skips intermediate state
3. **MISSING_ORIGIN** — No origin trace
4. **MISSING_SHARED_CAUSE** — No shared cause (علة)
5. **BLOCKING_DIFFERENCE** — Fariq (فارق) blocks transition
6. **IDENTITY_LOST** — Lost carrier or identity
7. **INCOMPLETE** — Minimal completeness violated
8. **NO_PROOF** — No TransitionProof provided

## Implementation Boundary

### Layer Position

This layer is **BEFORE** meaning extraction.

### What DTA Does

- ✅ Governs transitions between linguistic form states
- ✅ Preserves carriers and identities
- ✅ Enforces stepwise progression
- ✅ Requires proof for every transition
- ✅ Blocks forbidden semantic outputs

### What DTA Does NOT Do

- ❌ Does NOT produce meaning (معنى)
- ❌ Does NOT produce ifadah (إفادة)
- ❌ Does NOT produce hukm (حكم)
- ❌ Does NOT perform semantic analysis
- ❌ Does NOT interpret intentions

### Proof Requirement

Every transition without a valid **TransitionProof** is:

- Either **REJECTED** immediately, or
- **POSTPONED** until proof is supplied

There are no "automatic" or "assumed" transitions in DTA.

### LafzMufrad Governance

`LafzMufrad` is NOT meaning.

It is a **dal candidate** with preserved:

- **Effect** (أثر) — traced back to source
- **Rank** (رتبة) — epistemic certainty
- **Residuals** (بقايا) — documented uncertainties

## Relationship to T5

**T5** (if implemented) consumes the **effect** (أثر) produced by DTA but does NOT replace it.

DTA remains the constitutional kernel that:

- Enforces no-jump-to-meaning rule
- Requires origin + branch + shared_cause + identity
- Blocks any output tagged as meaning/ifadah/hukm

## API Summary

### Core Classes

- `DTASpace` — Transition state enum
- `DTARejectionKind` — Rejection classification
- `DTAForbiddenOutputGate` — Blocks semantic outputs
- `DTAMinimalCompleteness` — Ensures component preservation
- `DTAIdentityPreservation` — Verifies form preservation
- `DTAQiyasProof` — Structural analogy evidence
- `DTATransitionProof` — Complete transition proof bundle
- `DTALafzMufradAcceptanceProof` — LafzMufrad validation

### Core Functions

- `is_allowed_transition(from_state, to_state)` — Check if transition is structurally valid
- `accept_transition(proof)` — Gate function for all transitions
- `accept_lafz_mufrad(proof)` — Gate function for LafzMufrad acceptance

## Constitutional Summary

DTA implements the constitutional law that:

1. **Mind precedes language** — Linguistic form is not meaning
2. **Language reveals mind** — But DAL layer does not interpret revelation
3. **No certificate without proof** — Every transition requires valid proof
4. **No residual erasure** — All uncertainties are documented
5. **No silent level skip** — Every state transition is explicit
6. **No meaning before geometry** — Semantic content comes AFTER dal layer

---

**Version**: 1.0.0
**Layer**: Pre-meaning linguistic signification
**Scope**: Internal constitutional kernel
**Status**: Governance-only, no public API export
