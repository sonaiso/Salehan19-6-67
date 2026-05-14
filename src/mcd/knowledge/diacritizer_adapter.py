"""diacritizer_adapter.py — lazy adapter for Models_gpt52 Arabic diacritization.

Resolves the Models_gpt52 package, loads the word-aware transformer (with char-level
fallback), and exposes a single ``diacritize(text)`` call used by mishkat_root_lookup
to vocalize words before handing them to NAA.

Path resolution (first match wins):
  env var  GPT52_DIR          — explicit path to the Models_gpt52 directory
  <salehan>/Models_gpt52      — sibling of Salehan19-6-67 inside the salehan repo

If the package is unavailable, every call silently returns None so the caller
degrades to the unvocalized code path.
"""
from __future__ import annotations

import os
import pathlib
import sys
from functools import lru_cache

_ENV = "GPT52_DIR"

# mishkat_root_lookup.py lives at:
#   <salehan>/Salehan19-6-67/src/mcd/knowledge/diacritizer_adapter.py
# parents: [0]=knowledge [1]=mcd [2]=src [3]=Salehan19-6-67 [4]=salehan
_HERE = pathlib.Path(__file__).resolve()

_predictor = None   # None = not yet tried; False = unavailable


def _gpt52_dir() -> pathlib.Path | None:
    env = os.environ.get(_ENV)
    if env:
        p = pathlib.Path(env).expanduser().resolve()
        return p if p.is_dir() else None
    candidate = _HERE.parents[4] / "Models_gpt52"
    return candidate if candidate.is_dir() else None


def _load() -> object | None:
    """Lazy-load ModelPredictor; cache result. Returns predictor or None."""
    global _predictor
    if _predictor is not None:
        return _predictor if _predictor is not False else None

    gpt52 = _gpt52_dir()
    if gpt52 is None:
        _predictor = False
        return None

    # Insert Models_gpt52 onto sys.path so its src package is importable
    s = str(gpt52)
    if s not in sys.path:
        sys.path.insert(0, s)

    try:
        from src.services.predictor import ModelPredictor  # type: ignore

        # Prefer word-aware model; fall back to char-level
        word_pt  = gpt52 / "src" / "models" / "Word_level_scheduled" / "runs" / "teacher" / "best.pt"
        char_pt  = gpt52 / "src" / "models" / "Char_level_default"   / "runs" / "teacher" / "best.pt"

        model_path = word_pt if word_pt.exists() else (char_pt if char_pt.exists() else None)
        if model_path is None:
            _predictor = False
            return None

        _predictor = ModelPredictor(str(model_path))
        return _predictor

    except Exception:
        _predictor = False
        return None


def diacritize(text: str) -> str | None:
    """Return diacritized Arabic text, or None if the model is unavailable.

    The input is normalized (stray diacritics stripped, alef variants unified)
    before inference so the model sees clean unvocalized text.

    Args:
        text: Arabic word or short phrase (unvocalized or partially vocalized).

    Returns:
        Diacritized string on success, None if the model could not be loaded.
    """
    if not text or not text.strip():
        return None

    predictor = _load()
    if predictor is None:
        return None

    try:
        # normalize_arabic strips stray diacritics and unifies alef/hamza before inference
        from src.core.normalization import normalize_arabic  # type: ignore

        clean = normalize_arabic(text)
        diacritized, _ids, _map = predictor.predict(clean)
        return diacritized if diacritized else None
    except Exception:
        return None


def available() -> bool:
    """Return True if the diacritizer loaded successfully."""
    return _load() is not None
