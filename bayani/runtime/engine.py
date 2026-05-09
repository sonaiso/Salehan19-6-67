"""Bayani Mustadil Runtime Engine.

Entry point for the full epistemic pipeline.  Usage::

    from bayani.runtime.engine import MustadilRuntimeEngine

    engine = MustadilRuntimeEngine()
    output = engine.run("هل العام قطعي؟")

    print(output.prompt_type)
    print(output.audit.final_rank)
    print(output.audit.certainty_map)
"""

from __future__ import annotations

from bayani.runtime.audit import run_audit
from bayani.runtime.classifier import mustadil_prompt_classifier, prompt_type_classifier
from bayani.runtime.contracts import MustadilOutput, PromptInput
from bayani.runtime.layers import LAYER_REGISTRY
from bayani.runtime.router import get_required_layers
from bayani.runtime.trace import build_trace


class MustadilRuntimeEngine:
    """Orchestrates the full Bayani Mustadil epistemic pipeline.

    The engine:

    1. Classifies the prompt type (PT-01..PT-10).
    2. Classifies the prompt intent (MPC-01..MPC-11).
    3. Routes to the required pipeline layers via the router.
    4. Executes each layer in order.
    5. Records every layer transition in an epistemic trace.
    6. Runs the runtime audit against all invariants.
    7. Returns a :class:`~bayani.runtime.contracts.MustadilOutput`.
    """

    def run(self, prompt: str, mode: str = "analysis") -> MustadilOutput:
        """Execute the full pipeline for *prompt* and return structured output.

        Parameters
        ----------
        prompt:
            Raw Arabic (or English) prompt text.
        mode:
            Execution mode — ``"analysis"`` (default), ``"application"``, or
            ``"construction"``.

        Returns
        -------
        MustadilOutput
            Fully structured pipeline output including trace and audit.
        """
        prompt_input = PromptInput(prompt=prompt, mode=mode)

        # Step 1 — Prompt-Type Classification
        pt_result = prompt_type_classifier(prompt)

        # Step 2 — Intent Classification (MPC)
        intent_result = mustadil_prompt_classifier(prompt)

        # Step 3 — Route to required layers
        required_layers = get_required_layers(pt_result.type_id)

        # Step 4 — Execute layers in order
        layer_results = []
        context: dict = {
            "prompt_type": pt_result,
            "intent": intent_result,
        }
        for layer_name in required_layers:
            layer_fn = LAYER_REGISTRY.get(layer_name)
            if layer_fn is None:
                raise RuntimeError(f"Layer {layer_name!r} not found in LAYER_REGISTRY")
            result = layer_fn(prompt_input, context)
            layer_results.append(result)
            context[layer_name] = result

        # Step 5 — Build epistemic trace
        trace = build_trace(required_layers)

        # Step 6 — Run audit
        audit_result = run_audit(pt_result, intent_result, required_layers, layer_results)

        # Step 7 — Compose output
        final_response: str | None
        if audit_result.final_rank == "structured_answer_allowed":
            final_response = None  # downstream decoder/LLM fills this
        elif audit_result.final_rank == "deferred_pending_classification":
            final_response = "لا يمكن الحكم قبل اكتمال التصنيف المعرفي."
        else:
            final_response = (
                f"الرتبة: {audit_result.final_rank}. "
                f"الانتهاكات: {'; '.join(audit_result.violations)}"
            )

        return MustadilOutput(
            prompt_type=pt_result.type_id,
            intent=intent_result,
            required_layers=required_layers,
            layer_results=layer_results,
            trace=trace,
            audit=audit_result,
            final_response=final_response,
        )
