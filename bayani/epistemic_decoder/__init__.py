"""Epistemic Cognitive Decoder package.

Provides:

- :class:`~bayani.epistemic_decoder.decoder.EpistemicCognitiveDecoder`
  — the seven-unit orchestrator.
- Individual units in :mod:`bayani.epistemic_decoder.units`.
- Typed contracts in :mod:`bayani.epistemic_decoder.contracts`.

Quick start::

    from bayani.epistemic_decoder import EpistemicCognitiveDecoder

    decoder = EpistemicCognitiveDecoder()
    output = decoder.decode("ما الفرق بين العلم والثقافة؟")
    print(output.final_answer)
"""

from bayani.epistemic_decoder.decoder import EpistemicCognitiveDecoder

__all__ = ["EpistemicCognitiveDecoder"]
