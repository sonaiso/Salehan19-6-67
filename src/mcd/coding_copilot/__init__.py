"""AFJG Coding Copilot Simulator kernel package."""

from mcd.coding_copilot.architecture_evidence import ArchitectureEvidence
from mcd.coding_copilot.code_claim import CodeClaim
from mcd.coding_copilot.coding_copilot_kernel import CodingCopilotKernel
from mcd.coding_copilot.coding_judgment import CodingJudgment, build_coding_judgment, decide_final_judgment
from mcd.coding_copilot.coding_residual import CodingResidual
from mcd.coding_copilot.coding_reverse_trace import CodingReverseTrace
from mcd.coding_copilot.coding_status import (
    CodingStatus,
    PUBLIC_FINAL_CODING_JUDGMENTS,
    INTERNAL_SUSPEND,
    collapse_to_public_status,
    is_public_final_coding_judgment,
)
from mcd.coding_copilot.issue_understanding import IssueUnderstanding
from mcd.coding_copilot.patch_artifact import PatchArtifact
from mcd.coding_copilot.patch_plan import PatchPlan
from mcd.coding_copilot.repo_context import RepoContextMap
from mcd.coding_copilot.serializers import coding_judgment_to_dict, coding_judgment_to_json
from mcd.coding_copilot.static_evidence import StaticEvidence
from mcd.coding_copilot.test_evidence import TestEvidence

__all__ = [
    "ArchitectureEvidence",
    "CodeClaim",
    "CodingCopilotKernel",
    "CodingJudgment",
    "build_coding_judgment",
    "decide_final_judgment",
    "CodingResidual",
    "CodingReverseTrace",
    "CodingStatus",
    "PUBLIC_FINAL_CODING_JUDGMENTS",
    "INTERNAL_SUSPEND",
    "collapse_to_public_status",
    "is_public_final_coding_judgment",
    "IssueUnderstanding",
    "PatchArtifact",
    "PatchPlan",
    "RepoContextMap",
    "coding_judgment_to_dict",
    "coding_judgment_to_json",
    "StaticEvidence",
    "TestEvidence",
]
