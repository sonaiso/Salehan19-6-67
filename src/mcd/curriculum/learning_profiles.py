"""Learning profiles for curriculum selection."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LearningProfile:
    name: str
    levels: list[int]
    description: str
    use_industrial_bridge: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "levels": self.levels,
            "description": self.description,
            "use_industrial_bridge": self.use_industrial_bridge,
        }


PROFILES: dict[str, LearningProfile] = {
    "basic_reality": LearningProfile(
        name="basic_reality",
        levels=[1, 2, 3],
        description="Levels 1–3: things, properties, actions — foundational reality frame.",
    ),
    "relational_reasoning": LearningProfile(
        name="relational_reasoning",
        levels=[4, 5],
        description="Levels 4–5: relations, causes, effects — causal and relational thinking.",
    ),
    "evidence_certainty": LearningProfile(
        name="evidence_certainty",
        levels=[7],
        description="Level 7: evidence and certainty policy — epistemic discipline.",
    ),
    "mixed_reasoning": LearningProfile(
        name="mixed_reasoning",
        levels=[8],
        description="Level 8: mixed reasoning — adversarial and complex scenarios.",
    ),
    "full_curriculum": LearningProfile(
        name="full_curriculum",
        levels=[1, 2, 3, 4, 5, 6, 7, 8],
        description="Levels 1–8: complete cognitive curriculum.",
    ),
    "adversarial": LearningProfile(
        name="adversarial",
        levels=[8],
        description="Level 8: adversarial and mixed reasoning scenarios.",
    ),
    "full_curriculum_extended": LearningProfile(
        name="full_curriculum_extended",
        levels=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        description="Levels 1–10: complete extended curriculum including domain reasoning and graph-vector composition.",
    ),
    "industrial_curriculum": LearningProfile(
        name="industrial_curriculum",
        levels=[7, 8],
        description="Levels 7–8 + industrial bridge — production-ready evaluation.",
        use_industrial_bridge=True,
    ),
}


def get_profile(name: str) -> LearningProfile:
    if name not in PROFILES:
        raise ValueError(f"Unknown profile {name!r}. Available: {list(PROFILES)}")
    return PROFILES[name]
