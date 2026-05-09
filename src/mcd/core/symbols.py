"""Arabic Unicode symbol constants and character classification helpers."""
from __future__ import annotations

ARABIC_LETTERS_RANGE = (0x0621, 0x064A)
ARABIC_DIACRITICS = set(range(0x064B, 0x0653))
ARABIC_TATWEEL = '\u0640'
ARABIC_ALEF_FORMS = {'أ', 'إ', 'آ', 'ا', 'ى'}
ARABIC_WEAK_LETTERS = {'و', 'ي', 'ى', 'ا'}
ARABIC_HAMZA_FORMS = {'أ', 'إ', 'ؤ', 'ئ', 'ء'}

# Letters that do NOT connect to the left (only connect right)
_RIGHT_ONLY = {'ا', 'أ', 'إ', 'آ', 'ى', 'د', 'ذ', 'ر', 'ز', 'و', 'ء'}

_DIACRITIC_NAMES = {
    '\u064B': 'tanwin_f',
    '\u064C': 'tanwin_d',
    '\u064D': 'tanwin_k',
    '\u064E': 'fatha',
    '\u064F': 'damma',
    '\u0650': 'kasra',
    '\u0651': 'shadda',
    '\u0652': 'sukun',
}

_CHAR_NAMES = {
    'ا': 'alef', 'أ': 'alef_hamza_above', 'إ': 'alef_hamza_below',
    'آ': 'alef_madda', 'ب': 'ba', 'ت': 'ta', 'ث': 'tha',
    'ج': 'jeem', 'ح': 'ha', 'خ': 'kha', 'د': 'dal', 'ذ': 'thal',
    'ر': 'ra', 'ز': 'zain', 'س': 'seen', 'ش': 'sheen',
    'ص': 'sad', 'ض': 'dad', 'ط': 'ta_heavy', 'ظ': 'zha',
    'ع': 'ain', 'غ': 'ghain', 'ف': 'fa', 'ق': 'qaf',
    'ك': 'kaf', 'ل': 'lam', 'م': 'meem', 'ن': 'noon',
    'ه': 'ha_end', 'و': 'waw', 'ي': 'ya', 'ى': 'alef_maqsura',
    'ة': 'ta_marbuta', 'ء': 'hamza', 'ئ': 'ya_hamza', 'ؤ': 'waw_hamza',
}


def is_arabic_letter(ch: str) -> bool:
    return ARABIC_LETTERS_RANGE[0] <= ord(ch) <= ARABIC_LETTERS_RANGE[1] or ch == 'ة'


def is_diacritic(ch: str) -> bool:
    return ord(ch) in ARABIC_DIACRITICS


def is_weak_letter(ch: str) -> bool:
    return ch in ARABIC_WEAK_LETTERS


def is_hamza(ch: str) -> bool:
    return ch in ARABIC_HAMZA_FORMS


def connects_right(ch: str) -> bool:
    return is_arabic_letter(ch)


def connects_left(ch: str) -> bool:
    return is_arabic_letter(ch) and ch not in _RIGHT_ONLY


def char_to_name(ch: str) -> str:
    if ch in _DIACRITIC_NAMES:
        return _DIACRITIC_NAMES[ch]
    return _CHAR_NAMES.get(ch, f'u{ord(ch):04X}')
