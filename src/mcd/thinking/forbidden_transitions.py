"""Forbidden transitions for governed answer birth."""
from __future__ import annotations

THINKING_FORBIDDEN_TRANSITIONS: tuple[str, ...] = (
    "answer_without_intent_understanding",
    "intent_assumed_as_understood",
    "uncertainty_erasure",
    "thought_without_method",
    "style_without_method",
    "means_as_method",
    "means_as_judgment",
    "tool_output_as_evidence_without_governance",
    "fluent_language_as_proof",
    "metaphor_as_evidence",
    "association_as_causation",
    "statistical_pattern_as_truth",
    "scientific_method_as_worldview",
    "scientific_method_as_normative_judgment",
    "normative_judgment_without_normative_evidence",
    "word_as_reality",
    "answer_without_birth_trace",
    "residual_erasure",
    "silent_level_skip",
)


def find_forbidden_transitions(tags: list[str]) -> list[str]:
    """Filter input tags to registered forbidden transitions, normalized and deduplicated."""
    normalized = {(t or "").strip().lower() for t in THINKING_FORBIDDEN_TRANSITIONS}
    seen: set[str] = set()
    hits: list[str] = []
    for tag in tags:
        current = (tag or "").strip().lower()
        if current in normalized and current not in seen:
            seen.add(current)
            hits.append(current)
    return hits
