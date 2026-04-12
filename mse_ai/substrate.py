"""Canonical mse-cli substrate surface consumed by mse-ai.

This module centralizes every `mse_cli.*` import so the rest of the
package has one clear boundary with the foundation layer. If you need
a new foundation contract, add the re-export here — never bypass it.
"""

from __future__ import annotations

# ML baseline + walk-forward
from mse_cli.core.feature_catalog import build_feature_catalog_surface
from mse_cli.core.model_baselines import fit_baseline_model
from mse_cli.core.models.trading import OHLCVRecord
from mse_cli.core.walk_forward_splits import build_walk_forward_split_plan

# Signal / alpha detectors
from mse_cli.core.signal_alpha import (
    detect_accumulation_distribution,
    detect_turnover_liquidity_shocks,
)
from mse_cli.core.signal_backtest import build_signal_backtest_payload
from mse_cli.core.signal_engine import (
    detect_momentum,
    detect_price_anomalies,
    detect_volume_anomalies,
)

__all__ = [
    "OHLCVRecord",
    "build_feature_catalog_surface",
    "build_signal_backtest_payload",
    "build_walk_forward_split_plan",
    "detect_accumulation_distribution",
    "detect_momentum",
    "detect_price_anomalies",
    "detect_turnover_liquidity_shocks",
    "detect_volume_anomalies",
    "fit_baseline_model",
]
