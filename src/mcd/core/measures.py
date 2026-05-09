"""Measurement utilities: clamp, normalize, weighted average."""
from __future__ import annotations


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def normalize_scores(scores: dict[str, float]) -> dict[str, float]:
    total = sum(scores.values())
    if total == 0.0:
        n = len(scores)
        return {k: 1.0 / n if n else 0.0 for k in scores}
    return {k: v / total for k, v in scores.items()}


def weighted_average(values: list[float], weights: list[float]) -> float:
    if not values or not weights:
        return 0.0
    total_w = sum(weights)
    if total_w == 0.0:
        return 0.0
    return sum(v * w for v, w in zip(values, weights)) / total_w
