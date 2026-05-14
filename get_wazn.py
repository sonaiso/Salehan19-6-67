# -*- coding: utf-8 -*-
"""
get_wazn.py — يأخذ كلمة عربية مشكولة ويُرجع وزنها.
"""

import sys
import argparse

sys.path.insert(0, '.')
import match_wazn as m

DEFAULT_AWZAN_PATH = "data/awzan_cleaned.csv"
_AWZAN_DB = None


def load_db(path=None):
    global _AWZAN_DB
    if _AWZAN_DB is None or path is not None:
        _AWZAN_DB = m.load_awzan(path or DEFAULT_AWZAN_PATH)
    return _AWZAN_DB


def get_letters_only(text):
    return [c for c in text if c in m.ARABIC_LETTERS]


ROOT_PLACEHOLDERS = ("ف", "ع", "ل")


def extract_root(word, wazn):
    word_letters = get_letters_only(word)
    wazn_letters = get_letters_only(wazn)

    if len(word_letters) == len(wazn_letters):
        root = []
        for wl, zl in zip(word_letters, wazn_letters):
            if zl in ROOT_PLACEHOLDERS:
                root.append(wl)
        if root:
            return root

    base_word, _ = m.strip_suffix(word)
    if base_word != word:
        base_letters = get_letters_only(base_word)
        if len(base_letters) == len(wazn_letters):
            root = []
            for wl, zl in zip(base_letters, wazn_letters):
                if zl in ROOT_PLACEHOLDERS:
                    root.append(wl)
            if root:
                return root

    stripped = m.strip_al(word)
    if stripped != word:
        return extract_root(stripped, wazn)

    return None


def letter_similarity(word, wazn):
    word_letters = get_letters_only(word)
    wazn_letters = get_letters_only(wazn)
    if len(word_letters) != len(wazn_letters):
        return -10000
    score = 0
    for wl, zl in zip(word_letters, wazn_letters):
        if zl in ROOT_PLACEHOLDERS:
            continue
        if wl == zl:
            score += 1
        else:
            return -10000
    return score


def score_match(entry, word_structure, word=None):
    wazn_struct = entry["structure"]
    flex_count = 0
    for w, s in zip(wazn_struct, word_structure):
        if w == '_' and s != '_':
            flex_count += 1
        if s == '_' and w != '_':
            flex_count += 1

    letter_score = 0
    if word:
        letter_score = letter_similarity(word, entry["wazn"])

    underscores_in_wazn = wazn_struct.count('_')
    return (flex_count, -letter_score, underscores_in_wazn, len(wazn_struct))


def get_wazn(word, all_matches=False, awzan_path=None):
    db = load_db(awzan_path)
    matches, structure = m.find_matching_awzan(word, db)

    if not matches:
        return [] if all_matches else None

    sorted_matches = sorted(matches, key=lambda e: score_match(e, structure, word))

    enriched = []
    for entry in sorted_matches:
        root = extract_root(word, entry["wazn"])
        enriched.append({
            "wazn": entry["wazn"],
            "root": root,
            "example": entry["example"],
            "structure": entry["structure"],
        })

    if all_matches:
        return enriched

    return enriched[0]


def main():
    parser = argparse.ArgumentParser(description="أرجع وزن كلمة عربية مشكولة")
    parser.add_argument("words", nargs="*", help="كلمة أو كلمات للتحليل")
    parser.add_argument("--all", action="store_true", help="عرض كل الأوزان المطابقة")
    parser.add_argument("--awzan", default=DEFAULT_AWZAN_PATH, help="مسار ملف الأوزان")
    args = parser.parse_args()

    if args.words:
        words = args.words
    elif not sys.stdin.isatty():
        words = sys.stdin.read().split()
    else:
        print("الاستخدام: python3 get_wazn.py \"كَتَبَ\"")
        return

    db = load_db(args.awzan)

    for word in words:
        clean = word.strip(".,!?؟،;:()[]\"'")
        if not clean:
            continue

        matches, structure = m.find_matching_awzan(clean, db)

        if not matches:
            print(f"{clean}  →  لا يوجد وزن مطابق")
            continue

        sorted_matches = sorted(matches, key=lambda e: score_match(e, structure, clean))

        if args.all:
            print(f"\n{clean}  (بنية: {''.join(structure)})")
            for entry in sorted_matches:
                root = extract_root(clean, entry["wazn"])
                root_str = "-".join(root) if root else "؟"
                print(f"  . وزن: {entry['wazn']:<15s}  جذر: ({root_str})   مثال: {entry['example']}")
        else:
            best = sorted_matches[0]
            root = extract_root(clean, best["wazn"])
            root_str = "-".join(root) if root else "؟"
            print(f"{clean}  ->  وزن: {best['wazn']}   جذر: ({root_str})   (مثال: {best['example']})")


if __name__ == "__main__":
    main()
