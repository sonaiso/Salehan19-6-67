# ANSWER BIRTH GOVERNANCE

This governance layer prevents jumping from generated language to certificate.

`evaluate_answer_birth_contract` returns only:
- zero
- hypothesis
- certificate

Public judgment request handling:
- requested `zero` returns `zero`
- requested `hypothesis` returns `hypothesis` (no silent promotion)
- requested `certificate` can return `certificate` only when governed certificate gates pass

Key blocking conditions include:
- missing intent,
- missing method,
- missing means,
- missing or fatally broken birth trace,
- forbidden transitions,
- means acting as judgment,
- fluency treated as proof,
- scientific method used directly for worldview/normative judgment,
- normative judgment without normative evidence,
- residual erasure.

Trace completeness is split:
- `path_complete`: intent/consciousness/mentality/method/style/means/language chain exists
- `evidence_complete`: evidence refs exist and satisfy method rank requirements
- `certificate_complete`: path_complete + evidence_complete

Answer-birth certificate means certificate-eligible within this layer and does not replace ProofObject/GovernanceGate/ReverseTrace in core governance.
