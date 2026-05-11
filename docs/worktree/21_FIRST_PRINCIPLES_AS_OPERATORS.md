# 21 — First Principles as Operators

## Conception
- epistemic definition: forms bounded meaning without final proof judgment.
- mathematical form: `C=concept(I)`.
- programming contract: `ConceptionObject(conception_id, interpreted_meaning, concept_type, boundaries, examples, counterexamples, residuals)`.
- linguistic function: outputs usable concept representation.
- forbidden transitions: `judgment_without_subject`, `certificate_without_proof_object`.
- residuals: `concept_boundary_unclear`, `counterexample_gap`.

## Judgment
- epistemic definition: governed assignment after subject/domain/aspect/time/rank/evidence checks.
- mathematical form: `J=judge(C,E,Gate,Trace)`.
- programming contract: `JudgmentObject(judgment_id, claim_id, final_judgment, evidence_refs, residuals, reverse_trace, proof_object, governance_gate)`.
- linguistic function: emits governed epistemic status.
- forbidden transitions: `judgment_without_subject`, `certificate_without_evidence`, `certificate_without_proof_object`, `certificate_without_governance_gate`, `certificate_without_reverse_trace`.
- residuals: `missing_subject`, `insufficient_evidence`, `blocking_residual_present`.

## Operators
- `NoContradictionWithoutDomain`
- `NoDomainWithoutDesignation`
- `NoDesignationWithoutDistinction`
- `NoJudgmentWithoutSubject`
- `NoCertificateWithoutEvidence`
- `NoEvidenceWithoutClaimMatch`
- `NoDomainTransferWithoutBridge`
- `NoUniversalToParticularWithoutApplicability`

All operators must publish: `required_inputs`, `applies_before`, `applies_after`, `forbids`, `residual_on_violation`.
