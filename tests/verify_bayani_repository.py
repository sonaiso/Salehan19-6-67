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


def load_json(path):
    """Load and parse a UTF-8 JSON file."""
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def normalized(text):
    """Normalize text for case-insensitive comparison."""
    return text.casefold()


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
        prompt = normalized(self.prompt)
        for section in REQUIRED_PROMPT_SECTIONS:
            position = prompt.find(normalized(section))
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
        prompt = normalized(self.prompt)
        section_start = prompt.find(normalized("Allowed Outputs"))
        section_end = prompt.find(normalized("Required Output Structure"))
        self.assertGreaterEqual(section_start, 0)
        self.assertGreater(section_end, section_start)
        allowed_outputs_section = prompt[section_start:section_end].split("never output:", 1)[0]
        declared_outputs = [
            line.strip(" -")
            for line in allowed_outputs_section.splitlines()[1:]
            if line.strip(" -") and set(line.strip()) != {"━"}
        ]
        self.assertEqual(declared_outputs, [normalized(output) for output in ALLOWED_OUTPUTS])

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
