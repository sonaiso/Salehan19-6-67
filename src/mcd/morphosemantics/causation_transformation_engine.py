"""CausationTransformationEngine — models causation and transformation semantics.

In Arabic, the Form-II (فعَّل) and Form-IV (أفعَل) patterns are causative
operators.  Form-X (استفعل) combines request and causation.  This engine
resolves causation chains for a given word-pattern pair.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from mcd.morphosemantics.pattern_operator_registry import PatternOperatorRegistry


@dataclass
class CausationChain:
    word: str
    pattern_id: str
    causation_score: float
    request_score: float
    transformation_score: float
    chain_depth: int  # 0=simple, 1=one-step causation, 2=double causation
    chain_description: str

    def to_dict(self) -> dict:
        return {
            "word": self.word,
            "pattern_id": self.pattern_id,
            "causation_score": self.causation_score,
            "request_score": self.request_score,
            "transformation_score": self.transformation_score,
            "chain_depth": self.chain_depth,
            "chain_description": self.chain_description,
        }


_CAUSATIVE_PATTERNS = {"faala_ii", "afala_iv", "istafala_verb"}
_TRANSFORMATIVE_PATTERNS = {"tafaala_reflex", "tafaala_vi", "infaala_vii", "iftaala_viii"}


class CausationTransformationEngine:
    def __init__(self) -> None:
        self._registry = PatternOperatorRegistry()

    def analyse(self, word: str, pattern_id: str) -> CausationChain:
        op = self._registry.get(pattern_id)
        ov = op.operator_vector if op else {}
        causation = ov.get("causation", 0.0)
        request = ov.get("request", 0.0)
        mutawaa = ov.get("mutawaa", 0.0)
        reflexivity = ov.get("reflexivity", 0.0)
        transformation = max(mutawaa, reflexivity * 0.5)

        if pattern_id in _CAUSATIVE_PATTERNS:
            depth = 2 if request > 0.5 else 1
            desc = "request-causation" if request > 0.5 else "direct causation"
        elif pattern_id in _TRANSFORMATIVE_PATTERNS:
            depth = 1
            desc = "mutawaa/reflexive transformation"
        elif causation > 0.3:
            depth = 1
            desc = "mild causation"
        else:
            depth = 0
            desc = "no causation"

        return CausationChain(
            word=word,
            pattern_id=pattern_id,
            causation_score=causation,
            request_score=request,
            transformation_score=transformation,
            chain_depth=depth,
            chain_description=desc,
        )
