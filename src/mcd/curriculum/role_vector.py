"""RoleVector — build and validate role vectors for cognitive nodes."""
from __future__ import annotations

from .vector_space import ROLE_DIMENSIONS, zero_role_vector, normalize_vector, validate_vector_dimensions


def build_role_vector(node_type: str) -> dict[str, float]:
    """Build a role vector with 1.0 for the matching dimension, 0 elsewhere."""
    v = zero_role_vector()
    if node_type in ROLE_DIMENSIONS:
        v[node_type] = 1.0
    return v


def validate_role_vector(v: dict[str, float]) -> list[str]:
    return validate_vector_dimensions(v, ROLE_DIMENSIONS)


def blend_role_vectors(vectors: list[dict[str, float]], weights: list[float] | None = None) -> dict[str, float]:
    """Weighted blend of role vectors, normalized."""
    if not vectors:
        return zero_role_vector()
    if weights is None:
        weights = [1.0] * len(vectors)
    result = zero_role_vector()
    for v, w in zip(vectors, weights):
        for k in ROLE_DIMENSIONS:
            result[k] += v.get(k, 0.0) * w
    return normalize_vector(result)
