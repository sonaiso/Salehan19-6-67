"""HumanIndividualModel — models humans as species vs. individuals."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class HumanFrame:
    """Represents the human species level — general truths about humanity."""
    human_as_species: str = "الإنسان"
    mind: str = "عاقل"
    needs: list[str] = field(default_factory=list)
    instincts: list[str] = field(default_factory=list)
    language: str = "لغة"
    sociality: str = "اجتماعي"


@dataclass
class IndividualFrame:
    """Represents a specific individual — context-specific, not generalizable."""
    name: str
    context: str = ""
    knowledge_state: str = ""
    behavior: str = ""
    evidence: list[str] = field(default_factory=list)
    certainty: float = 0.5


class HumanIndividualModel:
    """
    Manages the distinction between human species claims and individual claims.

    Rule: Never apply a ruling about humanity as a whole from a single individual case.
    Generalization from one individual to all humans is an epistemic error.
    """

    def create_human_frame(self) -> HumanFrame:
        return HumanFrame(
            needs=["الغذاء", "الماء", "الأمن", "التواصل"],
            instincts=["الغريزة الجنسية", "غريزة البقاء", "غريزة التدين"],
        )

    def create_individual_frame(
        self,
        name: str,
        context: str = "",
        behavior: str = "",
        knowledge_state: str = "",
        evidence: Optional[list[str]] = None,
    ) -> IndividualFrame:
        return IndividualFrame(
            name=name,
            context=context,
            behavior=behavior,
            knowledge_state=knowledge_state,
            evidence=evidence or [],
            certainty=0.5,
        )

    def can_generalize_to_species(self, individual: IndividualFrame) -> tuple[bool, str]:
        """
        Returns (can_generalize, reason).
        A single individual case never generalizes to all humans.
        """
        return (
            False,
            "القياس من الفرد إلى النوع خطأ معرفي — الفرد الواحد لا يمثّل الجنس البشري",
        )
