# 09 — Reverse Trace

Every final judgment must support reverse traceability to its governed sources.

Requirements:
- Trace path is explicit and inspectable.
- ReverseTrace must connect judgment back through claim and evidence chain.
- Missing reverse trace blocks CERTIFICATE.
- ReverseTrace must reconstruct cognitive legitimacy, not only execution history.
- Reconstruction must expose transitions, measures, evidence basis, inference basis, residuals, and current certainty/completeness state as represented by existing ReverseTrace fields such as `certainty_chain` and `complete`.

Note: explicit runtime enforcement of a separately named `certainty_ceiling` contract belongs to a future enforcement PR.
