"""ProposalParser — deterministic, rule-based parser for GPTProposals.

No LLM calls. No network. Pure text heuristics.
"""
from __future__ import annotations

import re
import uuid

from .proposal_schema import (
    GPTProposal,
    ProposalGraph,
    ProposalCognitiveNode,
    ProposalCognitiveEdge,
    ProposalType,
)

# Certainty trigger words (Arabic + English)
_CERTAINTY_HIGH = re.compile(
    r"(بالتأكيد|قطعًا|لا شك|يقينًا|حتمًا|definitely|certainly|absolutely|always|كل|جميع|دائمًا)",
    re.UNICODE,
)
_HARM_HARAM = re.compile(r"(ضار|harm).{0,30}(حرام|haram)", re.UNICODE | re.DOTALL)
_HARAM_FROM_HARM = re.compile(r"(ضار|harm).{0,50}(حرام|haram)", re.UNICODE | re.DOTALL)
_GPT_AS_EVIDENCE = re.compile(
    r"(GPT|gpt|ChatGPT|النموذج|الذكاء الاصطناعي).{0,30}(قال|قالت|يؤكد|صحيح|موثوق|evidence|authority)",
    re.UNICODE,
)
_API_AS_EVIDENCE = re.compile(
    r"(API|api|واجهة).{0,30}(صحيح|موثوق|مصدر|يقول|قال|reliable|authority|evidence)",
    re.UNICODE,
)
_METAPHOR_LITERAL = re.compile(
    r"(مريض|جسد|علاج|body|sick|heal).{0,50}(حرفيًا|literally|كما|same as|نفس)",
    re.UNICODE | re.DOTALL,
)
_PROMPT_INJECTION = re.compile(
    r"(أجب|تجاهل|ignore|forget|pretend|افترض).{0,30}(بيقين|بدون|بلا).{0,20}(مصدر|دليل|evidence|source)",
    re.UNICODE,
)
_UNSUPPORTED_GEN = re.compile(
    r"(كل|جميع|معظم|all|every|most|always).{0,30}(شركات|ناس|مجتمع|people|companies|organizations)",
    re.UNICODE,
)


class ProposalParser:
    """Rule-based deterministic parser.

    Converts a GPTProposal into a ProposalGraph by detecting semantic patterns.
    """

    def parse_text_to_proposal_graph(self, proposal: GPTProposal) -> ProposalGraph:
        gpt_text = proposal.gpt_output
        input_text = proposal.input_text
        full_text = input_text + " " + gpt_text

        warnings: list[str] = []
        nodes: list[ProposalCognitiveNode] = []
        edges: list[ProposalCognitiveEdge] = []
        root_vector: dict[str, float] = {}
        certainty_policy = "probable_knowledge"
        evidence_status = "missing"

        gid = proposal.proposal_id

        # Root claim node
        claim_node = ProposalCognitiveNode(
            node_id=f"{gid}_claim",
            surface=gpt_text[:80],
            node_type="claim",
            certainty=0.5,
            evidence_refs=list(proposal.claimed_evidence),
        )
        nodes.append(claim_node)

        if proposal.claimed_evidence:
            evidence_status = "sufficient"
            root_vector["evidence_strength"] = 0.7
        else:
            root_vector["evidence_strength"] = 0.0
            warnings.append("no_evidence_provided")

        # Detect near-certainty without evidence
        if _CERTAINTY_HIGH.search(gpt_text) and not proposal.claimed_evidence:
            certainty_policy = "near_certainty"
            warnings.append("near_certainty_without_evidence")
            root_vector["certainty_claim"] = 0.9
        elif proposal.claimed_certainty in ("certain", "definite", "يقين"):
            certainty_policy = "near_certainty"
            if not proposal.claimed_evidence:
                warnings.append("near_certainty_without_evidence")
            root_vector["certainty_claim"] = 0.85
        else:
            root_vector["certainty_claim"] = 0.4

        # Detect harm→haram equivocation
        if _HARM_HARAM.search(full_text):
            harm_node = ProposalCognitiveNode(
                node_id=f"{gid}_harm",
                surface="harm",
                node_type="property",
            )
            haram_node = ProposalCognitiveNode(
                node_id=f"{gid}_haram",
                surface="haram",
                node_type="judgment",
            )
            nodes.extend([harm_node, haram_node])
            edges.append(ProposalCognitiveEdge(
                edge_id=f"{gid}_harm_entails_haram",
                source=f"{gid}_harm",
                relation="entails",
                target=f"{gid}_haram",
            ))
            warnings.append("harm_implies_haram")
            root_vector["harm_haram_equivocation"] = 1.0

        # Detect GPT/API as authority
        if _GPT_AS_EVIDENCE.search(full_text) or _API_AS_EVIDENCE.search(full_text):
            tool_node = ProposalCognitiveNode(
                node_id=f"{gid}_tool",
                surface="tool/API",
                node_type="tool",
                evidence_refs=[],
            )
            nodes.append(tool_node)
            edges.append(ProposalCognitiveEdge(
                edge_id=f"{gid}_tool_supports",
                source=f"{gid}_tool",
                relation="supports",
                target=f"{gid}_claim",
                evidence_refs=[],
            ))
            warnings.append("tool_api_not_standalone_evidence")
            root_vector["tool_as_evidence"] = 1.0

        # Detect metaphor treated as literal
        if _METAPHOR_LITERAL.search(full_text):
            warnings.append("metaphor_as_literal")
            root_vector["metaphor_literalization"] = 1.0

        # Detect prompt injection
        if _PROMPT_INJECTION.search(full_text):
            warnings.append("prompt_injection_detected")
            root_vector["injection_risk"] = 1.0

        # Detect unsupported generalization
        if _UNSUPPORTED_GEN.search(full_text) and not proposal.claimed_evidence:
            warnings.append("unsupported_generalization")
            root_vector["generalization_without_evidence"] = 1.0

        # Detect ambiguity
        if "ambiguous" in proposal.metadata.get("flags", []) or len(input_text.split()) < 3:
            warnings.append("ambiguous_requires_context")
            if certainty_policy == "near_certainty":
                certainty_policy = "suspend_judgment"

        # Proposal type specific checks
        if proposal.proposal_type == ProposalType.DATASET_EXAMPLE and not proposal.claimed_evidence:
            warnings.append("dataset_example_without_evidence")

        return ProposalGraph(
            graph_id=gid,
            nodes=nodes,
            edges=edges,
            root_vector=root_vector,
            evidence_status=evidence_status,
            certainty_policy=certainty_policy,
            warnings=warnings,
        )
