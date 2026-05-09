"""Role inferer: assigns role probabilities to each character."""
from __future__ import annotations

from mcd.core.symbols import is_arabic_letter, is_diacritic, is_weak_letter
from mcd.core.roles import RoleType, RoleVector
from mcd.core.measures import normalize_scores


class RoleInferer:

    def infer_roles(self, word: str, context: list[str] | None = None) -> list[tuple[str, RoleVector]]:
        if not word:
            return []
        prefix, prefix_prob = self._detect_prefix(word)
        suffix, suffix_prob = self._detect_suffix(word)

        # Strip prefix/suffix to get stem
        stem_start = len(prefix)
        stem_end = len(word) - len(suffix) if suffix else len(word)
        stem = word[stem_start:stem_end]

        results: list[tuple[str, RoleVector]] = []

        # Prefix characters
        for i, ch in enumerate(prefix):
            if word[:2] == 'ال' and i < 2:
                rv = RoleVector({"definite_article": prefix_prob, "prefix": 0.1})
            else:
                rv = RoleVector({"prefix": prefix_prob, "functional_particle": 0.2})
            results.append((ch, rv))

        # Stem characters
        stem_roles = self._infer_root_radicals(stem)
        for ch, score in stem_roles:
            if is_diacritic(ch):
                rv = RoleVector({"diacritic_marker": 0.95, "pattern_marker": 0.05})
            elif is_weak_letter(ch):
                rv = RoleVector({"weak_radical": score, "pattern_marker": 1.0 - score})
            else:
                rv = RoleVector({"root_radical": score, "pattern_marker": 1.0 - score})
            results.append((ch, rv))

        # Suffix characters
        for ch in suffix:
            rv = RoleVector({"suffix": suffix_prob, "case_marker": 1.0 - suffix_prob})
            results.append((ch, rv))

        return results

    def _detect_prefix(self, word: str) -> tuple[str, float]:
        if word.startswith('ال') and len(word) > 2:
            return 'ال', 0.95
        if len(word) > 3 and word[0] in ('ب', 'ل', 'ك', 'و', 'ف'):
            return word[0], 0.80
        return '', 0.0

    def _detect_suffix(self, word: str) -> tuple[str, float]:
        if word.endswith('ة') and len(word) > 1:
            return 'ة', 0.92
        if word.endswith('ون') and len(word) > 2:
            return 'ون', 0.90
        if word.endswith('ين') and len(word) > 2:
            return 'ين', 0.88
        if word.endswith('ات') and len(word) > 2:
            return 'ات', 0.85
        return '', 0.0

    def _infer_root_radicals(self, stem: str) -> list[tuple[str, float]]:
        results = []
        letters = [(c, i) for i, c in enumerate(stem) if is_arabic_letter(c)]
        for ch, idx in letters:
            if is_weak_letter(ch):
                score = 0.35
            else:
                score = 0.80
            results.append((ch, score))
        diacritics = [(c, i) for i, c in enumerate(stem) if is_diacritic(c)]
        # merge order
        all_chars = [(c, i, False) for c, i in letters] + [(c, i, True) for c, i in diacritics]
        all_chars.sort(key=lambda x: x[1])
        merged = []
        for ch, idx, is_d in all_chars:
            if is_d:
                merged.append((ch, 0.95))
            else:
                if is_weak_letter(ch):
                    merged.append((ch, 0.35))
                else:
                    merged.append((ch, 0.80))
        return merged
