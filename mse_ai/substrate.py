"""Canonical mse-cli substrate surface consumed by mse-ai.

This module centralizes every `mse_cli.*` import so the rest of the
package has one clear boundary with the foundation layer. If you need
a new foundation contract, add the re-export here — never bypass it.
"""

from __future__ import annotations

from mse_cli.core.feature_catalog import build_feature_catalog_surface
from mse_cli.core.model_baselines import fit_baseline_model
from mse_cli.core.walk_forward_splits import build_walk_forward_split_plan

__all__ = [
    "build_feature_catalog_surface",
    "fit_baseline_model",
    "build_walk_forward_split_plan",
]
