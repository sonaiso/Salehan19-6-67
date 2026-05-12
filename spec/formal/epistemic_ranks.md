# Epistemic Rank System

```python
class EpistemicRank(Enum):
    ZERO = 0
    POSSIBILITY = 1
    HYPOTHESIS = 2
    WEAK_EVIDENCE = 3
    STRONG_EVIDENCE = 4
    CERTIFICATE = 5
    FINAL_JUDGMENT = 6
```

## Core Rule

\[
\text{Rank(Evidence)} \ge \text{RequiredRank(Judgment)}
\]

## Notes

- This rank ladder is a transition-control scale, not an extra final public judgment set.
- Final public epistemic outputs remain constrained to:
  - ZERO
  - HYPOTHESIS
  - CERTIFICATE
