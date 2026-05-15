from mcd.math_governance import (
    PATH_CERTIFICATE,
    PATH_STRONG,
    PATH_ZERO_IN_PATH,
    CandidatePath,
    MetaControlLayer,
    MetaUnit,
)


def _unit(
    raw: str,
    pos: int,
    *,
    layer: str,
    role: str,
    pattern: str = "",
    evidence: list[str] | None = None,
    residuals: list[str] | None = None,
    constraints: dict[str, str] | None = None,
) -> MetaUnit:
    return MetaUnit(
        raw_unit=raw,
        position=pos,
        layer=layer,
        candidate_role=role,
        pattern=pattern,
        evidence=evidence or [],
        residuals=residuals or [],
        constraints=constraints or {},
    )


def _path(
    path_id: str,
    units: list[MetaUnit],
    *,
    passed: list[str] | None = None,
    failed: list[str] | None = None,
    evidence_chain: list[str] | None = None,
    score: float = 0.0,
    residuals: list[str] | None = None,
    rank_components: dict[str, float] | None = None,
    transformations: list[str] | None = None,
) -> CandidatePath:
    return CandidatePath(
        path_id=path_id,
        units=units,
        constraints_passed=passed or [],
        constraints_failed=failed or [],
        evidence_chain=evidence_chain or [],
        score=score,
        residuals=residuals or [],
        rank_components=rank_components
        or {
            "phonetic": 0.9,
            "morphological": 0.9,
            "syntactic": 0.9,
            "semantic": 0.9,
            "context": 0.9,
            "evidence": 0.9,
        },
        transformations=transformations or [],
    )


def test_is_augment_is_path_conditioned_not_absolute():
    mcl = MetaControlLayer()
    path_mafool = _path(
        "p1",
        [_unit("م", 0, layer="template", role="augment", pattern="مفعول")],
    )
    path_root = _path(
        "p2",
        [_unit("م", 0, layer="root", role="root", pattern="")],
    )

    assert mcl.is_augment("م", pattern="مفعول", path=path_mafool) is True
    assert mcl.is_augment("م", pattern="", path=path_root) is False


def test_impossible_detects_same_axis_building_inflection_conflict():
    mcl = MetaControlLayer()
    p = _path(
        "p_conflict",
        [
            _unit("ُ", 2, layer="ending", role="building"),
            _unit("ُ", 2, layer="ending", role="inflectional"),
        ],
        passed=[],
    )

    impossible, reasons = mcl.impossible(p)
    assert impossible is True
    assert any("inflectional_and_building_without_bridge" in r for r in reasons)


def test_govern_filters_impossible_keeps_topk_and_preserves_competing_residuals():
    mcl = MetaControlLayer()

    p1 = _path(
        "p1",
        [_unit("م", 0, layer="template", role="augment", evidence=["wazn"]), _unit("غ", 3, layer="root", role="root", evidence=["root"])],
        evidence_chain=["ctx:agent", "lex:istafala"],
        score=0.9,
        transformations=["T_pattern", "T_derivation"],
        rank_components={
            "phonetic": 0.98,
            "morphological": 0.97,
            "syntactic": 0.95,
            "semantic": 0.95,
            "context": 0.96,
            "evidence": 0.96,
        },
    )
    p2 = _path(
        "p2",
        [_unit("م", 0, layer="template", role="augment", evidence=["wazn"]), _unit("غ", 3, layer="root", role="root", evidence=["root"])],
        evidence_chain=["ctx:patient"],
        score=0.7,
        residuals=["missing_diacritics"],
        rank_components={
            "phonetic": 0.85,
            "morphological": 0.8,
            "syntactic": 0.72,
            "semantic": 0.7,
            "context": 0.65,
            "evidence": 0.7,
        },
    )
    p3 = _path(
        "p3",
        [
            _unit("ُ", 2, layer="ending", role="building"),
            _unit("ُ", 2, layer="ending", role="inflectional"),
        ],
        score=0.95,
    )

    capsule = mcl.govern(input_text="مستغفر", candidate_paths=[p1, p2, p3], top_k=2)

    assert capsule.selected_path is not None
    assert capsule.selected_path.path_id == "p1"
    assert [p.path_id for p in capsule.top_k_paths] == ["p1", "p2"]
    assert [p.path_id for p in capsule.rejected_paths] == ["p3"]
    assert capsule.judgment == "hypothesis"
    assert "competing_path" in capsule.residuals
    assert "competing_path:p2" in capsule.residuals
    assert "rejected_path:p3" in capsule.residuals


def test_zero_in_path_is_internal_status_public_judgment_is_zero():
    mcl = MetaControlLayer()
    p = _path(
        "p_zero",
        [_unit("x", 0, layer="ending", role="building"), _unit("x", 0, layer="ending", role="inflectional")],
    )

    capsule = mcl.govern(input_text="x", candidate_paths=[p], top_k=1)
    assessment = next(a for a in capsule.path_assessments if a.path_id == "p_zero")

    assert assessment.path_status == PATH_ZERO_IN_PATH
    assert capsule.judgment == "zero"


def test_path_certificate_maps_to_public_certificate():
    mcl = MetaControlLayer()
    units = [
        _unit("م", 0, layer="template", role="augment", evidence=["wazn"]),
        _unit("غ", 3, layer="root", role="root", evidence=["root"]),
        _unit("ر", 5, layer="syntax", role="derivational", evidence=["syntax", "corpus", "agreement"]),
    ]
    p = _path(
        "p_cert",
        units,
        evidence_chain=["ctx", "lex", "shahid", "sem", "trace", "proof", "reverse", "gate"],
        transformations=["T_pattern", "T_rank", "T_fold"],
        rank_components={
            "phonetic": 0.99,
            "morphological": 0.99,
            "syntactic": 0.99,
            "semantic": 0.99,
            "context": 0.99,
            "evidence": 0.99,
        },
    )

    capsule = mcl.govern(input_text="مستغفر", candidate_paths=[p], top_k=1)
    assessment = next(a for a in capsule.path_assessments if a.path_id == "p_cert")

    assert assessment.path_status == PATH_CERTIFICATE
    assert capsule.judgment == "certificate"
    assert capsule.governance_gate["passed"] is True
    assert capsule.proof_object is not None
    assert capsule.proof_object.judgment == "certificate"
    assert capsule.reverse_trace["replayable"] is True


def test_haraka_role_supports_mabni_with_i3rab_position_without_conflict():
    mcl = MetaControlLayer()

    role = mcl.haraka_role(
        is_mabni=True,
        has_governing_factor=True,
        syntactic_slot_requires_case=True,
    )
    mode = mcl.inflection_mode(
        is_mabni=True,
        has_i3rab_position=True,
        has_estimated_case=False,
        is_restricted_declinable=False,
    )

    assert role["building_role"] == "building"
    assert role["inflection_role"] == "none"
    assert "mabni_has_position_not_surface_case" in role["residuals"]
    assert mode == "mabni_with_i3rab_position"


def test_unfold_restores_why_not_only_what():
    mcl = MetaControlLayer()
    p = _path(
        "p1",
        [
            _unit("م", 0, layer="template", role="augment", evidence=["lex"]),
            _unit("ك", 1, layer="root", role="root", evidence=["root"]),
        ],
        evidence_chain=["ctx"],
        transformations=["T_pattern"],
    )
    capsule = mcl.govern(input_text="ملك", candidate_paths=[p], top_k=1)

    unfolded = mcl.unfold(capsule)
    assert unfolded["selected_path"]["path_id"] == "p1"
    assert unfolded["trace"]
    assert unfolded["constraints"]["passed"] == []
    assert unfolded["evidence"]
    assert unfolded["proof_object"] is not None
    assert "governance_gate" in unfolded
    assert "reverse_trace" in unfolded
    assert isinstance(unfolded["evidence_objects"], list)
    assert isinstance(unfolded["constraint_objects"], list)
    assert isinstance(unfolded["transition_objects"], list)


def test_certificate_downgrades_when_reverse_trace_is_not_replayable():
    mcl = MetaControlLayer()
    p = _path(
        "p_cert_gate_fail",
        [
            _unit("م", 0, layer="template", role="augment", evidence=["lex:pattern"]),
            _unit("ك", 1, layer="root", role="root", evidence=["root:attested"]),
        ],
        evidence_chain=[
            "ctx:governed",
            "corpus:attested",
            "syntax:agreement",
            "sem:licensed",
            "trace:stable",
            "proof:linked",
            "rank:high",
            "gate:ready",
        ],
        transformations=[],  # no transition replay path => gate should block certificate
        rank_components={
            "phonetic": 0.99,
            "morphological": 0.99,
            "syntactic": 0.99,
            "semantic": 0.99,
            "context": 0.99,
            "evidence": 0.99,
        },
    )
    capsule = mcl.govern(input_text="مكتب", candidate_paths=[p], top_k=1)
    assessment = next(a for a in capsule.path_assessments if a.path_id == "p_cert_gate_fail")

    assert assessment.path_status == PATH_STRONG
    assert capsule.judgment == "hypothesis"
    assert "certificate_blocked" in capsule.residuals
    assert capsule.governance_gate["passed"] is False
    assert "reverse_trace_replayable" in capsule.governance_gate["failures"]


def test_govern_rejects_non_positive_top_k():
    mcl = MetaControlLayer()
    p = _path("p1", [_unit("م", 0, layer="template", role="augment")])
    try:
        mcl.govern(input_text="x", candidate_paths=[p], top_k=0)
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "top_k" in str(exc)
