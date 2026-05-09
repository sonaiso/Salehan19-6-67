"""LearningEngine: learn from claims and update store."""
from __future__ import annotations

from dataclasses import dataclass
from mcd.engines.reasoning_engine import Claim
from mcd.core.nodes import KnowledgeNode
from mcd.core.certainty import Certainty


@dataclass
class LearningAction:
    action_type: str
    node_id: str
    reason: str
    old_certainty: float | None = None
    new_certainty: float | None = None

    def to_dict(self) -> dict:
        return {
            "action_type": self.action_type,
            "node_id": self.node_id,
            "reason": self.reason,
            "old_certainty": self.old_certainty,
            "new_certainty": self.new_certainty,
        }


class LearningEngine:
    VERIFIED_THRESHOLD = 0.75
    HYPOTHESIS_THRESHOLD = 0.40

    def __init__(self, store=None) -> None:
        self._store = store

    def learn(self, claims: list[Claim]) -> list[LearningAction]:
        actions: list[LearningAction] = []
        for claim in claims:
            if self._detect_conflict(claim):
                action = LearningAction(
                    action_type="suspended",
                    node_id=claim.claim_id,
                    reason="Conflict detected with existing knowledge",
                    old_certainty=claim.certainty.score,
                )
                actions.append(action)
                continue
            action = self._apply_update(claim)
            actions.append(action)
        return actions

    def _detect_conflict(self, claim: Claim) -> bool:
        if not self._store:
            return False
        # Check if claim contradicts a verified fact
        for fact in self._store.facts.all():
            if "لا " + claim.text in fact.claim or "ليس " + claim.text in fact.claim:
                return True
        return False

    def _apply_update(self, claim: Claim) -> LearningAction:
        score = claim.certainty.score

        if score >= self.VERIFIED_THRESHOLD:
            action_type = "stored_verified"
            if self._store:
                node = KnowledgeNode(
                    node_id=claim.claim_id,
                    level="claim",
                    surface=claim.text,
                    certainty=claim.certainty,
                )
                self._store.promote_to_verified(claim.claim_id)
                self._store.verified[claim.claim_id] = node
        elif score >= self.HYPOTHESIS_THRESHOLD:
            action_type = "stored_hypothesis"
            if self._store:
                node = KnowledgeNode(
                    node_id=claim.claim_id,
                    level="claim",
                    surface=claim.text,
                    certainty=claim.certainty,
                )
                self._store.store_hypothesis(node)
        else:
            action_type = "stored_weak"

        return LearningAction(
            action_type=action_type,
            node_id=claim.claim_id,
            reason=f"score={score:.3f}",
            new_certainty=score,
        )
