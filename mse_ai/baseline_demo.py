"""Minimal end-to-end demo: consume mse-cli substrate to train a baseline.

Demonstrates the architectural boundary: mse-ai imports the foundation
contract once (`substrate.fit_baseline_model`), builds a canonical
`training_matrix.v1` payload, and returns a deterministic
`baseline_model_fit.v1` result. No foundation contracts are redefined.
"""

from __future__ import annotations

from typing import Any

from .substrate import fit_baseline_model


def build_demo_training_matrix() -> dict[str, Any]:
    """Return a canonical `training_matrix.v1` payload for demo use.

    Two features (`momentum_roc_pct`, `volume_z_score`), one label
    (`fwd_return_5d`), eight rows split across TRAIN/VALIDATION/TEST.
    """
    feature_columns = [
        "signal_backtest_export__momentum_roc_pct",
        "signal_backtest_export__volume_z_score",
    ]
    rows = [
        ("2026-01-01", "TRAIN", -8.0, -2.0, 0.2),
        ("2026-01-02", "TRAIN", -4.0, -1.0, 0.1),
        ("2026-01-03", "TRAIN", 6.0, 1.2, 0.4),
        ("2026-01-04", "TRAIN", 10.0, 2.5, 0.6),
        ("2026-01-05", "VALIDATION", -5.0, -1.4, 0.2),
        ("2026-01-06", "VALIDATION", 7.0, 1.6, 0.5),
        ("2026-01-07", "TEST", -9.0, -2.2, 0.3),
        ("2026-01-08", "TEST", 12.0, 2.9, 0.7),
    ]
    return {
        "schema_version": "training_matrix.v1",
        "surface_id": "model.training_matrix",
        "dataset_id": "mse_ai::demo",
        "snapshot_id": "mse_ai::demo::smoke",
        "feature_surface_ids": ["signal.backtest_export"],
        "label_surface_id": "labels.forward_return",
        "target_field": "fwd_return_5d",
        "feature_columns": feature_columns,
        "rows": [
            {
                "row_id": f"APU:{as_of_date}",
                "symbol": "APU",
                "as_of_date": as_of_date,
                "split": split,
                "target": target,
                "target_field": "fwd_return_5d",
                "feature_map": {
                    feature_columns[0]: momentum,
                    feature_columns[1]: volume,
                },
                "feature_vector": [momentum, volume],
                "feature_surface_presence": ["signal.backtest_export"],
                "missing_feature_surfaces": [],
                "as_of_dates_by_surface": {"signal.backtest_export": as_of_date},
                "label_filters": {"complete_window": True, "liquidity_available": True},
                "source_rows": [],
                "provenance": {"source_path": "mse_ai.baseline_demo"},
                "lineage": {"lineage_key": f"APU:{as_of_date}"},
            }
            for as_of_date, split, target, momentum, volume in rows
        ],
    }


def run_demo_baseline() -> dict[str, Any]:
    """Fit the mse-cli logistic baseline over the demo matrix."""
    matrix = build_demo_training_matrix()
    return fit_baseline_model(matrix, model_kind="logistic_binary")
