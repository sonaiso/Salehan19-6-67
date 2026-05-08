"""Mock decoder adapter for testing the Bayani Mustadil Runtime Engine.

The mock decoder simulates a downstream language-model decoder by returning
a deterministic structured text response based on the
:class:`~bayani.runtime.contracts.MustadilOutput` it receives.

This allows the full pipeline — including engine, classifiers, layers, trace,
and audit — to be tested end-to-end without any real LLM calls.
"""

from __future__ import annotations

from bayani.runtime.contracts import MustadilOutput


class MockDecoder:
    """Deterministic mock of a downstream language-model decoder.

    Parameters
    ----------
    fixed_response:
        If provided this exact string is always returned, regardless of the
        pipeline output.  Useful for unit-testing specific downstream
        scenarios.
    """

    def __init__(self, fixed_response: str | None = None) -> None:
        self._fixed = fixed_response

    def decode(self, output: MustadilOutput) -> str:
        """Generate a mock response from *output*.

        Returns *fixed_response* if one was set, otherwise builds a
        descriptive summary from the audit result.
        """
        if self._fixed is not None:
            return self._fixed

        rank = output.audit.final_rank
        layers_run = ", ".join(output.required_layers[:3]) + (
            f" … (+{len(output.required_layers) - 3} more)"
            if len(output.required_layers) > 3
            else ""
        )

        if rank == "structured_answer_allowed":
            return (
                f"[MockDecoder] Prompt type: {output.prompt_type}. "
                f"Layers executed: {layers_run}. "
                f"Audit passed — structured answer may proceed."
            )
        elif rank == "hypothesis_only":
            return (
                f"[MockDecoder] Prompt type: {output.prompt_type}. "
                f"Rank: hypothesis_only. Violations: "
                + "; ".join(output.audit.violations)
            )
        else:
            return (
                f"[MockDecoder] Pipeline blocked. Rank: {rank}. "
                f"Violations: " + "; ".join(output.audit.violations)
            )
