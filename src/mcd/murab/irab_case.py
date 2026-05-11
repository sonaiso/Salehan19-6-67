"""IrabCase — dataclass and registry for Arabic grammatical cases."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class IrabCase:
    case_id: str
    name_ar: str
    name_en: str
    grammatical_function: str
    common_roles: list[str] = field(default_factory=list)
    possible_markers: list[str] = field(default_factory=list)
    semantic_projection: str = ""
    certainty_effect: str = "neutral"

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "name_ar": self.name_ar,
            "name_en": self.name_en,
            "grammatical_function": self.grammatical_function,
            "common_roles": self.common_roles,
            "possible_markers": self.possible_markers,
            "semantic_projection": self.semantic_projection,
            "certainty_effect": self.certainty_effect,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "IrabCase":
        return cls(**d)


_CASES: list[IrabCase] = [
    IrabCase(
        case_id="nominative",
        name_ar="رفع",
        name_en="Nominative",
        grammatical_function="marks subject, predicate, and mubtada",
        common_roles=["فاعل", "نائب فاعل", "مبتدأ", "خبر", "اسم كان", "خبر إن"],
        possible_markers=["damma", "waw", "alif", "nun"],
        semantic_projection="agent_or_subject",
        certainty_effect="raises_syntactic",
    ),
    IrabCase(
        case_id="accusative",
        name_ar="نصب",
        name_en="Accusative",
        grammatical_function="marks object, circumstantial, and khabar-kana",
        common_roles=["مفعول به", "مفعول مطلق", "مفعول لأجله", "مفعول فيه",
                      "مفعول معه", "حال", "تمييز", "مستثنى", "خبر كان", "اسم إن"],
        possible_markers=["fatha", "ya", "alif", "deleted_nun"],
        semantic_projection="patient_or_complement",
        certainty_effect="raises_syntactic",
    ),
    IrabCase(
        case_id="genitive",
        name_ar="جر",
        name_en="Genitive",
        grammatical_function="marks possession and prepositional objects",
        common_roles=["اسم مجرور بحرف جر", "مضاف إليه", "تابع مجرور"],
        possible_markers=["kasra", "ya", "fatha"],
        semantic_projection="possessor_or_oblique",
        certainty_effect="raises_syntactic",
    ),
    IrabCase(
        case_id="jussive",
        name_ar="جزم",
        name_en="Jussive",
        grammatical_function="marks negated or conditional imperfect verbs",
        common_roles=["فعل مضارع مجزوم", "فعل شرط", "جواب شرط"],
        possible_markers=["sukun", "deleted_nun", "deleted_weak_letter"],
        semantic_projection="verbal_mood",
        certainty_effect="raises_syntactic",
    ),
    IrabCase(
        case_id="indeclinable_local",
        name_ar="محلي",
        name_en="Indeclinable (local)",
        grammatical_function="marks words that cannot be inflected externally",
        common_roles=["اسم مبني", "فعل ماضٍ", "فعل أمر"],
        possible_markers=["local"],
        semantic_projection="fixed",
        certainty_effect="neutral",
    ),
    IrabCase(
        case_id="estimated",
        name_ar="تقديري",
        name_en="Estimated",
        grammatical_function="marker not visible due to word shape",
        common_roles=["مقصور", "منقوص", "مضاف إلى ياء المتكلم"],
        possible_markers=["estimated"],
        semantic_projection="inferred",
        certainty_effect="slightly_lower",
    ),
]


class IrabCaseRegistry:
    def __init__(self) -> None:
        self._store: dict[str, IrabCase] = {c.case_id: c for c in _CASES}

    def get(self, case_id: str) -> IrabCase | None:
        return self._store.get(case_id)

    def all(self) -> list[IrabCase]:
        return list(self._store.values())


# Module-level singleton
IRAB_CASE_REGISTRY = IrabCaseRegistry()


# Backward-compatible loader used by existing tests
def load_irab_case_registry() -> dict[str, "IrabCase"]:
    """Return a dict of case_id → IrabCase for backward compatibility."""
    return {c.case_id: c for c in IRAB_CASE_REGISTRY.all()}
