"""DependencyResolver — builds head-dependent edges from a list of MurabUnits."""
from __future__ import annotations

from mcd.murab.murab_schema import MurabUnit


class DependencyResolver:
    """Simple rule-based dependency edge builder.

    Returns a list of dicts: {head_id, dependent_id, relation}
    """

    def resolve(self, units: list[MurabUnit]) -> list[dict]:
        edges: list[dict] = []
        verb_unit: MurabUnit | None = None

        for unit in units:
            if unit.word_type in ("verb", "imperfect_verb"):
                verb_unit = unit
                continue

            if verb_unit is None:
                continue

            if unit.irab_case == "nominative" and unit.syntactic_role in ("فاعل", ""):
                edges.append({
                    "head_id": verb_unit.unit_id,
                    "dependent_id": unit.unit_id,
                    "relation": "nsubj",
                })

            elif unit.irab_case == "accusative":
                edges.append({
                    "head_id": verb_unit.unit_id,
                    "dependent_id": unit.unit_id,
                    "relation": "obj",
                })

            elif unit.irab_case == "genitive":
                edges.append({
                    "head_id": unit.unit_id,  # prep is the head
                    "dependent_id": unit.unit_id,
                    "relation": "obl",
                })

        # Idafa edges (consecutive noun pairs)
        for i in range(len(units) - 1):
            a, b = units[i], units[i + 1]
            if (a.word_type in ("noun", "proper_noun", "masdar")
                    and b.irab_case == "genitive"
                    and b.syntactic_role in ("مضاف إليه", "")):
                edges.append({
                    "head_id": a.unit_id,
                    "dependent_id": b.unit_id,
                    "relation": "nmod:poss",
                })

        return edges
