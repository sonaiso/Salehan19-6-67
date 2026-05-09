"""DomainVector — build and validate domain vectors."""
from __future__ import annotations

from .vector_space import DOMAIN_DIMENSIONS, zero_domain_vector, normalize_vector, validate_vector_dimensions


def build_domain_vector(domains: list[str]) -> dict[str, float]:
    """Build a domain vector with equal weight for all listed domains."""
    v = zero_domain_vector()
    for d in domains:
        if d in DOMAIN_DIMENSIONS:
            v[d] = 1.0
    return normalize_vector(v) if any(v.values()) else v


def validate_domain_vector(v: dict[str, float]) -> list[str]:
    return validate_vector_dimensions(v, DOMAIN_DIMENSIONS)


def blend_domain_vectors(vectors: list[dict[str, float]], weights: list[float] | None = None) -> dict[str, float]:
    """Weighted blend of domain vectors, normalized."""
    if not vectors:
        return zero_domain_vector()
    if weights is None:
        weights = [1.0] * len(vectors)
    result = zero_domain_vector()
    for v, w in zip(vectors, weights):
        for k in DOMAIN_DIMENSIONS:
            result[k] += v.get(k, 0.0) * w
    return normalize_vector(result)
