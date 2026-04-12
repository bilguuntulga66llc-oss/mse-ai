"""Smoke test: mse-ai consumes mse-cli substrate cleanly."""

from __future__ import annotations

from mse_ai.baseline_demo import build_demo_training_matrix, run_demo_baseline
from mse_ai.signal_demo import build_demo_records, run_demo_signal_backtest
from mse_ai.substrate import (
    OHLCVRecord,
    build_feature_catalog_surface,
    build_signal_backtest_payload,
    build_walk_forward_split_plan,
    detect_volume_anomalies,
    fit_baseline_model,
)


def test_substrate_imports_resolve():
    assert callable(fit_baseline_model)
    assert callable(build_feature_catalog_surface)
    assert callable(build_walk_forward_split_plan)
    assert callable(build_signal_backtest_payload)
    assert callable(detect_volume_anomalies)


def test_demo_training_matrix_is_canonical_shape():
    matrix = build_demo_training_matrix()
    assert matrix["schema_version"] == "training_matrix.v1"
    assert matrix["surface_id"] == "model.training_matrix"
    assert matrix["target_field"] == "fwd_return_5d"
    assert len(matrix["rows"]) == 8
    assert len(matrix["feature_columns"]) == 2


def test_demo_baseline_emits_canonical_fit_contract():
    fit = run_demo_baseline()
    assert fit["schema_version"] == "baseline_model_fit.v1"
    assert fit["surface_id"] == "model.baseline_fit"
    assert fit["model_kind"] == "logistic_binary"
    assert "model_params" in fit
    assert "evaluation" in fit
    assert "lineage" in fit


def test_demo_records_are_canonical_ohlcv():
    records = build_demo_records(symbol="APU")
    assert len(records) == 21
    assert all(isinstance(r, OHLCVRecord) for r in records)
    assert records[0].symbol == "APU"


def test_demo_signal_backtest_emits_canonical_contract():
    payload = run_demo_signal_backtest(symbol="APU")
    assert payload["schema_version"] == "signal_backtest.v1"
    assert payload.get("symbol") == "APU"
    assert "timeline" in payload or "rows" in payload or "events" in payload
