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
DECODER_PROMPT_PATH = ROOT / "docs/prompts/mustadil-decoder-pipeline.prompt.md"
README_PATH = ROOT / "README.md"

ALLOWED_OUTPUTS = ["Certificate", "Hypothesis", "Zero"]
README_REQUIRED_REFERENCES = [
    "docs/prompts/nabhani-mustadil-readiness.prompt.md",
    "docs/prompts/mustadil-decoder-pipeline.prompt.md",
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
    "mustadil_decoder_pipeline",
    "prompt_type_classifier",
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

# Mustadil Decoder Pipeline constants
REQUIRED_PIPELINE_LAYERS = [
    "reality_grounding_layer",
    "prior_opinion_filter_layer",
    "differentiation_layer",
    "essence_assignment_layer",
    "domain_assignment_layer",
    "relational_mapping_layer",
    "arabic_operator_layer",
    "binding_layer",
    "concept_formation_layer",
    "judgment_formation_layer",
    "signifier_analysis_layer",
    "signified_analysis_layer",
    "signifier_signified_relation_layer",
    "mantuq_layer",
    "mafhoom_layer",
    "general_specific_layer",
    "absolute_restricted_layer",
    "causal_juridical_relations_layer",
    "tahqeeq_manat_layer",
    "application_layer",
    "epistemic_audit_layer",
]
REQUIRED_PIPELINE_INVARIANT_NAMES = [
    "NoJudgmentBeforeEssenceAssignment",
    "NoApplicationWithoutTahqeqManat",
    "NoPriorOpinionAsEvidence",
    "NoMafhumStrongerThanMantuq",
    "NoIllahWithoutValidation",
    "NoBayaniLinguisticBeforeSemanticRelationalComplete",
    "NoJudgmentFormationBeforeEssenceDomainRelationsResolved",
]
EPISTEMIC_AUDIT_CERTAINTY_MAP_FIELDS = [
    "text_existence",
    "word_meaning",
    "scope",
    "external_application",
]
REQUIRED_DECODER_PROMPT_SECTIONS = [
    "Pipeline Order",
    "Golden Rule",
    "Layer 1",
    "Layer 21",
    "Pipeline Invariants",
    "Epistemic Audit",
    "Group Structure",
    "Prompt Type Classification",
]

# Layer-group membership map (used by group tests)
PIPELINE_LAYER_GROUPS = {
    "epistemic_existence": [
        "reality_grounding_layer",
        "prior_opinion_filter_layer",
    ],
    "semantic_relational": [
        "differentiation_layer",
        "essence_assignment_layer",
        "domain_assignment_layer",
        "relational_mapping_layer",
        "arabic_operator_layer",
        "binding_layer",
    ],
    "bayani_linguistic": [
        "concept_formation_layer",
        "judgment_formation_layer",
        "signifier_analysis_layer",
        "signified_analysis_layer",
        "signifier_signified_relation_layer",
        "mantuq_layer",
        "mafhoom_layer",
    ],
    "usuli_application": [
        "general_specific_layer",
        "absolute_restricted_layer",
        "causal_juridical_relations_layer",
        "tahqeeq_manat_layer",
        "application_layer",
    ],
    "audit": [
        "epistemic_audit_layer",
    ],
}
REQUIRED_GROUP_IDS = list(PIPELINE_LAYER_GROUPS.keys())

# Prompt Type Classifier constants
REQUIRED_PROMPT_TYPE_IDS = [
    "PT-01",
    "PT-02",
    "PT-03",
    "PT-04",
    "PT-05",
    "PT-06",
    "PT-07",
    "PT-08",
    "PT-09",
    "PT-10",
]
PROMPT_TYPE_REQUIRED_FIELDS = [
    "id",
    "name",
    "arabic_name",
    "example",
    "jump_risk",
    "processing_layer",
    "processing_flow",
    "constraint",
]
# Each of these prompt types must route through a specific pipeline layer
PROMPT_TYPE_LAYER_MAP = {
    "PT-01": "reality_grounding_layer",
    "PT-02": "essence_assignment_layer",
    "PT-03": "causal_juridical_relations_layer",
    "PT-04": "relational_mapping_layer",
    "PT-05": "arabic_operator_layer",
    "PT-06": "mantuq_layer",
    "PT-07": "mantuq_layer",   # mafhoom analysis begins from mantuq as prerequisite
    "PT-08": "general_specific_layer",
    "PT-09": "causal_juridical_relations_layer",
    "PT-10": "application_layer",
}
# PT-10 (Application) must reference tahqeeq al-manat in its processing_flow
PROMPT_TYPES_REQUIRING_TAHQEEQ_IN_FLOW = {"PT-10"}


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
        cls.decoder_prompt = DECODER_PROMPT_PATH.read_text(encoding="utf-8")
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
    # Mustadil Decoder Pipeline — spec structure
    # ------------------------------------------------------------------

    def test_decoder_pipeline_present_in_spec(self):
        self.assertIn("mustadil_decoder_pipeline", self.spec)

    def test_decoder_pipeline_has_all_21_layers(self):
        pipeline = self.spec["mustadil_decoder_pipeline"]
        for layer_key in REQUIRED_PIPELINE_LAYERS:
            self.assertIn(layer_key, pipeline, f"Missing pipeline layer: {layer_key}")

    def test_decoder_pipeline_order_matches_required_layers(self):
        pipeline = self.spec["mustadil_decoder_pipeline"]
        self.assertEqual(pipeline["pipeline_order"], REQUIRED_PIPELINE_LAYERS)

    def test_decoder_pipeline_layers_have_ascending_order(self):
        pipeline = self.spec["mustadil_decoder_pipeline"]
        for expected_order, layer_key in enumerate(REQUIRED_PIPELINE_LAYERS, start=1):
            layer = pipeline[layer_key]
            self.assertEqual(
                layer["layer_order"],
                expected_order,
                f"Layer {layer_key} must have layer_order={expected_order}",
            )

    def test_decoder_pipeline_layer_required_fields(self):
        pipeline = self.spec["mustadil_decoder_pipeline"]
        for layer_key in REQUIRED_PIPELINE_LAYERS:
            layer = pipeline[layer_key]
            for field in ("layer_order", "name", "purpose", "inputs", "outputs", "zero_types"):
                self.assertIn(field, layer, f"Layer {layer_key} missing field: {field}")
            self.assertGreater(len(layer["inputs"]), 0, f"Layer {layer_key} inputs must not be empty")
            self.assertGreater(len(layer["outputs"]), 0, f"Layer {layer_key} outputs must not be empty")

    def test_decoder_pipeline_has_golden_rule(self):
        pipeline = self.spec["mustadil_decoder_pipeline"]
        self.assertIn("golden_rule", pipeline)
        self.assertGreater(len(pipeline["golden_rule"]), 10)

    def test_decoder_pipeline_invariants_are_complete(self):
        pipeline = self.spec["mustadil_decoder_pipeline"]
        invariants = pipeline["pipeline_invariants"]
        invariant_names = {inv["name"] for inv in invariants}
        for required_name in REQUIRED_PIPELINE_INVARIANT_NAMES:
            self.assertIn(required_name, invariant_names, f"Missing pipeline invariant: {required_name}")
        ids = [inv["id"] for inv in invariants]
        self.assertEqual(len(ids), len(set(ids)), "Pipeline invariant IDs must be unique")

    def test_epistemic_audit_layer_has_certainty_map_fields(self):
        audit = self.spec["mustadil_decoder_pipeline"]["epistemic_audit_layer"]
        self.assertIn("certainty_map_fields", audit)
        for field in EPISTEMIC_AUDIT_CERTAINTY_MAP_FIELDS:
            self.assertIn(
                field,
                audit["certainty_map_fields"],
                f"epistemic_audit_layer.certainty_map_fields missing: {field}",
            )

    def test_epistemic_audit_layer_output_template_has_certainty_map(self):
        audit = self.spec["mustadil_decoder_pipeline"]["epistemic_audit_layer"]
        self.assertIn("output_template", audit)
        template = audit["output_template"]
        self.assertIn("certainty_map", template)
        for field in EPISTEMIC_AUDIT_CERTAINTY_MAP_FIELDS:
            self.assertIn(field, template["certainty_map"])

    # ------------------------------------------------------------------
    # Mustadil Decoder Pipeline — decoder prompt file
    # ------------------------------------------------------------------

    def test_decoder_prompt_file_exists(self):
        self.assertTrue(DECODER_PROMPT_PATH.exists())

    def test_decoder_prompt_has_required_sections(self):
        prompt = normalize_case(self.decoder_prompt)
        for section in REQUIRED_DECODER_PROMPT_SECTIONS:
            self.assertIn(
                normalize_case(section),
                prompt,
                f"Decoder prompt missing section: {section}",
            )

    def test_decoder_prompt_references_golden_rule(self):
        self.assertIn(normalize_case("Golden Rule"), normalize_case(self.decoder_prompt))

    def test_decoder_prompt_references_allowed_outputs(self):
        for output in ALLOWED_OUTPUTS:
            self.assertIn(output, self.decoder_prompt)

    # ------------------------------------------------------------------
    # Layer Groups — spec structure and assignment
    # ------------------------------------------------------------------

    def test_pipeline_has_five_layer_groups(self):
        pipeline = self.spec["mustadil_decoder_pipeline"]
        self.assertIn("layer_groups", pipeline)
        group_ids = [g["id"] for g in pipeline["layer_groups"]]
        for required_id in REQUIRED_GROUP_IDS:
            self.assertIn(required_id, group_ids, f"Missing layer group: {required_id}")
        self.assertEqual(len(group_ids), 5)

    def test_layer_groups_cover_all_21_layers(self):
        pipeline = self.spec["mustadil_decoder_pipeline"]
        covered = set()
        for group in pipeline["layer_groups"]:
            for layer_key in group["layers"]:
                self.assertNotIn(layer_key, covered, f"Layer {layer_key} appears in more than one group")
                covered.add(layer_key)
        self.assertEqual(covered, set(REQUIRED_PIPELINE_LAYERS))

    def test_each_layer_has_layer_group_field(self):
        pipeline = self.spec["mustadil_decoder_pipeline"]
        for layer_key in REQUIRED_PIPELINE_LAYERS:
            layer = pipeline[layer_key]
            self.assertIn("layer_group", layer, f"Layer {layer_key} missing layer_group field")
            self.assertIn(
                layer["layer_group"],
                REQUIRED_GROUP_IDS,
                f"Layer {layer_key} has unknown layer_group: {layer['layer_group']}",
            )

    def test_layer_group_assignments_match_expected(self):
        pipeline = self.spec["mustadil_decoder_pipeline"]
        for group_id, expected_layers in PIPELINE_LAYER_GROUPS.items():
            for layer_key in expected_layers:
                actual_group = pipeline[layer_key]["layer_group"]
                self.assertEqual(
                    actual_group,
                    group_id,
                    f"Layer {layer_key}: expected group={group_id}, got {actual_group}",
                )

    def test_semantic_relational_group_completes_before_bayani_linguistic(self):
        """All semantic_relational layers must have lower layer_order than all bayani_linguistic layers."""
        pipeline = self.spec["mustadil_decoder_pipeline"]
        sr_orders = [pipeline[lk]["layer_order"] for lk in PIPELINE_LAYER_GROUPS["semantic_relational"]]
        bl_orders = [pipeline[lk]["layer_order"] for lk in PIPELINE_LAYER_GROUPS["bayani_linguistic"]]
        self.assertLess(
            max(sr_orders),
            min(bl_orders),
            "All semantic_relational layers must finish before any bayani_linguistic layer starts",
        )

    def test_essence_domain_relations_precede_judgment_formation(self):
        """essence_assignment, domain_assignment, relational_mapping must all precede judgment_formation_layer."""
        pipeline = self.spec["mustadil_decoder_pipeline"]
        prerequisite_layers = ["essence_assignment_layer", "domain_assignment_layer", "relational_mapping_layer"]
        judgment_order = pipeline["judgment_formation_layer"]["layer_order"]
        for prereq in prerequisite_layers:
            prereq_order = pipeline[prereq]["layer_order"]
            self.assertLess(
                prereq_order,
                judgment_order,
                f"{prereq} (order {prereq_order}) must precede judgment_formation_layer (order {judgment_order})",
            )

    def test_application_layer_follows_tahqeeq_manat(self):
        pipeline = self.spec["mustadil_decoder_pipeline"]
        tahqeeq_order = pipeline["tahqeeq_manat_layer"]["layer_order"]
        application_order = pipeline["application_layer"]["layer_order"]
        self.assertLess(
            tahqeeq_order,
            application_order,
            "tahqeeq_manat_layer must precede application_layer",
        )

    def test_layer_groups_have_required_fields(self):
        pipeline = self.spec["mustadil_decoder_pipeline"]
        for group in pipeline["layer_groups"]:
            for field in ("id", "name", "description", "layers", "constraint"):
                self.assertIn(field, group, f"Group {group.get('id','?')} missing field: {field}")
            self.assertGreater(len(group["layers"]), 0)
            self.assertGreater(len(group["constraint"]), 10)

    # ------------------------------------------------------------------
    # Prompt Type Classifier — spec structure and coverage
    # ------------------------------------------------------------------

    def test_prompt_type_classifier_present_in_spec(self):
        self.assertIn("prompt_type_classifier", self.spec)
        ptc = self.spec["prompt_type_classifier"]
        for field in ("purpose", "governing_rule", "types", "pre_answer_classification_flow"):
            self.assertIn(field, ptc, f"prompt_type_classifier missing field: {field}")

    def test_prompt_type_classifier_has_ten_types(self):
        ptc = self.spec["prompt_type_classifier"]
        type_ids = [t["id"] for t in ptc["types"]]
        for required_id in REQUIRED_PROMPT_TYPE_IDS:
            self.assertIn(required_id, type_ids, f"Missing prompt type: {required_id}")
        self.assertEqual(len(type_ids), 10, "Exactly 10 prompt types are required")
        self.assertEqual(len(type_ids), len(set(type_ids)), "Prompt type IDs must be unique")

    def test_prompt_types_have_required_fields(self):
        ptc = self.spec["prompt_type_classifier"]
        for pt in ptc["types"]:
            for field in PROMPT_TYPE_REQUIRED_FIELDS:
                self.assertIn(field, pt, f"Prompt type {pt.get('id','?')} missing field: {field}")
            self.assertGreater(
                len(pt["processing_flow"]),
                1,
                f"Prompt type {pt['id']} processing_flow must have at least 2 steps",
            )
            self.assertGreater(
                len(pt["jump_risk"]),
                5,
                f"Prompt type {pt['id']} jump_risk must be non-trivial",
            )

    def test_prompt_type_layer_assignments_are_valid_pipeline_layers(self):
        """Each prompt type's processing_layer must be a known pipeline layer key."""
        ptc = self.spec["prompt_type_classifier"]
        for pt in ptc["types"]:
            self.assertIn(
                pt["processing_layer"],
                REQUIRED_PIPELINE_LAYERS,
                f"Prompt type {pt['id']} references unknown processing_layer: {pt['processing_layer']}",
            )

    def test_prompt_type_layer_assignments_match_expected(self):
        """Spot-check that specific prompt types map to the correct pipeline layers."""
        ptc = self.spec["prompt_type_classifier"]
        by_id = {t["id"]: t for t in ptc["types"]}
        for type_id, expected_layer in PROMPT_TYPE_LAYER_MAP.items():
            self.assertEqual(
                by_id[type_id]["processing_layer"],
                expected_layer,
                f"Prompt type {type_id}: expected processing_layer={expected_layer}",
            )

    def test_application_prompt_type_requires_tahqeeq_constraint(self):
        """PT-10 (Application) must mention tahqeeq al-manat in its processing_flow."""
        ptc = self.spec["prompt_type_classifier"]
        by_id = {t["id"]: t for t in ptc["types"]}
        pt10 = by_id["PT-10"]
        flow_text = " ".join(pt10["processing_flow"]).casefold()
        self.assertIn(
            "tahqeeq",
            flow_text,
            "PT-10 (Application) processing_flow must reference tahqeeq al-manat",
        )

    def test_mafhoom_prompt_type_references_mantuq(self):
        """PT-07 (Mafhoom) processing_flow must reference mantuq as a prerequisite."""
        ptc = self.spec["prompt_type_classifier"]
        by_id = {t["id"]: t for t in ptc["types"]}
        pt07 = by_id["PT-07"]
        flow_text = " ".join(pt07["processing_flow"]).casefold()
        self.assertIn(
            "منطوق",
            flow_text,
            "PT-07 (Mafhoom) processing_flow must reference mantuq",
        )

    def test_prompt_type_governing_rule_is_non_trivial(self):
        ptc = self.spec["prompt_type_classifier"]
        self.assertGreater(len(ptc["governing_rule"]), 20)

    def test_pre_answer_classification_flow_has_all_ten_types(self):
        ptc = self.spec["prompt_type_classifier"]
        flow = ptc["pre_answer_classification_flow"]
        self.assertGreaterEqual(len(flow), 10, "pre_answer_classification_flow must have at least 10 steps")


if __name__ == "__main__":
    unittest.main(verbosity=2)
