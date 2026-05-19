# AFU Fractal Definition (the *definition-of-definition*)

This page is the single canonical statement of the AFU fractal-definition
template introduced in PR 2. The codified template lives in
`src/mcd/afu/fractal_definition/template.py`; everything below documents
why that template exists and what it guarantees.

## 1. The 15-field template (§4 of the brief)

```
FractalDefinition =
⟨ name, layer, carrier, domain,
  prior_information, distinction,
  relation_before, relation_after,
  function,
  formation_gate, backward_gate,
  evidence, residuals, rank, output_contract ⟩
```

## 2. Constructional law (§15)

```
∀ D ∈ FractalDefinition:
    formation_gate(D) ≠ ∅  ∧  backward_gate(D) ≠ ∅
otherwise:  D is rejected with AFUContractError("not_fractal: ...")
```

A definition without **both** gates is not a fractal definition. The
template's constructor enforces this; `is_fractal()` re-runs the same
checks non-destructively for diagnostics.

## 3. Runtime law (§14) — *forward alone is insufficient*

Every concept exposes two mandatory functions:

| Function          | Direction | Output                |
| ----------------- | --------- | --------------------- |
| `forward_define`  | →         | `LicensedOutput`      |
| `backward_verify` | ←         | `EpistemicRank`       |

The base `FractalDefinitionRuntime` raises `NotImplementedError` for
both. The shipped `NullFractalRuntime` provides a fail-closed default so
unfinished layers are *legal but capped at HYPOTHESIS*: `forward_define`
emits a `LicensedOutput` carrying the blocking `unknown_gate` residual;
`backward_verify` returns `ZERO` on any blocking residual in the later
effect, otherwise `HYPOTHESIS`. Neither path can reach `CERTIFICATE`
until a real evaluator is registered in the Gate Registry.

## 4. Closure law (§17) — ordering

```
1. FractalDefinition     ← PR 2
2. Gate                  ← PR 2
3. Evidence              ← PR 2
4. Residual              ← PR 2 (adapter over residual_taxonomy)
5. Rank                  ← PR 2 (re-export; see §6 below)
6. ForwardTransition     ← PR 2
7. BackwardVerification  ← PR 2
8. LicensedOutput        ← PR 1
9. Layer-specific definitions  ← PR 3+
```

No layer-specific concept (حرف, جذر, دال, حكم, تنزيل, …) may land
before this template is in place.

## 5. Field → enforcement → witness test

| Field               | Enforced by                                  | Witness test                                                       |
| ------------------- | -------------------------------------------- | ------------------------------------------------------------------ |
| `name`              | `_nonempty("name", ...)`                     | `test_blank_scalar_field_is_rejected[name]`                        |
| `layer`             | `_nonempty("layer", ...)`                    | `test_blank_scalar_field_is_rejected[layer]`                       |
| `carrier`           | `_nonempty("carrier", ...)`                  | `test_blank_scalar_field_is_rejected[carrier]`                     |
| `domain`            | `_nonempty("domain", ...)`                   | `test_blank_scalar_field_is_rejected[domain]`                      |
| `prior_information` | `freeze_strings(...)`                        | `test_strings_are_stripped_and_tuples_frozen`                      |
| `distinction`       | `freeze_strings(...)` + non-empty check      | `test_distinction_must_be_nonempty`                                |
| `relation_before`   | `freeze_strings(...)`                        | `test_strings_are_stripped_and_tuples_frozen`                      |
| `relation_after`    | `freeze_strings(...)`                        | `test_strings_are_stripped_and_tuples_frozen`                      |
| `function`          | `_nonempty("function", ...)`                 | `test_blank_scalar_field_is_rejected[function]`                    |
| `formation_gate`    | §15 law in `__post_init__`                   | `test_missing_formation_gate_is_not_fractal`                       |
| `backward_gate`     | §15 law in `__post_init__`                   | `test_missing_backward_gate_is_not_fractal`                        |
| `evidence`          | `Evidence.__post_init__`                     | `test_evidence_certificate_without_anchor_is_rejected`             |
| `residuals`         | `Residual.__post_init__` + `cap_by_residuals`| `test_certificate_downgraded_by_blocking_residual`                 |
| `rank`              | `normalize_rank` + `cap_by_residuals`        | `test_rank_clamped_to_public_lattice`                              |
| `output_contract`   | `_nonempty("output_contract", ...)`          | `test_blank_scalar_field_is_rejected[output_contract]`             |

## 6. Why `Rank.LICENSED` is **not** introduced

The brief's §13 sketch proposes a four-level rank
`ZERO / HYPOTHESIS / LICENSED / CERTIFICATE`. The constitution forbids a
fourth final epistemic status: only `ZERO`, `HYPOTHESIS`, and
`CERTIFICATE` are valid terminal judgments.

We resolve this by treating licensure as a *property of an output* —
already encoded by `LicensedOutput` — rather than a fourth rank. The
fractal-definition layer therefore re-exports `EpistemicRank` under the
alias `Rank` and refuses internal kernel ranks via `assert_public`.

## 7. What is NOT in this PR

* No layer-specific definitions (`LetterDefinition`, `RootDefinition`,
  `JudgmentDefinition`, …). The brief's six worked examples (§§6–12)
  ride entirely as YAML fixtures under
  `tests/afu/fractal_definition/fixtures/`.
* No populated Gate Registry. The registry is shipped empty, and
  `GateRegistry.evaluate` on any id returns the fail-closed
  `unknown_gate` verdict.
* No stages, no runner, no public API, no CLI.
* No theory imports under `mcd.afu.*`; the AST-level guard
  `tests/afu/test_no_theory_imports.py` enforces this.
* No `Rank.LICENSED` (see §6).
