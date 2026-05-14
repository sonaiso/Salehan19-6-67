from mcd.math_governance.level_schema import ALL_LEVELS
from mcd.patterns import MetaPattern, MetaPatternRegistry, build_layered_pattern_pipeline
from mcd.qualification.layer_sovereignty_registry import LayerSovereigntyRegistry


def test_meta_pattern_registry_round_trip() -> None:
    registry = MetaPatternRegistry()
    meta = MetaPattern(
        meta_id="meta.form_role.default",
        applies_to_layers=("lexeme", "morphology"),
        form_kind="FormState",
        role_kind="RoleState",
        composition_operator="tensor_like",
        required_domain="layer_match",
        required_scope="layer_scope",
        required_rank="HYPOTHESIS",
        closure_schema="chi_L",
        minimum_completion_schema="MC_L",
        governor_schema="governor.L",
        residual_schema="preserve_no_erasure",
        trace_schema="replayable",
        allowed_bridge_schema="explicit_only",
        forbidden_bridge_schema="silent_level_skip",
    )

    registry.register(meta)
    loaded = registry.get("meta.form_role.default")

    assert loaded is not None
    assert loaded.meta_id == "meta.form_role.default"
    assert "morphology" in loaded.applies_to_layers


def test_layer_pipeline_references_layer_sovereignty_registry() -> None:
    sovereignty = LayerSovereigntyRegistry()
    layers = {layer.level: layer for layer in build_layered_pattern_pipeline()}

    assert set(layers) == {level.name for level in ALL_LEVELS}
    morphology_layer = layers["morphology"]
    sovereignty_entry = sovereignty.get("morphology")
    assert sovereignty_entry is not None
    assert morphology_layer.governor == sovereignty_entry.governor
    assert sovereignty_entry.closure_function in morphology_layer.closure_functions
    assert morphology_layer.minimum_completion == sovereignty_entry.minimum_completion
