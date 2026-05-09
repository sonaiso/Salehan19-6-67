"""LLM adapter stub for the Bayani Mustadil Runtime Engine.

In v0.1 this module provides a *stub* LLM adapter that demonstrates the
interface contract:

- The adapter must receive a fully audited
  :class:`~bayani.runtime.contracts.MustadilOutput` **before** any call to
  the LLM is made.
- The adapter constructs a constrained prompt that includes the prompt type,
  intent, required layers, and forbidden jumps so the LLM cannot bypass the
  epistemic pipeline.

To use a real LLM, subclass :class:`LLMAdapter` and override
:meth:`_call_llm`.
"""

from __future__ import annotations

from bayani.runtime.contracts import MustadilOutput


class LLMAdapterError(RuntimeError):
    """Raised when the adapter refuses to call the LLM."""


class LLMAdapter:
    """Base LLM adapter — builds a constrained prompt and calls the LLM.

    The adapter enforces that the LLM is *only called after* the engine has
    produced a :class:`MustadilOutput` with a passing audit.

    Parameters
    ----------
    model_name:
        Identifier of the target language model (for logging/routing).
    """

    def __init__(self, model_name: str = "stub") -> None:
        self.model_name = model_name

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def complete(self, output: MustadilOutput, user_prompt: str) -> str:
        """Generate an LLM completion constrained by the pipeline output.

        Raises
        ------
        LLMAdapterError
            If the audit did not pass (final_rank is not
            ``"structured_answer_allowed"``).
        """
        if output.audit.final_rank != "structured_answer_allowed":
            raise LLMAdapterError(
                f"LLM call refused: audit rank is {output.audit.final_rank!r}. "
                f"Violations: {output.audit.violations}"
            )

        constrained_prompt = self._build_constrained_prompt(output, user_prompt)
        return self._call_llm(constrained_prompt)

    # ------------------------------------------------------------------
    # Internal helpers — override _call_llm in subclasses
    # ------------------------------------------------------------------

    def _build_constrained_prompt(
        self, output: MustadilOutput, user_prompt: str
    ) -> str:
        """Build the constrained prompt that will be sent to the LLM."""
        forbidden_jumps = output.audit.jumps_prevented
        certainty_map = output.audit.certainty_map

        lines = [
            "=== Bayani Mustadil Constrained Prompt ===",
            f"Prompt type: {output.prompt_type}",
            f"Primary purpose: {output.intent.primary_purpose}",
            f"Required layers executed: {', '.join(output.required_layers)}",
            f"Forbidden jumps checked: {', '.join(forbidden_jumps)}",
            f"Certainty map: {certainty_map}",
            "---",
            "User question:",
            user_prompt,
            "---",
            "Instruction: Answer within the boundaries defined by the certainty map. "
            "Do not exceed the audit-permitted rank.",
        ]
        return "\n".join(lines)

    def _call_llm(self, constrained_prompt: str) -> str:
        """Send *constrained_prompt* to the language model and return the response.

        This is a stub implementation that returns the prompt unchanged.
        Override this method to integrate a real LLM backend (e.g. OpenAI,
        local Ollama, etc.).
        """
        # Stub: echo the constrained prompt as the "response"
        return f"[LLMAdapter stub — model={self.model_name}]\n{constrained_prompt}"
