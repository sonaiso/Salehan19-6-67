"""Arabic text normalizer."""
from __future__ import annotations

import re
from enum import Enum
from mcd.core.symbols import ARABIC_DIACRITICS, ARABIC_TATWEEL


class NormalizationMode(str, Enum):
    STRICT = "strict"
    LIGHT = "light"
    SEARCH = "search"
    MORPHOLOGICAL = "morphological"


class ArabicNormalizer:

    def normalize(self, text: str, mode: NormalizationMode = NormalizationMode.LIGHT) -> str:
        text = self._remove_tatweel(text)
        text = self._normalize_whitespace(text)

        if mode == NormalizationMode.LIGHT:
            text = self._unify_alef(text)
            text = self._normalize_yeh(text)

        elif mode == NormalizationMode.STRICT:
            text = self._unify_alef(text)
            text = self._normalize_yeh(text)
            text = self._remove_diacritics(text)

        elif mode == NormalizationMode.SEARCH:
            text = self._unify_alef(text)
            text = self._normalize_yeh(text)
            text = self._remove_diacritics(text)

        elif mode == NormalizationMode.MORPHOLOGICAL:
            text = self._unify_alef(text)
            text = self._preserve_hamza(text)

        return text

    def _remove_tatweel(self, text: str) -> str:
        return text.replace(ARABIC_TATWEEL, '')

    def _normalize_whitespace(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip()

    def _unify_alef(self, text: str) -> str:
        return text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')

    def _remove_diacritics(self, text: str) -> str:
        return ''.join(ch for ch in text if ord(ch) not in ARABIC_DIACRITICS)

    def _preserve_hamza(self, text: str) -> str:
        return text  # hamza forms kept as-is in morphological mode

    def _normalize_yeh(self, text: str) -> str:
        return text.replace('ى', 'ي')
