"""PipelineRegistry — canonical 21-layer Bayani reasoning pipeline.

Implements the ordered registry of all 21 theoretical layer keys from the
Bayani Knowledge System base theory, grouped into 5 functional sets.

The registry has two roles:

  1. **Documentation** — it is the single source of truth mapping each
     theoretical layer key to the code object that implements it.

  2. **Enforcement** — PipelineExecutor.run() walks the layers in order and
     raises LayerSkipError if any layer is attempted out of sequence or if a
     required predecessor has not been completed.

Theoretical invariant enforced here:
  ``NoLevelSkipInPipeline`` — no layer may begin before all earlier layers
  in the same group have completed without error.  Cross-group: no group may
  begin before the previous group is fully complete.

Governing principle (usul al-fiqh):
  لا حكم بلا محل، ولا محل بلا تمييز، ولا تمييز بلا تعيين،
  ولا تعيين بلا نسب، ولا نسب بلا عوامل، ولا ربط بلا معلومات،
  ولا مفهوم بلا واقع، ولا تنزيل بلا تحقيق مناط.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


# ── Layer group enumeration ───────────────────────────────────────────────────

class LayerGroup(str, Enum):
    EPISTEMIC_EXISTENCE   = "Group1_EpistemicExistence"    # Layers  1-2
    SEMANTIC_RELATIONAL   = "Group2_SemanticRelational"    # Layers  3-8
    BAYANI_LINGUISTIC     = "Group3_BayaniLinguistic"      # Layers  9-15
    USULI_APPLICATION     = "Group4_UsuliApplication"      # Layers 16-20
    AUDIT                 = "Group5_Audit"                 # Layer  21


# ── Layer descriptor ──────────────────────────────────────────────────────────

@dataclass
class LayerDescriptor:
    """Describes one layer in the 21-layer pipeline."""
    number:       int                        # 1-based sequence number
    key:          str                        # theoretical layer key
    group:        LayerGroup
    description:  str                        # what the layer does
    arabic_name:  str                        # Arabic concept name
    impl_fn:      Optional[Callable] = None  # callable that runs this layer
    required:     bool = True                # if False, layer may be skipped


# ── Execution state ───────────────────────────────────────────────────────────

@dataclass
class LayerResult:
    layer_key:  str
    success:    bool
    output:     Any = None
    error:      Optional[str] = None
    skipped:    bool = False


class LayerSkipError(RuntimeError):
    """Raised when a layer is executed out of order."""


class LayerFailureError(RuntimeError):
    """Raised when a required layer fails and execution cannot continue."""


# ── Registry ──────────────────────────────────────────────────────────────────

class PipelineRegistry:
    """Registry of all 21 theoretical layer keys in their canonical order.

    Call ``register(layer_key, fn)`` to attach an implementation to a layer.
    Call ``executor(context)`` to get a PipelineExecutor ready to run.
    """

    # Canonical ordered layer definitions
    _LAYERS: list[LayerDescriptor] = [

        # ── Group 1 — Epistemic Existence (Layers 1–2) ───────────────────────
        LayerDescriptor(
            number=1, key="reality_grounding_layer",
            group=LayerGroup.EPISTEMIC_EXISTENCE,
            arabic_name="طبقة التأسيس الواقعي",
            description=(
                "Establishes what actually exists and is empirically grounded in the "
                "input. Separates documented information from assertion. Nothing can "
                "be reasoned about until its reality is established."
            ),
        ),
        LayerDescriptor(
            number=2, key="prior_opinion_filter_layer",
            group=LayerGroup.EPISTEMIC_EXISTENCE,
            arabic_name="طبقة تصفية الرأي السابق",
            description=(
                "Removes prior opinion from the evidential record. No pre-existing "
                "judgment, LLM output, or inherited assumption may be treated as "
                "evidence. This is the primary anti-hallucination gate."
            ),
        ),

        # ── Group 2 — Semantic-Relational (Layers 3–8) ───────────────────────
        LayerDescriptor(
            number=3, key="differentiation_layer",
            group=LayerGroup.SEMANTIC_RELATIONAL,
            arabic_name="طبقة التمييز",
            description=(
                "Distinguishes the entities involved from each other and from their "
                "properties. Required before essence can be assigned — you cannot "
                "assign the essence of something you have not yet distinguished."
            ),
        ),
        LayerDescriptor(
            number=4, key="essence_assignment_layer",
            group=LayerGroup.SEMANTIC_RELATIONAL,
            arabic_name="طبقة تعيين الماهية",
            description=(
                "Assigns the essential nature (ماهية) of each distinguished entity. "
                "Required before any judgment can be formed — invariant: "
                "NoJudgmentBeforeEssenceAssignment."
            ),
        ),
        LayerDescriptor(
            number=5, key="domain_assignment_layer",
            group=LayerGroup.SEMANTIC_RELATIONAL,
            arabic_name="طبقة تعيين المجال",
            description=(
                "Assigns the domain of discourse: epistemic, practical, shari, or "
                "social. Shari judgments require revelation evidence and cannot be "
                "issued from Layer 4 alone. Required before Layer 6."
            ),
        ),
        LayerDescriptor(
            number=6, key="relational_mapping_layer",
            group=LayerGroup.SEMANTIC_RELATIONAL,
            arabic_name="طبقة رسم العلاقات",
            description=(
                "Maps the 13 nisbah (نسبة) relational types between entities: "
                "predicative, causal, conditional, purposive, temporal, locative, "
                "circumstantial, instrumental, possessive, comparative, attributive, "
                "exceptional, and partitive."
            ),
        ),
        LayerDescriptor(
            number=7, key="arabic_operator_layer",
            group=LayerGroup.SEMANTIC_RELATIONAL,
            arabic_name="طبقة المشغّلات العربية",
            description=(
                "Parses the 17 Arabic operator categories (particles, conjunctions, "
                "conditional tools, exception tools, interrogatives, etc.) to identify "
                "the logical structure of the text."
            ),
        ),
        LayerDescriptor(
            number=8, key="binding_layer",
            group=LayerGroup.SEMANTIC_RELATIONAL,
            arabic_name="طبقة الربط",
            description=(
                "Binds semantic roles to their carriers. Resolves pronoun reference, "
                "ellipsis, and scope. No concept can be formed until its referents are "
                "bound — invariant: NoConceptWithoutBinding."
            ),
        ),

        # ── Group 3 — Bayani-Linguistic (Layers 9–15) ────────────────────────
        LayerDescriptor(
            number=9, key="concept_formation_layer",
            group=LayerGroup.BAYANI_LINGUISTIC,
            arabic_name="طبقة تكوين المفهوم",
            description=(
                "Forms concepts by grounding words in the reality established in "
                "Groups 1–2. Produces the ConceptCenter for each key term. Cannot "
                "begin before layers 4, 5, and 8 are complete."
            ),
        ),
        LayerDescriptor(
            number=10, key="judgment_formation_layer",
            group=LayerGroup.BAYANI_LINGUISTIC,
            arabic_name="طبقة تكوين الحكم",
            description=(
                "Forms propositional judgments from grounded concepts. Cannot begin "
                "before layers 4 (essence), 5 (domain), and 6 (relations) are complete."
            ),
        ),
        LayerDescriptor(
            number=11, key="signifier_analysis_layer",
            group=LayerGroup.BAYANI_LINGUISTIC,
            arabic_name="طبقة تحليل الدال",
            description=(
                "Analyses the signifier (دال) — the linguistic form as written or "
                "spoken. Includes morphological analysis, pattern recognition, and "
                "surface form disambiguation."
            ),
        ),
        LayerDescriptor(
            number=12, key="signified_analysis_layer",
            group=LayerGroup.BAYANI_LINGUISTIC,
            arabic_name="طبقة تحليل المدلول",
            description=(
                "Analyses the signified (مدلول) — what the linguistic form refers to "
                "in reality. Requires Layer 11 to have identified the dal first."
            ),
        ),
        LayerDescriptor(
            number=13, key="signifier_signified_relation_layer",
            group=LayerGroup.BAYANI_LINGUISTIC,
            arabic_name="طبقة علاقة الدال بالمدلول",
            description=(
                "Establishes the relationship between signifier and signified: "
                "identity, inclusion, entailment, or metaphor. Required before "
                "mantuq/mafhoom analysis."
            ),
        ),
        LayerDescriptor(
            number=14, key="mantuq_layer",
            group=LayerGroup.BAYANI_LINGUISTIC,
            arabic_name="طبقة المنطوق",
            description=(
                "Analyses the explicit stated meaning (دلالة المنطوق) — what the "
                "text directly asserts. This always takes precedence over implied "
                "meaning (Layer 15)."
            ),
        ),
        LayerDescriptor(
            number=15, key="mafhoom_layer",
            group=LayerGroup.BAYANI_LINGUISTIC,
            arabic_name="طبقة المفهوم",
            description=(
                "Analyses the implied meaning (دلالة المفهوم). Invariant: "
                "NoMafhumStrongerThanMantuq — implied meaning never overrides "
                "explicit meaning from Layer 14."
            ),
        ),

        # ── Group 4 — Usuli-Application (Layers 16–20) ───────────────────────
        LayerDescriptor(
            number=16, key="general_specific_layer",
            group=LayerGroup.USULI_APPLICATION,
            arabic_name="طبقة العام والخاص",
            description=(
                "Resolves aam/khas (العام والخاص) scope — is the ruling or concept "
                "universal or restricted to a specific subset? Determines the "
                "breadth of application."
            ),
        ),
        LayerDescriptor(
            number=17, key="absolute_restricted_layer",
            group=LayerGroup.USULI_APPLICATION,
            arabic_name="طبقة المطلق والمقيّد",
            description=(
                "Resolves mutlaq/muqayyad (المطلق والمقيّد) — does a condition "
                "or qualification restrict the absolute scope of the ruling?"
            ),
        ),
        LayerDescriptor(
            number=18, key="causal_juridical_relations_layer",
            group=LayerGroup.USULI_APPLICATION,
            arabic_name="طبقة العلاقات السببية",
            description=(
                "Establishes the illah (علة — legal/logical cause) and maps "
                "causal-juridical relations. Required for qiyas (analogy) and "
                "for Layer 19 to verify the cause is present in the target case."
            ),
        ),
        LayerDescriptor(
            number=19, key="tahqeeq_manat_layer",
            group=LayerGroup.USULI_APPLICATION,
            arabic_name="طبقة تحقيق المناط",
            description=(
                "Verifies that the conditions required to apply the rule actually "
                "hold in the target case (تحقيق المناط). This is the critical "
                "blocking gate — Layer 20 cannot begin if ManatStatus is not "
                "APPLICABLE or PARTIALLY_APPLICABLE."
            ),
        ),
        LayerDescriptor(
            number=20, key="application_layer",
            group=LayerGroup.USULI_APPLICATION,
            arabic_name="طبقة التنزيل",
            description=(
                "Applies the rule to the verified case. Cannot begin unless "
                "Layer 19 has returned ManatStatus.APPLICABLE. If manat is not "
                "verified, output is routed to HYPOTHESIS or ZERO."
            ),
        ),

        # ── Group 5 — Audit (Layer 21) ────────────────────────────────────────
        LayerDescriptor(
            number=21, key="epistemic_audit_layer",
            group=LayerGroup.AUDIT,
            arabic_name="طبقة المراجعة المعرفية",
            description=(
                "Final review and certainty mapping. Computes the AnswerScore via "
                "AnswerScorer (7-dimensional formula with HallucinationRisk). Checks "
                "for blocking zeros. Generates the ReverseTrace. Produces the "
                "ProofObject with status certificate | hypothesis | zero."
            ),
        ),
    ]

    def __init__(self) -> None:
        # Build lookup by key
        self._by_key: dict[str, LayerDescriptor] = {
            ld.key: ld for ld in self._LAYERS
        }
        # Mutable impl map — populated via register()
        self._impls: dict[str, Callable] = {}

    # ── Registration ──────────────────────────────────────────────────────────

    def register(self, layer_key: str, fn: Callable) -> None:
        """Attach a callable implementation to a layer key.

        Args:
            layer_key: One of the 21 canonical layer keys.
            fn: Callable that accepts a context dict and returns a LayerResult.

        Raises:
            KeyError: If layer_key is not a recognised theoretical key.
        """
        if layer_key not in self._by_key:
            raise KeyError(
                f"Unknown layer key: '{layer_key}'. "
                f"Valid keys: {sorted(self._by_key)}"
            )
        self._impls[layer_key] = fn

    # ── Introspection ─────────────────────────────────────────────────────────

    @property
    def layers(self) -> list[LayerDescriptor]:
        """All 21 layer descriptors in canonical order."""
        return list(self._LAYERS)

    def layer(self, key: str) -> LayerDescriptor:
        """Return the descriptor for a given layer key."""
        return self._by_key[key]

    def layers_in_group(self, group: LayerGroup) -> list[LayerDescriptor]:
        """Return all layer descriptors belonging to a given group."""
        return [ld for ld in self._LAYERS if ld.group == group]

    def is_registered(self, key: str) -> bool:
        """True if an implementation has been attached to this layer."""
        return key in self._impls

    def coverage(self) -> dict[str, bool]:
        """Return {layer_key: is_registered} for all 21 layers."""
        return {ld.key: self.is_registered(ld.key) for ld in self._LAYERS}

    def unregistered_layers(self) -> list[LayerDescriptor]:
        """Return descriptors for layers that have no implementation attached."""
        return [ld for ld in self._LAYERS if not self.is_registered(ld.key)]

    # ── Executor factory ──────────────────────────────────────────────────────

    def executor(self, context: dict) -> "PipelineExecutor":
        """Return a PipelineExecutor bound to this registry and the given context."""
        return PipelineExecutor(registry=self, context=context)


# ── Executor ──────────────────────────────────────────────────────────────────

class PipelineExecutor:
    """Walks the 21-layer pipeline in order, enforcing NoLevelSkipInPipeline.

    Usage::

        registry = PipelineRegistry()
        registry.register("reality_grounding_layer", my_grounder)
        # ... register other layers ...

        executor = registry.executor({"text": "..."})
        results  = executor.run()
    """

    def __init__(self, registry: PipelineRegistry, context: dict) -> None:
        self._registry = registry
        self._context  = dict(context)
        self._results:  dict[str, LayerResult] = {}
        self._completed: list[str] = []

    # ── Group-level gate ──────────────────────────────────────────────────────

    def _group_complete(self, group: LayerGroup) -> bool:
        """True if every required layer in the group has completed successfully."""
        for ld in self._registry.layers_in_group(group):
            if not ld.required:
                continue
            result = self._results.get(ld.key)
            if result is None or not result.success:
                return False
        return True

    # ── Tahqiq gate (Layer 19 → 20 hard block) ────────────────────────────────

    def _check_tahqiq_gate(self) -> Optional[str]:
        """Return a blocker string if tahqiq al-manat has not been verified."""
        tahqiq = self._results.get("tahqeeq_manat_layer")
        if tahqiq is None:
            return "TAHQIQ_GATE: tahqeeq_manat_layer has not been run"
        if not tahqiq.success:
            return f"TAHQIQ_GATE: tahqeeq_manat_layer failed — {tahqiq.error}"
        output = tahqiq.output or {}
        status = output.get("manat_status", "")
        if status not in ("applicable", "partially_applicable"):
            return f"TAHQIQ_GATE: manat_status='{status}' — application blocked"
        return None

    # ── Single-layer execution ────────────────────────────────────────────────

    def _run_layer(self, ld: LayerDescriptor) -> LayerResult:
        """Execute one layer, enforcing ordering and the tahqiq gate."""

        # ── Ordering: check that all prior layers in earlier groups are done ─
        groups_in_order = list(LayerGroup)
        current_group_idx = groups_in_order.index(ld.group)
        for earlier_group in groups_in_order[:current_group_idx]:
            if not self._group_complete(earlier_group):
                raise LayerSkipError(
                    f"Cannot run layer {ld.number} ({ld.key}) — "
                    f"{earlier_group.value} is not yet complete. "
                    f"NoLevelSkipInPipeline invariant violated."
                )

        # ── Special gate: Layer 20 requires verified tahqiq ──────────────────
        if ld.key == "application_layer":
            blocker = self._check_tahqiq_gate()
            if blocker:
                return LayerResult(
                    layer_key=ld.key,
                    success=False,
                    error=blocker,
                )

        # ── No implementation registered — skip if optional, fail if required ─
        if not self._registry.is_registered(ld.key):
            if not ld.required:
                return LayerResult(layer_key=ld.key, success=True, skipped=True)
            return LayerResult(
                layer_key=ld.key,
                success=False,
                error=f"UNREGISTERED: no implementation for required layer '{ld.key}'",
            )

        # ── Run the implementation ────────────────────────────────────────────
        fn = self._registry._impls[ld.key]
        try:
            output = fn(self._context)
            # Allow implementations to return a LayerResult directly
            if isinstance(output, LayerResult):
                return output
            # Or any dict/object — wrap it
            return LayerResult(layer_key=ld.key, success=True, output=output)
        except Exception as exc:  # noqa: BLE001
            return LayerResult(
                layer_key=ld.key,
                success=False,
                error=f"{type(exc).__name__}: {exc}",
            )

    # ── Full pipeline run ─────────────────────────────────────────────────────

    def run(self, stop_on_failure: bool = False) -> list[LayerResult]:
        """Execute all 21 layers in canonical order.

        Args:
            stop_on_failure: If True, halt on the first required-layer failure.
                             If False (default), continue and collect all errors.

        Returns:
            Ordered list of LayerResult — one per layer.
        """
        ordered_results: list[LayerResult] = []

        for ld in self._registry.layers:
            try:
                result = self._run_layer(ld)
            except LayerSkipError as exc:
                result = LayerResult(layer_key=ld.key, success=False, error=str(exc))
                if stop_on_failure and ld.required:
                    self._results[ld.key] = result
                    ordered_results.append(result)
                    raise LayerFailureError(
                        f"Required layer {ld.number} ({ld.key}) skipped out of order: {exc}"
                    ) from exc
            self._results[ld.key] = result
            ordered_results.append(result)
            if result.success and not result.skipped:
                self._completed.append(ld.key)
            elif not result.success and ld.required and stop_on_failure:
                raise LayerFailureError(
                    f"Required layer {ld.number} ({ld.key}) failed: {result.error}"
                )

        return ordered_results

    def run_up_to(self, layer_key: str) -> list[LayerResult]:
        """Run all layers up to and including the named layer (by key)."""
        target_num = self._registry.layer(layer_key).number
        ordered_results: list[LayerResult] = []
        for ld in self._registry.layers:
            if ld.number > target_num:
                break
            result = self._run_layer(ld)
            self._results[ld.key] = result
            ordered_results.append(result)
            if result.success and not result.skipped:
                self._completed.append(ld.key)
        return ordered_results

    @property
    def results(self) -> dict[str, LayerResult]:
        """Results keyed by layer key, for completed layers."""
        return dict(self._results)

    @property
    def completed_keys(self) -> list[str]:
        """Layer keys that have completed successfully, in order."""
        return list(self._completed)


# ── Module-level default registry ─────────────────────────────────────────────

#: Singleton registry — use this unless you need test isolation.
default_registry = PipelineRegistry()
