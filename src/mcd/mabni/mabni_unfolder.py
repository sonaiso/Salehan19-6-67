"""MabniUnfolder — main orchestrator for the Mabni analysis pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mcd.mabni.answer_particle_resolver import AnswerParticleResolver
from mcd.mabni.attached_pronoun_unfolder import AttachedPronounUnfolder
from mcd.mabni.conditional_engine import ConditionalEngine
from mcd.mabni.counterfactual_engine import CounterfactualEngine
from mcd.mabni.demonstrative_resolver import DemonstrativeResolver
from mcd.mabni.emphasis_evidence_separator import EmphasisEvidenceSeparator
from mcd.mabni.exception_restriction_engine import ExceptionRestrictionEngine
from mcd.mabni.in_resolver import InResolver
from mcd.mabni.la_resolver import LaResolver
from mcd.mabni.ma_resolver import MaResolver
from mcd.mabni.mabni_certainty_policy import MabniCertaintyPolicy
from mcd.mabni.mabni_graph_builder import MabniGraph, MabniGraphBuilder
from mcd.mabni.mabni_registry import MabniRegistry
from mcd.mabni.mabni_trace_linker import MabniTraceLinker, MabniTraceReport
from mcd.mabni.man_resolver import ManResolver
from mcd.mabni.preposition_resolver import PrepositionResolver
from mcd.mabni.qasr_engine import QasrEngine
from mcd.mabni.relative_pronoun_resolver import RelativePronounResolver
from mcd.mabni.speech_act_resolver import SpeechActResolver


@dataclass
class MabniUnfoldResult:
    text: str
    speech_act: dict[str, Any] = field(default_factory=dict)
    ma_result: dict[str, Any] = field(default_factory=dict)
    man_result: dict[str, Any] = field(default_factory=dict)
    in_result: dict[str, Any] = field(default_factory=dict)
    la_result: dict[str, Any] = field(default_factory=dict)
    conditional_result: dict[str, Any] = field(default_factory=dict)
    counterfactual_result: dict[str, Any] = field(default_factory=dict)
    qasr_result: dict[str, Any] = field(default_factory=dict)
    exception_result: dict[str, Any] = field(default_factory=dict)
    emphasis_result: dict[str, Any] = field(default_factory=dict)
    demonstrative_result: dict[str, Any] = field(default_factory=dict)
    relative_result: dict[str, Any] = field(default_factory=dict)
    answer_result: dict[str, Any] = field(default_factory=dict)
    pronoun_results: list[dict[str, Any]] = field(default_factory=list)
    preposition_results: list[dict[str, Any]] = field(default_factory=list)
    certainty_policies: list[dict[str, Any]] = field(default_factory=list)
    graph: dict[str, Any] = field(default_factory=dict)
    trace: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "speech_act": self.speech_act,
            "ma_result": self.ma_result,
            "man_result": self.man_result,
            "in_result": self.in_result,
            "la_result": self.la_result,
            "conditional_result": self.conditional_result,
            "counterfactual_result": self.counterfactual_result,
            "qasr_result": self.qasr_result,
            "exception_result": self.exception_result,
            "emphasis_result": self.emphasis_result,
            "demonstrative_result": self.demonstrative_result,
            "relative_result": self.relative_result,
            "answer_result": self.answer_result,
            "pronoun_results": self.pronoun_results,
            "preposition_results": self.preposition_results,
            "certainty_policies": self.certainty_policies,
            "graph": self.graph,
            "trace": self.trace,
            "warnings": self.warnings,
        }


class MabniUnfolder:
    """Orchestrates all Mabni analysis components for a given Arabic text."""

    def __init__(self) -> None:
        self._registry = MabniRegistry()
        self._speech_act = SpeechActResolver()
        self._ma = MaResolver()
        self._man = ManResolver()
        self._in = InResolver()
        self._la = LaResolver()
        self._conditional = ConditionalEngine()
        self._counterfactual = CounterfactualEngine()
        self._qasr = QasrEngine()
        self._exception = ExceptionRestrictionEngine()
        self._emphasis = EmphasisEvidenceSeparator()
        self._demonstrative = DemonstrativeResolver()
        self._relative = RelativePronounResolver()
        self._answer = AnswerParticleResolver()
        self._pronouns = AttachedPronounUnfolder()
        self._prepositions = PrepositionResolver()
        self._certainty_policy = MabniCertaintyPolicy()
        self._graph_builder = MabniGraphBuilder()
        self._trace_linker = MabniTraceLinker()

    def unfold(self, text: str, previous_question: str = "") -> MabniUnfoldResult:
        result = MabniUnfoldResult(text=text)

        result.speech_act = self._speech_act.resolve(text).to_dict()
        result.ma_result = self._ma.resolve(text).to_dict()
        result.man_result = self._man.resolve(text).to_dict()
        result.in_result = self._in.resolve(text).to_dict()
        result.la_result = self._la.resolve(text).to_dict()
        result.conditional_result = self._conditional.analyze(text).to_dict()
        result.counterfactual_result = self._counterfactual.analyze(text).to_dict()
        result.qasr_result = self._qasr.analyze(text).to_dict()
        result.exception_result = self._exception.analyze(text).to_dict()
        result.emphasis_result = self._emphasis.analyze(text).to_dict()
        result.demonstrative_result = self._demonstrative.resolve(text).to_dict()
        result.relative_result = self._relative.resolve(text).to_dict()
        result.answer_result = self._answer.resolve(text, previous_question=previous_question).to_dict()
        result.pronoun_results = [p.to_dict() for p in self._pronouns.unfold(text)]
        result.preposition_results = [p.to_dict() for p in self._prepositions.resolve_all(text)]

        # Collect all warnings
        for key in ("speech_act", "ma_result", "man_result", "in_result", "la_result",
                    "conditional_result", "counterfactual_result", "qasr_result",
                    "exception_result", "emphasis_result", "demonstrative_result",
                    "relative_result", "answer_result"):
            d = getattr(result, key, {})
            if isinstance(d, dict):
                result.warnings.extend(d.get("warnings", []))
        for p in result.pronoun_results:
            result.warnings.extend(p.get("warnings", []))
        for p in result.preposition_results:
            result.warnings.extend(p.get("warnings", []))

        # Certainty policies from registry operators
        for op in self._registry.get_all():
            policy = self._certainty_policy.evaluate(op)
            result.certainty_policies.append({"operator_id": op.operator_id, **policy.to_dict()})

        # Build graph
        unfold_dict = result.to_dict()
        graph: MabniGraph = self._graph_builder.build(unfold_dict, graph_id=f"mabni_{hash(text)}")
        result.graph = graph.to_dict()

        # Build trace
        trace: MabniTraceReport = self._trace_linker.link(text, unfold_dict, graph=graph)
        result.trace = trace.to_dict()

        return result
