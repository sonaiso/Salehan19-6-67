"""Extended residual schema for foldable learning — Phase 7.2."""
from __future__ import annotations
from mcd.residual_learning.residual_schema import CognitiveResidual, Severity


class ResidualType:
    STRUCTURAL = "structural_residual"
    EDGE = "edge_residual"
    VECTOR = "vector_residual"
    EVIDENCE = "evidence_residual"
    CERTAINTY = "certainty_residual"
    DOMAIN = "domain_residual"
    CAUSALITY = "causality_residual"
    METAPHOR = "metaphor_residual"
    TOOL_EVIDENCE = "tool_evidence_residual"
    GPT_AS_EVIDENCE = "gpt_as_evidence_residual"
    HARM_HARAM = "harm_haram_residual"
    INJECTION = "injection_residual"
    AMBIGUITY = "ambiguity_residual"
    UNSUPPORTED_GENERALIZATION = "unsupported_generalization_residual"
    TRACEABILITY = "traceability_residual"

    ALL = [
        STRUCTURAL, EDGE, VECTOR, EVIDENCE, CERTAINTY, DOMAIN,
        CAUSALITY, METAPHOR, TOOL_EVIDENCE, GPT_AS_EVIDENCE, HARM_HARAM,
        INJECTION, AMBIGUITY, UNSUPPORTED_GENERALIZATION, TRACEABILITY,
    ]


__all__ = ["ResidualType", "CognitiveResidual", "Severity"]
