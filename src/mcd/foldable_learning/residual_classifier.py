"""ResidualClassifier — classify residuals by type families."""
from __future__ import annotations
from mcd.residual_learning.residual_schema import CognitiveResidual, Severity
from .residual_schema import ResidualType

__all__ = ["ResidualClassifier"]

_BLOCKING_TYPES = {ResidualType.HARM_HARAM, ResidualType.INJECTION, ResidualType.GPT_AS_EVIDENCE}
_HIGH_TYPES = {ResidualType.TOOL_EVIDENCE, ResidualType.CERTAINTY, ResidualType.EVIDENCE, ResidualType.UNSUPPORTED_GENERALIZATION, ResidualType.TRACEABILITY}
_MEDIUM_TYPES = {ResidualType.CAUSALITY, ResidualType.METAPHOR, ResidualType.AMBIGUITY, ResidualType.EDGE, ResidualType.DOMAIN}


class ResidualClassifier:
    def classify_severity(self, residual: CognitiveResidual) -> str:
        for rt in residual.residual_types:
            if rt in _BLOCKING_TYPES:
                return Severity.BLOCKING.value
        for rt in residual.residual_types:
            if rt in _HIGH_TYPES:
                return Severity.HIGH.value
        for rt in residual.residual_types:
            if rt in _MEDIUM_TYPES:
                return Severity.MEDIUM.value
        return Severity.LOW.value

    def is_blocking(self, residual: CognitiveResidual) -> bool:
        return self.classify_severity(residual) == Severity.BLOCKING.value

    def get_primary_type(self, residual: CognitiveResidual) -> str | None:
        if not residual.residual_types:
            return None
        for rt in (ResidualType.HARM_HARAM, ResidualType.INJECTION, ResidualType.GPT_AS_EVIDENCE):
            if rt in residual.residual_types:
                return rt
        return residual.residual_types[0]
