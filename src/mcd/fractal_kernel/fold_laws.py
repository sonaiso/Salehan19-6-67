from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class FoldOperation:
    fold_id: str
    input_unit_ids: list[str]
    output_fold_unit_id: str
    preserved_relations: list[str] = field(default_factory=list)
    preserved_vectors: list[str] = field(default_factory=list)
    lost_details: list[str] = field(default_factory=list)
    summary_signature: str = ""

    def to_dict(self) -> dict:
        return {
            "fold_id": self.fold_id,
            "input_unit_ids": self.input_unit_ids,
            "output_fold_unit_id": self.output_fold_unit_id,
            "preserved_relations": self.preserved_relations,
            "preserved_vectors": self.preserved_vectors,
            "lost_details": self.lost_details,
            "summary_signature": self.summary_signature,
        }


@dataclass
class UnfoldOperation:
    unfold_id: str
    fold_unit_id: str
    output_unit_ids: list[str]
    restored_relations: list[str] = field(default_factory=list)
    restored_vectors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "unfold_id": self.unfold_id,
            "fold_unit_id": self.fold_unit_id,
            "output_unit_ids": self.output_unit_ids,
            "restored_relations": self.restored_relations,
            "restored_vectors": self.restored_vectors,
        }


@dataclass
class RefoldCheck:
    original_fold_id: str
    refolded_fold_id: str
    consistency_score: float = 0.0
    lost_in_refold: list[str] = field(default_factory=list)
    passed: bool = False

    def to_dict(self) -> dict:
        return {
            "original_fold_id": self.original_fold_id,
            "refolded_fold_id": self.refolded_fold_id,
            "consistency_score": self.consistency_score,
            "lost_in_refold": self.lost_in_refold,
            "passed": self.passed,
        }


class FoldLawEnforcer:
    """Validates fold/unfold/refold operations against the kernel laws."""

    # Law 1: Trace Preservation
    def check_trace_preservation(self, fold: FoldOperation, trace_refs: list[str]) -> tuple[bool, list[str]]:
        if not trace_refs:
            return False, ["FOLD LAW 1 VIOLATION: No trace_refs for fold operation"]
        return True, []

    # Law 2: Evidence Preservation
    def check_evidence_preservation(self, original_evidence_required: bool,
                                    fold: FoldOperation) -> tuple[bool, list[str]]:
        if original_evidence_required and "evidence" not in fold.preserved_vectors:
            return False, ["FOLD LAW 2 VIOLATION: Evidence requirement must be preserved in fold"]
        return True, []

    # Law 3: Certainty Non-Increase
    def check_certainty_non_increase(self, pre_certainty: float,
                                     post_certainty: float) -> tuple[bool, list[str]]:
        if post_certainty > pre_certainty + 1e-9:
            return False, [f"FOLD LAW 3 VIOLATION: Fold increased certainty ({pre_certainty} → {post_certainty})"]
        return True, []

    # Law 4: Refold Consistency
    def check_refold_consistency(self, original_fold: FoldOperation,
                                  refolded_fold: FoldOperation) -> RefoldCheck:
        lost = []
        # Check preserved relations
        for rel in original_fold.preserved_relations:
            if rel not in refolded_fold.preserved_relations:
                lost.append(f"relation:{rel}")
        # Check preserved vectors
        for vec in original_fold.preserved_vectors:
            if vec not in refolded_fold.preserved_vectors:
                lost.append(f"vector:{vec}")
        consistency_score = 1.0 - (len(lost) / max(
            len(original_fold.preserved_relations) + len(original_fold.preserved_vectors), 1
        ))
        return RefoldCheck(
            original_fold_id=original_fold.fold_id,
            refolded_fold_id=refolded_fold.fold_id,
            consistency_score=consistency_score,
            lost_in_refold=lost,
            passed=len(lost) == 0,
        )

    # Law 5: No Proof from Fold Alone
    def check_no_proof_from_fold_alone(self, evidence_refs: list[str],
                                        is_certificate: bool) -> tuple[bool, list[str]]:
        if is_certificate and not evidence_refs:
            return False, ["FOLD LAW 5 VIOLATION: No proof can be Certificate from fold alone without evidence"]
        return True, []
