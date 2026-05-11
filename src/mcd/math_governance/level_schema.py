from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CognitiveLevel:
    level_id: str
    name: str
    order: int
    allowed_unit_types: list[str] = field(default_factory=list)
    required_fields: list[str] = field(default_factory=list)
    allowed_morphisms_to_next: list[str] = field(default_factory=list)
    allowed_morphisms_from_previous: list[str] = field(default_factory=list)


_LEVEL_ROWS = [
    ("L0_RAW_TEXT", "raw_text"),
    ("L1_UNICODE", "unicode"),
    ("L2_GRAPHEME", "grapheme"),
    ("L3_ORTHOGRAPHIC_UNIT", "orthographic_unit"),
    ("L4_TOKEN", "token"),
    ("L5_LEXEME", "lexeme"),
    ("L6_MORPHOLOGY", "morphology"),
    ("L7_PHRASE", "phrase"),
    ("L8_CLAUSE", "clause"),
    ("L9_SENTENCE", "sentence"),
    ("L10_PARAGRAPH", "paragraph"),
    ("L11_SECTION", "section"),
    ("L12_FULL_TEXT", "full_text"),
    ("L13_DISCOURSE_GRAPH", "discourse_graph"),
    ("L14_CLAIM_GRAPH", "claim_graph"),
    ("L15_PROOF_OBJECT", "proof_object"),
    ("L16_FINAL_JUDGMENT", "final_judgment"),
]


DEFAULT_REQUIRED_FIELDS = [
    "unit_id",
    "level_id",
    "unit_type",
    "raw_span",
    "normalized_span",
    "raw_text",
    "normalized_text",
    "pre_unit_ids",
    "post_unit_ids",
    "trace_refs",
    "morphism_in",
    "morphism_out",
    "pre_to_post_relation",
    "residuals",
    "beta_status",
]


ALL_LEVELS: list[CognitiveLevel] = [
    CognitiveLevel(
        level_id=lid,
        name=name,
        order=i,
        allowed_unit_types=[name, "unit", "cognitive_unit"],
        required_fields=list(DEFAULT_REQUIRED_FIELDS),
    )
    for i, (lid, name) in enumerate(_LEVEL_ROWS)
]

LEVELS_BY_ID = {level.level_id: level for level in ALL_LEVELS}
LEVELS_BY_NAME = {level.name: level for level in ALL_LEVELS}


def get_level(level_id_or_name: str) -> CognitiveLevel | None:
    return LEVELS_BY_ID.get(level_id_or_name) or LEVELS_BY_NAME.get(level_id_or_name)


def next_level(level_id_or_name: str) -> CognitiveLevel | None:
    level = get_level(level_id_or_name)
    if level is None:
        return None
    idx = level.order + 1
    if idx >= len(ALL_LEVELS):
        return None
    return ALL_LEVELS[idx]


def previous_level(level_id_or_name: str) -> CognitiveLevel | None:
    level = get_level(level_id_or_name)
    if level is None:
        return None
    idx = level.order - 1
    if idx < 0:
        return None
    return ALL_LEVELS[idx]


def level_chain() -> list[str]:
    return [lvl.name for lvl in ALL_LEVELS]
