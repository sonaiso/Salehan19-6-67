"""IrabMarker — harakat/marker dataclass and registry."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class IrabMarker:
    marker_id: str
    name_ar: str
    name_en: str
    marker_type: str  # original|subsidiary|estimated|local
    cases_marked: list[str] = field(default_factory=list)
    visibility: str = "apparent"  # apparent|estimated|local|prevented

    def to_dict(self) -> dict:
        return {
            "marker_id": self.marker_id,
            "name_ar": self.name_ar,
            "name_en": self.name_en,
            "marker_type": self.marker_type,
            "cases_marked": self.cases_marked,
            "visibility": self.visibility,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "IrabMarker":
        return cls(**d)


_MARKERS: list[IrabMarker] = [
    IrabMarker(
        marker_id="damma",
        name_ar="ضمة",
        name_en="Damma (ُ)",
        marker_type="original",
        cases_marked=["nominative"],
        visibility="apparent",
    ),
    IrabMarker(
        marker_id="fatha",
        name_ar="فتحة",
        name_en="Fatha (َ)",
        marker_type="original",
        cases_marked=["accusative"],
        visibility="apparent",
    ),
    IrabMarker(
        marker_id="kasra",
        name_ar="كسرة",
        name_en="Kasra (ِ)",
        marker_type="original",
        cases_marked=["genitive"],
        visibility="apparent",
    ),
    IrabMarker(
        marker_id="sukun",
        name_ar="سكون",
        name_en="Sukun (ْ)",
        marker_type="original",
        cases_marked=["jussive"],
        visibility="apparent",
    ),
    IrabMarker(
        marker_id="alif",
        name_ar="ألف",
        name_en="Alif (ا)",
        marker_type="subsidiary",
        cases_marked=["accusative"],  # for أسماء خمسة in accusative, dual
        visibility="apparent",
    ),
    IrabMarker(
        marker_id="waw",
        name_ar="واو",
        name_en="Waw (و)",
        marker_type="subsidiary",
        cases_marked=["nominative"],  # جمع مذكر سالم nominative, أسماء خمسة
        visibility="apparent",
    ),
    IrabMarker(
        marker_id="ya",
        name_ar="ياء",
        name_en="Ya (ي)",
        marker_type="subsidiary",
        cases_marked=["genitive", "accusative"],  # dual genitive/accusative, جمع مذكر
        visibility="apparent",
    ),
    IrabMarker(
        marker_id="nun",
        name_ar="نون",
        name_en="Nun (ن)",
        marker_type="subsidiary",
        cases_marked=["nominative"],  # أفعال خمسة nominative
        visibility="apparent",
    ),
    IrabMarker(
        marker_id="deleted_nun",
        name_ar="حذف النون",
        name_en="Deleted Nun",
        marker_type="subsidiary",
        cases_marked=["accusative", "jussive"],  # أفعال خمسة
        visibility="apparent",
    ),
    IrabMarker(
        marker_id="estimated",
        name_ar="مقدّر",
        name_en="Estimated",
        marker_type="estimated",
        cases_marked=["nominative", "accusative", "genitive"],
        visibility="estimated",
    ),
    IrabMarker(
        marker_id="local",
        name_ar="محلي",
        name_en="Local (مبني)",
        marker_type="local",
        cases_marked=["indeclinable_local"],
        visibility="local",
    ),
    IrabMarker(
        marker_id="none",
        name_ar="لا إعراب",
        name_en="None",
        marker_type="original",
        cases_marked=[],
        visibility="prevented",
    ),
]


class IrabMarkerRegistry:
    def __init__(self) -> None:
        self._store: dict[str, IrabMarker] = {m.marker_id: m for m in _MARKERS}

    def get(self, marker_id: str) -> IrabMarker | None:
        return self._store.get(marker_id)

    def all(self) -> list[IrabMarker]:
        return list(self._store.values())


IRAB_MARKER_REGISTRY = IrabMarkerRegistry()


# Backward-compatible loader used by existing tests
def load_irab_marker_registry() -> dict[str, "IrabMarker"]:
    """Return a dict of marker_id → IrabMarker for backward compatibility."""
    return {m.marker_id: m for m in IRAB_MARKER_REGISTRY.all()}
