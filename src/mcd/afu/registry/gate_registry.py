"""Immutable Gate Registry — empty in PR 2.

The registry is the *only* sanctioned place where a gate identifier is
mapped to a concrete :class:`Gate`. In PR 2 the registry ships empty by
construction: any call to :meth:`GateRegistry.evaluate` produces the
fail-closed :func:`unknown_gate_verdict`, which carries the
``unknown_gate`` residual and therefore caps any downstream rank at
HYPOTHESIS.

This guarantees a property required by §6 of the PR plan:

    Until a real predicate is registered, no concrete
    ``FractalDefinitionRuntime`` can accidentally certify itself.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from mcd.afu.contracts._common import AFUContractError

from ..core.gate import Gate, GateStatus, GateVerdict, unknown_gate_verdict


@dataclass(frozen=True)
class GateRegistry:
    """An immutable mapping ``gate_id -> Gate``.

    Construct a new registry with :meth:`register` rather than mutating
    the existing one. ``__contains__`` and :meth:`get` are O(1).
    """

    _gates: Mapping[str, Gate] = field(default_factory=dict)

    def __post_init__(self) -> None:
        cleaned: dict[str, Gate] = {}
        for gid, gate in (self._gates or {}).items():
            key = str(gid or "").strip()
            if not key:
                raise AFUContractError("GateRegistry: empty gate_id is not allowed")
            if not isinstance(gate, Gate):
                raise AFUContractError(
                    f"GateRegistry[{key!r}] must be a Gate instance"
                )
            if gate.spec.gate_id != key:
                raise AFUContractError(
                    f"GateRegistry key {key!r} does not match Gate.spec.gate_id "
                    f"{gate.spec.gate_id!r}"
                )
            cleaned[key] = gate
        # freeze into a real (read-only-ish) dict — frozen dataclass keeps
        # the attribute itself unassignable; we additionally rebind to a
        # plain dict snapshot to avoid leaking the caller's mutable map.
        object.__setattr__(self, "_gates", dict(cleaned))

    def __contains__(self, gate_id: str) -> bool:
        return str(gate_id or "").strip() in self._gates

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._gates)

    def gate_ids(self) -> tuple[str, ...]:
        """Return the registered gate identifiers in deterministic order."""
        return tuple(sorted(self._gates.keys()))

    def get(self, gate_id: str) -> Gate | None:
        return self._gates.get(str(gate_id or "").strip())

    def register(self, gate: Gate) -> "GateRegistry":
        """Return a new registry that additionally contains ``gate``.

        Re-registration of an existing ``gate_id`` is forbidden — the
        registry is append-only by construction so the audit trail is
        monotone.
        """
        if not isinstance(gate, Gate):
            raise AFUContractError("GateRegistry.register expects a Gate instance")
        gid = gate.spec.gate_id
        if gid in self._gates:
            raise AFUContractError(
                f"GateRegistry: gate_id {gid!r} is already registered"
            )
        merged = dict(self._gates)
        merged[gid] = gate
        return GateRegistry(_gates=merged)

    def evaluate(self, gate_id: str, state: object) -> GateVerdict:
        """Evaluate ``gate_id`` against ``state``.

        Fail-closed semantics:

        * Unknown gate → :func:`unknown_gate_verdict` (UNKNOWN, blocking
          residual ``unknown_gate``).
        * Registered gate with no evaluator → same UNKNOWN verdict, so a
          spec-only entry cannot be mistaken for a passing predicate.
        * Evaluator raising → UNKNOWN verdict with an
          ``unknown_gate_evaluation_error`` residual; the original error
          is *not* swallowed silently in the rank.
        """
        gate = self.get(gate_id)
        if gate is None:
            return unknown_gate_verdict(gate_id)
        if gate.evaluator is None:
            return unknown_gate_verdict(gate_id)
        try:
            verdict = gate.evaluator(state)
        except Exception as exc:  # noqa: BLE001 — fail-closed by design
            return GateVerdict(
                gate_id=gate_id,
                status=GateStatus.UNKNOWN,
                residuals=("unknown_gate_evaluation_error",),
                note=f"Gate evaluator raised: {type(exc).__name__}: {exc}",
            )
        if not isinstance(verdict, GateVerdict):
            return GateVerdict(
                gate_id=gate_id,
                status=GateStatus.UNKNOWN,
                residuals=("unknown_gate_evaluation_error",),
                note="Gate evaluator returned a non-GateVerdict value.",
            )
        return verdict


def empty_registry() -> GateRegistry:
    """The canonical empty registry shipped with PR 2."""
    return GateRegistry(_gates={})


__all__ = ["GateRegistry", "empty_registry"]
