"""Localization module — thin wrapper around ar.json.

Usage:
    from localization import t, t_rel, t_role, t_cert

    t("agent_of", "relation_types")   # -> "فاعل"
    t_rel("has_root")                  # -> "له جذر"
    t_role("agent_noun")               # -> "اسم فاعل"
    t_cert("hypothesis")               # -> "فرضية"
    t_label("root")                    # -> "الجذر"
"""
from __future__ import annotations
import json
from pathlib import Path
from functools import lru_cache

_AR = Path(__file__).parent / "ar.json"


@lru_cache(maxsize=1)
def _data() -> dict:
    with open(_AR, encoding="utf-8") as fh:
        return json.load(fh)


def t(key: str, section: str, fallback: str | None = None) -> str:
    """Generic translate: t(key, section) → Arabic string, or fallback/key if missing."""
    return _data().get(section, {}).get(key, fallback if fallback is not None else key)


def t_rel(relation_type: str) -> str:
    """Translate a relation_type string → Arabic."""
    return t(relation_type, "relation_types")


def t_role(role: str) -> str:
    """Translate a morphological role string → Arabic."""
    return t(role, "roles")


def t_hint(semantic_hint: str) -> str:
    """Translate a semantic_hint string → Arabic."""
    return t(semantic_hint, "semantic_hints")


def t_cert(level: str) -> str:
    """Translate a certainty level string → Arabic."""
    return t(level, "certainty_levels")


def t_label(label: str) -> str:
    """Translate a UI label string → Arabic."""
    return t(label, "labels")
