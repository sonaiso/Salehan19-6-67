"""ContextualPatternResolver — resolves ambiguous Arabic words using context.

Many Arabic words are structurally ambiguous: the same surface form can map
to multiple pattern/root combinations with different meanings.  This resolver
applies heuristic context signals to select the most likely reading.

Key ambiguous words handled:
  عَيْن  — eye | spring | spy | essence/self | gold
  مَكتَب — place/office | institution | instrument (contextual)
  مَغرِب — prayer time | direction West | country Morocco
  عِلم   — knowledge | flag/banner
  عامِل  — agent/doer | employee | cause/factor
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "morphosemantics"


@dataclass
class ContextualResolution:
    word: str
    candidate_meanings: list[dict]
    context_selected_meaning: str
    confidence: float
    required_context: list[str]
    certainty_policy: str

    def to_dict(self) -> dict:
        return {
            "word": self.word,
            "candidate_meanings": self.candidate_meanings,
            "context_selected_meaning": self.context_selected_meaning,
            "confidence": self.confidence,
            "required_context": self.required_context,
            "certainty_policy": self.certainty_policy,
        }


# Built-in disambiguation table
_AMBIGUOUS: dict[str, list[dict]] = {
    "عَيْن": [
        {"meaning": "عضو الإبصار", "domain": "anatomy", "context_signal": ["جَسَد", "رُؤية", "نَظَر"], "weight": 0.4},
        {"meaning": "عَين الماء", "domain": "geography", "context_signal": ["ماء", "نَبع", "وادي"], "weight": 0.2},
        {"meaning": "جاسوس", "domain": "social", "context_signal": ["تَجَسُّس", "حَرب", "سِر"], "weight": 0.15},
        {"meaning": "ذات وجوهر", "domain": "philosophy", "context_signal": ["فَلسَفة", "وُجود", "هُوِيَّة"], "weight": 0.15},
        {"meaning": "نَقد ذَهَبي", "domain": "commerce", "context_signal": ["مال", "تِجارة", "ذَهَب"], "weight": 0.1},
    ],
    "عين": [
        {"meaning": "عضو الإبصار", "domain": "anatomy", "context_signal": ["جَسَد", "رُؤية", "نَظَر"], "weight": 0.4},
        {"meaning": "عَين الماء", "domain": "geography", "context_signal": ["ماء", "نَبع", "وادي"], "weight": 0.2},
        {"meaning": "جاسوس", "domain": "social", "context_signal": ["تَجَسُّس", "حَرب", "سِر"], "weight": 0.15},
        {"meaning": "ذات وجوهر", "domain": "philosophy", "context_signal": ["فَلسَفة", "وُجود", "هُوِيَّة"], "weight": 0.15},
        {"meaning": "نَقد ذَهَبي", "domain": "commerce", "context_signal": ["مال", "تِجارة", "ذَهَب"], "weight": 0.1},
    ],
    "مَكتَب": [
        {"meaning": "مكان العمل المكتبي", "domain": "place", "context_signal": ["مَكان", "مَوظَّف", "عَمَل"], "weight": 0.6},
        {"meaning": "مؤسسة", "domain": "institution", "context_signal": ["مُنظَّمة", "إدارة", "رَسمي"], "weight": 0.3},
        {"meaning": "آلة كتابة (السياق)", "domain": "instrument", "context_signal": ["آلة", "حاسوب", "طابِعة"], "weight": 0.1},
    ],
    "مكتب": [
        {"meaning": "مكان العمل المكتبي", "domain": "place", "context_signal": ["مَكان", "مَوظَّف", "عَمَل"], "weight": 0.6},
        {"meaning": "مؤسسة", "domain": "institution", "context_signal": ["مُنظَّمة", "إدارة", "رَسمي"], "weight": 0.3},
        {"meaning": "آلة كتابة (السياق)", "domain": "instrument", "context_signal": ["آلة", "حاسوب", "طابِعة"], "weight": 0.1},
    ],
    "مَغرِب": [
        {"meaning": "وقت صلاة المغرب", "domain": "temporal", "context_signal": ["صَلاة", "وَقت", "أذان"], "weight": 0.4},
        {"meaning": "الجهة الغربية", "domain": "spatial", "context_signal": ["اتِّجاه", "شَرق", "غَرب"], "weight": 0.3},
        {"meaning": "دولة المغرب", "domain": "geographical", "context_signal": ["بَلَد", "دَولة", "أفريقيا"], "weight": 0.3},
    ],
    "مغرب": [
        {"meaning": "وقت صلاة المغرب", "domain": "temporal", "context_signal": ["صَلاة", "وَقت", "أذان"], "weight": 0.4},
        {"meaning": "الجهة الغربية", "domain": "spatial", "context_signal": ["اتِّجاه", "شَرق", "غَرب"], "weight": 0.3},
        {"meaning": "دولة المغرب", "domain": "geographical", "context_signal": ["بَلَد", "دَولة", "أفريقيا"], "weight": 0.3},
    ],
    "عِلم": [
        {"meaning": "المعرفة والعلوم", "domain": "cognitive", "context_signal": ["مَعرِفة", "بَحث", "دِراسة"], "weight": 0.8},
        {"meaning": "الراية والعَلَم", "domain": "artifact", "context_signal": ["راية", "دَولة", "رَفَع"], "weight": 0.2},
    ],
    "علم": [
        {"meaning": "المعرفة والعلوم", "domain": "cognitive", "context_signal": ["مَعرِفة", "بَحث", "دِراسة"], "weight": 0.8},
        {"meaning": "الراية والعَلَم", "domain": "artifact", "context_signal": ["راية", "دَولة", "رَفَع"], "weight": 0.2},
    ],
    "عامِل": [
        {"meaning": "الفاعل النحوي", "domain": "grammar", "context_signal": ["نَحو", "إعراب", "فاعِل"], "weight": 0.3},
        {"meaning": "الموظف العامل", "domain": "social", "context_signal": ["عَمَل", "وَظيفة", "مَصنَع"], "weight": 0.4},
        {"meaning": "السبب والعامل", "domain": "logical", "context_signal": ["سَبَب", "تَأثير", "نَتيجة"], "weight": 0.3},
    ],
    "عامل": [
        {"meaning": "الفاعل النحوي", "domain": "grammar", "context_signal": ["نَحو", "إعراب", "فاعِل"], "weight": 0.3},
        {"meaning": "الموظف العامل", "domain": "social", "context_signal": ["عَمَل", "وَظيفة", "مَصنَع"], "weight": 0.4},
        {"meaning": "السبب والعامل", "domain": "logical", "context_signal": ["سَبَب", "تَأثير", "نَتيجة"], "weight": 0.3},
    ],
}


class ContextualPatternResolver:
    """Resolves ambiguous Arabic pattern readings using context signals."""

    def __init__(self) -> None:
        self._data: dict[str, list[dict]] = dict(_AMBIGUOUS)
        self._load()

    def _load(self) -> None:
        path = _DATA_DIR / "contextual_pattern_examples_ar.jsonl"
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    d = json.loads(line)
                    word = d.get("word", "")
                    candidates = d.get("candidates", [])
                    if word and candidates:
                        self._data.setdefault(word, candidates)
        except (FileNotFoundError, json.JSONDecodeError, TypeError):
            pass

    def resolve(self, word: str, context_tokens: Optional[list[str]] = None) -> ContextualResolution:
        candidates = self._data.get(word, [])
        if not candidates:
            return ContextualResolution(
                word=word,
                candidate_meanings=[],
                context_selected_meaning=word,
                confidence=0.5,
                required_context=[],
                certainty_policy="unknown",
            )

        context_tokens = context_tokens or []
        best_candidate = candidates[0]
        best_score = 0.0

        for cand in candidates:
            base_weight = cand.get("weight", 0.0)
            signals = cand.get("context_signal", [])
            matches = sum(1 for sig in signals for tok in context_tokens if sig in tok or tok in sig)
            score = base_weight + matches * 0.2
            if score > best_score:
                best_score = score
                best_candidate = cand

        required = best_candidate.get("context_signal", [])
        return ContextualResolution(
            word=word,
            candidate_meanings=[{"meaning": c["meaning"], "domain": c["domain"]} for c in candidates],
            context_selected_meaning=best_candidate["meaning"],
            confidence=min(1.0, best_score),
            required_context=required,
            certainty_policy="samai" if len(candidates) > 2 else "qiyasi",
        )

    def is_ambiguous(self, word: str) -> bool:
        return word in self._data and len(self._data[word]) > 1
