"""Arabic morphological pattern matcher."""
from __future__ import annotations

from mcd.core.symbols import is_arabic_letter, is_weak_letter, ARABIC_HAMZA_FORMS

ARABIC_PATTERNS = [
    {"pattern": "فعل",    "template": "CCC",      "role": "verb",          "semantic_hint": "action",           "certainty_base": 0.70},
    {"pattern": "فاعل",   "template": "CACC",     "role": "agent_noun",    "semantic_hint": "doer of action",   "certainty_base": 0.75},
    {"pattern": "مفعول",  "template": "maCCuC",   "role": "passive_noun",  "semantic_hint": "acted upon",       "certainty_base": 0.72},
    {"pattern": "فعيل",   "template": "CaCiC",    "role": "adjective",     "semantic_hint": "quality/intense",  "certainty_base": 0.70},
    {"pattern": "فعلة",   "template": "CaCCa",    "role": "noun_instance", "semantic_hint": "single instance",  "certainty_base": 0.68},
    {"pattern": "مفعلة",  "template": "maCCaCa",  "role": "place_noun",    "semantic_hint": "place of action",  "certainty_base": 0.65},
    {"pattern": "استفعل", "template": "istaFCaL", "role": "verb_x",        "semantic_hint": "seeking/deeming",  "certainty_base": 0.75},
    {"pattern": "تفاعل",  "template": "taFaCaL",  "role": "verb_vi",       "semantic_hint": "mutual action",    "certainty_base": 0.72},
    {"pattern": "افتعل",  "template": "iFtaCaL",  "role": "verb_viii",     "semantic_hint": "reflexive action", "certainty_base": 0.72},
    {"pattern": "انفعل",  "template": "inFaCaL",  "role": "verb_vii",      "semantic_hint": "passive action",   "certainty_base": 0.70},
]

# Map: pattern Arabic letters → root slots (C positions in template)
_PATTERN_STRUCTURES = {
    "فعل":    {"length": 3, "root_positions": [0, 1, 2]},
    "فاعل":   {"length": 4, "root_positions": [0, 2, 3], "fixed": {1: 'ا'}},
    "مفعول":  {"length": 5, "root_positions": [1, 2, 4], "fixed": {0: 'م', 3: 'و'}},
    "فعيل":   {"length": 4, "root_positions": [0, 1, 3], "fixed": {2: 'ي'}},
    "فعلة":   {"length": 4, "root_positions": [0, 1, 2], "fixed": {3: 'ة'}},
    "مفعلة":  {"length": 5, "root_positions": [1, 2, 3], "fixed": {0: 'م', 4: 'ة'}},
    "استفعل": {"length": 6, "root_positions": [3, 4, 5], "fixed": {0: 'ا', 1: 'س', 2: 'ت'}},
    "تفاعل":  {"length": 5, "root_positions": [1, 3, 4], "fixed": {0: 'ت', 2: 'ا'}},
    "افتعل":  {"length": 5, "root_positions": [1, 3, 4], "fixed": {0: 'ا', 2: 'ت'}},
    "انفعل":  {"length": 5, "root_positions": [2, 3, 4], "fixed": {0: 'ا', 1: 'ن'}},
}


def _strip_diacritics(word: str) -> str:
    from mcd.core.symbols import is_diacritic
    return ''.join(c for c in word if not is_diacritic(c))


def _normalize_alef(word: str) -> str:
    return word.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')


class PatternMatcher:

    def match(self, word: str) -> list[dict]:
        clean = _strip_diacritics(word)
        results = []
        for pat in ARABIC_PATTERNS:
            struct = _PATTERN_STRUCTURES.get(pat["pattern"])
            if struct is None:
                continue
            score = self._score_match(clean, struct)
            if score > 0:
                root = self._extract_root_from_pattern(clean, pat["template"])
                results.append({
                    "pattern": pat["pattern"],
                    "template": pat["template"],
                    "role": pat["role"],
                    "semantic_hint": pat["semantic_hint"],
                    "certainty": round(pat["certainty_base"] * score, 3),
                    "root": root or "",
                })
        results.sort(key=lambda x: x["certainty"], reverse=True)
        return results

    def best_match(self, word: str) -> dict | None:
        matches = self.match(word)
        return matches[0] if matches else None

    def _score_match(self, clean_word: str, struct: dict) -> float:
        expected_len = struct["length"]
        fixed = struct.get("fixed", {})

        # Check length
        if len(clean_word) != expected_len:
            # Allow ±1 for some patterns due to normalization
            if abs(len(clean_word) - expected_len) > 1:
                return 0.0
            return 0.3

        score = 1.0
        for pos, expected_char in fixed.items():
            if pos < len(clean_word):
                actual = _normalize_alef(clean_word[pos])
                if actual != _normalize_alef(expected_char):
                    score *= 0.3
            else:
                score *= 0.5

        root_positions = struct["root_positions"]
        root_chars = [clean_word[p] for p in root_positions if p < len(clean_word)]
        # Root chars should be Arabic consonants (not weak letters ideally)
        consonant_ratio = sum(1 for c in root_chars if is_arabic_letter(c) and c not in ('ا', 'و', 'ي', 'ى')) / max(len(root_chars), 1)
        score *= (0.5 + 0.5 * consonant_ratio)
        return score

    def _extract_root_from_pattern(self, clean_word: str, template: str) -> str | None:
        # Find 'C' positions in template (root consonants)
        # Map template chars to word chars
        # Simple: look at the _PATTERN_STRUCTURES root_positions
        for pat in ARABIC_PATTERNS:
            if pat["template"] == template:
                struct = _PATTERN_STRUCTURES.get(pat["pattern"])
                if struct and len(clean_word) == struct["length"]:
                    root_chars = [clean_word[p] for p in struct["root_positions"] if p < len(clean_word)]
                    return ''.join(root_chars)
        # Fallback: extract consonants
        consonants = [c for c in clean_word if is_arabic_letter(c) and c not in ('ا', 'و', 'ي', 'ى', 'م', 'ن', 'ت', 'س')]
        return ''.join(consonants[:3]) if consonants else None
