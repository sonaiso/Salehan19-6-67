"""MorphosemanticPatternMiner — mines morphosemantic patterns from word lists.

Given a list of Arabic words, this miner groups them by root family, assigns
pattern operators, and produces a frequency-weighted pattern map suitable for
downstream statistical or linguistic analysis.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import defaultdict
from typing import Optional

from mcd.morphosemantics.morphosemantic_trace_linker import MorphosemanticTraceLinker, _KNOWN_WORDS
from mcd.morphosemantics.pattern_operator_registry import PatternOperatorRegistry


@dataclass
class PatternFrequency:
    pattern_id: str
    pattern_form: str
    count: int
    root_ids: list[str]
    words: list[str]

    def to_dict(self) -> dict:
        return {
            "pattern_id": self.pattern_id,
            "pattern_form": self.pattern_form,
            "count": self.count,
            "root_ids": self.root_ids,
            "words": self.words,
        }


@dataclass
class MiningResult:
    total_words: int
    linked_words: int
    pattern_frequencies: list[PatternFrequency]
    root_family_map: dict[str, list[str]]  # root_id → list of words

    def to_dict(self) -> dict:
        return {
            "total_words": self.total_words,
            "linked_words": self.linked_words,
            "pattern_frequencies": [p.to_dict() for p in self.pattern_frequencies],
            "root_family_map": self.root_family_map,
        }


class MorphosemanticPatternMiner:
    """Mines morphosemantic patterns from an iterable of Arabic words."""

    def __init__(self) -> None:
        self._linker = MorphosemanticTraceLinker()
        self._registry = PatternOperatorRegistry()

    def mine(self, words: list[str]) -> MiningResult:
        pattern_counts: dict[str, list[str]] = defaultdict(list)
        root_family: dict[str, list[str]] = defaultdict(list)
        linked = 0

        for word in words:
            entry = _KNOWN_WORDS.get(word)
            if entry:
                root_id, pattern_id = entry
                pattern_counts[pattern_id].append(word)
                root_family[root_id].append(word)
                linked += 1

        freq_list: list[PatternFrequency] = []
        for pid, wlist in sorted(pattern_counts.items(), key=lambda x: -len(x[1])):
            op = self._registry.get(pid)
            form = op.pattern_form if op else pid
            root_ids = list({_KNOWN_WORDS[w][0] for w in wlist if w in _KNOWN_WORDS})
            freq_list.append(PatternFrequency(
                pattern_id=pid,
                pattern_form=form,
                count=len(wlist),
                root_ids=root_ids,
                words=wlist,
            ))

        return MiningResult(
            total_words=len(words),
            linked_words=linked,
            pattern_frequencies=freq_list,
            root_family_map={k: list(v) for k, v in root_family.items()},
        )
