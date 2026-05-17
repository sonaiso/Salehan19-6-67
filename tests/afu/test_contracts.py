"""Tests for the AFU PR 1 contracts.

These tests pin the constitutional invariants of the contracts so
later PRs (registry, stages, runner, property tests) inherit a stable
spine.
"""
from __future__ import annotations

import dataclasses

import pytest

from mcd.afu import AFU_CONTRACT_VERSION, AFU_SCHEMA_VERSION
from mcd.afu.contracts import (
    AFUContractError,
    ALLOWED_PUBLIC_RANKS,
    AnswerPlan,
    EpistemicRank,
    LicensedOutput,
    LicensedResponse,
    LinkedUnderstanding,
    Obligations,
    PriorInformationFilter,
    PromptReality,
    ResponseAudit,
    TraceStep,
    UnderstandingJudgment,
    UnderstandingPayload,
    normalize_rank,
)


# ---------------------------------------------------------------------------
# Builders for a complete, well-formed pipeline (used by several tests)
# ---------------------------------------------------------------------------


def _reality() -> PromptReality:
    return PromptReality(
        raw_text="السلام عليكم",
        normalized_text="السلام عليكم",
        language="ar",
        has_arabic=True,
        has_diacritics=False,
        explicit_segments=("السلام", "عليكم"),
        user_stated_goal="greeting",
        rank=EpistemicRank.HYPOTHESIS,
    )


def _filter(allowed=("project rule X",), blocked=("assistant bias Y",)) -> PriorInformationFilter:
    return PriorInformationFilter(
        allowed_prior_information=allowed,
        blocked_prior_opinions=blocked,
        rank=EpistemicRank.HYPOTHESIS,
    )


def _linked(reality: PromptReality, filt: PriorInformationFilter) -> LinkedUnderstanding:
    return LinkedUnderstanding(
        prompt_reality=reality,
        prior_filter=filt,
        linked_prior_information=filt.allowed_prior_information,
        linked_summary="linked",
        rank=EpistemicRank.HYPOTHESIS,
    )


def _judgment(certified: bool = False) -> UnderstandingJudgment:
    return UnderstandingJudgment(
        main_judgment="user greets",
        supporting_evidence=("السلام",),
        rejected_interpretations=("user is asking a question",),
        rank=EpistemicRank.CERTIFICATE if certified else EpistemicRank.HYPOTHESIS,
    )


def _payload(
    judgment_rank: EpistemicRank = EpistemicRank.HYPOTHESIS,
    payload_rank: EpistemicRank = EpistemicRank.HYPOTHESIS,
) -> UnderstandingPayload:
    r = _reality()
    f = _filter()
    return UnderstandingPayload(
        prompt_reality=r,
        prior_filter=f,
        linked_understanding=_linked(r, f),
        judgment=UnderstandingJudgment(
            main_judgment="user greets",
            supporting_evidence=("السلام",),
            rank=judgment_rank,
        ),
        explicit_request=("greet back",),
        task_type="greeting",
        user_goal="reply",
        rank=payload_rank,
    )


def _obligations(rank: EpistemicRank = EpistemicRank.HYPOTHESIS) -> Obligations:
    return Obligations(
        must_do=("respond politely",),
        must_not_do=("ignore user",),
        answer_shape=("short reply",),
        rank=rank,
    )


def _plan(rank: EpistemicRank = EpistemicRank.HYPOTHESIS) -> AnswerPlan:
    return AnswerPlan(sections=("greeting",), sequence=("greeting",), rank=rank)


def _audit_pass(rank: EpistemicRank = EpistemicRank.CERTIFICATE) -> ResponseAudit:
    return ResponseAudit(
        answers_user_request=True,
        violates_exclusions=False,
        rank=rank,
    )


# ---------------------------------------------------------------------------
# Schema / versioning / framing
# ---------------------------------------------------------------------------


def test_schema_versions_are_present_on_every_contract():
    contracts = [
        _reality(),
        _filter(),
        _linked(_reality(), _filter()),
        _judgment(),
        _payload(),
        _obligations(),
        _plan(),
        _audit_pass(EpistemicRank.HYPOTHESIS),
    ]
    for c in contracts:
        assert getattr(c, "schema_version") == AFU_SCHEMA_VERSION
        assert getattr(c, "contract_version") == AFU_CONTRACT_VERSION


def test_only_three_public_ranks_are_legal():
    assert ALLOWED_PUBLIC_RANKS == frozenset(
        {EpistemicRank.ZERO, EpistemicRank.HYPOTHESIS, EpistemicRank.CERTIFICATE}
    )


def test_internal_kernel_ranks_are_clamped_to_hypothesis():
    # Kernel ranks like WEAK_EVIDENCE / STRONG_EVIDENCE are not public AFU
    # statuses; passing them must not silently elevate the contract.
    pr = PromptReality(raw_text="x", rank=EpistemicRank.STRONG_EVIDENCE)
    assert pr.rank == EpistemicRank.HYPOTHESIS
    assert normalize_rank(EpistemicRank.WEAK_EVIDENCE) == EpistemicRank.HYPOTHESIS


# ---------------------------------------------------------------------------
# Frozenness
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "obj",
    [
        _reality(),
        _filter(),
        _linked(_reality(), _filter()),
        _judgment(),
        _obligations(),
        _plan(),
        _audit_pass(EpistemicRank.HYPOTHESIS),
        TraceStep(stage="s", summary="ok"),
        LicensedOutput(),
    ],
)
def test_contracts_are_frozen(obj):
    with pytest.raises(dataclasses.FrozenInstanceError):
        obj.rank = EpistemicRank.CERTIFICATE  # type: ignore[misc]


# ---------------------------------------------------------------------------
# PromptReality
# ---------------------------------------------------------------------------


def test_prompt_reality_requires_non_empty_raw_text():
    with pytest.raises(AFUContractError):
        PromptReality(raw_text="")


def test_prompt_reality_allows_local_certificate_for_observable_fact():
    # "the text is Arabic" is a directly observable property and is one
    # of the narrow claims allowed at CERTIFICATE at this stage.
    pr = PromptReality(
        raw_text="مرحبا",
        has_arabic=True,
        rank=EpistemicRank.CERTIFICATE,
    )
    assert pr.rank == EpistemicRank.CERTIFICATE


# ---------------------------------------------------------------------------
# PriorInformationFilter — Nabhani separation
# ---------------------------------------------------------------------------


def test_prior_filter_rejects_item_in_both_allowed_and_blocked():
    with pytest.raises(AFUContractError):
        PriorInformationFilter(
            allowed_prior_information=("ambiguous fact",),
            blocked_prior_opinions=("ambiguous fact",),
        )


# ---------------------------------------------------------------------------
# Linker — forbidden transition: prior_opinion_into_linker
# ---------------------------------------------------------------------------


def test_linker_blocks_prior_opinion_into_linker():
    r = _reality()
    f = _filter(allowed=("ok",), blocked=("bias",))
    with pytest.raises(AFUContractError, match="prior_opinion_into_linker"):
        LinkedUnderstanding(
            prompt_reality=r,
            prior_filter=f,
            linked_prior_information=("bias",),
        )


def test_linker_rejects_information_not_in_allowed_set():
    r = _reality()
    f = _filter(allowed=("ok",), blocked=())
    with pytest.raises(AFUContractError, match="subset"):
        LinkedUnderstanding(
            prompt_reality=r,
            prior_filter=f,
            linked_prior_information=("never declared",),
        )


# ---------------------------------------------------------------------------
# UnderstandingPayload
# ---------------------------------------------------------------------------


def test_payload_blocks_silent_level_skip_when_linker_mismatches_stages():
    r1 = _reality()
    r2 = PromptReality(raw_text="OTHER")  # different upstream object
    f = _filter()
    linked = _linked(r1, f)
    with pytest.raises(AFUContractError, match="silent_level_skip"):
        UnderstandingPayload(
            prompt_reality=r2,
            prior_filter=f,
            linked_understanding=linked,
            judgment=_judgment(),
        )


def test_payload_rank_is_meet_of_components():
    # Even if the caller requests CERTIFICATE, the payload rank cannot
    # exceed the meet of all stage ranks.
    p = _payload(judgment_rank=EpistemicRank.HYPOTHESIS, payload_rank=EpistemicRank.CERTIFICATE)
    assert p.rank == EpistemicRank.HYPOTHESIS


def test_payload_complete_requires_supporting_evidence():
    r = _reality()
    f = _filter()
    j = UnderstandingJudgment(main_judgment="hi", supporting_evidence=())
    p = UnderstandingPayload(
        prompt_reality=r,
        prior_filter=f,
        linked_understanding=_linked(r, f),
        judgment=j,
    )
    assert not p.complete()


# ---------------------------------------------------------------------------
# UnderstandingJudgment
# ---------------------------------------------------------------------------


def test_judgment_certificate_requires_supporting_evidence():
    j = UnderstandingJudgment(
        main_judgment="x",
        supporting_evidence=(),
        rank=EpistemicRank.CERTIFICATE,
    )
    assert j.rank == EpistemicRank.HYPOTHESIS


# ---------------------------------------------------------------------------
# Obligations / AnswerPlan
# ---------------------------------------------------------------------------


def test_obligations_reject_must_do_must_not_do_overlap():
    with pytest.raises(AFUContractError):
        Obligations(must_do=("respond",), must_not_do=("respond",))


def test_answer_plan_sequence_must_reference_known_sections():
    with pytest.raises(AFUContractError):
        AnswerPlan(sections=("intro",), sequence=("conclusion",))


# ---------------------------------------------------------------------------
# ResponseAudit downgrades
# ---------------------------------------------------------------------------


def test_audit_missing_required_parts_forces_zero():
    a = ResponseAudit(
        answers_user_request=True,
        missing_required_parts=("evidence",),
        rank=EpistemicRank.CERTIFICATE,
    )
    assert a.rank == EpistemicRank.ZERO
    assert not a.passed()


def test_audit_overclaim_downgrades_certificate():
    a = ResponseAudit(
        answers_user_request=True,
        overclaims=("global certainty",),
        rank=EpistemicRank.CERTIFICATE,
    )
    assert a.rank == EpistemicRank.HYPOTHESIS


def test_audit_passes_only_when_clean():
    assert _audit_pass(EpistemicRank.HYPOTHESIS).passed()
    assert not ResponseAudit(answers_user_request=False).passed()


# ---------------------------------------------------------------------------
# LicensedResponse — the two flagship forbidden transitions
# ---------------------------------------------------------------------------


def test_licensed_response_blocks_answer_before_understanding_payload():
    # Payload with no supporting_evidence → incomplete.
    r = _reality()
    f = _filter()
    incomplete_payload = UnderstandingPayload(
        prompt_reality=r,
        prior_filter=f,
        linked_understanding=_linked(r, f),
        judgment=UnderstandingJudgment(main_judgment="x", supporting_evidence=()),
    )
    assert not incomplete_payload.complete()

    with pytest.raises(AFUContractError, match="answer_before_understanding_payload"):
        LicensedResponse(
            answer="here is your answer",
            understanding=incomplete_payload,
            obligations=_obligations(),
            answer_plan=_plan(),
            audit=_audit_pass(EpistemicRank.HYPOTHESIS),
        )


def test_licensed_response_allows_empty_answer_without_understanding():
    # Same incomplete payload, but with empty answer (a clarification
    # request, not an answer) must be allowed.
    r = _reality()
    f = _filter()
    incomplete = UnderstandingPayload(
        prompt_reality=r,
        prior_filter=f,
        linked_understanding=_linked(r, f),
        judgment=UnderstandingJudgment(main_judgment="x", supporting_evidence=()),
    )
    lr = LicensedResponse(
        answer="",
        understanding=incomplete,
        obligations=_obligations(),
        answer_plan=_plan(),
        audit=ResponseAudit(missing_required_parts=("understanding",)),
    )
    assert lr.rank == EpistemicRank.ZERO


def test_licensed_response_blocks_global_certificate_without_narrow_attestation():
    # Everything CERTIFICATE but no narrow_certificates → must downgrade.
    p = _payload(judgment_rank=EpistemicRank.CERTIFICATE, payload_rank=EpistemicRank.CERTIFICATE)
    lr = LicensedResponse(
        answer="hi",
        understanding=p,
        obligations=_obligations(EpistemicRank.CERTIFICATE),
        answer_plan=_plan(EpistemicRank.CERTIFICATE),
        audit=_audit_pass(EpistemicRank.CERTIFICATE),
        narrow_certificates=(),  # nothing attested
        rank=EpistemicRank.CERTIFICATE,
    )
    assert lr.rank == EpistemicRank.HYPOTHESIS


def test_licensed_response_allows_certificate_only_with_narrow_attestation():
    # Build every upstream stage at CERTIFICATE so the meet does not
    # drag the response down.
    r = PromptReality(raw_text="مرحبا", has_arabic=True, rank=EpistemicRank.CERTIFICATE)
    f = PriorInformationFilter(rank=EpistemicRank.CERTIFICATE)
    linked = LinkedUnderstanding(
        prompt_reality=r,
        prior_filter=f,
        linked_prior_information=(),
        rank=EpistemicRank.CERTIFICATE,
    )
    p = UnderstandingPayload(
        prompt_reality=r,
        prior_filter=f,
        linked_understanding=linked,
        judgment=UnderstandingJudgment(
            main_judgment="user greets",
            supporting_evidence=("مرحبا",),
            rank=EpistemicRank.CERTIFICATE,
        ),
        rank=EpistemicRank.CERTIFICATE,
    )
    lr = LicensedResponse(
        answer="hi",
        understanding=p,
        obligations=_obligations(EpistemicRank.CERTIFICATE),
        answer_plan=_plan(EpistemicRank.CERTIFICATE),
        audit=_audit_pass(EpistemicRank.CERTIFICATE),
        narrow_certificates=("text_is_arabic",),
        rank=EpistemicRank.CERTIFICATE,
    )
    assert p.rank == EpistemicRank.CERTIFICATE
    assert lr.rank == EpistemicRank.CERTIFICATE


def test_licensed_response_rank_is_meet_of_components():
    p = _payload(judgment_rank=EpistemicRank.HYPOTHESIS)
    lr = LicensedResponse(
        answer="hi",
        understanding=p,
        obligations=_obligations(EpistemicRank.HYPOTHESIS),
        answer_plan=_plan(EpistemicRank.HYPOTHESIS),
        audit=_audit_pass(EpistemicRank.CERTIFICATE),
        narrow_certificates=("text_is_arabic",),
        rank=EpistemicRank.CERTIFICATE,
    )
    assert lr.rank == EpistemicRank.HYPOTHESIS


# ---------------------------------------------------------------------------
# Residual taxonomy interplay — blocking residuals cannot coexist with
# a CERTIFICATE rank at any contract.
# ---------------------------------------------------------------------------


def test_blocking_residual_downgrades_certificate_on_every_contract():
    block = ("certificate_with_blocking_residuals",)
    pr = PromptReality(raw_text="x", rank=EpistemicRank.CERTIFICATE, residuals=block)
    assert pr.rank == EpistemicRank.HYPOTHESIS

    f = PriorInformationFilter(rank=EpistemicRank.CERTIFICATE, residuals=block)
    assert f.rank == EpistemicRank.HYPOTHESIS

    j = UnderstandingJudgment(
        main_judgment="x",
        supporting_evidence=("ev",),
        rank=EpistemicRank.CERTIFICATE,
        residuals=block,
    )
    assert j.rank == EpistemicRank.HYPOTHESIS

    o = Obligations(rank=EpistemicRank.CERTIFICATE, residuals=block)
    assert o.rank == EpistemicRank.HYPOTHESIS

    ap = AnswerPlan(rank=EpistemicRank.CERTIFICATE, residuals=block)
    assert ap.rank == EpistemicRank.HYPOTHESIS

    audit = ResponseAudit(
        answers_user_request=True,
        rank=EpistemicRank.CERTIFICATE,
        residuals=block,
    )
    assert audit.rank == EpistemicRank.HYPOTHESIS


# ---------------------------------------------------------------------------
# Licensed envelope (Φᵢ shape)
# ---------------------------------------------------------------------------


def test_licensed_output_envelope_shape():
    env = LicensedOutput(
        selected_gates=("scope_gate",),
        evidence=("excerpt",),
        residuals=(),
        rank=EpistemicRank.HYPOTHESIS,
    )
    assert env.selected_gates == ("scope_gate",)
    assert env.evidence == ("excerpt",)
    assert env.rank == EpistemicRank.HYPOTHESIS


def test_trace_step_requires_stage_and_summary():
    with pytest.raises(AFUContractError):
        TraceStep(stage="", summary="x")
    with pytest.raises(AFUContractError):
        TraceStep(stage="s", summary="")


# ---------------------------------------------------------------------------
# AFU contracts module must NOT import any theory module (constitutional)
# ---------------------------------------------------------------------------


def test_afu_contracts_do_not_import_theory_modules():
    import mcd.afu.contracts as pkg

    forbidden = {
        "mantuq",
        "mafhum",
        "qiyas",
        "naskh",
        "illah",
        "manat",
        "dal",
        "madlul",
        "nisbah",
        "ifadah",
    }
    # Inspect the namespace + all submodules' source files for theory imports.
    import importlib
    import pkgutil

    found: list[str] = []
    for mod_info in pkgutil.walk_packages(pkg.__path__, prefix="mcd.afu.contracts."):
        m = importlib.import_module(mod_info.name)
        src_file = getattr(m, "__file__", None)
        if not src_file:
            continue
        with open(src_file, "r", encoding="utf-8") as fh:
            src = fh.read()
        for term in forbidden:
            # A real import would look like "import X" or "from X" — comments
            # and docstring mentions are allowed.
            for needle in (f"import {term}", f"from {term}", f"from .{term}", f"from mcd.{term}"):
                if needle in src:
                    found.append(f"{mod_info.name}:{needle}")
    assert not found, f"theory_module_runtime_without_gate: {found}"
