"""CompositionFunction — deterministic composition of child vectors."""
from __future__ import annotations

from dataclasses import dataclass, field

from .vector_space import (
    ROLE_DIMENSIONS, DOMAIN_DIMENSIONS,
    normalize_vector, validate_vector_dimensions,
)


@dataclass
class CompositionInput:
    child_vectors: list[dict[str, float]]
    relation_bias: dict[str, float] = field(default_factory=dict)
    domain_bias: dict[str, float] = field(default_factory=dict)
    evidence_bias: dict[str, float] = field(default_factory=dict)
    ambiguity_penalty: float = 0.0
    contradiction_penalty: float = 0.0
    fake_evidence_penalty: float = 0.0
    weights: list[float] | None = None


@dataclass
class CompositionResult:
    vector: dict[str, float]
    penalties_applied: dict[str, float]
    explanation: str

    def to_dict(self) -> dict:
        return {
            "vector": self.vector,
            "penalties_applied": self.penalties_applied,
            "explanation": self.explanation,
        }


def compose_vectors(inp: CompositionInput) -> CompositionResult:
    """
    V(parent) = Normalize(
        Σ wi * V(child_i)
        + RelationBias + DomainBias + EvidenceBias
        - AmbiguityPenalty - ContradictionPenalty - FakeEvidencePenalty
    )

    Deterministic: same input always gives same output.
    Unknown dimensions cause a ValueError.
    Output values are clamped to [0, 1].
    """
    if not inp.child_vectors:
        return CompositionResult(
            vector={},
            penalties_applied={},
            explanation="no child vectors provided",
        )

    # Determine dimensions from first child
    all_dims = list(inp.child_vectors[0].keys())

    # Validate all children have same dimensions
    for i, v in enumerate(inp.child_vectors):
        unknown = [k for k in v if k not in all_dims]
        if unknown:
            raise ValueError(f"child_vector[{i}] has unknown dimensions: {unknown}")

    weights = inp.weights if inp.weights else [1.0] * len(inp.child_vectors)
    if len(weights) != len(inp.child_vectors):
        raise ValueError("weights length must match child_vectors length")

    # Weighted sum
    result: dict[str, float] = {d: 0.0 for d in all_dims}
    for v, w in zip(inp.child_vectors, weights):
        for d in all_dims:
            result[d] += v.get(d, 0.0) * w

    # Add biases (only for known dims)
    for d, bias in inp.relation_bias.items():
        if d in result:
            result[d] += bias
    for d, bias in inp.domain_bias.items():
        if d in result:
            result[d] += bias
    for d, bias in inp.evidence_bias.items():
        if d in result:
            result[d] += bias

    penalties_applied: dict[str, float] = {}

    # Ambiguity penalty: lower certainty/judgment dimensions
    if inp.ambiguity_penalty > 0.0:
        for d in ["judgment", "claim", "near_certainty", "strong_knowledge"]:
            if d in result:
                result[d] = max(0.0, result[d] - inp.ambiguity_penalty)
        penalties_applied["ambiguity"] = inp.ambiguity_penalty

    # Contradiction penalty: lower near_certainty
    if inp.contradiction_penalty > 0.0:
        for d in ["near_certainty", "judgment"]:
            if d in result:
                result[d] = max(0.0, result[d] - inp.contradiction_penalty)
        penalties_applied["contradiction"] = inp.contradiction_penalty

    # Fake evidence penalty: lower evidence/certainty dimensions
    if inp.fake_evidence_penalty > 0.0:
        for d in ["evidence", "source", "near_certainty", "strong_knowledge"]:
            if d in result:
                result[d] = max(0.0, result[d] - inp.fake_evidence_penalty)
        penalties_applied["fake_evidence"] = inp.fake_evidence_penalty

    # Normalize (clamp to [0,1])
    total = sum(result.values())
    if total > 0:
        result = {k: min(1.0, v / total) for k, v in result.items()}
    else:
        result = {k: 0.0 for k in result}

    explanation_parts = [f"composed {len(inp.child_vectors)} child vectors"]
    if penalties_applied:
        explanation_parts.append(f"penalties: {penalties_applied}")

    return CompositionResult(
        vector=result,
        penalties_applied=penalties_applied,
        explanation=", ".join(explanation_parts),
    )
