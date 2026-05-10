"""RootFamilyGraph — models the full family of words derived from a single root.

A root family (عائلة الجذر) is the complete set of derived forms grouped by
pattern type: verbs, agent nouns, patient nouns, place nouns, masdars, nisba
forms, diminutives, broken plurals, etc.  This graph represents those
relationships as a navigable structure.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from mcd.morphosemantics.root_ontology import RootNode, get_root_by_id
from mcd.morphosemantics.masdar_event_ontology import get_masdars_by_root
from mcd.morphosemantics.morphosemantic_trace_linker import _KNOWN_WORDS


@dataclass
class RootFamilyMember:
    word: str
    pattern_id: str
    role: str  # agent|patient|place|masdar|nisba|diminutive|plural|verb|attribute

    def to_dict(self) -> dict:
        return {"word": self.word, "pattern_id": self.pattern_id, "role": self.role}


_PATTERN_ROLE_MAP = {
    "faail": "agent",
    "mafuul": "patient",
    "mafal_place": "place",
    "mafala_place": "place",
    "faaaal_intense": "agent_intensified",
    "istafala_verb": "verb",
    "tafaala_reflex": "verb",
    "faiil_attr": "attribute",
    "fuayyil_dim": "diminutive",
    "afaal_plural": "plural",
    "fiaal_plural": "plural",
    "fuuul_plural": "plural",
    "fual_plural": "plural",
    "nisba_yaa": "nisba",
    "mustafl_patient": "patient",
    "mufaail_agent": "agent",
    "fiaala_masdar_craft": "masdar",
}


@dataclass
class RootFamilyGraph:
    root_id: str
    root_node: Optional[dict]
    members: list[RootFamilyMember]
    masdar_events: list[dict]
    radicals_str: str

    def to_dict(self) -> dict:
        return {
            "root_id": self.root_id,
            "root_node": self.root_node,
            "members": [m.to_dict() for m in self.members],
            "masdar_events": self.masdar_events,
            "radicals_str": self.radicals_str,
        }


class RootFamilyGraphBuilder:
    """Builds a RootFamilyGraph for a given root_id."""

    def build(self, root_id: str) -> RootFamilyGraph:
        root = get_root_by_id(root_id)
        root_dict = root.to_dict() if root else None
        radicals_str = "–".join(root.radicals) if root else root_id

        # Collect all known words for this root
        members: list[RootFamilyMember] = []
        for word, (rid, pid) in _KNOWN_WORDS.items():
            if rid == root_id:
                role = _PATTERN_ROLE_MAP.get(pid, "derived")
                members.append(RootFamilyMember(word=word, pattern_id=pid, role=role))

        # Deduplicate (same word, same pattern may appear with/without diacritics)
        seen = set()
        unique_members = []
        for m in members:
            key = (m.word, m.pattern_id, m.role)
            if key not in seen:
                seen.add(key)
                unique_members.append(m)

        masdars = [ev.to_dict() for ev in get_masdars_by_root(root_id)]

        return RootFamilyGraph(
            root_id=root_id,
            root_node=root_dict,
            members=unique_members,
            masdar_events=masdars,
            radicals_str=radicals_str,
        )
