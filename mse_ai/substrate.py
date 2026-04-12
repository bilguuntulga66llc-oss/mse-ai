"""Canonical mse-cli substrate surface consumed by mse-ai.

Single boundary — every mse_cli.* import lives here. No other module
in this package imports from mse_cli directly.
"""

from __future__ import annotations

from mse_cli.core.feature_catalog import build_feature_catalog_surface
from mse_cli.core.model_baselines import fit_baseline_model
from mse_cli.core.models.trading import OHLCVRecord
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
from mse_cli.core.training_dataset_manifest import build_training_dataset_manifest
from mse_cli.core.walk_forward_splits import build_walk_forward_split_plan
from mse_cli.sdk import MSEClient

__all__ = [
    "MSEClient",
    "OHLCVRecord",
    "build_feature_catalog_surface",
    "build_signal_backtest_payload",
    "build_training_dataset_manifest",
    "build_walk_forward_split_plan",
    "detect_accumulation_distribution",
    "detect_momentum",
    "detect_price_anomalies",
    "detect_turnover_liquidity_shocks",
    "detect_volume_anomalies",
    "fit_baseline_model",
]
