"""VectorSpace — loads and validates registry dimensions."""
from __future__ import annotations

import json
from pathlib import Path

_CONTRACTS_DIR = Path(__file__).parent.parent.parent.parent / "data" / "contracts"


def _load_vector_dims() -> dict:
    path = _CONTRACTS_DIR / "vector_dimensions.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    # Fallback hardcoded dims
    return {
        "role_vector": {"dimensions": [
            "thing", "property", "action", "relation", "cause", "effect",
            "instrument", "time", "place", "evidence", "claim", "judgment",
            "source", "tool",
        ]},
        "domain_vector": {"dimensions": [
            "universe", "human", "life", "science", "culture", "civilization",
            "technology", "language", "method", "industrial", "education",
            "enterprise", "safety", "product",
        ]},
        "evidence_vector": {"dimensions": [
            "sensory", "experimental", "linguistic", "textual", "historical",
            "shari", "technical", "contextual", "source_api", "document",
            "benchmark",
        ]},
        "certainty_vector": {"dimensions": [
            "suspend", "hypothesis", "probable_knowledge", "strong_knowledge",
            "near_certainty",
        ]},
    }


_DIMS = _load_vector_dims()

ROLE_DIMENSIONS: list[str] = _DIMS["role_vector"]["dimensions"]
DOMAIN_DIMENSIONS: list[str] = _DIMS["domain_vector"]["dimensions"]
EVIDENCE_DIMENSIONS: list[str] = _DIMS["evidence_vector"]["dimensions"]
CERTAINTY_DIMENSIONS: list[str] = _DIMS["certainty_vector"]["dimensions"]


def zero_role_vector() -> dict[str, float]:
    return {d: 0.0 for d in ROLE_DIMENSIONS}


def zero_domain_vector() -> dict[str, float]:
    return {d: 0.0 for d in DOMAIN_DIMENSIONS}


def zero_evidence_vector() -> dict[str, float]:
    return {d: 0.0 for d in EVIDENCE_DIMENSIONS}


def zero_certainty_vector() -> dict[str, float]:
    return {d: 0.0 for d in CERTAINTY_DIMENSIONS}


def normalize_vector(v: dict[str, float]) -> dict[str, float]:
    total = sum(v.values())
    if total == 0.0:
        return dict(v)
    return {k: val / total for k, val in v.items()}


def validate_vector_dimensions(v: dict[str, float], expected: list[str]) -> list[str]:
    """Return list of violations (empty if valid)."""
    violations = []
    missing = [d for d in expected if d not in v]
    unknown = [k for k in v if k not in expected]
    for d in missing:
        violations.append(f"missing dimension: {d}")
    for k in unknown:
        violations.append(f"unknown dimension: {k}")
    for k, val in v.items():
        if not (0.0 <= val <= 1.0):
            violations.append(f"dimension '{k}' value {val} out of [0,1]")
    return violations
