from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid

DIMENSION_TYPES = {
    "role", "domain", "operator", "evidence", "certainty",
    "trace", "proof", "residual", "pragmatic", "irab", "morphosemantic"
}

@dataclass
class VectorDimension:
    name: str
    dimension_type: str
    range_min: float = 0.0
    range_max: float = 1.0
    definition: str = ""
    allowed_layers: list[str] = field(default_factory=list)
    aggregation_rule: str = "max"
    conflict_rule: str = "lower_wins"
    requires_trace: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "dimension_type": self.dimension_type,
            "range_min": self.range_min,
            "range_max": self.range_max,
            "definition": self.definition,
            "allowed_layers": self.allowed_layers,
            "aggregation_rule": self.aggregation_rule,
            "conflict_rule": self.conflict_rule,
            "requires_trace": self.requires_trace,
        }


@dataclass
class UnifiedVector:
    vector_id: str
    vector_type: str
    dimensions: dict[str, float] = field(default_factory=dict)
    source_unit_ids: list[str] = field(default_factory=list)
    source_trace_refs: list[str] = field(default_factory=list)
    normalized: bool = False
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.source_unit_ids and not self.source_trace_refs:
            raise ValueError("UnifiedVector must have source_unit_ids or source_trace_refs")
        for k, v in self.dimensions.items():
            if not (0.0 <= v <= 1.0):
                raise ValueError(f"Dimension '{k}' value {v} out of [0,1] range")

    @staticmethod
    def make_id() -> str:
        return f"VEC-{uuid.uuid4().hex[:8]}"

    def to_dict(self) -> dict:
        return {
            "vector_id": self.vector_id,
            "vector_type": self.vector_type,
            "dimensions": self.dimensions,
            "source_unit_ids": self.source_unit_ids,
            "source_trace_refs": self.source_trace_refs,
            "normalized": self.normalized,
            "metadata": self.metadata,
        }


_DEFAULT_DIMENSIONS: list[VectorDimension] = [
    VectorDimension("role_vector", "role", definition="Semantic role weight"),
    VectorDimension("domain_vector", "domain", definition="Domain relevance"),
    VectorDimension("operator_vector", "operator", definition="Operator strength"),
    VectorDimension("evidence_vector", "evidence", definition="Evidence weight", requires_trace=True),
    VectorDimension("certainty_vector", "certainty", definition="Certainty level"),
    VectorDimension("trace_vector", "trace", definition="Traceability score", requires_trace=True),
    VectorDimension("proof_vector", "proof", definition="Proof confidence", requires_trace=True),
    VectorDimension("residual_vector", "residual", definition="GPT residual magnitude"),
    VectorDimension("pragmatic_vector", "pragmatic", definition="Pragmatic force"),
    VectorDimension("irab_vector", "irab", definition="I'rab/syntactic position"),
    VectorDimension("morphosemantic_vector", "morphosemantic", definition="Morphosemantic weight"),
    VectorDimension("syntactic_certainty", "certainty", definition="Syntactic position certainty"),
    VectorDimension("factual_certainty", "certainty", definition="Factual/empirical certainty", requires_trace=True),
    VectorDimension("evidence_creation", "evidence", definition="Evidence creation capacity", requires_trace=True),
    VectorDimension("discourse_force", "pragmatic", definition="Discourse/emphasis force"),
]


class UnifiedVectorSpaceRegistry:
    def __init__(self) -> None:
        self._dimensions: dict[str, VectorDimension] = {d.name: d for d in _DEFAULT_DIMENSIONS}

    def register_dimension(self, dim: VectorDimension) -> None:
        self._dimensions[dim.name] = dim

    def get_dimension(self, name: str) -> Optional[VectorDimension]:
        return self._dimensions.get(name)

    def known_dimensions(self) -> list[str]:
        return list(self._dimensions.keys())

    def validate_vector(self, vec: UnifiedVector) -> tuple[bool, list[str]]:
        """Returns (valid, violations)."""
        violations = []
        for k in vec.dimensions:
            if k not in self._dimensions:
                violations.append(f"Unknown dimension: {k}")
        return len(violations) == 0, violations

    def validate_evidence_creation(self, vec: UnifiedVector, operator_type: str) -> tuple[bool, list[str]]:
        """Ensure evidence_creation doesn't rise from Mabni alone."""
        violations = []
        ec = vec.dimensions.get("evidence_creation", 0.0)
        if ec > 0.0 and operator_type == "mabni" and not vec.source_trace_refs:
            violations.append("evidence_creation cannot be raised by MabniOperator without trace evidence")
        return len(violations) == 0, violations

    def validate_factual_certainty(self, vec: UnifiedVector, operator_type: str) -> tuple[bool, list[str]]:
        """Ensure factual_certainty doesn't rise from I'rab alone."""
        violations = []
        fc = vec.dimensions.get("factual_certainty", 0.0)
        if fc > 0.0 and operator_type == "murab" and not vec.source_trace_refs:
            violations.append("factual_certainty cannot be raised by IrabOperator without independent evidence")
        return len(violations) == 0, violations

    def get_all(self) -> list[VectorDimension]:
        return list(self._dimensions.values())
