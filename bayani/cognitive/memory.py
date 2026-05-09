"""ThreeLayerMemory — Atomic / Relational / Conceptual knowledge store.

The Nabhani epistemological framework requires three distinct memory layers:

1. **Atomic Memory** (ذاكرة ذرية)
   Stores individual Unicode symbols with their feature and role vectors.
   These are the stable orthographic/phonological primitives.

2. **Relational Memory** (ذاكرة علائقية)
   Stores roots, patterns, and relation edges between morphological and
   syntactic units.  Each entry has a certainty weight that can be updated
   when new evidence arrives (learner mode).

3. **Conceptual Memory** (ذاكرة مفاهيمية)
   Stores verified concepts, judgments, and certainty levels.  A concept
   is only promoted here after passing the Evidence Gate (score ≥ threshold).

The memory supports two operational modes:

* **Knower mode** — read-only; the system reasons from stored knowledge
  without modifying any weights.
* **Learner mode** — read-write; the system may update relation weights,
  add new relations, raise or lower certainty, and promote new concepts.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Atomic Memory Entry
# ---------------------------------------------------------------------------

@dataclass
class AtomicEntry:
    """One entry in the Atomic Memory layer."""
    symbol: str
    unicode_codepoint: int
    features: Dict[str, Any] = field(default_factory=dict)
    role_vector: Dict[str, float] = field(default_factory=dict)
    access_count: int = 0          # how many times this symbol was encoded


# ---------------------------------------------------------------------------
# Relational Memory Entry
# ---------------------------------------------------------------------------

@dataclass
class RelationalEntry:
    """One entry in the Relational Memory layer."""
    entry_id: str                   # unique key, e.g. "root:كتب" or "rel:agent_of:كتب→طالب"
    entry_type: str                 # "root" | "pattern" | "relation" | "prefix" | "suffix"
    surface: str                    # surface form of the root / morpheme
    description: str = ""           # human-readable description
    field_label: str = ""           # semantic field (e.g. "تدوين")
    patterns: List[str] = field(default_factory=list)   # associated patterns
    certainty: float = 0.0          # current certainty weight [0, 1]
    evidence: List[str] = field(default_factory=list)   # evidence strings
    access_count: int = 0

    def update_certainty(self, delta: float) -> None:
        """Add *delta* to :attr:`certainty`, clamped to [0, 1]."""
        self.certainty = round(max(0.0, min(1.0, self.certainty + delta)), 4)


# ---------------------------------------------------------------------------
# Conceptual Memory Entry
# ---------------------------------------------------------------------------

@dataclass
class ConceptualEntry:
    """One entry in the Conceptual Memory layer."""
    concept_id: str                 # unique identifier
    name: str                       # surface label (e.g. "كاتب")
    definition: str = ""            # grounded definition
    grounded_reality: str = ""      # reality type it maps to
    contextual_status: str = "literal"   # "literal" | "metaphorical" | "technical"
    certainty: float = 0.0          # current certainty
    evidence: List[str] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)
    access_count: int = 0

    def update_certainty(self, delta: float) -> None:
        """Add *delta* to :attr:`certainty`, clamped to [0, 1]."""
        self.certainty = round(max(0.0, min(1.0, self.certainty + delta)), 4)


# ---------------------------------------------------------------------------
# Three-Layer Memory
# ---------------------------------------------------------------------------

class ThreeLayerMemory:
    """Structured three-layer epistemological memory.

    Usage::

        mem = ThreeLayerMemory()

        # Store an atomic entry
        mem.store_atom("ك", features={...}, role_vector={...})

        # Store a root relation
        mem.store_relation("root:كتب", "root", "كتب", certainty=0.90,
                           field_label="تدوين", patterns=["فاعل", "مفعول"])

        # Store a verified concept
        mem.store_concept("c-katib", "كاتب",
                          definition="من قام بفعل الكتابة",
                          certainty=0.84)

        # Retrieve
        entry = mem.get_relation("root:كتب")
        concept = mem.get_concept("c-katib")

        # Update in learner mode
        mem.update_relation_certainty("root:كتب", delta=+0.05)

        # Mark weak
        mem.mark_relation_weak("root:كتب")
    """

    def __init__(self) -> None:
        self._atomic: Dict[str, AtomicEntry] = {}
        self._relational: Dict[str, RelationalEntry] = {}
        self._conceptual: Dict[str, ConceptualEntry] = {}

    # ------------------------------------------------------------------
    # Atomic layer
    # ------------------------------------------------------------------

    def store_atom(
        self,
        symbol: str,
        features: Optional[Dict[str, Any]] = None,
        role_vector: Optional[Dict[str, float]] = None,
    ) -> AtomicEntry:
        """Store or update an atomic entry for *symbol*."""
        cp = ord(symbol)
        if symbol not in self._atomic:
            self._atomic[symbol] = AtomicEntry(
                symbol=symbol,
                unicode_codepoint=cp,
                features=features or {},
                role_vector=role_vector or {},
            )
        else:
            entry = self._atomic[symbol]
            if features:
                entry.features.update(features)
            if role_vector:
                entry.role_vector.update(role_vector)
        self._atomic[symbol].access_count += 1
        return self._atomic[symbol]

    def get_atom(self, symbol: str) -> Optional[AtomicEntry]:
        """Retrieve the atomic entry for *symbol*, or None."""
        entry = self._atomic.get(symbol)
        if entry:
            entry.access_count += 1
        return entry

    # ------------------------------------------------------------------
    # Relational layer
    # ------------------------------------------------------------------

    def store_relation(
        self,
        entry_id: str,
        entry_type: str,
        surface: str,
        *,
        description: str = "",
        field_label: str = "",
        patterns: Optional[List[str]] = None,
        certainty: float = 0.0,
        evidence: Optional[List[str]] = None,
    ) -> RelationalEntry:
        """Store or update a relational entry."""
        if entry_id not in self._relational:
            self._relational[entry_id] = RelationalEntry(
                entry_id=entry_id,
                entry_type=entry_type,
                surface=surface,
                description=description,
                field_label=field_label,
                patterns=patterns or [],
                certainty=certainty,
                evidence=evidence or [],
            )
        else:
            rel = self._relational[entry_id]
            if certainty > rel.certainty:
                rel.certainty = round(certainty, 4)
            if evidence:
                rel.evidence.extend(
                    e for e in evidence if e not in rel.evidence
                )
            if patterns:
                rel.patterns.extend(
                    p for p in patterns if p not in rel.patterns
                )
        self._relational[entry_id].access_count += 1
        return self._relational[entry_id]

    def get_relation(self, entry_id: str) -> Optional[RelationalEntry]:
        """Retrieve a relational entry by *entry_id*, or None."""
        entry = self._relational.get(entry_id)
        if entry:
            entry.access_count += 1
        return entry

    def update_relation_certainty(self, entry_id: str, delta: float) -> bool:
        """Adjust the certainty of a relational entry by *delta*.  Returns True on success."""
        entry = self._relational.get(entry_id)
        if entry is None:
            return False
        entry.update_certainty(delta)
        return True

    def mark_relation_weak(self, entry_id: str, threshold: float = 0.30) -> None:
        """Lower the relation certainty to *threshold* if it exceeds it."""
        entry = self._relational.get(entry_id)
        if entry and entry.certainty > threshold:
            entry.certainty = round(threshold, 4)

    # ------------------------------------------------------------------
    # Conceptual layer
    # ------------------------------------------------------------------

    def store_concept(
        self,
        concept_id: str,
        name: str,
        *,
        definition: str = "",
        grounded_reality: str = "",
        contextual_status: str = "literal",
        certainty: float = 0.0,
        evidence: Optional[List[str]] = None,
        related_concepts: Optional[List[str]] = None,
    ) -> ConceptualEntry:
        """Store or update a conceptual entry."""
        if concept_id not in self._conceptual:
            self._conceptual[concept_id] = ConceptualEntry(
                concept_id=concept_id,
                name=name,
                definition=definition,
                grounded_reality=grounded_reality,
                contextual_status=contextual_status,
                certainty=certainty,
                evidence=evidence or [],
                related_concepts=related_concepts or [],
            )
        else:
            cpt = self._conceptual[concept_id]
            if certainty > cpt.certainty:
                cpt.certainty = round(certainty, 4)
            if definition:
                cpt.definition = definition
            if evidence:
                cpt.evidence.extend(
                    e for e in evidence if e not in cpt.evidence
                )
        self._conceptual[concept_id].access_count += 1
        return self._conceptual[concept_id]

    def get_concept(self, concept_id: str) -> Optional[ConceptualEntry]:
        """Retrieve a conceptual entry by *concept_id*, or None."""
        entry = self._conceptual.get(concept_id)
        if entry:
            entry.access_count += 1
        return entry

    def update_concept_certainty(self, concept_id: str, delta: float) -> bool:
        """Adjust the certainty of a concept by *delta*.  Returns True on success."""
        entry = self._conceptual.get(concept_id)
        if entry is None:
            return False
        entry.update_certainty(delta)
        return True

    def mark_concept_weak(self, concept_id: str, threshold: float = 0.30) -> None:
        """Lower the concept certainty to *threshold* if it exceeds it."""
        entry = self._conceptual.get(concept_id)
        if entry and entry.certainty > threshold:
            entry.certainty = round(threshold, 4)

    # ------------------------------------------------------------------
    # Snapshot / export
    # ------------------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """Return a JSON-serializable snapshot of all three memory layers."""
        return {
            "atomic": {
                sym: {
                    "symbol": e.symbol,
                    "unicode": f"U+{e.unicode_codepoint:04X}",
                    "access_count": e.access_count,
                }
                for sym, e in self._atomic.items()
            },
            "relational": {
                eid: {
                    "type": e.entry_type,
                    "surface": e.surface,
                    "description": e.description,
                    "field_label": e.field_label,
                    "certainty": e.certainty,
                    "patterns": e.patterns,
                    "evidence": e.evidence,
                    "access_count": e.access_count,
                }
                for eid, e in self._relational.items()
            },
            "conceptual": {
                cid: {
                    "name": c.name,
                    "definition": c.definition,
                    "grounded_reality": c.grounded_reality,
                    "certainty": c.certainty,
                    "status": c.contextual_status,
                    "evidence": c.evidence,
                    "access_count": c.access_count,
                }
                for cid, c in self._conceptual.items()
            },
        }

    @property
    def atom_count(self) -> int:
        return len(self._atomic)

    @property
    def relation_count(self) -> int:
        return len(self._relational)

    @property
    def concept_count(self) -> int:
        return len(self._conceptual)
