"""EstimatedIrabEngine — handles Arabic إعراب تقديري (estimated I'rab)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class EstimatedType(str, Enum):
    MAQSUR = "maqsur"      # مقصور - ends in alif (تعذر)
    MANQUS = "manqus"      # منقوص - ends in ya' (ثقل)
    MUDAF_TO_YA = "mudaf_to_ya"  # مضاف إلى ياء المتكلم


@dataclass
class EstimatedIrabResult:
    surface: str
    estimated_type: EstimatedType
    reason: str  # تعذر|ثقل|اشتغال المحل
    irab_case: str
    irab_marker: str
    marker_visibility: str  # always "estimated"
    certainty: float

    def to_dict(self) -> dict:
        return {
            "surface": self.surface,
            "estimated_type": self.estimated_type.value,
            "reason": self.reason,
            "irab_case": self.irab_case,
            "irab_marker": self.irab_marker,
            "marker_visibility": self.marker_visibility,
            "certainty": self.certainty,
        }


class EstimatedIrabEngine:
    """Handles estimated I'rab for مقصور، منقوص، مضاف إلى ياء المتكلم."""

    ALIF_MAQSURA = '\u0649'  # ى
    ALIF = '\u0627'          # ا
    YA = '\u064a'            # ي

    def analyze(self, surface: str, irab_case: str) -> EstimatedIrabResult:
        """Analyze if surface has estimated I'rab."""
        stripped = self._strip_diacritics(surface)

        if stripped.endswith('ي') and len(stripped) > 2:
            return EstimatedIrabResult(
                surface=surface,
                estimated_type=EstimatedType.MUDAF_TO_YA,
                reason="اشتغال المحل بحركة المناسبة",
                irab_case=irab_case,
                irab_marker="estimated",
                marker_visibility="estimated",
                certainty=0.9,
            )

        if stripped.endswith('ى') or (stripped.endswith('ا') and len(stripped) > 2 and not stripped.endswith('ان')):
            return EstimatedIrabResult(
                surface=surface,
                estimated_type=EstimatedType.MAQSUR,
                reason="تعذر",
                irab_case=irab_case,
                irab_marker="estimated",
                marker_visibility="estimated",
                certainty=0.85,
            )

        if stripped.endswith('ي') and irab_case in {"nominative", "genitive"}:
            return EstimatedIrabResult(
                surface=surface,
                estimated_type=EstimatedType.MANQUS,
                reason="ثقل",
                irab_case=irab_case,
                irab_marker="estimated",
                marker_visibility="estimated",
                certainty=0.8,
            )

        return EstimatedIrabResult(
            surface=surface,
            estimated_type=EstimatedType.MAQSUR,
            reason="none",
            irab_case=irab_case,
            irab_marker="apparent",
            marker_visibility="apparent",
            certainty=1.0,
        )

    def _strip_diacritics(self, text: str) -> str:
        diacritics = set('\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652')
        return ''.join(c for c in text if c not in diacritics)
