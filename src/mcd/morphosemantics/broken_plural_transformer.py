"""BrokenPluralTransformer — transforms Arabic singulars to broken plural forms.

Arabic broken plurals (جمع التكسير) are the primary pluralisation mechanism
for most nouns.  Unlike sound plurals (جمع المذكر السالم / جمع المؤنث السالم),
broken plurals involve an internal restructuring of the word according to a
pattern.  This module maps known singulars to their broken plural patterns.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "morphosemantics"


@dataclass
class BrokenPluralResult:
    singular: str
    plural_form: str
    plural_pattern: str  # أفعال|فِعال|فُعول|فُعَل|أفعِلة|فُعُل|فعالة|...
    certainty_policy: str  # qiyasi|samai
    certainty: float

    def to_dict(self) -> dict:
        return {
            "singular": self.singular,
            "plural_form": self.plural_form,
            "plural_pattern": self.plural_pattern,
            "certainty_policy": self.certainty_policy,
            "certainty": self.certainty,
        }


# High-confidence known broken plurals
_KNOWN: dict[str, dict] = {
    "كِتاب": {"plural_form": "كُتُب", "plural_pattern": "فُعُل",
              "certainty_policy": "samai", "certainty": 1.0},
    "رَجُل": {"plural_form": "رِجال", "plural_pattern": "فِعال",
              "certainty_policy": "samai", "certainty": 1.0},
    "بَيت": {"plural_form": "بُيوت", "plural_pattern": "فُعول",
             "certainty_policy": "samai", "certainty": 1.0},
    "جَبَل": {"plural_form": "جِبال", "plural_pattern": "فِعال",
              "certainty_policy": "samai", "certainty": 1.0},
    "عِلم": {"plural_form": "عُلوم", "plural_pattern": "فُعول",
             "certainty_policy": "samai", "certainty": 1.0},
    "بَحر": {"plural_form": "بِحار", "plural_pattern": "فِعال",
             "certainty_policy": "samai", "certainty": 1.0},
    "قَلب": {"plural_form": "قُلوب", "plural_pattern": "فُعول",
             "certainty_policy": "samai", "certainty": 1.0},
    "فِعل": {"plural_form": "أفعال", "plural_pattern": "أفعال",
             "certainty_policy": "qiyasi", "certainty": 0.9},
    "قَول": {"plural_form": "أقوال", "plural_pattern": "أفعال",
             "certainty_policy": "qiyasi", "certainty": 0.9},
    "عَمَل": {"plural_form": "أعمال", "plural_pattern": "أفعال",
              "certainty_policy": "qiyasi", "certainty": 0.9},
    "صورة": {"plural_form": "صُوَر", "plural_pattern": "فُعَل",
             "certainty_policy": "samai", "certainty": 1.0},
    "دَولة": {"plural_form": "دُوَل", "plural_pattern": "فُعَل",
              "certainty_policy": "samai", "certainty": 1.0},
    "شَجَرة": {"plural_form": "أشجار", "plural_pattern": "أفعال",
               "certainty_policy": "qiyasi", "certainty": 0.9},
    "كَلِمة": {"plural_form": "كَلِمات", "plural_pattern": "فَعِلات",
               "certainty_policy": "qiyasi", "certainty": 0.85},
    "مَدينة": {"plural_form": "مُدُن", "plural_pattern": "فُعُل",
               "certainty_policy": "samai", "certainty": 0.9},
    "شَهر": {"plural_form": "أشهُر", "plural_pattern": "أفعُل",
             "certainty_policy": "samai", "certainty": 1.0},
}


class BrokenPluralTransformer:
    """Transforms Arabic singulars to their broken plural forms."""

    def __init__(self) -> None:
        self._data: dict[str, dict] = dict(_KNOWN)
        self._load()

    def _load(self) -> None:
        path = _DATA_DIR / "broken_plural_patterns.json"
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for entry in data.get("entries", []):
                singular = entry.pop("singular")
                self._data[singular] = entry
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
            pass

    def transform(self, singular: str) -> Optional[BrokenPluralResult]:
        d = self._data.get(singular)
        if d is None:
            return None
        return BrokenPluralResult(
            singular=singular,
            plural_form=d.get("plural_form") or d.get("plural", ""),
            plural_pattern=d.get("plural_pattern") or d.get("pattern", ""),
            certainty_policy=d.get("certainty_policy", "samai"),
            certainty=d.get("certainty", 0.8),
        )

    def all_singulars(self) -> list[str]:
        return list(self._data.keys())
