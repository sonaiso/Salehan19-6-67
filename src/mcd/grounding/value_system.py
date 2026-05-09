"""ValueSystem — models epistemic, practical, aesthetic, shari, and social values."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ValueType(str, Enum):
    EPISTEMIC = "epistemic"   # صحيح / خطأ
    PRACTICAL = "practical"   # نافع / ضار
    AESTHETIC = "aesthetic"   # جميل / قبيح
    SHARI = "shari"           # واجب / حرام / مندوب / مكروه / مباح
    SOCIAL = "social"         # مقبول / مرفوض


class JudgmentType(str, Enum):
    CORRECT = "correct"
    WRONG = "wrong"
    BENEFICIAL = "beneficial"
    HARMFUL = "harmful"
    BEAUTIFUL = "beautiful"
    UGLY = "ugly"
    WAJIB = "wajib"
    HARAM = "haram"
    MANDUB = "mandub"
    MAKRUH = "makruh"
    MUBAH = "mubah"
    ACCEPTABLE = "acceptable"
    REJECTED = "rejected"
    UNKNOWN = "unknown"


@dataclass
class ValueFrame:
    value: str
    value_type: ValueType
    domain: str
    measure: str
    evidence_type: str
    judgment_type: JudgmentType
    certainty: float = 0.5
    warnings: list[str] = field(default_factory=list)


# Mapping terms to (value_type, judgment_type, evidence_type)
_TERM_MAP: dict[str, tuple[ValueType, JudgmentType, str]] = {
    "ضار":       (ValueType.PRACTICAL, JudgmentType.HARMFUL,     "empirical"),
    "ضارًا":     (ValueType.PRACTICAL, JudgmentType.HARMFUL,     "empirical"),
    "ضارة":      (ValueType.PRACTICAL, JudgmentType.HARMFUL,     "empirical"),
    "نافع":      (ValueType.PRACTICAL, JudgmentType.BENEFICIAL,  "empirical"),
    "نافعًا":    (ValueType.PRACTICAL, JudgmentType.BENEFICIAL,  "empirical"),
    "نافعة":     (ValueType.PRACTICAL, JudgmentType.BENEFICIAL,  "empirical"),
    "حرام":      (ValueType.SHARI,     JudgmentType.HARAM,       "revelation"),
    "محرم":      (ValueType.SHARI,     JudgmentType.HARAM,       "revelation"),
    "واجب":      (ValueType.SHARI,     JudgmentType.WAJIB,       "revelation"),
    "مندوب":     (ValueType.SHARI,     JudgmentType.MANDUB,      "revelation"),
    "مكروه":     (ValueType.SHARI,     JudgmentType.MAKRUH,      "revelation"),
    "مباح":      (ValueType.SHARI,     JudgmentType.MUBAH,       "revelation"),
    "جائز":      (ValueType.SHARI,     JudgmentType.MUBAH,       "revelation"),
    "صحيح":      (ValueType.EPISTEMIC, JudgmentType.CORRECT,     "logical"),
    "خطأ":       (ValueType.EPISTEMIC, JudgmentType.WRONG,       "logical"),
    "جميل":      (ValueType.AESTHETIC, JudgmentType.BEAUTIFUL,   "aesthetic"),
    "قبيح":      (ValueType.AESTHETIC, JudgmentType.UGLY,        "aesthetic"),
    "مقبول":     (ValueType.SOCIAL,    JudgmentType.ACCEPTABLE,  "social"),
    "مرفوض":     (ValueType.SOCIAL,    JudgmentType.REJECTED,    "social"),
}

# Common subjects we track
_SUBJECT_KEYWORDS = {
    "الكذب", "الصدق", "الظلم", "العدل", "الفساد", "الغش", "الأمانة",
    "السرقة", "الزنا", "القتل", "الشرك", "الكبائر",
}


class ValueSystemModel:
    """Extracts value frames from Arabic text."""

    def analyze(self, text: str) -> list[ValueFrame]:
        words = text.replace("؟", "").replace("،", "").replace(".", "").split()
        frames: list[ValueFrame] = []

        # Find subject
        subject = ""
        for word in words:
            if any(kw in word for kw in _SUBJECT_KEYWORDS):
                subject = word
                break
        if not subject:
            subject = words[0] if words else "غير محدد"

        # Detect value judgments
        for word in words:
            if word in _TERM_MAP:
                value_type, judgment, evidence_type = _TERM_MAP[word]
                frame_warnings: list[str] = []
                certainty = 0.6

                # Shari judgment needs revelation evidence
                if value_type == ValueType.SHARI:
                    frame_warnings.append("shari_needs_revelation_evidence")
                    certainty = 0.4  # lower without actual revelation evidence

                frames.append(ValueFrame(
                    value=subject,
                    value_type=value_type,
                    domain=value_type.value,
                    measure=word,
                    evidence_type=evidence_type,
                    judgment_type=judgment,
                    certainty=certainty,
                    warnings=frame_warnings,
                ))

        return frames
