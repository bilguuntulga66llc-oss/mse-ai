"""Smoke tests: mse-ai substrate boundary is clean and callable."""

from __future__ import annotations

from mse_ai.substrate import (
    MSEClient,
    OHLCVRecord,
    build_feature_catalog_surface,
    build_signal_backtest_payload,
    build_training_dataset_manifest,
    build_walk_forward_split_plan,
    detect_momentum,
    detect_price_anomalies,
    detect_volume_anomalies,
    fit_baseline_model,
)


def test_substrate_boundary_imports_resolve():
    """Every re-exported symbol must be callable."""
    assert callable(MSEClient)
    assert callable(fit_baseline_model)
    assert callable(build_feature_catalog_surface)
    assert callable(build_walk_forward_split_plan)
    assert callable(build_signal_backtest_payload)
    assert callable(build_training_dataset_manifest)
    assert callable(detect_volume_anomalies)
    assert callable(detect_price_anomalies)
    assert callable(detect_momentum)


def test_ohlcv_record_type_available():
    """The canonical trade record type must be importable."""
    assert OHLCVRecord is not None


def test_feature_catalog_is_live():
    """The credential-free feature catalog must return a canonical payload."""
    client = MSEClient()
    try:
        payload = client.research_feature_catalog()
    finally:
        client.close()
    assert payload["schema_version"] == "feature_catalog.v1"
    assert len(payload.get("surfaces", [])) > 0


def test_label_catalog_is_live():
    """The credential-free label catalog must return a canonical payload."""
    client = MSEClient()
    try:
        payload = client.research_label_catalog()
    finally:
        client.close()
    assert payload["schema_version"] == "label_catalog.v1"
    assert payload["summary"]["surface_count"] > 0


def test_strategy_baseline_catalog_is_live():
    """The credential-free strategy baseline catalog must list strategies."""
    client = MSEClient()
    try:
        payload = client.research_strategy_baseline_catalog()
    finally:
        client.close()
    assert payload["schema_version"] == "strategy_baseline_catalog.v1"
    assert payload["strategy_count"] > 0
    for s in payload["strategies"]:
        assert s["deterministic"] is True
        assert s["credential_free"] is True
        assert s["point_in_time_safe"] is True
