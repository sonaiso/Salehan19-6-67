# -*- coding: utf-8 -*-
"""Compatibility shim -- the segmenter now lives in segmenter.py.

Any import of the form:
    from analyzer.segmentation.conservative import segment_token
will still work via this re-export.
"""
from analyzer.segmentation.segmenter import (  # noqa: F401
    segment_token,
    stem_surfaces_for_wazn,
)
