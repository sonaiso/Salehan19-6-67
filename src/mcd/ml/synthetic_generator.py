"""Synthetic governed answer-birth dataset generator (PR #98)."""
from __future__ import annotations

import json
import random
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

from mcd.ml.example_validator import validate_training_example
from mcd.ml.nabhani_features import validate_nabhani_features


# Constitutional epistemic triad: repository law allows no fourth final status.
FINAL_JUDGMENT_TRIAD: tuple[str, ...] = ("zero", "hypothesis", "certificate")
MISSING_TO_RESIDUAL = {
    "reality": "missing_reality",
    "source": "missing_source",
    "prior_information": "missing_prior_information",
    "linking": "missing_linking",
    "correspondence": "missing_correspondence",
    "evidence": "missing_evidence",
}


@dataclass(frozen=True)
class CategorySpec:
    key: str
    intent_status: str


CATEGORY_SPECS: tuple[CategorySpec, ...] = (
    CategorySpec("explicit_intent_valid_rational_path", "explicit"),
    CategorySpec("inferred_intent_uncertainty_preserved", "inferred"),
    CategorySpec("ambiguous_intent_uncertainty_preserved", "ambiguous"),
    CategorySpec("ambiguous_intent_uncertainty_erased", "ambiguous"),
    CategorySpec("missing_intent", "missing"),
    CategorySpec("missing_reality", "explicit"),
    CategorySpec("missing_source", "explicit"),
    CategorySpec("missing_prior_information", "explicit"),
    CategorySpec("missing_linking", "explicit"),
    CategorySpec("invalid_linking", "explicit"),
    CategorySpec("missing_correspondence", "explicit"),
    CategorySpec("missing_evidence", "explicit"),
    CategorySpec("path_complete_evidence_incomplete", "explicit"),
    CategorySpec("complete_birth_final_certificate_blocked", "explicit"),
    CategorySpec("valid_empirical_scientific_method", "explicit"),
    CategorySpec("scientific_method_used_for_worldview", "explicit"),
    CategorySpec("scientific_method_used_for_normative_legal_shari", "explicit"),
    CategorySpec("formal_method_valid_proof_path", "explicit"),
    CategorySpec("formal_method_without_reality_correspondence", "explicit"),
    CategorySpec("linguistic_method_valid_language_output", "explicit"),
    CategorySpec("linguistic_fluency_treated_as_proof", "explicit"),
    CategorySpec("means_as_judgment", "explicit"),
    CategorySpec("missing_means", "explicit"),
    CategorySpec("residual_erasure", "explicit"),
    CategorySpec("final_certificate_with_all_gates", "explicit"),
)


class SyntheticAnswerBirthDatasetGenerator:
    """Create deterministic synthetic governed answer-birth examples."""

    def __init__(self, *, seed: int = 97) -> None:
        self._seed = seed
        self._rng = random.Random(seed)

    def generate_examples(self, *, total_examples: int = 10_000) -> list[dict]:
        if total_examples <= 0:
            raise ValueError("total_examples must be > 0")
        category_keys = self._balanced_categories(total_examples)
        examples: list[dict] = []
        for idx, category_key in enumerate(category_keys, start=1):
            sample = self._build_base_sample(idx=idx, category_key=category_key)
            self._apply_category(sample, category_key=category_key, idx=idx)
            self._finalize_sample(sample)
            self._validate_sample_or_raise(sample)
            examples.append(sample)
        return examples

    def split_examples(
        self,
        examples: list[dict],
        *,
        train_size: int = 8000,
        validation_size: int = 1000,
        test_size: int = 1000,
    ) -> dict[str, list[dict]]:
        expected_total = train_size + validation_size + test_size
        if len(examples) != expected_total:
            raise ValueError(f"split sizes ({expected_total}) do not match examples ({len(examples)})")
        shuffled = list(examples)
        self._rng.shuffle(shuffled)
        train = shuffled[:train_size]
        validation = shuffled[train_size : train_size + validation_size]
        test = shuffled[train_size + validation_size :]
        return {"train": train, "validation": validation, "test": test}

    def write_dataset(
        self,
        output_dir: Path,
        *,
        total_examples: int = 10_000,
        train_size: int = 8000,
        validation_size: int = 1000,
        test_size: int = 1000,
    ) -> dict:
        output_dir.mkdir(parents=True, exist_ok=True)
        examples = self.generate_examples(total_examples=total_examples)
        splits = self.split_examples(
            examples,
            train_size=train_size,
            validation_size=validation_size,
            test_size=test_size,
        )

        split_paths = {
            name: output_dir / f"{name}.jsonl"
            for name in ("train", "validation", "test")
        }
        for split_name, path in split_paths.items():
            self._write_jsonl(path, splits[split_name])

        stats = self.compute_stats(examples)
        stats["seed"] = self._seed
        stats["total_examples"] = len(examples)
        stats["splits"] = {
            "train": len(splits["train"]),
            "validation": len(splits["validation"]),
            "test": len(splits["test"]),
        }
        stats["files"] = {name: str(path) for name, path in split_paths.items()}

        stats_path = output_dir / "stats.json"
        stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {
            "output_dir": str(output_dir),
            "stats_path": str(stats_path),
            "split_paths": {name: str(path) for name, path in split_paths.items()},
            "stats": stats,
        }

    def compute_stats(self, examples: list[dict]) -> dict:
        def _count_tokens(values: list[str]) -> dict[str, int]:
            counter = Counter(values)
            return dict(sorted(counter.items()))

        blocker_counter: Counter[str] = Counter()
        residual_counter: Counter[str] = Counter()
        feature_completeness = {"complete": 0, "incomplete": 0}

        for sample in examples:
            for blocker in sample["expected"]["blockers"]:
                blocker_counter[str(blocker)] += 1
            for residual in sample["expected"]["residuals"]:
                residual_counter[str(residual)] += 1

            if sample["nabhani_features"]["missing_features"]:
                feature_completeness["incomplete"] += 1
            else:
                feature_completeness["complete"] += 1

        return {
            "counts": {
                "intent_status": _count_tokens([s["intent_frame"]["intent_status"] for s in examples]),
                "method_type": _count_tokens([s["thinking_method"]["method_type"] for s in examples]),
                "judgment_domain": _count_tokens([s["nabhani_features"]["judgment_domain"] for s in examples]),
                "output_kind": _count_tokens([s["mentality_frame"]["output_kind"] for s in examples]),
                "means_type": _count_tokens([s["thinking_means"]["means_type"] for s in examples]),
                "has_reality": _count_tokens([str(s["nabhani_features"]["has_reality"]).lower() for s in examples]),
                "has_source": _count_tokens([str(s["nabhani_features"]["has_source"]).lower() for s in examples]),
                "has_prior_information": _count_tokens([str(s["nabhani_features"]["has_prior_information"]).lower() for s in examples]),
                "has_linking": _count_tokens([str(s["nabhani_features"]["has_linking"]).lower() for s in examples]),
                "linking_validity": _count_tokens([s["nabhani_features"]["linking_validity"] for s in examples]),
                "has_correspondence": _count_tokens([str(s["nabhani_features"]["has_correspondence"]).lower() for s in examples]),
                "has_evidence": _count_tokens([str(s["nabhani_features"]["has_evidence"]).lower() for s in examples]),
                "certainty_rank": _count_tokens([s["nabhani_features"]["certainty_rank"] for s in examples]),
                "birth_judgment": _count_tokens([s["expected"]["birth_judgment"] for s in examples]),
                "final_judgment": _count_tokens([s["expected"]["final_judgment"] for s in examples]),
                "blocker": dict(sorted(blocker_counter.items())),
                "residual": dict(sorted(residual_counter.items())),
                "nabhani_feature_completeness": feature_completeness,
            }
        }

    def _balanced_categories(self, total_examples: int) -> list[str]:
        categories = [spec.key for spec in CATEGORY_SPECS]
        repeated = [categories[i % len(categories)] for i in range(total_examples)]
        self._rng.shuffle(repeated)
        return repeated

    def _build_base_sample(self, *, idx: int, category_key: str) -> dict:
        output_kind = "descriptive"
        method_type = "rational"
        sample_id = f"AB-SYN-{idx:05d}"
        means_pool = [
            "llm",
            "database",
            "source_text",
            "experiment",
            "calculator",
            "code",
            "human_input",
            "external_tool",
            "internal_reasoning",
            "model_reasoning",
        ]
        means_type = means_pool[idx % len(means_pool)]
        return {
            "sample_id": sample_id,
            "user_request": f"Synthetic governed request #{idx} ({category_key}).",
            "context": f"synthetic governed answer-birth generation | category:{category_key}",
            "intent_frame": {
                "intent_status": "explicit",
                "normalized_request": "synthetic governed request",
                "inferred_intent": "produce governed answer-birth output",
                "uncertainty_preserved": True,
                "residuals": [],
            },
            "consciousness_frame": {
                "awareness_object": "governed claim",
                "attention_state": "focused",
                "distinction_state": "high",
                "reality_refs": [f"artifact:{idx}"],
                "prior_information_refs": [f"prior:{idx}"],
            },
            "mentality_frame": {
                "base_orientation": "analytic",
                "domain": "synthetic",
                "output_kind": output_kind,
                "worldview_assumptions": [],
            },
            "thinking_method": {
                "method_type": method_type,
                "required_inputs": ["intent", "trace", "evidence"],
                "allowed_outputs": [output_kind],
                "forbidden_outputs": ["worldview", "normative", "legal", "shari"],
                "required_evidence_rank": "medium",
            },
            "thinking_style": {
                "style_type": "analysis",
                "required_method_type": method_type,
            },
            "thinking_means": {
                "means_type": means_type,
                "can_issue_judgment": False,
            },
            "thought_trace": {
                "trace_path_complete": True,
                "trace_evidence_complete": True,
                "trace_certificate_complete": False,
                "intent_ref": f"intent:{sample_id}",
                "consciousness_ref": f"consciousness:{sample_id}",
                "mentality_ref": f"mentality:{sample_id}",
                "method_ref": f"method:{method_type}",
                "style_ref": "style:analysis",
                "means_ref": f"means:{means_type}",
                "language_ref": f"language:{sample_id}",
                "evidence_refs": [f"rank:medium::{sample_id}:ev1"],
                "evidence_rank": {
                    "thinking": "medium",
                    "core": "hypothesis",
                },
            },
            "concept_graph": {
                "nodes": [
                    {"id": "n1", "kind": "user_intent", "label": "governed intent"},
                    {"id": "n2", "kind": "method", "label": method_type},
                    {"id": "n3", "kind": "evidence", "label": "ranked evidence"},
                    {"id": "n4", "kind": "judgment", "label": "hypothesis"},
                ],
                "edges": [
                    {"source": "n1", "target": "n2", "relation": "requires"},
                    {"source": "n3", "target": "n4", "relation": "supports"},
                ],
            },
            "nabhani_features": {
                "has_reality": True,
                "reality_kind": "artifact",
                "reality_status": "present",
                "reality_access_mode": "trace",
                "has_source": True,
                "source_type": "repository_artifact",
                "source_rank": "governed",
                "source_role": "evidence_candidate",
                "has_prior_information": True,
                "prior_information_kind": "project_context",
                "prior_information_sufficiency": "sufficient",
                "has_linking": True,
                "linking_type": "rational_link",
                "linking_validity": "valid",
                "has_correspondence": True,
                "correspondence_type": "direct_match",
                "has_evidence": True,
                "evidence_type": "governed_trace",
                "evidence_sufficiency": "sufficient",
                "evidence_matches_claim_domain": True,
                "method_type": method_type,
                "judgment_domain": "epistemic",
                "thinking_type": "deep",
                "thinking_domain_scope": "rational_general",
                "thinking_topic": "general",
                "matrix_method_alignment": True,
                "matrix_topic_alignment": True,
                "matrix_gate_reality": True,
                "matrix_gate_sense": True,
                "matrix_gate_prior_information": True,
                "matrix_gate_domain": True,
                "matrix_gate_depth": True,
                "matrix_gate_enlightenment": True,
                "matrix_gate_action": True,
                "certainty_rank": "hypothesis",
                "rank_source": "feature_annotation",
                "missing_features": [],
                "feature_residuals": [],
            },
            "language_output": "Governed synthetic output preserving residuals and judgment boundaries.",
            "proof_object_ref": "",
            "governance_gate_passed": False,
            "reverse_trace_ref": "",
            "requested_public_judgment": "hypothesis",
            "expected": {
                "intent_status": "explicit",
                "method_type": method_type,
                "output_kind": output_kind,
                "birth_judgment": "hypothesis",
                "final_judgment": "hypothesis",
                "certificate_eligibility": False,
                "blockers": [],
                "residuals": [],
            },
        }

    def _apply_category(self, sample: dict, *, category_key: str, idx: int) -> None:
        f = sample["nabhani_features"]
        expected = sample["expected"]
        intent = sample["intent_frame"]
        trace = sample["thought_trace"]
        method = sample["thinking_method"]
        mentality = sample["mentality_frame"]

        if category_key == "explicit_intent_valid_rational_path":
            expected["certificate_eligibility"] = True
            f["certainty_rank"] = "strong_evidence"
            trace["evidence_rank"] = {"thinking": "high", "core": "strong_evidence"}
            trace["evidence_refs"] = [f"rank:high::{idx}:ev1"]
            sample["requested_public_judgment"] = "hypothesis"

        elif category_key == "inferred_intent_uncertainty_preserved":
            intent["intent_status"] = "inferred"
            intent["inferred_intent"] = "inferred governed intent"
            intent["uncertainty_preserved"] = True
            intent["residuals"].append("intent_inferred")

        elif category_key == "ambiguous_intent_uncertainty_preserved":
            intent["intent_status"] = "ambiguous"
            intent["uncertainty_preserved"] = True
            intent["residuals"].append("intent_not_fully_explicit")

        elif category_key == "ambiguous_intent_uncertainty_erased":
            intent["intent_status"] = "ambiguous"
            intent["uncertainty_preserved"] = False
            expected["blockers"].append("residual_erasure")
            expected["residuals"].extend(["intent_not_fully_explicit", "residual_erasure"])
            expected["birth_judgment"] = "zero"
            expected["final_judgment"] = "zero"
            f["certainty_rank"] = "zero"
            trace["evidence_rank"] = {"thinking": "none", "core": "zero"}
            trace["evidence_refs"] = []

        elif category_key == "missing_intent":
            intent["intent_status"] = "missing"
            intent["normalized_request"] = ""
            intent["inferred_intent"] = ""
            intent["residuals"].append("missing_intent")
            expected["residuals"].append("missing_intent")
            expected["birth_judgment"] = "zero"
            expected["final_judgment"] = "zero"
            f["certainty_rank"] = "zero"
            trace["evidence_rank"] = {"thinking": "none", "core": "zero"}
            trace["evidence_refs"] = []

        elif category_key == "missing_reality":
            f["has_reality"] = False
            f["reality_status"] = "missing"
            f["reality_access_mode"] = "none"
            sample["consciousness_frame"]["reality_refs"] = []
            expected["final_judgment"] = "zero"
            f["certainty_rank"] = "possibility"
            trace["evidence_rank"] = {"thinking": "low", "core": "possibility"}

        elif category_key == "missing_source":
            f["has_source"] = False
            f["source_type"] = "none"
            f["source_rank"] = "none"
            f["source_role"] = "none"
            expected["final_judgment"] = "zero"
            f["certainty_rank"] = "possibility"
            trace["evidence_rank"] = {"thinking": "low", "core": "possibility"}

        elif category_key == "missing_prior_information":
            f["has_prior_information"] = False
            f["prior_information_kind"] = "none"
            f["prior_information_sufficiency"] = "absent"
            sample["consciousness_frame"]["prior_information_refs"] = []
            expected["final_judgment"] = "hypothesis"
            f["certainty_rank"] = "hypothesis"

        elif category_key == "missing_linking":
            f["has_linking"] = False
            f["linking_type"] = "missing"
            f["linking_validity"] = "missing"
            expected["final_judgment"] = "zero"
            f["certainty_rank"] = "possibility"
            trace["trace_path_complete"] = False
            trace["evidence_rank"] = {"thinking": "low", "core": "possibility"}

        elif category_key == "invalid_linking":
            f["has_linking"] = True
            f["linking_type"] = "invalid_link"
            f["linking_validity"] = "invalid"
            expected["blockers"].append("invalid_linking")
            expected["final_judgment"] = "zero"
            f["certainty_rank"] = "possibility"
            trace["evidence_rank"] = {"thinking": "low", "core": "possibility"}

        elif category_key == "missing_correspondence":
            f["has_correspondence"] = False
            f["correspondence_type"] = "missing"
            expected["final_judgment"] = "zero"
            f["certainty_rank"] = "possibility"
            trace["trace_evidence_complete"] = False
            trace["evidence_rank"] = {"thinking": "low", "core": "possibility"}

        elif category_key == "missing_evidence":
            f["has_evidence"] = False
            f["evidence_type"] = "none"
            f["evidence_sufficiency"] = "absent"
            expected["certificate_eligibility"] = False
            expected["final_judgment"] = "hypothesis"
            f["certainty_rank"] = "hypothesis"
            trace["trace_evidence_complete"] = False
            trace["evidence_refs"] = []
            trace["evidence_rank"] = {"thinking": "medium", "core": "hypothesis"}

        elif category_key == "path_complete_evidence_incomplete":
            trace["trace_path_complete"] = True
            trace["trace_evidence_complete"] = False
            f["has_evidence"] = False
            f["evidence_type"] = "none"
            f["evidence_sufficiency"] = "insufficient"
            expected["residuals"].append("incomplete_evidence_rank")
            expected["certificate_eligibility"] = False
            expected["birth_judgment"] = "hypothesis"
            expected["final_judgment"] = "hypothesis"
            f["certainty_rank"] = "hypothesis"
            trace["evidence_refs"] = []
            trace["evidence_rank"] = {"thinking": "medium", "core": "hypothesis"}

        elif category_key == "complete_birth_final_certificate_blocked":
            trace["trace_path_complete"] = True
            trace["trace_evidence_complete"] = True
            trace["trace_certificate_complete"] = True
            f["has_evidence"] = True
            f["has_correspondence"] = True
            f["evidence_type"] = "governed_trace"
            f["evidence_sufficiency"] = "governed"
            f["certainty_rank"] = "certificate"
            trace["evidence_refs"] = [f"rank:governed::{idx}:ev1"]
            trace["evidence_rank"] = {"thinking": "governed", "core": "certificate"}
            expected["birth_judgment"] = "certificate"
            expected["final_judgment"] = "hypothesis"
            expected["certificate_eligibility"] = True
            expected["residuals"].extend(
                [
                    "certificate_without_proof_object",
                    "certificate_without_governance_gate",
                    "certificate_without_reverse_trace",
                ]
            )
            sample["requested_public_judgment"] = "certificate"

        elif category_key == "valid_empirical_scientific_method":
            method["method_type"] = "scientific"
            method["allowed_outputs"] = ["empirical"]
            method["forbidden_outputs"] = ["worldview", "normative", "legal", "shari"]
            method["required_evidence_rank"] = "high"
            sample["thinking_style"]["required_method_type"] = "scientific"
            sample["thinking_style"]["style_type"] = "experiment"
            mentality["output_kind"] = "empirical"
            f["method_type"] = "scientific"
            f["judgment_domain"] = "empirical"
            f["evidence_type"] = "empirical_evidence"
            f["evidence_sufficiency"] = "sufficient"
            f["certainty_rank"] = "strong_evidence"
            trace["method_ref"] = "method:scientific"
            trace["style_ref"] = "style:experiment"
            trace["evidence_refs"] = [f"rank:high::{idx}:ev1"]
            trace["evidence_rank"] = {"thinking": "high", "core": "strong_evidence"}
            expected["certificate_eligibility"] = True

        elif category_key == "scientific_method_used_for_worldview":
            self._apply_category(sample, category_key="valid_empirical_scientific_method", idx=idx)
            mentality["output_kind"] = "worldview"
            f["judgment_domain"] = "worldview"
            f["evidence_matches_claim_domain"] = False
            expected["blockers"].append("scientific_method_as_worldview")
            expected["residuals"].append("scientific_method_as_worldview")
            expected["certificate_eligibility"] = False
            expected["birth_judgment"] = "zero"
            expected["final_judgment"] = "zero"
            f["certainty_rank"] = "zero"
            trace["evidence_rank"] = {"thinking": "none", "core": "zero"}

        elif category_key == "scientific_method_used_for_normative_legal_shari":
            self._apply_category(sample, category_key="valid_empirical_scientific_method", idx=idx)
            normative_outputs = ["normative", "legal", "shari"]
            chosen = normative_outputs[idx % len(normative_outputs)]
            mentality["output_kind"] = chosen
            f["judgment_domain"] = chosen
            f["evidence_matches_claim_domain"] = False
            expected["blockers"].append("scientific_method_as_normative_judgment")
            expected["residuals"].append("scientific_method_as_normative_judgment")
            expected["certificate_eligibility"] = False
            expected["birth_judgment"] = "zero"
            expected["final_judgment"] = "zero"
            f["certainty_rank"] = "zero"
            trace["evidence_rank"] = {"thinking": "none", "core": "zero"}

        elif category_key == "formal_method_valid_proof_path":
            method["method_type"] = "formal"
            method["allowed_outputs"] = ["formal"]
            method["forbidden_outputs"] = ["worldview", "normative"]
            method["required_evidence_rank"] = "high"
            sample["thinking_style"]["required_method_type"] = "formal"
            sample["thinking_style"]["style_type"] = "proof"
            mentality["output_kind"] = "formal"
            f["method_type"] = "formal"
            f["judgment_domain"] = "formal"
            f["evidence_type"] = "formal_proof"
            f["evidence_sufficiency"] = "sufficient"
            f["certainty_rank"] = "strong_evidence"
            trace["method_ref"] = "method:formal"
            trace["style_ref"] = "style:proof"
            trace["evidence_refs"] = [f"rank:high::{idx}:formal-proof"]
            trace["evidence_rank"] = {"thinking": "high", "core": "strong_evidence"}
            expected["certificate_eligibility"] = True

        elif category_key == "formal_method_without_reality_correspondence":
            self._apply_category(sample, category_key="formal_method_valid_proof_path", idx=idx)
            f["has_reality"] = False
            f["reality_status"] = "missing"
            f["reality_access_mode"] = "none"
            f["has_correspondence"] = False
            f["correspondence_type"] = "missing"
            expected["certificate_eligibility"] = False
            expected["final_judgment"] = "zero"
            f["certainty_rank"] = "possibility"
            trace["trace_evidence_complete"] = False
            trace["evidence_rank"] = {"thinking": "low", "core": "possibility"}

        elif category_key == "linguistic_method_valid_language_output":
            method["method_type"] = "linguistic"
            method["allowed_outputs"] = ["linguistic"]
            method["forbidden_outputs"] = ["worldview", "normative", "legal", "shari"]
            method["required_evidence_rank"] = "medium"
            sample["thinking_style"]["required_method_type"] = "linguistic"
            sample["thinking_style"]["style_type"] = "linguistic_analysis"
            mentality["output_kind"] = "linguistic"
            f["method_type"] = "linguistic"
            f["judgment_domain"] = "linguistic"
            f["evidence_type"] = "source_ref"
            f["evidence_sufficiency"] = "partial"
            f["certainty_rank"] = "hypothesis"
            trace["method_ref"] = "method:linguistic"
            trace["style_ref"] = "style:linguistic_analysis"
            trace["evidence_refs"] = [f"rank:medium::{idx}:ling"]
            trace["evidence_rank"] = {"thinking": "medium", "core": "hypothesis"}

        elif category_key == "linguistic_fluency_treated_as_proof":
            self._apply_category(sample, category_key="linguistic_method_valid_language_output", idx=idx)
            mentality["output_kind"] = "worldview"
            f["judgment_domain"] = "worldview"
            f["evidence_matches_claim_domain"] = False
            expected["blockers"].append("fluent_language_as_proof")
            expected["residuals"].append("fluent_language_as_proof")
            expected["certificate_eligibility"] = False
            expected["birth_judgment"] = "zero"
            expected["final_judgment"] = "zero"
            f["certainty_rank"] = "zero"
            trace["evidence_rank"] = {"thinking": "none", "core": "zero"}

        elif category_key == "means_as_judgment":
            sample["thinking_means"]["means_type"] = "external_tool"
            expected["blockers"].append("means_as_judgment")
            expected["residuals"].append("means_as_judgment")
            expected["birth_judgment"] = "zero"
            expected["final_judgment"] = "zero"
            f["certainty_rank"] = "zero"
            trace["evidence_rank"] = {"thinking": "none", "core": "zero"}

        elif category_key == "missing_means":
            sample["thinking_means"]["means_type"] = "model_reasoning"
            expected["blockers"].append("missing_means")
            expected["residuals"].append("missing_means")
            expected["birth_judgment"] = "zero"
            expected["final_judgment"] = "zero"
            f["certainty_rank"] = "zero"
            trace["evidence_rank"] = {"thinking": "none", "core": "zero"}

        elif category_key == "residual_erasure":
            expected["blockers"].append("residual_erasure")
            expected["residuals"].append("residual_erasure")
            expected["birth_judgment"] = "zero"
            expected["final_judgment"] = "zero"
            f["certainty_rank"] = "zero"
            trace["evidence_rank"] = {"thinking": "none", "core": "zero"}

        elif category_key == "final_certificate_with_all_gates":
            trace["trace_path_complete"] = True
            trace["trace_evidence_complete"] = True
            trace["trace_certificate_complete"] = True
            trace["evidence_refs"] = [f"rank:governed::{idx}:proof"]
            trace["evidence_rank"] = {"thinking": "governed", "core": "certificate"}
            f["has_reality"] = True
            f["has_correspondence"] = True
            f["has_evidence"] = True
            f["evidence_matches_claim_domain"] = True
            f["evidence_type"] = "proof_object"
            f["evidence_sufficiency"] = "governed"
            f["source_rank"] = "proof_object"
            f["source_role"] = "proof"
            f["certainty_rank"] = "certificate"
            expected["birth_judgment"] = "certificate"
            expected["final_judgment"] = "certificate"
            expected["certificate_eligibility"] = True
            sample["proof_object_ref"] = f"proof:{idx}"
            sample["governance_gate_passed"] = True
            sample["reverse_trace_ref"] = f"reverse:{idx}"
            sample["requested_public_judgment"] = "certificate"

        else:
            raise ValueError(f"unsupported category: {category_key}")

    def _finalize_sample(self, sample: dict) -> None:
        features = sample["nabhani_features"]
        expected = sample["expected"]
        intent = sample["intent_frame"]
        self._sync_thinking_matrix(sample)

        missing_features = {
            token
            for token in (
                "reality" if not features["has_reality"] else "",
                "source" if not features["has_source"] else "",
                "prior_information" if not features["has_prior_information"] else "",
                "linking" if not features["has_linking"] else "",
                "correspondence" if not features["has_correspondence"] else "",
                "evidence" if not features["has_evidence"] else "",
            )
            if token
        }
        features["missing_features"] = sorted(missing_features)

        feature_residuals = set(features.get("feature_residuals", []))
        for missing in features["missing_features"]:
            feature_residuals.add(MISSING_TO_RESIDUAL[missing])
        features["feature_residuals"] = sorted(feature_residuals)

        residuals = set(expected.get("residuals", []))
        residuals.update(intent.get("residuals", []))
        residuals.update(features["feature_residuals"])

        expected["residuals"] = sorted(r for r in residuals if r)
        expected["blockers"] = sorted(set(token for token in expected.get("blockers", []) if token))

        expected["intent_status"] = sample["intent_frame"]["intent_status"]
        expected["method_type"] = sample["thinking_method"]["method_type"]
        expected["output_kind"] = sample["mentality_frame"]["output_kind"]

        if expected["birth_judgment"] not in FINAL_JUDGMENT_TRIAD:
            raise ValueError(
                f"birth_judgment violates constitutional triad law: {expected['birth_judgment']!r}; expected {FINAL_JUDGMENT_TRIAD}"
            )
        if expected["final_judgment"] not in FINAL_JUDGMENT_TRIAD:
            raise ValueError(
                f"final_judgment violates constitutional triad law: {expected['final_judgment']!r}; expected {FINAL_JUDGMENT_TRIAD}"
            )

        if expected["birth_judgment"] == "certificate":
            sample["thought_trace"]["trace_path_complete"] = True
            sample["thought_trace"]["trace_evidence_complete"] = True
            features["has_evidence"] = True
            if features["certainty_rank"] not in {"strong_evidence", "certificate"}:
                features["certainty_rank"] = "certificate"

        if expected["final_judgment"] == "certificate":
            sample["proof_object_ref"] = sample["proof_object_ref"] or f"proof:{sample['sample_id']}"
            sample["governance_gate_passed"] = True
            sample["reverse_trace_ref"] = sample["reverse_trace_ref"] or f"reverse:{sample['sample_id']}"
            features["has_reality"] = True
            features["has_correspondence"] = True
            features["has_evidence"] = True
            features["evidence_matches_claim_domain"] = True
            features["certainty_rank"] = "certificate"
            sample["thought_trace"]["trace_path_complete"] = True
            sample["thought_trace"]["trace_evidence_complete"] = True
            sample["thought_trace"]["trace_certificate_complete"] = True
            sample["thought_trace"]["evidence_rank"] = {"thinking": "governed", "core": "certificate"}
            if not sample["thought_trace"]["evidence_refs"]:
                sample["thought_trace"]["evidence_refs"] = [f"rank:governed::{sample['sample_id']}:proof"]

    def _infer_topic_for_sample(self, sample: dict) -> str:
        output_kind = str(sample["mentality_frame"].get("output_kind", "")).strip().lower()
        method_type = str(sample["thinking_method"].get("method_type", "")).strip().lower()
        request = str(sample.get("user_request", "")).strip()

        if method_type == "scientific":
            return "material"
        if output_kind == "worldview":
            return "creed"
        if output_kind in {"normative", "legal", "shari"}:
            return "legislation"
        if output_kind == "linguistic":
            return "concept"
        if "مجتمع" in request or "نهضة" in request:
            return "society"
        return "general"

    def _sync_thinking_matrix(self, sample: dict) -> None:
        features = sample["nabhani_features"]
        method_type = str(sample["thinking_method"].get("method_type", "")).strip().lower()
        judgment_domain = str(features.get("judgment_domain", "")).strip().lower()

        features["thinking_domain_scope"] = (
            "scientific_experimental" if method_type == "scientific" else "rational_general"
        )
        features["thinking_topic"] = self._infer_topic_for_sample(sample)
        if features["thinking_topic"] in {"society", "renaissance"}:
            features["thinking_type"] = "enlightened"
        else:
            features["thinking_type"] = "deep"

        features["matrix_method_alignment"] = not (
            features["thinking_domain_scope"] == "scientific_experimental"
            and judgment_domain in {"worldview", "shari", "normative", "legal"}
        )
        features["matrix_topic_alignment"] = True
        features["matrix_gate_reality"] = bool(features.get("has_reality"))
        features["matrix_gate_sense"] = bool(features.get("has_source"))
        features["matrix_gate_prior_information"] = bool(features.get("has_prior_information"))
        features["matrix_gate_domain"] = bool(features.get("matrix_method_alignment"))
        features["matrix_gate_depth"] = features["thinking_type"] in {"deep", "enlightened"}
        features["matrix_gate_enlightenment"] = (
            features["thinking_type"] == "enlightened"
            or features["thinking_topic"] not in {"society", "renaissance"}
        )
        features["matrix_gate_action"] = bool(sample["thinking_method"].get("allowed_outputs"))

        if not features["matrix_method_alignment"]:
            residuals = set(features.get("feature_residuals", []))
            residuals.add("matrix_method_topic_misalignment")
            features["feature_residuals"] = sorted(residuals)

        expected = sample["expected"]
        certificate_attempted = expected["birth_judgment"] == "certificate" or sample["requested_public_judgment"] == "certificate"
        if expected["final_judgment"] != "certificate" and certificate_attempted:
            if not sample.get("proof_object_ref"):
                expected["residuals"] = sorted(set(expected["residuals"]) | {"certificate_without_proof_object"})
            if not sample.get("governance_gate_passed"):
                expected["residuals"] = sorted(set(expected["residuals"]) | {"certificate_without_governance_gate"})
            if not sample.get("reverse_trace_ref"):
                expected["residuals"] = sorted(set(expected["residuals"]) | {"certificate_without_reverse_trace"})

    def _validate_sample_or_raise(self, sample: dict) -> None:
        if sample["expected"]["birth_judgment"] == "certificate":
            if not sample["thought_trace"]["trace_path_complete"] or not sample["thought_trace"]["trace_evidence_complete"]:
                raise ValueError("birth certificate requires complete path and evidence trace")

        if sample["expected"]["final_judgment"] == "certificate":
            missing_requirements = [
                field
                for field, satisfied in (
                    ("proof_object_ref", bool(sample.get("proof_object_ref"))),
                    ("governance_gate_passed", bool(sample.get("governance_gate_passed"))),
                    ("reverse_trace_ref", bool(sample.get("reverse_trace_ref"))),
                    ("has_reality", bool(sample["nabhani_features"].get("has_reality"))),
                    ("has_correspondence", bool(sample["nabhani_features"].get("has_correspondence"))),
                    ("has_evidence", bool(sample["nabhani_features"].get("has_evidence"))),
                    ("evidence_matches_claim_domain", bool(sample["nabhani_features"].get("evidence_matches_claim_domain"))),
                )
                if not satisfied
            ]
            if missing_requirements:
                raise ValueError(
                    "final certificate sample missing required governance gates: " + ", ".join(missing_requirements)
                )

        features_report = validate_nabhani_features(deepcopy(sample["nabhani_features"]))
        if not features_report.valid:
            details = "; ".join(f"{e.field}: {e.message}" for e in features_report.errors)
            raise ValueError(f"invalid nabhani_features in {sample['sample_id']}: {details}")

        report = validate_training_example(deepcopy(sample))
        if not report.valid:
            details = "; ".join(f"{e.field}: {e.message}" for e in report.errors)
            raise ValueError(f"invalid training example in {sample['sample_id']}: {details}")

        final_judgment = sample["expected"]["final_judgment"]
        if final_judgment not in FINAL_JUDGMENT_TRIAD:
            raise ValueError(f"invalid final_judgment {final_judgment!r}; expected one of {FINAL_JUDGMENT_TRIAD}")

    @staticmethod
    def _write_jsonl(path: Path, samples: list[dict]) -> None:
        lines = [json.dumps(item, ensure_ascii=False, sort_keys=True) for item in samples]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_synthetic_answer_birth_dataset(
    *,
    output_dir: Path,
    seed: int = 97,
    total_examples: int = 10_000,
    train_size: int = 8000,
    validation_size: int = 1000,
    test_size: int = 1000,
) -> dict:
    generator = SyntheticAnswerBirthDatasetGenerator(seed=seed)
    return generator.write_dataset(
        output_dir=output_dir,
        total_examples=total_examples,
        train_size=train_size,
        validation_size=validation_size,
        test_size=test_size,
    )
