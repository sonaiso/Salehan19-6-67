"""``FractalDefinition`` — the universal 15-field template.

Every concept in the project — حرف, حركة, جذر, وزن, دال, مدلول, نسبة,
إفادة, حكم, تنزيل — must be expressible as an instance of this dataclass.
The fields and laws are dictated by §§4 and 15 of the user brief.

Constructional law (§15): a definition lacking a non-empty
``formation_gate`` or ``backward_gate`` is *not* a fractal definition
and the constructor raises :class:`AFUContractError`. This is the
single most important invariant of the AFU layer; every future layer
inherits it transitively.

Rank-cap law: when ``rank == CERTIFICATE`` and any ``residuals`` entry
blocks certification, the rank is downgraded to HYPOTHESIS. The
residual is *kept* (no erasure).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, Iterable, TypeVar

from mcd.afu.contracts._common import (
    AFUContractError,
    EpistemicRank,
    LicensedOutput,
    freeze_strings,
)

from ..core.rank_lattice import cap_by_residuals
from .evidence import Evidence
from .rank import normalize_rank
from .residual import Residual

T = TypeVar("T")


def _nonempty(name: str, value: object) -> str:
    if not str(value or "").strip():
        raise AFUContractError(f"FractalDefinition.{name} must be non-empty")
    return str(value).strip()


def _coerce_residual(entry: object) -> Residual:
    if isinstance(entry, Residual):
        return entry
    if isinstance(entry, str):
        return Residual.of(entry)
    raise AFUContractError(
        "FractalDefinition.residuals entries must be Residual or str code"
    )


def _coerce_evidence(entry: object) -> Evidence:
    if isinstance(entry, Evidence):
        return entry
    raise AFUContractError("FractalDefinition.evidence entries must be Evidence")


@dataclass(frozen=True)
class FractalDefinition(Generic[T]):
    """The universal 15-field template.

    Fields (in the order of §4 of the brief):

    1. ``name``               — non-empty string.
    2. ``layer``              — non-empty string.
    3. ``carrier``            — non-empty string.
    4. ``domain``             — non-empty string.
    5. ``prior_information``  — frozen tuple of strings (may be empty).
    6. ``distinction``        — frozen tuple of strings (MUST be non-empty:
       a definition without distinction has no meaning).
    7. ``relation_before``    — frozen tuple of strings (may be empty for
       atomic units).
    8. ``relation_after``     — frozen tuple of strings (may be empty for
       terminal units).
    9. ``function``           — non-empty string.
    10. ``formation_gate``    — non-empty string (§15 law).
    11. ``backward_gate``     — non-empty string (§15 law).
    12. ``evidence``          — frozen tuple of :class:`Evidence`.
    13. ``residuals``         — frozen tuple of :class:`Residual`.
    14. ``rank``              — public lattice (clamped).
    15. ``output_contract``   — non-empty string.
    """

    name: str
    layer: str
    carrier: str
    domain: str
    prior_information: tuple[str, ...] = field(default=())
    distinction: tuple[str, ...] = field(default=())
    relation_before: tuple[str, ...] = field(default=())
    relation_after: tuple[str, ...] = field(default=())
    function: str = ""
    formation_gate: str = ""
    backward_gate: str = ""
    evidence: tuple[Evidence, ...] = field(default=())
    residuals: tuple[Residual, ...] = field(default=())
    rank: EpistemicRank = EpistemicRank.HYPOTHESIS
    output_contract: str = ""

    def __post_init__(self) -> None:
        # Scalar non-empty fields. Each violation is reported by field
        # name to keep test failures readable.
        object.__setattr__(self, "name", _nonempty("name", self.name))
        object.__setattr__(self, "layer", _nonempty("layer", self.layer))
        object.__setattr__(self, "carrier", _nonempty("carrier", self.carrier))
        object.__setattr__(self, "domain", _nonempty("domain", self.domain))
        object.__setattr__(self, "function", _nonempty("function", self.function))
        object.__setattr__(
            self, "output_contract", _nonempty("output_contract", self.output_contract)
        )

        # §15 — the constructional law of the fractal definition.
        formation = str(self.formation_gate or "").strip()
        backward = str(self.backward_gate or "").strip()
        if not formation or not backward:
            raise AFUContractError(
                "not_fractal: missing formation_gate or backward_gate"
            )
        object.__setattr__(self, "formation_gate", formation)
        object.__setattr__(self, "backward_gate", backward)

        # Tuple-of-string fields.
        object.__setattr__(
            self, "prior_information", freeze_strings(self.prior_information)
        )
        distinction = freeze_strings(self.distinction)
        if not distinction:
            # §4: distinction is the very mechanism by which the unit is
            # told apart from its neighbours. A definition without it is
            # meaningless and cannot anchor any gate.
            raise AFUContractError("FractalDefinition.distinction must be non-empty")
        object.__setattr__(self, "distinction", distinction)
        object.__setattr__(
            self, "relation_before", freeze_strings(self.relation_before)
        )
        object.__setattr__(self, "relation_after", freeze_strings(self.relation_after))

        # Typed sub-collections.
        object.__setattr__(
            self,
            "evidence",
            tuple(_coerce_evidence(e) for e in (self.evidence or ())),
        )
        residuals = tuple(_coerce_residual(r) for r in (self.residuals or ()))
        object.__setattr__(self, "residuals", residuals)

        # Rank: clamp to the public lattice, then cap by blocking residuals.
        rank = normalize_rank(self.rank)
        rank = cap_by_residuals(rank, [r.code for r in residuals])
        object.__setattr__(self, "rank", rank)

    # --- projections ----------------------------------------------------------
    def residual_codes(self) -> tuple[str, ...]:
        """Return residual codes as plain strings, in declared order."""
        return tuple(r.code for r in self.residuals)

    def evidence_summaries(self) -> tuple[str, ...]:
        """Return a deterministic textual summary of each evidence record."""
        return tuple(f"{e.source}::{e.claim}" for e in self.evidence)

    def to_licensed_output(self) -> LicensedOutput:
        """Project the definition into the AFU :class:`LicensedOutput`.

        This is the bridge that lets a fractal definition take part in
        :func:`mcd.afu.core.licensed_bind.bind_licensed` and flow through
        the ``Φᵢ(Sᵢ) = Sᵢ₊₁`` chain alongside ordinary stage outputs.
        """
        return LicensedOutput(
            selected_gates=(self.formation_gate, self.backward_gate),
            evidence=self.evidence_summaries(),
            residuals=self.residual_codes(),
            rank=self.rank,
        )

    # --- ergonomic constructors ----------------------------------------------
    @classmethod
    def build(
        cls,
        *,
        name: str,
        layer: str,
        carrier: str,
        domain: str,
        function: str,
        formation_gate: str,
        backward_gate: str,
        output_contract: str,
        distinction: Iterable[str],
        prior_information: Iterable[str] = (),
        relation_before: Iterable[str] = (),
        relation_after: Iterable[str] = (),
        evidence: Iterable[Evidence] = (),
        residuals: Iterable[Residual | str] = (),
        rank: EpistemicRank | str = EpistemicRank.HYPOTHESIS,
    ) -> "FractalDefinition[T]":
        """Keyword-only builder; preferred over the positional constructor."""
        return cls(
            name=name,
            layer=layer,
            carrier=carrier,
            domain=domain,
            prior_information=tuple(prior_information),
            distinction=tuple(distinction),
            relation_before=tuple(relation_before),
            relation_after=tuple(relation_after),
            function=function,
            formation_gate=formation_gate,
            backward_gate=backward_gate,
            evidence=tuple(evidence),
            residuals=tuple(residuals),
            rank=rank,
            output_contract=output_contract,
        )


__all__ = ["FractalDefinition"]
