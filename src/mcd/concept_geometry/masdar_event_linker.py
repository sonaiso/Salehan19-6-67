"""MasdarEventLinker — links masdar (verbal noun) to its event abstraction."""
from __future__ import annotations


class MasdarEventLinker:
    """Links masdar forms to their abstracted event and root family."""

    _MASDAR_EVENTS: dict[str, dict] = {
        "كتابة": {"event_class": "communication", "root": "ك ت ب", "event_id": "writing"},
        "قراءة": {"event_class": "cognition", "root": "ق ر أ", "event_id": "reading"},
        "زراعة": {"event_class": "production", "root": "ز ر ع", "event_id": "cultivation"},
        "تعليم": {"event_class": "education", "root": "ع ل م", "event_id": "teaching"},
        "تعلم": {"event_class": "education", "root": "ع ل م", "event_id": "learning"},
        "شرب": {"event_class": "action", "root": "ش ر ب", "event_id": "drinking"},
        "أكل": {"event_class": "action", "root": "أ ك ل", "event_id": "eating"},
        "علم": {"event_class": "cognition", "root": "ع ل م", "event_id": "knowing"},
        "حكم": {"event_class": "judgment", "root": "ح ك م", "event_id": "judging"},
        "بناء": {"event_class": "production", "root": "ب ن ي", "event_id": "building"},
    }

    def get_event(self, masdar: str) -> dict:
        return self._MASDAR_EVENTS.get(masdar, {})

    def get_event_class(self, masdar: str) -> str:
        return self._MASDAR_EVENTS.get(masdar, {}).get("event_class", "unknown")

    def get_root(self, masdar: str) -> str:
        return self._MASDAR_EVENTS.get(masdar, {}).get("root", "")

    def all_masdars(self) -> list[str]:
        return list(self._MASDAR_EVENTS.keys())
