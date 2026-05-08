import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlparse

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "spec/bayani-knowledge-system.json"
SCHEMA_PATH = ROOT / "schema/bayani-knowledge-system.schema.json"
PROMPT_PATH = ROOT / "docs/prompts/nabhani-mustadil-readiness.prompt.md"
README_PATH = ROOT / "README.md"

ALLOWED_OUTPUTS = ["Certificate", "Hypothesis", "Zero"]
README_REQUIRED_REFERENCES = [
    "docs/prompts/nabhani-mustadil-readiness.prompt.md",
    "spec/bayani-knowledge-system.json",
    "schema/bayani-knowledge-system.schema.json",
    "tests/verify_bayani_repository.py",
]
REQUIRED_SPEC_KEYS = [
    "formal_kernel",
    "knowledge_foundation",
    "ontology",
    "grammar_engine",
    "reasoning_engine",
    "answer_analysis_engine",
    "governance_engine",
    "malakah_methodology",
]
REQUIRED_PROOF_INVARIANTS = [
    "NoCertificateWithBlockingZero",
    "NoClaimWithoutEvidence",
    "NoTransitionWithoutContract",
    "NoLevelSkip",
    "HypothesisMustBeDeclared",
    "NoIrabWithoutAmil",
    "NoMafhumWithoutMantuq",
    "NoLearningWithoutTest",
    "NoSourceFreeExternalClaim",
]
REQUIRED_MALAKAH_MACHINES = [
    "rule_applicability_machine",
    "rule_manat_detector",
    "prior_opinion_filter",
    "epistemic_candidate_generation_machine",
    "failure_predictor_binding",
    "mustadil_competence_score",
]
EXPECTED_READINESS_CHECK_COUNT = 12
EXPECTED_PROGRESSIVE_LEVELS = 10
MIN_ADVERSARIAL_CASES = 10
MIN_INVARIANTS = 15
EXPECTED_EVALUATION_GATES = {
    "GapDetector",
    "LeapDetector",
    "TraceValidator",
    "ProofRankChecker",
    "ZeroGuard",
    "FailurePredictor",
    "ReliabilityScorer",
}
REQUIRED_PROMPT_SECTIONS = [
    "Core Axiom",
    "Formal Function",
    "Formal Kernel",
    "Non-Negotiable Invariants",
    "Mustadil Readiness Check",
    "Allowed Outputs",
    "Required Output Structure",
    "Mathematical Evaluation Layer",
    "Knowledge Storage Architecture",
    "Learning Architecture",
    "GPT-style Answers Policy",
    "Final Governing Rule",
]
PROMPT_DISALLOWED_OUTPUTS_LABEL = "Never Output:"

# PR #1 — formal kernel, reasoning engine, grammar engine, ontology, schema artifacts
FORMAL_KERNEL_EQUATION = "S + D + T + E + Z + C + R + P"
FORMAL_KERNEL_SYMBOLS = {"S", "D", "T", "E", "Z", "C", "R", "P"}
REASONING_ENGINE_CONFLICT_TYPES_COUNT = 10
REASONING_ENGINE_TARJIH_RULES_COUNT = 10
MIN_ONTOLOGY_TOP_TYPES = 5
RECURSIVE_RELATION_SIGNATURE = "R(level_n, level_n+1)"

# PR #2 — answer analysis engine
ANSWER_ANALYSIS_PIPELINE = [
    "Answer Segmentation",
    "Epistemic Candidate Generation",
    "Candidate Ranking",
    "Claim Extraction",
    "Concept Extraction",
    "Relation Extraction",
    "Evidence Detection",
    "Judgment Classification",
    "Mujmal Detection",
    "Bayan Requirement",
    "Proof Check",
    "Status Assignment",
]
ANSWER_ANALYSIS_STATUS_POLICY_KEYS = {"certificate", "hypothesis", "zero"}

# PR #4 — mustadil readiness layer
MIN_BLOCKING_ZEROS = 5
PROOF_RANK_POLICY_REQUIRED_KEYS = {"ranks", "rules"}

# PR #7 — README scope declaration
README_NO_RUNTIME_PHRASE = "دون تنفيذ runtime في هذا المستودع"

# Deep system-correctness tests
RECURSIVE_RELATION_EXAMPLE_COUNT = 7
RECURSIVE_RELATION_INVARIANT_COUNT = 4
DAL_INTEGRITY_RULE = "السياق لا يكسر الدال."
EXCEPTION_REGISTRY_ZERO_TYPES = {"ExceptionWithoutEvidence", "ExceptionOvergeneralization"}
MIN_ELLIPSIS_TYPES = 5
REFERENCE_ZERO_TYPE_REQUIRED = "NoAntecedent"
REQUIRED_TOP_TYPE_FIELDS = {"id", "label", "arabic_label", "definition"}
REQUIRED_CONCEPT_EXAMPLE_FIELDS = {"concept", "ontological_type", "roles"}


def load_json(path):
    """Load and parse a UTF-8 JSON file."""
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def normalize_case(text):
    """Use Unicode case folding for locale-independent comparisons instead of lower()."""
    return text.casefold()


def normalize_prompt_output_line(line):
    """Strip optional Markdown list markers and spaces from one prompt output line."""
    return line.strip(" -")


def is_prompt_separator(line):
    """Return whether a prompt line is only the visual section separator."""
    return set(line.strip()) == {"━"}


def markdown_slug(heading):
    """Build a GitHub-style heading anchor, preserving Arabic letters."""
    # Strip inline HTML so headings with tags resolve to the same anchor text.
    slug = re.sub(r"<[^>]+>", "", heading.strip().lower())
    slug = re.sub(r"[^\w\u0600-\u06ff\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug.strip("-")


def heading_anchors(markdown):
    """Extract Markdown heading anchors for same-page and cross-file link checks."""
    anchors = set()
    for match in re.finditer(r"^#{1,6}\s+(.+)$", markdown, re.MULTILINE):
        anchors.add(markdown_slug(match.group(1)))
    return anchors


def resolve_markdown_link(markdown_path, link_path):
    """Resolve root-absolute and document-relative Markdown link targets."""
    if link_path.startswith("/"):
        return ROOT / link_path.lstrip("/")
    return markdown_path.parent / link_path


class BayaniRepositoryVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_json(SCHEMA_PATH)
        cls.spec = load_json(SPEC_PATH)
        cls.prompt = PROMPT_PATH.read_text(encoding="utf-8")
        cls.readme = README_PATH.read_text(encoding="utf-8")

    def test_schema_is_valid_draft_2020_12(self):
        self.assertEqual(
            self.schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        jsonschema.Draft202012Validator.check_schema(self.schema)

    def test_spec_json_parses(self):
        self.assertIsInstance(load_json(SPEC_PATH), dict)

    def test_schema_json_parses(self):
        self.assertIsInstance(load_json(SCHEMA_PATH), dict)

    def test_spec_matches_schema(self):
        jsonschema.validate(self.spec, self.schema)

    def test_markdown_links_resolve(self):
        for markdown_path in ROOT.rglob("*.md"):
            markdown = markdown_path.read_text(encoding="utf-8")
            anchors = heading_anchors(markdown)
            # Match regular Markdown links while excluding image links.
            for label, target in re.findall(r"(?<!\!)\[([^\]]+)\]\(([^)]+)\)", markdown):
                parsed = urlparse(target)
                if parsed.scheme in {"http", "https", "mailto"}:
                    continue
                link_path = unquote(parsed.path)
                anchor = unquote(parsed.fragment)
                if not link_path:
                    self.assertIn(
                        markdown_slug(anchor),
                        anchors,
                        f"{markdown_path}: broken same-page anchor link {anchor!r} in {target}",
                    )
                    continue
                resolved = resolve_markdown_link(markdown_path, link_path)
                self.assertTrue(resolved.exists(), f"{markdown_path}: broken markdown link {label!r} -> {target}")
                if anchor and resolved.suffix == ".md":
                    linked_anchors = heading_anchors(resolved.read_text(encoding="utf-8"))
                    self.assertIn(markdown_slug(anchor), linked_anchors, f"{markdown_path}: broken anchor {target}")

    def test_readme_references_required_repository_files(self):
        for documented_path in README_REQUIRED_REFERENCES:
            self.assertIn(documented_path, self.readme)
            self.assertTrue((ROOT / documented_path).exists())

    def test_prompt_file_exists(self):
        self.assertTrue(PROMPT_PATH.exists())

    def test_prompt_has_required_sections_in_order(self):
        previous_position = -1
        prompt = normalize_case(self.prompt)
        for section in REQUIRED_PROMPT_SECTIONS:
            position = prompt.find(normalize_case(section))
            self.assertGreater(position, previous_position, f"Missing or out-of-order prompt section: {section}")
            previous_position = position

    def test_spec_includes_required_architectural_layers(self):
        for key in REQUIRED_SPEC_KEYS:
            self.assertIn(key, self.spec)

    def test_prompt_and_spec_share_output_contract(self):
        layer = self.spec["mustadil_readiness_layer"]
        self.assertEqual(layer["allowed_outputs"], ALLOWED_OUTPUTS)
        self.assertEqual(layer["output_contract"]["state_enum"], ALLOWED_OUTPUTS)
        for output in ALLOWED_OUTPUTS:
            self.assertIn(output, self.prompt)
        prompt = normalize_case(self.prompt)
        section_start = prompt.find(normalize_case("Allowed Outputs"))
        section_end = prompt.find(normalize_case("Required Output Structure"))
        self.assertGreaterEqual(section_start, 0)
        self.assertGreater(section_end, section_start)
        allowed_outputs_section = prompt[section_start:section_end].split(
            normalize_case(PROMPT_DISALLOWED_OUTPUTS_LABEL),
            1,
        )[0]
        declared_outputs = []
        # Skip the section heading; the remaining non-separator lines must be the output triad.
        for line in allowed_outputs_section.splitlines()[1:]:
            output_line = normalize_prompt_output_line(line)
            if output_line and not is_prompt_separator(line):
                declared_outputs.append(output_line)
        self.assertEqual(declared_outputs, [normalize_case(output) for output in ALLOWED_OUTPUTS])

    def test_mustadil_readiness_gates_are_complete(self):
        layer = self.spec["mustadil_readiness_layer"]
        self.assertEqual(len(layer["readiness_checks"]), EXPECTED_READINESS_CHECK_COUNT)
        self.assertEqual({gate["name"] for gate in layer["mathematical_evaluation_layer"]}, EXPECTED_EVALUATION_GATES)
        for gate in EXPECTED_EVALUATION_GATES:
            self.assertIn(gate, self.prompt)

    def test_mustadil_spec_tests_cover_all_allowed_outputs(self):
        layer = self.spec["mustadil_readiness_layer"]
        expected_states = {test["expected_state"] for test in layer["spec_tests"]}
        self.assertEqual(expected_states, set(ALLOWED_OUTPUTS))
        self.assertEqual(len({test["id"] for test in layer["spec_tests"]}), len(layer["spec_tests"]))

    def test_governance_test_cases_cover_certificate_hypothesis_and_zero(self):
        cases = self.spec["governance_engine"]["test_cases"]
        expected_states = {case["expected"]["result_type"] for case in cases}
        self.assertEqual(expected_states, set(ALLOWED_OUTPUTS))
        self.assertEqual(len({case["id"] for case in cases}), len(cases))

    def test_learning_events_have_regression_tests(self):
        for event in self.spec["governance_engine"]["learning_events"]:
            self.assertTrue(event["tests_added"], f"{event['id']} must list regression tests")

    def test_progressive_and_adversarial_coverage(self):
        methodology = self.spec["malakah_methodology"]
        levels = methodology["progressive_malakah_test_suite"]["levels"]
        self.assertEqual([level["level"] for level in levels], list(range(1, EXPECTED_PROGRESSIVE_LEVELS + 1)))

        adversarial_cases = methodology["adversarial_epistemic_cases"]
        self.assertGreaterEqual(len(adversarial_cases), MIN_ADVERSARIAL_CASES)
        self.assertTrue(all(case["blocked_result"] == "Certificate" for case in adversarial_cases))
        self.assertEqual(len({case["id"] for case in adversarial_cases}), len(adversarial_cases))

    def test_executable_invariant_coverage_is_declared(self):
        methodology = self.spec["malakah_methodology"]
        coverage = methodology["executable_invariant_coverage"]
        self.assertIn("UntestedInvariant", coverage["outputs"])
        self.assertIn("UnimplementedInvariant", coverage["outputs"])
        self.assertIn("InvariantWithoutTest", coverage["zero_types"])

        invariants = self.spec["governance_engine"]["proof_layer"]["invariants"]
        self.assertGreaterEqual(len(invariants), MIN_INVARIANTS)
        self.assertEqual(len({invariant["id"] for invariant in invariants}), len(invariants))
        self.assertEqual(len({invariant["name"] for invariant in invariants}), len(invariants))

    def test_governance_proof_layer_includes_required_invariants(self):
        invariant_names = {
            invariant["name"] for invariant in self.spec["governance_engine"]["proof_layer"]["invariants"]
        }
        for invariant in REQUIRED_PROOF_INVARIANTS:
            self.assertIn(invariant, invariant_names)

    def test_malakah_methodology_includes_required_machines(self):
        methodology = self.spec["malakah_methodology"]
        for machine in REQUIRED_MALAKAH_MACHINES:
            self.assertIn(machine, methodology)

    def test_con_0001_is_managed_as_hypothesis(self):
        """CON-0001 (vocalization_conflict on كتب) must be managed_ambiguity/Hypothesis.

        Rationale (from existing repo rules):
        - LEARN-0001: unvocalized Arabic token must be HypothesisUntilHarakaOrContext.
        - TEST-0001: كتب without tashkil must yield Hypothesis.
        - tarjih_rules: unresolved conflict blocks Certificate, not produces one.
        Therefore the conflict is not open-ended; it is deterministically managed as
        managed_ambiguity with result_type Hypothesis.
        """
        conflicts = self.spec["reasoning_engine"]["conflicts"]
        con_0001 = next((c for c in conflicts if c["id"] == "CON-0001"), None)
        self.assertIsNotNone(con_0001, "CON-0001 must be present in reasoning_engine.conflicts")
        self.assertEqual(
            con_0001["status"],
            "managed_ambiguity",
            "CON-0001 must have status='managed_ambiguity' (governed by LEARN-0001 and TEST-0001)",
        )
        self.assertEqual(
            con_0001["result_type"],
            "Hypothesis",
            "CON-0001 must yield result_type='Hypothesis' (unvocalized token, per repo rules)",
        )

    # ------------------------------------------------------------------
    # PR #1 — formal kernel, reasoning engine, grammar engine, ontology,
    #          schema artifacts
    # ------------------------------------------------------------------

    def test_formal_kernel_equation_and_components(self):
        kernel = self.spec["formal_kernel"]
        self.assertEqual(kernel["equation"], FORMAL_KERNEL_EQUATION)
        self.assertEqual(set(kernel["components"].keys()), FORMAL_KERNEL_SYMBOLS)

    def test_reasoning_engine_has_conflict_types_and_tarjih_rules(self):
        engine = self.spec["reasoning_engine"]
        self.assertEqual(len(engine["conflict_types"]), REASONING_ENGINE_CONFLICT_TYPES_COUNT)
        self.assertEqual(len(engine["tarjih_rules"]), REASONING_ENGINE_TARJIH_RULES_COUNT)

    def test_grammar_engine_declares_amil_categories(self):
        engine = self.spec["grammar_engine"]
        self.assertIsInstance(engine["amil_categories"], list)
        self.assertGreater(len(engine["amil_categories"]), 0)

    def test_ontology_declares_top_types(self):
        ontology = self.spec["ontology"]
        top_types = ontology["top_types"]
        self.assertGreaterEqual(len(top_types), MIN_ONTOLOGY_TOP_TYPES)
        for top_type in top_types:
            self.assertIn("id", top_type)
            self.assertIn("label", top_type)

    def test_schema_artifacts_declare_upper_entities_laravel_models_and_neo4j_graph(self):
        artifacts = self.spec["schema_artifacts"]
        self.assertGreater(len(artifacts["upper_entities"]), 0)
        self.assertGreater(len(artifacts["laravel_models"]), 0)
        self.assertGreater(len(artifacts["neo4j_graph"]), 0)

    def test_reasoning_engine_recursive_relation_signature(self):
        engine = self.spec["reasoning_engine"]
        self.assertEqual(engine["recursive_relation"]["signature"], RECURSIVE_RELATION_SIGNATURE)

    # ------------------------------------------------------------------
    # PR #2 — answer analysis engine
    # ------------------------------------------------------------------

    def test_answer_analysis_pipeline_is_complete(self):
        engine = self.spec["answer_analysis_engine"]
        self.assertEqual(engine["pipeline"], ANSWER_ANALYSIS_PIPELINE)

    def test_answer_analysis_status_policy_covers_all_outputs(self):
        engine = self.spec["answer_analysis_engine"]
        self.assertEqual(set(engine["status_policy"].keys()), ANSWER_ANALYSIS_STATUS_POLICY_KEYS)

    def test_answer_analysis_examples_cover_all_output_states(self):
        engine = self.spec["answer_analysis_engine"]
        result_types = {ex["result_type"] for ex in engine["example_analyses"]}
        self.assertEqual(result_types, set(ALLOWED_OUTPUTS))

    # ------------------------------------------------------------------
    # PR #4 — mustadil readiness layer (blocking zeros + proof rank)
    # ------------------------------------------------------------------

    def test_mustadil_blocking_zeros_are_declared(self):
        layer = self.spec["mustadil_readiness_layer"]
        blocking_zeros = layer["blocking_zeros"]
        self.assertGreaterEqual(len(blocking_zeros), MIN_BLOCKING_ZEROS)
        for zero in blocking_zeros:
            self.assertIsInstance(zero, str)
            self.assertTrue(zero, "Every blocking zero must be a non-empty string")

    def test_mustadil_proof_rank_policy_has_ranks_and_rules(self):
        layer = self.spec["mustadil_readiness_layer"]
        policy = layer["proof_rank_policy"]
        for key in PROOF_RANK_POLICY_REQUIRED_KEYS:
            self.assertIn(key, policy)
        self.assertGreater(len(policy["ranks"]), 0)
        self.assertGreater(len(policy["rules"]), 0)

    # ------------------------------------------------------------------
    # PR #7 — README scope clarity (no runtime implementation)
    # ------------------------------------------------------------------

    def test_readme_declares_no_runtime_implementation(self):
        self.assertIn(README_NO_RUNTIME_PHRASE, self.readme)

    # ------------------------------------------------------------------
    # Deep system-correctness tests
    # ------------------------------------------------------------------

    def test_ontology_relation_type_declares_binary_binding(self):
        """ONT-RELATION must exist and its definition must assert it binds two or more parties.
        Every reference_rule must declare a non-empty, typed constraints list.
        """
        ont = self.spec["ontology"]
        top_type_ids = {t["id"] for t in ont["top_types"]}
        self.assertIn("ONT-RELATION", top_type_ids)
        relation_type = next(t for t in ont["top_types"] if t["id"] == "ONT-RELATION")
        self.assertIn("طرفين", relation_type["definition"])

        for rule in self.spec["grammar_engine"]["reference_rules"]:
            self.assertIn("constraints", rule, f"{rule['id']} must declare constraints")
            self.assertGreater(len(rule["constraints"]), 0, f"{rule['id']} constraints must be non-empty")
            for constraint in rule["constraints"]:
                self.assertIsInstance(constraint, str)

    def test_recursive_relation_closure_covers_all_levels(self):
        """The recursive relation must document seven level-transitions and four invariants.
        Every example must follow the 'X Certificate → Y Evidence' arrow pattern.
        """
        rr = self.spec["reasoning_engine"]["recursive_relation"]
        self.assertEqual(len(rr["examples"]), RECURSIVE_RELATION_EXAMPLE_COUNT)
        self.assertEqual(len(rr["invariant"]), RECURSIVE_RELATION_INVARIANT_COUNT)
        for example in rr["examples"]:
            self.assertIn("Certificate", example, f"example {example!r} must contain 'Certificate'")
            self.assertIn("Evidence", example, f"example {example!r} must contain 'Evidence'")

    def test_dal_madlool_separation_is_enforced_in_layer_integrity(self):
        """The layer integrity score must guard dal (signifier) from context override.
        amil_rules must distinguish surface effects (dal) from semantic meaning (madlool).
        """
        lis = self.spec["malakah_methodology"]["layer_integrity_score"]
        self.assertIn("context_breaks_dal", lis["checks"])
        self.assertIn(DAL_INTEGRITY_RULE, lis["rules"])
        self.assertIn("dal_integrity", lis["score_fields"])
        self.assertIn("LayerBreak", lis["zero_types"])

        for rule in self.spec["grammar_engine"]["amil_rules"]:
            self.assertIn("input_contract", rule, f"{rule['id']} must have input_contract (dal layer)")
            self.assertIn("effects", rule, f"{rule['id']} must have effects")
            self.assertIn("semantic_effect", rule, f"{rule['id']} must declare semantic_effect (madlool)")

    def test_amil_and_reference_rules_declare_blocking_constraints(self):
        """Every amil_rule must have at least one BLOCKING zero with type and severity.
        Every reference_rule must list constraints; reference_zero_types must be non-empty.
        """
        ge = self.spec["grammar_engine"]
        for rule in ge["amil_rules"]:
            self.assertIn("zeros", rule, f"{rule['id']} must declare zeros")
            for zero in rule["zeros"]:
                self.assertIn("type", zero, f"{rule['id']} zero missing 'type'")
                self.assertIn("severity", zero, f"{rule['id']} zero missing 'severity'")
            blocking = [z for z in rule["zeros"] if z.get("severity") == "BLOCKING"]
            self.assertGreater(len(blocking), 0, f"{rule['id']} must have at least one BLOCKING zero")

        for rule in ge["reference_rules"]:
            self.assertGreater(len(rule.get("constraints", [])), 0, f"{rule['id']} must declare constraints")

        self.assertGreater(len(ge["reference_zero_types"]), 0)

    def test_probabilistic_signals_are_bounded_and_outcome_consistent(self):
        """Confidence and strength values must be in (0, 1]; Certificate requires confidence > 0.5.
        expansion_discipline_machine must accept ProbabilisticSignal as an input.
        """
        ge = self.spec["grammar_engine"]
        for rule in ge["reference_rules"]:
            if "confidence" in rule:
                self.assertGreater(rule["confidence"], 0, f"{rule['id']} confidence must be > 0")
                self.assertLessEqual(rule["confidence"], 1, f"{rule['id']} confidence must be ≤ 1")
                if rule.get("result_type") == "Certificate":
                    self.assertGreater(
                        rule["confidence"],
                        0.5,
                        f"{rule['id']} Certificate result_type requires confidence > 0.5",
                    )

        for rule in ge["qarina_rules"]:
            if "strength" in rule:
                self.assertGreater(rule["strength"], 0, f"{rule['id']} strength must be > 0")
                self.assertLessEqual(rule["strength"], 1, f"{rule['id']} strength must be ≤ 1")

        edm = self.spec["malakah_methodology"]["expansion_discipline_machine"]
        self.assertIn("ProbabilisticSignal", edm["inputs"])

    def test_exception_registry_distinguishes_exceptions_from_zeros(self):
        """Exceptions licensed with rule+evidence+limits are not Zeros.
        Unlicensed exceptions stay Hypothesis; over-generalization is a declared zero_type.
        """
        er = self.spec["malakah_methodology"]["exception_registry"]
        self.assertGreater(len(er["exception_types"]), 0)
        self.assertEqual(set(er["zero_types"]), EXCEPTION_REGISTRY_ZERO_TYPES)
        self.assertTrue(
            any("Exception ليس Zero" in rule for rule in er["rules"]),
            "exception_registry.rules must assert that Exception ≠ Zero when licensed",
        )
        self.assertTrue(
            any("Hypothesis" in rule for rule in er["rules"]),
            "exception_registry.rules must route unlicensed exceptions to Hypothesis",
        )

    def test_ellipsis_rules_require_qarina_for_estimation_and_yield_zero_otherwise(self):
        """Ellipsis without qarina and without estimation capability must produce Zero.
        ellipsis_types must cover at least MIN_ELLIPSIS_TYPES distinct deletion patterns.
        """
        ge = self.spec["grammar_engine"]
        self.assertGreaterEqual(len(ge["ellipsis_types"]), MIN_ELLIPSIS_TYPES)

        for rule in ge["ellipsis_rules"]:
            for field in ("id", "surface", "missing_element", "can_estimate", "result_type"):
                self.assertIn(field, rule, f"{rule.get('id', '?')} must have field {field!r}")
            if not rule["can_estimate"] and not rule.get("qarina_available", False):
                self.assertEqual(
                    rule["result_type"],
                    "Zero",
                    f"{rule['id']}: can_estimate=False + no qarina must yield Zero",
                )

        self.assertGreater(len(ge["ellipsis_ruleset_rules"]), 0)
        self.assertIn(REFERENCE_ZERO_TYPE_REQUIRED, ge["reference_zero_types"])

    def test_ontology_daal_madlool_tree_is_fully_computable(self):
        """Every node in the ontology tree must carry id, label, arabic_label, and definition.
        Every concept_example must reference a valid top_type and declare computable roles.
        """
        ont = self.spec["ontology"]
        valid_ontological_type_labels = {t["label"] for t in ont["top_types"]}

        # Every top_type has all required fields
        for top_type in ont["top_types"]:
            for field in REQUIRED_TOP_TYPE_FIELDS:
                self.assertIn(field, top_type, f"top_type {top_type.get('id', '?')} missing {field!r}")

        for example in ont["concept_examples"]:
            for field in REQUIRED_CONCEPT_EXAMPLE_FIELDS:
                self.assertIn(field, example, f"concept_example {example.get('concept', '?')} missing {field!r}")
            self.assertIn(
                example["ontological_type"],
                valid_ontological_type_labels,
                f"concept {example['concept']!r} references unknown type {example['ontological_type']!r}",
            )
            for role_name, role_data in example["roles"].items():
                self.assertIsInstance(role_data, dict, f"role {role_name!r} must be a dict")
                self.assertIn("required", role_data, f"role {role_name!r} must declare 'required'")
                self.assertIsInstance(role_data["required"], bool)

        self.assertGreater(len(ont["rules"]), 0)
        for rule in ont["rules"]:
            self.assertIsInstance(rule, str)
            self.assertTrue(rule)


if __name__ == "__main__":
    unittest.main(verbosity=2)
