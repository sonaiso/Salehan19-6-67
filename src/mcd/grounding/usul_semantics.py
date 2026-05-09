"""UsulSemantics — advanced Arabic usul al-fiqh semantic analysis."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class DalalahType(str, Enum):
    MUTABAQA = "mutabaqa"
    TADAMMUN = "tadammun"
    ILTIZAM = "iltizam"


class IltizamType(str, Enum):
    LOGICAL = "logical"
    EMPIRICAL = "empirical"
    LINGUISTIC = "linguistic"
    CUSTOMARY = "customary"
    METAPHORICAL = "metaphorical"
    WEAK_ASSOCIATION = "weak_association"


class GeneralityLevel(str, Enum):
    AAM = "aam"
    KHAS = "khas"
    MUTLAQ = "mutlaq"
    MUQAYYAD = "muqayyad"


class TruthMetaphor(str, Enum):
    HAQIQAH = "haqiqah"
    MAJAZ = "majaz"


@dataclass
class UsulSemanticFrame:
    dal: str
    madlul: str
    dalalah_type: DalalahType
    mantuq: str = ""
    mafhum: str = ""
    generality: GeneralityLevel = GeneralityLevel.MUTLAQ
    restriction: str = ""
    truth_or_metaphor: TruthMetaphor = TruthMetaphor.HAQIQAH
    illah: Optional[str] = None
    qiyas_candidate: bool = False
    certainty: float = 0.5
    warnings: list[str] = field(default_factory=list)


# Named constants
_INITIAL_CERTAINTY = 0.7


class AdvancedArabicUsulSemantics:
    """Rule-based usul al-fiqh semantic analyzer."""

    # Weak iltizam types that don't serve as strong evidence
    _WEAK_ILTIZAM = {IltizamType.METAPHORICAL, IltizamType.WEAK_ASSOCIATION, IltizamType.CUSTOMARY}
    # Strong iltizam types
    _STRONG_ILTIZAM = {IltizamType.LOGICAL, IltizamType.EMPIRICAL}

    def analyze(
        self,
        dal: str,
        madlul: str,
        context: str = "",
        dalalah_type: DalalahType = DalalahType.MUTABAQA,
        iltizam_type: Optional[IltizamType] = None,
        generality: GeneralityLevel = GeneralityLevel.MUTLAQ,
        restriction: str = "",
        illah: Optional[str] = None,
        qiyas_requested: bool = False,
        truth_or_metaphor: TruthMetaphor = TruthMetaphor.HAQIQAH,
        mantuq: str = "",
        mafhum: str = "",
    ) -> UsulSemanticFrame:
        warnings: list[str] = []
        certainty = _INITIAL_CERTAINTY
        effective_generality = generality
        effective_qiyas = qiyas_requested

        # Rule: qiyas requires illah
        if qiyas_requested:
            if not illah:
                warnings.append("qiyas_without_illah")
                effective_qiyas = False
                certainty -= 0.15
            else:
                certainty += 0.05

        # Rule: iltizam strength affects certainty
        if dalalah_type == DalalahType.ILTIZAM and iltizam_type is not None:
            if iltizam_type in self._WEAK_ILTIZAM:
                warnings.append("weak_iltizam_evidence")
                certainty -= 0.2
            elif iltizam_type in self._STRONG_ILTIZAM:
                certainty += 0.1

        # Rule: aam becomes khas when restriction is present
        if generality == GeneralityLevel.AAM and restriction:
            effective_generality = GeneralityLevel.KHAS
            warnings.append("aam_restricted_to_khas")

        # Rule: mutlaq becomes muqayyad when restriction is present
        if generality == GeneralityLevel.MUTLAQ and restriction:
            effective_generality = GeneralityLevel.MUQAYYAD

        # Rule: majaz lowers certainty
        if truth_or_metaphor == TruthMetaphor.MAJAZ:
            certainty -= 0.1
            warnings.append("majaz_usage_detected")

        certainty = max(0.0, min(1.0, certainty))

        return UsulSemanticFrame(
            dal=dal,
            madlul=madlul,
            dalalah_type=dalalah_type,
            mantuq=mantuq,
            mafhum=mafhum,
            generality=effective_generality,
            restriction=restriction,
            truth_or_metaphor=truth_or_metaphor,
            illah=illah,
            qiyas_candidate=effective_qiyas,
            certainty=certainty,
            warnings=warnings,
        )
