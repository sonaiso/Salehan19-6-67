# -*- coding: utf-8 -*-
"""
match_wazn.py — مكتبة مساعدة لـ get_wazn.py
تحوّل الكلمة المشكولة إلى بنية CV وتبحث عن المطابقات في قاعدة الأوزان.
"""
import csv, re

# ── الحروف العربية ────────────────────────────────────────────────────────────
ARABIC_LETTERS = set(
    [chr(c) for c in range(0x0621, 0x063B)] +
    [chr(c) for c in range(0x0641, 0x064B)] +
    list("ةىءئؤإأآ")
)

SHORT_VOWELS = {'َ', 'ُ', 'ِ'}   # فتحة، ضمة، كسرة
SUKUN        = 'ْ'                          # سكون
SHADDA       = 'ّ'                          # شدة
TANWIN       = {'ً', 'ٌ', 'ٍ'}    # تنوين
LONG_VOWELS  = set("اويى")
DIACRITICS   = SHORT_VOWELS | {SUKUN, SHADDA} | TANWIN | {'ٓ', 'ٰ'}


# ── بنية CV ───────────────────────────────────────────────────────────────────
def get_cv_structure(word: str) -> str:
    """تحويل كلمة مشكولة إلى بنيتها CV (مثال: كَتَبَ → CVCVCV)."""
    chars = list(word)
    result = []
    prev_was_vowel = False
    i = 0
    while i < len(chars):
        ch = chars[i]

        # تجاهل الحركات مستقلة
        if ch in DIACRITICS:
            i += 1
            continue

        # حرف مد بعد حركة = مطوّل (V إضافية فقط)
        if ch in LONG_VOWELS and prev_was_vowel:
            result.append('V')
            prev_was_vowel = False
            i += 1
            continue

        if ch in ARABIC_LETTERS or ch in LONG_VOWELS:
            result.append('C')
            prev_was_vowel = False

            # نبحث عن الحركة التي تليه
            j = i + 1

            # شدة → حرف مضاعف (شدة قبل الحركة: ل+ّ+َ)
            if j < len(chars) and chars[j] == SHADDA:
                result.append('C')
                j += 1

            # حركة قصيرة أو تنوين
            if j < len(chars) and (chars[j] in SHORT_VOWELS or chars[j] in TANWIN):
                next_j = j + 1
                # شدة بعد الحركة (ل+َ+ّ) — الترميز البديل الشائع
                # المعنى: الحرف مضاعف، والحركة على النسخة الثانية منه
                # فينتج: C (الأولى بلا حركة) + C (الثانية) + V (حركتها) = CCV
                if next_j < len(chars) and chars[next_j] == SHADDA:
                    result.append('C')   # النسخة الثانية من الحرف
                    result.append('V')   # حركتها
                    prev_was_vowel = True
                    i = next_j + 1
                else:
                    result.append('V')
                    prev_was_vowel = True
                    i = j + 1
                continue
            # سكون
            if j < len(chars) and chars[j] == SUKUN:
                prev_was_vowel = False
                i = j + 1
                continue

        i += 1

    return ''.join(result)


# ── تجريد ─────────────────────────────────────────────────────────────────────
def strip_al(word: str) -> str:
    """تجريد أل التعريف."""
    m = re.sub(r'^ال', '', word)
    return m if m else word


def strip_suffix(word: str):
    """تجريد اللاحقات الشائعة. يُرجع (الأساس، اللاحقة)."""
    suffixes = ['ون', 'ين', 'ان', 'ات', 'ة', 'ا', 'ي', 'ك', 'ه',
                'ها', 'هم', 'هن', 'كم', 'كن', 'نا']
    for suf in sorted(suffixes, key=len, reverse=True):
        if word.endswith(suf) and len(word) > len(suf) + 1:
            return word[:-len(suf)], suf
    return word, ''


# ── تحميل قاعدة الأوزان ────────────────────────────────────────────────────────
def load_awzan(path: str) -> list:
    """تحميل قاعدة الأوزان من ملف CSV."""
    db = []
    with open(path, encoding='utf-8', newline='') as f:
        for row in csv.DictReader(f):
            wazn    = row.get('الوزن',    '').strip()
            example = row.get('مثال',     '').strip()
            cv_wazn = row.get('CV_الوزن', '').strip()
            if wazn and cv_wazn:
                db.append({
                    'wazn':      wazn,
                    'example':   example,
                    'structure': list(cv_wazn),
                })
    return db


# ── تطبيع بنية CV ─────────────────────────────────────────────────────────────
def _normalize_structure(structure: list) -> list:
    """
    تزيل V المنفردة في نهاية البنية (حركة الإعراب) لتوافق
    صيغة قاعدة الأوزان التي تُخزَّن بدون حركة نهائية.
    مثال: CVCVCV → CVCVC  |  CVCCVCVC → CVCCVCVC (لا تغيير)
    """
    s = list(structure)
    # نحذف V نهائية منفردة (لا يسبقها V ولا يتبعها C)
    while len(s) >= 2 and s[-1] == 'V' and s[-2] == 'C':
        s.pop()
        break   # نزيل V واحدة فقط
    return s


# ── البحث عن الأوزان المطابقة ──────────────────────────────────────────────────
def find_matching_awzan(word: str, db: list):
    """
    يبحث عن الأوزان التي تطابق بنية CV للكلمة.
    يُرجع (قائمة المطابقات، بنية الكلمة كقائمة).

    يجرّب:
      1. البنية كما هي
      2. البنية بعد حذف V الإعرابية النهائية
      3. البنية بعد تجريد أل + كلا الحالتين السابقتين
    """
    cv        = get_cv_structure(word)
    structure = list(cv)

    # الهياكل التي سنجرّبها بالترتيب
    candidates = [structure, _normalize_structure(structure)]

    # نجرّب أيضاً بعد تجريد أل
    bare = strip_al(word)
    if bare != word:
        bare_cv     = get_cv_structure(bare)
        bare_struct = list(bare_cv)
        candidates += [bare_struct, _normalize_structure(bare_struct)]

    # همزة الوصل: إذا بدأت البنية بـ CC (ا + حرف ساكن) نُدخل V بعد الحرف الأول
    # لأن إِ = CV وليس C فقط: اسْتَخْرَج → إِسْتَخْرَج = CV+C+CV+C+CV+C
    for base_struct in list(candidates):
        if len(base_struct) >= 2 and base_struct[0] == 'C' and base_struct[1] == 'C':
            # نُدخل V بعد الحرف الأول (hamza wasla تحمل كسرة ضمنية)
            wasla_fixed = [base_struct[0], 'V'] + base_struct[1:]
            if wasla_fixed not in candidates:
                candidates.append(wasla_fixed)
            norm_wasla = _normalize_structure(wasla_fixed)
            if norm_wasla not in candidates:
                candidates.append(norm_wasla)

    # نُزيل المكررات مع الحفاظ على الترتيب
    seen = []
    for c in candidates:
        if c not in seen:
            seen.append(c)
    candidates = seen

    matches_found = []
    best_structure = structure   # ما نُرجعه كـ"بنية الكلمة"

    for struct in candidates:
        n = len(struct)
        for entry in db:
            wazn_struct = entry['structure']
            if len(wazn_struct) != n:
                continue
            ok = all(
                w == '_' or s == '_' or w == s
                for w, s in zip(wazn_struct, struct)
            )
            if ok and entry not in matches_found:
                matches_found.append(entry)

        if matches_found:
            best_structure = struct
            break   # وجدنا مطابقات بهذه البنية، نكتفي بها

    return matches_found, best_structure
