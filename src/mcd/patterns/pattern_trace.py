from __future__ import annotations

from dataclasses import dataclass

from mcd.patterns.core import ClosureJudgment


@dataclass(frozen=True)
class PatternTrace:
    trace_id: str
    layer: str
    pattern_id: str
    judgment: ClosureJudgment
    residuals: tuple[str, ...]
    refs: tuple[str, ...]
