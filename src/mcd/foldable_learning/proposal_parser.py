"""ProposalParser — foldable learning layer wrapping base parser."""
from __future__ import annotations
import re
from mcd.residual_learning.proposal_parser import ProposalParser as _BaseParser
from mcd.residual_learning.proposal_schema import GPTProposal, ProposalGraph

__all__ = ["ProposalParser"]

_GPT_MARKERS = ["gpt", "chatgpt", "النموذج", "الذكاء الاصطناعي"]
_API_AUTHORITY_EXT = re.compile(r"(API|api|استعلام API).{0,50}(أكد|يؤكد|صحيح|موثوق|مصدر)", re.UNICODE)
_GPT_EVIDENCE_EXT = re.compile(r"(الذكاء الاصطناعي|ChatGPT|النموذج اللغوي|GPT).{0,50}(لا يخطئ|يكفي|كدليل|أثبت|جاء من)", re.UNICODE)
_STALE_SOURCE = re.compile(r"(دراسة|تقرير|مصدر|بحث).{0,20}(19[0-9]{2}|20[01][0-9]).{0,50}(لا تزال|سارية|معتمدة|صالحة)", re.UNICODE)
_CONFLICT_IGNORED = re.compile(r"(رغم|بالرغم|على الرغم).{0,30}(خلاف|اختلاف|تعارض)", re.UNICODE)

_CATEGORY_WARNINGS: dict[str, list[str]] = {
    "stale_source_as_current": ["stale_source_used", "evidence_residual"],
    "conflict_ignored": ["conflict_ignored", "ambiguous_requires_context"],
    "wrong_domain": ["wrong_domain_application"],
    "analogy_without_illah": ["analogy_without_illah"],
    "answer_without_source": ["no_evidence_provided"],
    "ambiguity_ignored": ["ambiguous_requires_context"],
    "legal_certainty_without_source": ["near_certainty_without_evidence"],
    "medical_certainty_without_source": ["near_certainty_without_evidence"],
}


class ProposalParser:
    def __init__(self) -> None:
        self._base = _BaseParser()

    def parse(self, proposal: GPTProposal) -> ProposalGraph:
        graph = self._base.parse_text_to_proposal_graph(proposal)
        full_text = proposal.input_text + " " + proposal.gpt_output

        # gpt_as_evidence via claimed_evidence
        for e in proposal.claimed_evidence:
            if any(m in e.lower() for m in _GPT_MARKERS):
                if "gpt_as_evidence" not in graph.warnings:
                    graph.warnings.append("gpt_as_evidence")
                break

        # Extended detections
        if _API_AUTHORITY_EXT.search(full_text) and "tool_api_not_standalone_evidence" not in graph.warnings:
            graph.warnings.append("tool_api_not_standalone_evidence")
        if _GPT_EVIDENCE_EXT.search(full_text) and "gpt_as_evidence" not in graph.warnings:
            graph.warnings.append("gpt_as_evidence")
        if _STALE_SOURCE.search(full_text) and "stale_source_used" not in graph.warnings:
            graph.warnings.append("stale_source_used")
        if _CONFLICT_IGNORED.search(full_text) and "conflict_ignored" not in graph.warnings:
            graph.warnings.append("conflict_ignored")

        # Category-based for deterministic mock proposals
        category = proposal.metadata.get("category", "")
        for w in _CATEGORY_WARNINGS.get(category, []):
            if w not in graph.warnings:
                graph.warnings.append(w)

        return graph
