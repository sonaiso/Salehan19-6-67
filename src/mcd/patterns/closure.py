from __future__ import annotations

from mcd.core.epistemic_rank import is_rank_sufficient
from mcd.patterns.core import ClosureJudgment, ClosureResult, MinimumCompletion, Pattern
from mcd.patterns.form_role import FormRoleHypothesis


def _has_form_field(hypothesis: FormRoleHypothesis, field: str) -> bool:
    if hasattr(hypothesis.form, field):
        value = getattr(hypothesis.form, field)
        return bool(value)
    return field in set(hypothesis.form.symbols) | set(hypothesis.form.invariants)


def _has_role_field(hypothesis: FormRoleHypothesis, field: str) -> bool:
    if hasattr(hypothesis.role, field):
        value = getattr(hypothesis.role, field)
        return bool(value)
    return bool(hypothesis.role.features.get(field))


def satisfies_minimum_completion(hypothesis: FormRoleHypothesis, minimum_completion: MinimumCompletion) -> bool:
    if hypothesis.layer != minimum_completion.layer:
        return False

    available_dependencies = (
        set(hypothesis.trace_refs)
        | set(hypothesis.residuals)
        | set(hypothesis.form.source_refs)
        | set(hypothesis.role.evidence_refs)
    )

    if any(
        not _has_form_field(hypothesis, form_field)
        for form_field in minimum_completion.required_form_fields
    ):
        return False
    if any(
        not _has_role_field(hypothesis, role_field)
        for role_field in minimum_completion.required_role_fields
    ):
        return False
    if any(dep not in available_dependencies for dep in minimum_completion.required_dependencies):
        return False
    if not is_rank_sufficient(hypothesis.role.rank, minimum_completion.required_evidence_rank):
        return False
    if any(barrier in hypothesis.residuals for barrier in minimum_completion.fatal_barriers):
        return False
    return True


def close_layer(
    hypothesis: FormRoleHypothesis,
    pattern: Pattern,
    minimum_completion: MinimumCompletion,
) -> ClosureResult:
    blockers: list[str] = []
    residuals = list(dict.fromkeys((*hypothesis.residuals,)))

    in_domain = (
        hypothesis.layer == pattern.layer == minimum_completion.layer
        and hypothesis.form.layer == pattern.layer
        and hypothesis.role.layer == pattern.layer
    )
    if not in_domain:
        blockers.append("layer_domain_mismatch")

    if hypothesis.pattern_id != pattern.pattern_id:
        blockers.append("pattern_mismatch")

    fatal_barriers = set(pattern.fatal_barriers) | set(minimum_completion.fatal_barriers)
    active_fatal = [barrier for barrier in fatal_barriers if barrier in hypothesis.residuals]
    if active_fatal:
        blockers.extend(sorted(active_fatal))

    mc_satisfied = in_domain and not active_fatal and satisfies_minimum_completion(hypothesis, minimum_completion)

    if blockers and ("layer_domain_mismatch" in blockers or active_fatal):
        judgment = ClosureJudgment.ZERO
        chi = 0
    elif mc_satisfied:
        judgment = ClosureJudgment.CERTIFICATE
        chi = 1
    elif in_domain:
        judgment = ClosureJudgment.HYPOTHESIS
        chi = 0
    else:
        judgment = ClosureJudgment.ZERO
        chi = 0

    return ClosureResult(
        layer=hypothesis.layer,
        pattern_id=pattern.pattern_id,
        judgment=judgment,
        chi=chi,
        mc_satisfied=mc_satisfied,
        residuals=tuple(residuals),
        blockers=tuple(dict.fromkeys(blockers)),
        trace_refs=hypothesis.trace_refs,
    )
