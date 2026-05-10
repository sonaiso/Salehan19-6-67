"""IdafaEngine — detects and analyzes Arabic إضافة (genitive construct)."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class IdafaRelation:
    mudaf: str
    mudaf_ilayh: str
    idafa_type: str  # possession|specification|part_whole|masdar_to_agent|masdar_to_patient|lafziyya|ma'nawiyya
    mudaf_id: str
    mudaf_ilayh_id: str
    certainty: float

    def to_dict(self) -> dict:
        return {
            "mudaf": self.mudaf,
            "mudaf_ilayh": self.mudaf_ilayh,
            "idafa_type": self.idafa_type,
            "mudaf_id": self.mudaf_id,
            "mudaf_ilayh_id": self.mudaf_ilayh_id,
            "certainty": self.certainty,
        }


def _strip_diacritics(text: str) -> str:
    diacritics = set('\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652')
    return ''.join(c for c in text if c not in diacritics)


class IdafaEngine:
    """Detects إضافة (genitive construct) relations in Arabic text."""

    MASDAR_PATTERNS = {"كِتَابَة", "قِرَاءَة", "كَتْب", "قِرَاء", "فَهْم", "عِلْم"}

    def detect_idafa(self, tokens: list) -> list:
        """Detect idafa relations from list of token strings."""
        relations = []

        for i in range(len(tokens) - 1):
            tok = tokens[i]
            next_tok = tokens[i + 1]

            stripped_tok = _strip_diacritics(tok)
            stripped_next = _strip_diacritics(next_tok)

            no_tanwin = not tok.endswith('\u064b') and not tok.endswith('\u064c') and not tok.endswith('\u064d')
            next_has_kasra = next_tok.endswith('\u0650') or next_tok.endswith('\u064d') or next_tok.startswith('ال')

            if no_tanwin and next_has_kasra and stripped_tok and stripped_next:
                idafa_type = self._classify_idafa(stripped_tok, stripped_next)
                relations.append(IdafaRelation(
                    mudaf=tok,
                    mudaf_ilayh=next_tok,
                    idafa_type=idafa_type,
                    mudaf_id=f"tok_{i}",
                    mudaf_ilayh_id=f"tok_{i+1}",
                    certainty=0.7,
                ))

        return relations

    def _classify_idafa(self, mudaf: str, mudaf_ilayh: str) -> str:
        """Classify the type of idafa relation."""
        if mudaf in {_strip_diacritics(w) for w in self.MASDAR_PATTERNS}:
            return "masdar_to_agent"
        if any(part in mudaf for part in ["جزء", "بعض", "كل", "نصف"]):
            return "part_whole"
        return "possession"
