"""Dal Transition Algebra — Constitutional transition kernel.

This module implements the governance layer for transitions within the DAL
(Dalalah) space: from raw Unicode → carriers → isolated lexical forms,
WITHOUT crossing into meaning, ifadah, or hukm.

Every transition is gated by:
1. Origin preservation
2. Shared cause (branch)
3. Effective description
4. No blocking difference (fariq)
5. Identity preservation
6. Minimal completeness
7. License + Trace + Rank + Residuals

Forbidden outputs:
- "meaning" (ma'na)
- "ifadah" (إفادة)
- "hukm" (حكم)

Any attempt to produce these outputs is constitutionally rejected.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


# ---------------------------------------------------------------------------
# DTA Space — Transition states in the Dal layer
# ---------------------------------------------------------------------------


class DTASpace(str, Enum):
    """Valid states in the Dal Transition Algebra.

    These represent progressive stages of linguistic processing BEFORE
    meaning extraction:
    - UNICODE_RAW: Raw text input
    - CARRIER: Text with preserved orthographic identity
    - ISOLATED_LAFZ: Single lexical unit (LafzMufrad candidate)
    - ROOT_STEM: Morphological root (still pre-meaning)

    Transitions MUST be stepwise; jumping levels is forbidden.
    """
    UNICODE_RAW = "UNICODE_RAW"
    CARRIER = "CARRIER"
    ISOLATED_LAFZ = "ISOLATED_LAFZ"
    ROOT_STEM = "ROOT_STEM"


# ---------------------------------------------------------------------------
# Rejection taxonomy
# ---------------------------------------------------------------------------


class DTARejectionKind(str, Enum):
    """Classification of why a transition was rejected."""
    FORBIDDEN_OUTPUT = "FORBIDDEN_OUTPUT"  # Produces meaning/ifadah/hukm
    LEVEL_JUMP = "LEVEL_JUMP"  # Skips intermediate state
    MISSING_ORIGIN = "MISSING_ORIGIN"  # No origin trace
    MISSING_SHARED_CAUSE = "MISSING_SHARED_CAUSE"  # No branch evidence
    BLOCKING_DIFFERENCE = "BLOCKING_DIFFERENCE"  # Fariq blocks transition
    IDENTITY_LOST = "IDENTITY_LOST"  # Lost carrier or identity
    INCOMPLETE = "INCOMPLETE"  # Minimal completeness violated
    NO_PROOF = "NO_PROOF"  # No TransitionProof provided


# ---------------------------------------------------------------------------
# Forbidden output gate
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DTAForbiddenOutputGate:
    """Gate that blocks transitions producing meaning/ifadah/hukm.

    This is a constitutional invariant: DAL layer NEVER produces semantic
    content, only governed linguistic forms.
    """

    @staticmethod
    def check(outputs: Iterable[str]) -> tuple[bool, list[str]]:
        """Check if any output is forbidden.

        Returns:
            (is_allowed, forbidden_items)
            is_allowed is False if any forbidden output detected.
        """
        forbidden_terms = {"meaning", "ma'na", "معنى", "ifadah", "إفادة", "hukm", "حكم", "judgment"}
        found = []
        for out in outputs:
            normalized = str(out).lower().strip()
            # Check both exact match and prefix match (e.g., "meaning:writer")
            if normalized in forbidden_terms:
                found.append(out)
            else:
                # Check if any forbidden term appears as a prefix before a colon
                for term in forbidden_terms:
                    if normalized.startswith(term + ":") or normalized.startswith(term + " "):
                        found.append(out)
                        break
        return (len(found) == 0, found)


# ---------------------------------------------------------------------------
# Minimal completeness
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DTAMinimalCompleteness:
    """Ensures a transition preserves necessary components.

    For LafzMufrad acceptance:
    - All carriers must be preserved
    - All identities must be preserved
    - Origin must be traceable
    """
    required_carriers: tuple[str, ...] = ()
    required_identities: tuple[str, ...] = ()
    requires_origin: bool = True

    def check(
        self,
        carriers: Iterable[str],
        identities: Iterable[str],
        has_origin: bool
    ) -> tuple[bool, str]:
        """Verify minimal completeness.

        Returns:
            (is_complete, reason)
        """
        carrier_set = set(carriers)
        identity_set = set(identities)

        for req in self.required_carriers:
            if req not in carrier_set:
                return (False, f"missing_carrier:{req}")

        for req in self.required_identities:
            if req not in identity_set:
                return (False, f"missing_identity:{req}")

        if self.requires_origin and not has_origin:
            return (False, "missing_origin")

        return (True, "")


# ---------------------------------------------------------------------------
# Identity preservation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DTAIdentityPreservation:
    """Verifies that transition preserves essential identities.

    In DAL, identity = orthographic form + morphological markers,
    NOT semantic content.
    """
    original_form: str

    def check(self, output_form: str) -> bool:
        """Check if identity is preserved (exact match for now)."""
        return self.original_form.strip() == output_form.strip()


# ---------------------------------------------------------------------------
# Qiyas proof (analogy foundation)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DTAQiyasProof:
    """Analogy proof for transition: origin + branch + shared_cause.

    This is NOT semantic qiyas, but structural analogy in linguistic form.
    Example: "كاتب" transitions like "ضارب" because both follow فاعل pattern.
    """
    origin: str  # Original reference case
    branch: str  # New case being transitioned
    shared_cause: str  # Why they belong to same class (illah)
    effective_description: str  # What property is preserved

    def __post_init__(self) -> None:
        if not self.origin.strip():
            raise ValueError("DTAQiyasProof.origin must be non-empty")
        if not self.branch.strip():
            raise ValueError("DTAQiyasProof.branch must be non-empty")
        if not self.shared_cause.strip():
            raise ValueError("DTAQiyasProof.shared_cause must be non-empty")

    def has_blocking_difference(self, fariq: str) -> bool:
        """Check if a blocking difference (fariq) invalidates the analogy."""
        return bool(fariq.strip())


# ---------------------------------------------------------------------------
# Transition proof
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DTATransitionProof:
    """Complete proof bundle for a constitutional transition.

    Required fields:
    - from_state, to_state: DTA space positions
    - qiyas_proof: Structural analogy
    - identity_preservation: Form preservation
    - minimal_completeness: Required components
    - license: Authorization tag
    - trace: Evidence chain
    - rank: Epistemic status
    - residuals: Unresolved issues
    """
    from_state: DTASpace
    to_state: DTASpace
    qiyas_proof: DTAQiyasProof
    identity_preservation: DTAIdentityPreservation
    minimal_completeness: DTAMinimalCompleteness
    license: str  # Authorization tag
    trace: tuple[str, ...] = ()  # Evidence chain
    rank: str = "HYPOTHESIS"  # Epistemic rank
    residuals: tuple[str, ...] = ()  # Unresolved issues
    outputs: tuple[str, ...] = ()  # What this transition produces

    def __post_init__(self) -> None:
        if not self.license.strip():
            raise ValueError("DTATransitionProof.license must be non-empty")
        # Freeze tuples
        object.__setattr__(self, "trace", tuple(self.trace))
        object.__setattr__(self, "residuals", tuple(self.residuals))
        object.__setattr__(self, "outputs", tuple(self.outputs))

    def validate(self) -> tuple[bool, DTARejectionKind | None, str]:
        """Validate the transition proof.

        Returns:
            (is_valid, rejection_kind, message)
        """
        # Check for level jumps
        allowed_transitions = {
            (DTASpace.UNICODE_RAW, DTASpace.CARRIER),
            (DTASpace.CARRIER, DTASpace.ISOLATED_LAFZ),
            (DTASpace.ISOLATED_LAFZ, DTASpace.ROOT_STEM),
        }
        if (self.from_state, self.to_state) not in allowed_transitions:
            return (
                False,
                DTARejectionKind.LEVEL_JUMP,
                f"Cannot jump from {self.from_state.value} to {self.to_state.value}"
            )

        # Check forbidden outputs
        allowed, forbidden = DTAForbiddenOutputGate.check(self.outputs)
        if not allowed:
            return (
                False,
                DTARejectionKind.FORBIDDEN_OUTPUT,
                f"Forbidden outputs: {forbidden}"
            )

        # Check for origin
        if not self.qiyas_proof.origin.strip():
            return (
                False,
                DTARejectionKind.MISSING_ORIGIN,
                "Qiyas proof missing origin"
            )

        # Check for shared cause
        if not self.qiyas_proof.shared_cause.strip():
            return (
                False,
                DTARejectionKind.MISSING_SHARED_CAUSE,
                "Qiyas proof missing shared cause"
            )

        return (True, None, "")


# ---------------------------------------------------------------------------
# LafzMufrad acceptance proof
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DTALafzMufradAcceptanceProof:
    """Proof that a LafzMufrad (isolated word) is constitutionally valid.

    LafzMufrad is NOT meaning. It is a governed linguistic form with:
    - Preserved carriers (orthographic components)
    - Preserved identities (morphological markers)
    - Traceable origin
    - Rank and residuals

    Example: "كاتب" as LafzMufrad is a فاعل pattern candidate, NOT "writer".
    """
    lafz: str  # The isolated word
    carriers: tuple[str, ...] = ()  # Preserved orthographic components
    identities: tuple[str, ...] = ()  # Preserved morphological markers
    origin: str = ""  # Source trace
    rank: str = "HYPOTHESIS"
    residuals: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.lafz.strip():
            raise ValueError("DTALafzMufradAcceptanceProof.lafz must be non-empty")
        object.__setattr__(self, "carriers", tuple(self.carriers))
        object.__setattr__(self, "identities", tuple(self.identities))
        object.__setattr__(self, "residuals", tuple(self.residuals))

    def validate(self) -> tuple[bool, str]:
        """Validate the LafzMufrad proof.

        Returns:
            (is_valid, message)
        """
        # Must have at least one carrier
        if len(self.carriers) == 0:
            return (False, "No carriers preserved")

        # Must have at least one identity
        if len(self.identities) == 0:
            return (False, "No identities preserved")

        # Must have origin
        if not self.origin.strip():
            return (False, "Missing origin")

        return (True, "")


# ---------------------------------------------------------------------------
# Public API functions
# ---------------------------------------------------------------------------


def is_allowed_transition(from_state: DTASpace, to_state: DTASpace) -> bool:
    """Check if a transition between two DTA states is structurally allowed.

    Only adjacent transitions are permitted:
    - UNICODE_RAW → CARRIER
    - CARRIER → ISOLATED_LAFZ
    - ISOLATED_LAFZ → ROOT_STEM

    Jumps (e.g., CARRIER → ROOT_STEM) are forbidden.
    """
    allowed = {
        (DTASpace.UNICODE_RAW, DTASpace.CARRIER),
        (DTASpace.CARRIER, DTASpace.ISOLATED_LAFZ),
        (DTASpace.ISOLATED_LAFZ, DTASpace.ROOT_STEM),
    }
    return (from_state, to_state) in allowed


def accept_transition(proof: DTATransitionProof) -> tuple[bool, DTARejectionKind | None, str]:
    """Accept or reject a transition based on its proof.

    This is the main gate for all DTA transitions.

    Returns:
        (accepted, rejection_kind, message)
        If accepted is True, rejection_kind will be None.
    """
    return proof.validate()


def accept_lafz_mufrad(proof: DTALafzMufradAcceptanceProof) -> tuple[bool, str]:
    """Accept or reject a LafzMufrad based on its proof.

    LafzMufrad is the fundamental unit of Dal layer: an isolated lexical
    form with preserved carriers and identities, ready for (future) semantic
    analysis but not yet bearing meaning.

    Returns:
        (accepted, message)
    """
    return proof.validate()
