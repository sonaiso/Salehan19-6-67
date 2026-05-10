"""RootFamilyLinker — links words to their root family within concept geometry."""
from __future__ import annotations


class RootFamilyLinker:
    """Links a surface form to its root family string."""

    _ROOT_MAP: dict[str, str] = {
        "كاتب": "ك ت ب", "مكتوب": "ك ت ب", "مكتب": "ك ت ب",
        "كتابة": "ك ت ب", "مكتبة": "ك ت ب", "كتابي": "ك ت ب", "كتاب": "ك ت ب",
        "عالم": "ع ل م", "معلوم": "ع ل م", "تعليم": "ع ل م", "متعلم": "ع ل م",
        "علم": "ع ل م", "علمي": "ع ل م", "معلم": "ع ل م",
        "زارع": "ز ر ع", "مزروع": "ز ر ع", "زراعة": "ز ر ع",
        "مزرعة": "ز ر ع", "زراعي": "ز ر ع",
        "قارئ": "ق ر أ", "مقروء": "ق ر أ", "قراءة": "ق ر أ",
        "شارب": "ش ر ب", "مشروب": "ش ر ب", "شرب": "ش ر ب",
    }

    def get_root_family(self, surface: str) -> str:
        return self._ROOT_MAP.get(surface, "")

    def get_family_members(self, root: str) -> list[str]:
        return [s for s, r in self._ROOT_MAP.items() if r == root]
