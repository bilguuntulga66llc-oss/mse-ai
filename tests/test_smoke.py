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


# ─── Strategy pipeline (deterministic, in-process) ─────────────────


class _FakeStrategyClient:
    """In-process client that returns canonical strategy_baseline.v1 payloads."""

    def __init__(self) -> None:
        self.closed = False
        self.calls: list[dict] = []

    def close(self) -> None:
        self.closed = True

    def research_strategy_baseline(
        self,
        *,
        symbol: str,
        strategy: str,
        limit: int,
        period: str = "1Y",
        short_window: int = 10,
        long_window: int = 30,
        bollinger_window: int = 20,
        bollinger_num_std: float = 2.0,
    ) -> dict:
        self.calls.append({"symbol": symbol, "strategy": strategy, "limit": limit})
        pnl_map = {
            "buy_and_hold": 5.25,
            "momentum_ma_crossover": -1.5,
            "mean_reversion_bollinger": 12.75,
        }
        trade_map = {
            "buy_and_hold": 1,
            "momentum_ma_crossover": 3,
            "mean_reversion_bollinger": 2,
        }
        return {
            "schema_version": "strategy_baseline.v1",
            "symbol": symbol.upper(),
            "strategy": strategy,
            "summary": {
                "bar_count": 120,
                "first_date": "2025-01-02",
                "last_date": "2025-06-30",
                "final_pnl_pct": pnl_map.get(strategy, 0.0),
                "max_pnl_pct": pnl_map.get(strategy, 0.0) + 1.0,
                "min_pnl_pct": pnl_map.get(strategy, 0.0) - 1.0,
                "max_drawdown_pct": 3.4,
                "trade_count": trade_map.get(strategy, 0),
                "long_bar_count": 80,
                "flat_bar_count": 40,
            },
            "events": [],
        }


def test_run_strategy_backtest_forwards_kwargs():
    from mse_ai.strategy import run_strategy_backtest

    fake = _FakeStrategyClient()
    payload = run_strategy_backtest(
        "apu", strategy="momentum_ma_crossover", limit=60, client=fake,
    )

    assert payload["strategy"] == "momentum_ma_crossover"
    assert payload["symbol"] == "APU"
    assert fake.calls == [{"symbol": "apu", "strategy": "momentum_ma_crossover", "limit": 60}]
    assert fake.closed is False  # client was externally supplied


def test_compare_strategies_ranks_by_final_pnl():
    from mse_ai.strategy import compare_strategies

    fake = _FakeStrategyClient()
    payload = compare_strategies("apu", limit=60, client=fake)

    assert payload["schema_version"] == "mse_ai_strategy_comparison.v1"
    assert payload["symbol"] == "APU"
    assert payload["strategies_evaluated"] == [
        "buy_and_hold",
        "momentum_ma_crossover",
        "mean_reversion_bollinger",
    ]
    # mean_reversion_bollinger has highest P&L (12.75), momentum lowest (-1.5)
    ranked = [row["strategy"] for row in payload["comparison"]]
    assert ranked == [
        "mean_reversion_bollinger",
        "buy_and_hold",
        "momentum_ma_crossover",
    ]
    assert payload["best_strategy"] == "mean_reversion_bollinger"
    assert payload["worst_strategy"] == "momentum_ma_crossover"
    assert payload["summary"]["positive_pnl_count"] == 2
    assert payload["summary"]["negative_pnl_count"] == 1
    assert payload["window"] == {
        "bar_count": 120,
        "first_date": "2025-01-02",
        "last_date": "2025-06-30",
    }


def test_render_comparison_contains_ranking_table():
    from mse_ai.strategy import compare_strategies, render_comparison

    payload = compare_strategies("apu", limit=60, client=_FakeStrategyClient())
    rendered = render_comparison(payload)

    assert "Strategy comparison: APU" in rendered
    assert "mean_reversion_bollinger" in rendered
    assert "buy_and_hold" in rendered
    assert "Best by final P&L: mean_reversion_bollinger" in rendered


def test_compare_strategies_rejects_empty_strategy_list():
    from mse_ai.strategy import compare_strategies

    import pytest

    with pytest.raises(ValueError):
        compare_strategies("apu", strategies=[], client=_FakeStrategyClient())


def test_main_compare_command_renders_default(monkeypatch, capsys):
    import mse_ai.main as cli

    monkeypatch.setattr(
        cli,
        "compare_strategies",
        lambda symbol, limit: {
            "schema_version": "mse_ai_strategy_comparison.v1",
            "symbol": symbol.upper(),
            "limit": limit,
            "period": "1Y",
            "window": {"bar_count": 10, "first_date": "x", "last_date": "y"},
            "comparison": [{"strategy": "buy_and_hold", "final_pnl_pct": 5.0,
                            "max_drawdown_pct": 1.0, "trade_count": 1, "long_bar_count": 5}],
            "best_strategy": "buy_and_hold",
            "worst_strategy": "buy_and_hold",
            "summary": {"strategy_count": 1, "positive_pnl_count": 1, "negative_pnl_count": 0},
        },
    )

    assert cli.main(["compare", "apu", "--limit", "60"]) == 0
    out = capsys.readouterr().out
    assert "Strategy comparison: APU" in out
    assert "buy_and_hold" in out


def test_main_compare_command_json_flag(monkeypatch, capsys):
    import json as jsonlib
    import mse_ai.main as cli

    monkeypatch.setattr(
        cli,
        "compare_strategies",
        lambda symbol, limit: {
            "schema_version": "mse_ai_strategy_comparison.v1",
            "symbol": symbol.upper(),
            "limit": limit,
            "best_strategy": "buy_and_hold",
        },
    )

    assert cli.main(["compare", "APU", "--json"]) == 0
    out = capsys.readouterr().out
    payload = jsonlib.loads(out)
    assert payload["best_strategy"] == "buy_and_hold"


def test_main_strategy_command_forwards_name(monkeypatch, capsys):
    import mse_ai.main as cli

    captured: dict = {}

    def fake_run(symbol, strategy, limit):
        captured["symbol"] = symbol
        captured["strategy"] = strategy
        captured["limit"] = limit
        return {"schema_version": "strategy_baseline.v1", "strategy": strategy}

    monkeypatch.setattr(cli, "run_strategy_backtest", fake_run)

    assert cli.main(["strategy", "apu", "--name", "momentum_ma_crossover", "--limit", "90"]) == 0
    assert captured == {"symbol": "apu", "strategy": "momentum_ma_crossover", "limit": 90}
