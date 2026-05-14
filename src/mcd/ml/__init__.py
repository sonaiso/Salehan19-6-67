"""ML dataset contracts for governed answer-birth training."""
from __future__ import annotations

from mcd.ml.dataset_schema import (
    CORE_EVIDENCE_RANK_TOKENS,
    THINKING_EVIDENCE_RANK_TOKENS,
    load_answer_birth_training_example_schema,
    load_concept_graph_schema,
    load_governed_trace_schema,
    load_nabhani_features_schema,
    load_json_file,
)
from mcd.ml.example_validator import (
    ExampleValidationError,
    ExampleValidationReport,
    validate_training_example,
)
from mcd.ml.nabhani_features import (
    NabhaniFeatureFrame,
    NabhaniFeatureValidationError,
    NabhaniFeatureValidationReport,
    derive_nabhani_features_from_example,
    nabhani_features_to_training_vector,
    validate_nabhani_features,
)
from mcd.ml.serialization import dump_json, load_json
from mcd.ml.synthetic_generator import (
    CATEGORY_SPECS,
    SyntheticAnswerBirthDatasetGenerator,
    generate_synthetic_answer_birth_dataset,
)

__all__ = [
    "THINKING_EVIDENCE_RANK_TOKENS",
    "CORE_EVIDENCE_RANK_TOKENS",
    "load_json_file",
    "load_answer_birth_training_example_schema",
    "load_concept_graph_schema",
    "load_governed_trace_schema",
    "load_nabhani_features_schema",
    "ExampleValidationError",
    "ExampleValidationReport",
    "validate_training_example",
    "NabhaniFeatureFrame",
    "NabhaniFeatureValidationError",
    "NabhaniFeatureValidationReport",
    "derive_nabhani_features_from_example",
    "validate_nabhani_features",
    "nabhani_features_to_training_vector",
    "CATEGORY_SPECS",
    "SyntheticAnswerBirthDatasetGenerator",
    "generate_synthetic_answer_birth_dataset",
    "dump_json",
    "load_json",
]
