"""MabniRegistry — loads Mabni operators from JSON file with built-in fallback."""
from __future__ import annotations

import json
from pathlib import Path

from mcd.mabni.mabni_operator import MabniOperator
from mcd.mabni.mabni_schema import CertaintyEffect, LogicalFunction, MabniType, PragmaticFunction

_DEFAULT_DATA_PATH = Path(__file__).parent.parent.parent.parent / "data" / "mabni" / "mabni_registry_ar.json"

# Minimal built-in fallback — covers the most critical operators
_BUILTIN_OPERATORS: list[dict] = [
    {
        "operator_id": "MA_NEG_001", "surface": "ما", "normalized": "ما",
        "mabni_type": "negation", "logical_function": "negation", "pragmatic_function": "assertion",
        "affects_evidence": True, "affects_certainty": True, "creates_evidence": False,
        "certainty_effect": "lower", "trace_ids": [], "examples": ["ما جاء زيد"],
    },
    {
        "operator_id": "MA_INT_002", "surface": "ما", "normalized": "ما",
        "mabni_type": "interrogative", "logical_function": "speech_act", "pragmatic_function": "question",
        "affects_evidence": False, "affects_certainty": True, "creates_evidence": False,
        "certainty_effect": "suspend", "trace_ids": [], "examples": ["ما هذا؟"],
    },
    {
        "operator_id": "MA_REL_003", "surface": "ما", "normalized": "ما",
        "mabni_type": "relative", "logical_function": "reference", "pragmatic_function": "assertion",
        "affects_evidence": False, "affects_certainty": False, "creates_evidence": False,
        "certainty_effect": "none", "trace_ids": [], "examples": ["ما تفعله يُحسب لك"],
    },
    {
        "operator_id": "MAN_INT_001", "surface": "من", "normalized": "من",
        "mabni_type": "interrogative", "logical_function": "speech_act", "pragmatic_function": "question",
        "affects_evidence": False, "affects_certainty": True, "creates_evidence": False,
        "certainty_effect": "suspend", "trace_ids": [], "examples": ["من جاء؟"],
    },
    {
        "operator_id": "MAN_REL_002", "surface": "من", "normalized": "من",
        "mabni_type": "relative", "logical_function": "reference", "pragmatic_function": "assertion",
        "affects_evidence": False, "affects_certainty": False, "creates_evidence": False,
        "certainty_effect": "none", "trace_ids": [], "examples": ["من يعمل يُكافأ"],
    },
    {
        "operator_id": "IN_CON_001", "surface": "إن", "normalized": "إن",
        "mabni_type": "conditional", "logical_function": "condition", "pragmatic_function": "assertion",
        "affects_evidence": False, "affects_certainty": True, "creates_evidence": False,
        "certainty_effect": "suspend", "trace_ids": [], "examples": ["إن جاء زيد أكرمته"],
    },
    {
        "operator_id": "INNA_EMP_003", "surface": "إنّ", "normalized": "إن",
        "mabni_type": "emphasis", "logical_function": "emphasis", "pragmatic_function": "assertion",
        "affects_evidence": False, "affects_certainty": True, "creates_evidence": False,
        "certainty_effect": "emphasis_only", "trace_ids": [], "examples": ["إنّ الله غفور"],
    },
    {
        "operator_id": "INNAMA_QSR_004", "surface": "إنما", "normalized": "إنما",
        "mabni_type": "restriction", "logical_function": "qasr", "pragmatic_function": "assertion",
        "affects_evidence": True, "affects_certainty": True, "creates_evidence": False,
        "certainty_effect": "scope_limit", "trace_ids": [], "examples": ["إنما الأعمال بالنيات"],
    },
    {
        "operator_id": "LA_NEG_001", "surface": "لا", "normalized": "لا",
        "mabni_type": "negation", "logical_function": "negation", "pragmatic_function": "denial",
        "affects_evidence": True, "affects_certainty": True, "creates_evidence": False,
        "certainty_effect": "lower", "trace_ids": [], "examples": ["لا إله إلا الله"],
    },
    {
        "operator_id": "LA_NAH_002", "surface": "لا", "normalized": "لا",
        "mabni_type": "prohibition_marker", "logical_function": "speech_act", "pragmatic_function": "prohibition",
        "affects_evidence": False, "affects_certainty": False, "creates_evidence": False,
        "certainty_effect": "none", "trace_ids": [], "examples": ["لا تكذب"],
    },
    {
        "operator_id": "ILLA_EXC_001", "surface": "إلا", "normalized": "إلا",
        "mabni_type": "exception", "logical_function": "exception", "pragmatic_function": "assertion",
        "affects_evidence": True, "affects_certainty": True, "creates_evidence": False,
        "certainty_effect": "scope_limit", "trace_ids": [], "examples": ["ما جاء إلا زيد"],
    },
    {
        "operator_id": "HATHA_DEM_001", "surface": "هذا", "normalized": "هذا",
        "mabni_type": "demonstrative", "logical_function": "reference", "pragmatic_function": "assertion",
        "affects_evidence": False, "affects_certainty": False, "creates_evidence": False,
        "certainty_effect": "none", "trace_ids": [], "examples": ["هذا الكتاب"],
    },
    {
        "operator_id": "ALLATHI_REL_001", "surface": "الذي", "normalized": "الذي",
        "mabni_type": "relative", "logical_function": "reference", "pragmatic_function": "assertion",
        "affects_evidence": False, "affects_certainty": False, "creates_evidence": False,
        "certainty_effect": "none", "trace_ids": [], "examples": ["الرجل الذي جاء"],
    },
    {
        "operator_id": "NAAM_ANS_001", "surface": "نعم", "normalized": "نعم",
        "mabni_type": "answer", "logical_function": "answer", "pragmatic_function": "confirmation",
        "affects_evidence": False, "affects_certainty": False, "creates_evidence": False,
        "certainty_effect": "none", "trace_ids": [], "examples": ["نعم، حضر"],
    },
    {
        "operator_id": "HAL_INT_001", "surface": "هل", "normalized": "هل",
        "mabni_type": "interrogative", "logical_function": "speech_act", "pragmatic_function": "question",
        "affects_evidence": False, "affects_certainty": True, "creates_evidence": False,
        "certainty_effect": "suspend", "trace_ids": [], "examples": ["هل جاء؟"],
    },
    {
        "operator_id": "LAW_CON_001", "surface": "لو", "normalized": "لو",
        "mabni_type": "conditional", "logical_function": "condition", "pragmatic_function": "wish",
        "affects_evidence": False, "affects_certainty": True, "creates_evidence": False,
        "certainty_effect": "suspend", "trace_ids": [], "examples": ["لو جاء لأكرمته"],
    },
    {
        "operator_id": "LAWLA_CON_001", "surface": "لولا", "normalized": "لولا",
        "mabni_type": "conditional", "logical_function": "condition", "pragmatic_function": "assertion",
        "affects_evidence": False, "affects_certainty": True, "creates_evidence": False,
        "certainty_effect": "suspend", "trace_ids": [], "examples": ["لولا زيد لهلكنا"],
    },
    {
        "operator_id": "QAD_EMP_001", "surface": "قد", "normalized": "قد",
        "mabni_type": "emphasis", "logical_function": "emphasis", "pragmatic_function": "assertion",
        "affects_evidence": False, "affects_certainty": True, "creates_evidence": False,
        "certainty_effect": "emphasis_only", "trace_ids": [], "examples": ["قد جاء زيد"],
    },
]


def _make_operator(d: dict) -> MabniOperator:
    return MabniOperator(
        operator_id=d["operator_id"],
        surface=d["surface"],
        normalized=d["normalized"],
        mabni_type=MabniType(d["mabni_type"]),
        logical_function=LogicalFunction(d["logical_function"]),
        pragmatic_function=PragmaticFunction(d["pragmatic_function"]),
        affects_evidence=bool(d["affects_evidence"]),
        affects_certainty=bool(d["affects_certainty"]),
        creates_evidence=False,  # always False
        certainty_effect=CertaintyEffect(d["certainty_effect"]),
        trace_ids=list(d.get("trace_ids", [])),
        examples=list(d.get("examples", [])),
    )


class MabniRegistry:
    """Registry of Arabic Mabni operators loaded from JSON file."""

    def __init__(self, data_path: Path | str | None = None) -> None:
        path = Path(data_path) if data_path else _DEFAULT_DATA_PATH
        self._operators: list[MabniOperator] = []
        self._by_surface: dict[str, list[MabniOperator]] = {}
        self._load(path)

    def _load(self, path: Path) -> None:
        try:
            with path.open(encoding="utf-8") as fh:
                data = json.load(fh)
            raw = data.get("operators", [])
        except (FileNotFoundError, json.JSONDecodeError):
            raw = _BUILTIN_OPERATORS

        for d in raw:
            try:
                op = _make_operator(d)
                self._operators.append(op)
                self._by_surface.setdefault(op.surface, []).append(op)
            except (KeyError, ValueError):
                continue

        # Always ensure fallback operators are available
        existing_ids = {op.operator_id for op in self._operators}
        for d in _BUILTIN_OPERATORS:
            if d["operator_id"] not in existing_ids:
                try:
                    op = _make_operator(d)
                    self._operators.append(op)
                    self._by_surface.setdefault(op.surface, []).append(op)
                except (KeyError, ValueError):
                    continue

    def get(self, surface: str) -> MabniOperator | None:
        """Return first matching operator for surface form (or None)."""
        results = self._by_surface.get(surface, [])
        return results[0] if results else None

    def get_all_for_surface(self, surface: str) -> list[MabniOperator]:
        """Return all operators matching a surface form."""
        return self._by_surface.get(surface, [])

    def get_all(self) -> list[MabniOperator]:
        return list(self._operators)

    def count(self) -> int:
        return len(self._operators)
