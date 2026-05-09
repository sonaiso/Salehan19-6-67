"""NabhaniDecoder — high-level pipeline integrating MCD and NERL.

Pipeline:
  input
  → MCD decode
  → DomainJudge (classify epistemic vs shari)
  → DalMadlulMapper
  → ConceptGrounder
  → RationalMethodJudge
  → CorrespondenceChecker
  → FakeEvidenceDetector
  → ConflictResolver
  → CognitiveMeasureBuilder (if eligible)
  → Final structured answer
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Optional

from mcd.engines.decoder import MinimalCognitiveDecoder
from mcd.knowledge.prior_store import PriorKnowledgeStore
from mcd.knowledge.seed_data import load_seed_data
from mcd.nabhani.cognitive_measure import CognitiveMeasureBuilder
from mcd.nabhani.concept_grounder import ConceptGrounder
from mcd.nabhani.conflict_resolver import ConflictResolver
from mcd.nabhani.correspondence_checker import CorrespondenceChecker
from mcd.nabhani.dal_madlul_mapper import DalMadlulMapper
from mcd.nabhani.domain_judge import DomainJudge
from mcd.nabhani.fake_evidence_detector import FakeEvidenceDetector
from mcd.nabhani.rational_method_judge import RationalMethodJudge


class NabhaniDecoder:
    """Full NERL pipeline on top of MCD."""

    def __init__(self, store: Optional[PriorKnowledgeStore] = None) -> None:
        if store is None:
            store = PriorKnowledgeStore()
            load_seed_data(store)
        self._store = store
        self._mcd = MinimalCognitiveDecoder(store=store)
        self._domain_judge = DomainJudge()
        self._dal_mapper = DalMadlulMapper()
        self._grounder = ConceptGrounder()
        self._rational_judge = RationalMethodJudge()
        self._corr_checker = CorrespondenceChecker()
        self._fake_detector = FakeEvidenceDetector()
        self._conflict_resolver = ConflictResolver()
        self._measure_builder = CognitiveMeasureBuilder()

    def decode(self, text: str) -> Dict[str, Any]:
        # --- Step 1: MCD ---
        mcd_output = self._mcd.decode(text)
        mcd_certainty: float = mcd_output.certainty["score"]

        # --- Step 2: Domain classification ---
        domain_judgment = self._domain_judge.classify_text(text)

        # --- Step 3: Dal-Madlul mapping ---
        dal_madlul = self._dal_mapper.map_text(text, self._store)

        # --- Step 4: Concept grounding (per word) ---
        words = text.split()
        grounded_concepts = [self._grounder.ground(w, self._store) for w in words]

        # --- Step 5: Build claim dict for NERL engines ---
        prior_info: Optional[str] = None
        if mcd_output.claims:
            first_claim = mcd_output.claims[0]
            prior_info = (first_claim.get("prior_information") or [None])[0] if isinstance(first_claim.get("prior_information"), list) else first_claim.get("prior_information")

        sense_source: Optional[str] = None
        for node in mcd_output.nodes:
            hint = node.get("features", {}).get("semantic_hint")
            if hint:
                sense_source = hint
                break
        if not sense_source and mcd_certainty > 0.50:
            sense_source = "linguistic"

        claim_dict: Dict[str, Any] = {
            "text": text,
            "target_reality": mcd_output.nodes[0]["surface"] if mcd_output.nodes else None,
            "sense_source": sense_source,
            "prior_information": prior_info,
            "relation_chain": mcd_output.relations if mcd_output.relations else None,
            "correspondence_test": bool(mcd_output.relations),
            "evidence": [{"source_type": "linguistic", "strength": mcd_certainty}] if mcd_certainty > 0.0 else [],
            "certainty": mcd_certainty,
            "domain": domain_judgment.domain,
        }

        # --- Step 6: Rational method judgment ---
        rational_judgment = self._rational_judge.judge(claim_dict)

        # --- Step 7: Correspondence ---
        reality_ctx = " ".join(n["surface"] for n in mcd_output.nodes)
        correspondence = self._corr_checker.check(
            text,
            reality=reality_ctx,
            prior_store=self._store,
            relations=mcd_output.relations,
        )

        # --- Step 8: Fake evidence ---
        fake_report = self._fake_detector.detect(claim_dict)

        # --- Step 9: Conflict resolution ---
        conflict = self._conflict_resolver.resolve(mcd_output.claims)

        # --- Step 10: Measure ---
        measures_created: List[Dict[str, Any]] = []
        measure_claim: Dict[str, Any] = {
            "text": text,
            "certainty": mcd_certainty,
            "evidence_strength": mcd_certainty,
            "domain": domain_judgment.domain,
            "has_conflict": conflict.conflict_type not in ("none",),
        }
        measure = self._measure_builder.build(measure_claim)
        if measure:
            measures_created.append(asdict(measure))

        # --- Step 11: Epistemic status ---
        epistemic_status = self._determine_status(
            domain_judgment, rational_judgment, mcd_certainty, conflict
        )

        return {
            "input": text,
            "mcd_analysis": {
                "normalized": mcd_output.normalized,
                "nodes": mcd_output.nodes,
                "relations": mcd_output.relations,
                "answer": mcd_output.answer,
            },
            "domain": {
                "judgment_type": domain_judgment.judgment_type,
                "status": domain_judgment.status,
                "can_reason_without_revelation": domain_judgment.can_reason_without_revelation,
                "explanation": domain_judgment.explanation,
            },
            "dal_madlul": [
                {
                    "dal": m.dal,
                    "madlul": m.madlul,
                    "concept": m.concept,
                    "grounding_status": m.grounding_status,
                    "dalalah_type": m.dalalah_type,
                }
                for m in dal_madlul
            ],
            "grounded_concepts": [
                {
                    "name": g.name,
                    "status": g.status,
                    "certainty": g.certainty,
                    "grounded_reality": g.grounded_reality,
                }
                for g in grounded_concepts
            ],
            "claims": mcd_output.claims,
            "rational_judgment": {
                "accepted": rational_judgment.accepted,
                "status": rational_judgment.status,
                "missing_requirements": rational_judgment.missing_requirements,
                "violated_axioms": rational_judgment.violated_axioms,
                "explanation": rational_judgment.explanation,
                "certainty_hint": rational_judgment.certainty_hint,
            },
            "correspondence": {
                "match_score": correspondence.match_score,
                "match_type": correspondence.match_type,
                "contradictions": correspondence.contradictions,
                "explanation": correspondence.explanation,
            },
            "fake_evidence_report": {
                "has_fake_evidence": fake_report.has_fake_evidence,
                "detected_types": fake_report.detected_types,
                "severity": fake_report.severity,
                "explanation": fake_report.explanation,
            },
            "conflicts": [
                {
                    "conflict_type": conflict.conflict_type,
                    "resolution_strategy": conflict.resolution_strategy,
                    "explanation": conflict.explanation,
                }
            ],
            "certainty": {
                "score": mcd_certainty,
                "level": mcd_output.certainty["level"],
            },
            "measures_created": measures_created,
            "final_answer": mcd_output.answer,
            "epistemic_status": epistemic_status,
        }

    # ------------------------------------------------------------------

    @staticmethod
    def _determine_status(
        domain_judgment: Any,
        rational_judgment: Any,
        certainty_score: float,
        conflict: Any,
    ) -> str:
        # Shari claims without revelation evidence are always suspended
        if (
            domain_judgment.judgment_type == "normative_shari"
            and domain_judgment.status == "no_shari_ruling_available"
        ):
            return "suspended"

        if rational_judgment.status == "rejected":
            return "rejected"

        if certainty_score >= 0.90:
            return "verified"
        if certainty_score >= 0.75:
            return "probable"
        if certainty_score >= 0.60:
            return "hypothesis"

        if rational_judgment.status == "suspended":
            return "suspended"

        return "rejected"
