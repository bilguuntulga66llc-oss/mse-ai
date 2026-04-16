"""Smoke tests: mse-ai is a clean product consumer of mse-cli."""

from __future__ import annotations

from pathlib import Path


def test_substrate_boundary_is_public_sdk_only():
    from mse_ai.substrate import MSEClient

    substrate_source = Path(__file__).parents[1].joinpath("mse_ai", "substrate.py").read_text(encoding="utf-8")
    assert callable(MSEClient)
    assert "mse_cli.core" not in substrate_source
    assert "from mse_cli.sdk import MSEClient" in substrate_source


def test_feature_catalog_is_live():
    """The credential-free feature catalog must return a canonical payload."""
    from mse_ai.substrate import MSEClient

    client = MSEClient()
    try:
        payload = client.research_feature_catalog()
    finally:
        client.close()
    assert payload["schema_version"] == "feature_catalog.v1"
    assert len(payload.get("surfaces", [])) > 0


def test_label_catalog_is_live():
    """The credential-free label catalog must return a canonical payload."""
    from mse_ai.substrate import MSEClient

    client = MSEClient()
    try:
        payload = client.research_label_catalog()
    finally:
        client.close()
    assert payload["schema_version"] == "label_catalog.v1"
    assert payload["summary"]["surface_count"] > 0


def test_strategy_baseline_catalog_is_live():
    """The credential-free strategy baseline catalog must list strategies."""
    from mse_ai.substrate import MSEClient

    client = MSEClient()
    try:
        payload = client.research_strategy_baseline_catalog()
    finally:
        client.close()
    assert payload["schema_version"] == "strategy_baseline_catalog.v1"
    assert payload["strategy_count"] > 0
    for strategy in payload["strategies"]:
        assert strategy["deterministic"] is True
        assert strategy["credential_free"] is True
        assert strategy["point_in_time_safe"] is True


class _FakeFoundationClient:
    def __init__(self) -> None:
        self.closed = False
        self.calls: list[dict] = []

    def close(self) -> None:
        self.closed = True

    def research_baseline_model_fit(
        self,
        *,
        symbol: str,
        model_kind: str,
        limit: int,
        period: str,
    ) -> dict:
        self.calls.append(
            {
                "method": "research_baseline_model_fit",
                "symbol": symbol,
                "model_kind": model_kind,
                "limit": limit,
                "period": period,
            }
        )
        return {
            "schema_version": "baseline_model_fit.v1",
            "model_kind": model_kind,
            "dataset_id": f"{symbol.upper()}:ohlcv:2026-01-01:2026-01-12",
        }

    def research_signal_backtest(self, **kwargs) -> dict:  # noqa: ANN003
        self.calls.append({"method": "research_signal_backtest", **kwargs})
        return {
            "schema_version": "signal_backtest.v1",
            "symbol": str(kwargs["symbol"]).upper(),
            "config": dict(kwargs),
        }

    def research_strategy_baseline(self, **kwargs) -> dict:  # noqa: ANN003
        self.calls.append({"method": "research_strategy_baseline", **kwargs})
        return {
            "schema_version": "strategy_baseline.v1",
            "symbol": str(kwargs["symbol"]).upper(),
            "strategy": kwargs["strategy"],
        }

    def research_strategy_comparison(self, **kwargs) -> dict:  # noqa: ANN003
        self.calls.append({"method": "research_strategy_comparison", **kwargs})
        strategies = list(kwargs.get("strategies") or [
            "buy_and_hold",
            "momentum_ma_crossover",
            "mean_reversion_bollinger",
        ])
        comparison = [
            {
                "strategy": "mean_reversion_bollinger",
                "final_pnl_pct": 12.75,
                "max_drawdown_pct": 2.0,
                "trade_count": 2,
                "long_bar_count": 80,
            },
            {
                "strategy": "buy_and_hold",
                "final_pnl_pct": 5.25,
                "max_drawdown_pct": 3.4,
                "trade_count": 1,
                "long_bar_count": 80,
            },
            {
                "strategy": "momentum_ma_crossover",
                "final_pnl_pct": -1.5,
                "max_drawdown_pct": 4.0,
                "trade_count": 3,
                "long_bar_count": 70,
            },
        ]
        comparison = [row for row in comparison if row["strategy"] in strategies]
        valid = [row for row in comparison if isinstance(row.get("final_pnl_pct"), (int, float))]
        return {
            "schema_version": "strategy_comparison.v1",
            "symbol": str(kwargs["symbol"]).upper(),
            "limit": kwargs["limit"],
            "period": kwargs["period"],
            "window": {"bar_count": 120, "first_date": "2025-01-02", "last_date": "2025-06-30"},
            "strategies_evaluated": strategies,
            "comparison": comparison,
            "best_strategy": valid[0]["strategy"] if valid else None,
            "worst_strategy": valid[-1]["strategy"] if valid else None,
            "summary": {
                "strategy_count": len(comparison),
                "positive_pnl_count": sum(1 for row in valid if row["final_pnl_pct"] > 0),
                "negative_pnl_count": sum(1 for row in valid if row["final_pnl_pct"] < 0),
                "unknown_pnl_count": len(comparison) - len(valid),
            },
        }


def test_run_baseline_fit_delegates_to_foundation_surface():
    from mse_ai.baseline import run_baseline_fit

    fake = _FakeFoundationClient()
    payload = run_baseline_fit("apu", limit=12, client=fake)

    assert payload["schema_version"] == "baseline_model_fit.v1"
    assert payload["model_kind"] == "logistic_binary"
    assert payload["dataset_id"].startswith("APU:ohlcv:")
    assert fake.calls == [
        {
            "method": "research_baseline_model_fit",
            "symbol": "apu",
            "model_kind": "logistic_binary",
            "limit": 12,
            "period": "ALL",
        }
    ]
    assert fake.closed is False


def test_signal_backtest_delegates_detector_options_to_foundation_surface():
    from mse_ai.signal import run_signal_backtest

    fake = _FakeFoundationClient()
    payload = run_signal_backtest(
        "apu",
        limit=12,
        std_floor=0.5,
        adaptive_threshold=True,
        range_threshold=1.25,
        client=fake,
    )

    assert payload["schema_version"] == "signal_backtest.v1"
    assert fake.calls == [
        {
            "method": "research_signal_backtest",
            "symbol": "apu",
            "limit": 12,
            "window": 20,
            "threshold": 2.0,
            "period": 20,
            "std_floor": 0.5,
            "adaptive_threshold": True,
            "range_threshold": 1.25,
        }
    ]


def test_run_strategy_backtest_forwards_kwargs():
    from mse_ai.strategy import run_strategy_backtest

    fake = _FakeFoundationClient()
    payload = run_strategy_backtest(
        "apu",
        strategy="momentum_ma_crossover",
        limit=60,
        client=fake,
    )

    assert payload["strategy"] == "momentum_ma_crossover"
    assert payload["symbol"] == "APU"
    assert fake.calls[0] == {
        "method": "research_strategy_baseline",
        "symbol": "apu",
        "strategy": "momentum_ma_crossover",
        "limit": 60,
        "period": "1Y",
        "short_window": 10,
        "long_window": 30,
        "bollinger_window": 20,
        "bollinger_num_std": 2.0,
    }
    assert fake.closed is False


def test_compare_strategies_delegates_to_foundation_comparison():
    from mse_ai.strategy import compare_strategies

    fake = _FakeFoundationClient()
    payload = compare_strategies("apu", limit=60, client=fake)

    assert payload["schema_version"] == "strategy_comparison.v1"
    assert payload["symbol"] == "APU"
    assert payload["strategies_evaluated"] == [
        "buy_and_hold",
        "momentum_ma_crossover",
        "mean_reversion_bollinger",
    ]
    assert payload["best_strategy"] == "mean_reversion_bollinger"
    assert payload["worst_strategy"] == "momentum_ma_crossover"
    assert fake.calls == [
        {
            "method": "research_strategy_comparison",
            "symbol": "apu",
            "strategies": (),
            "limit": 60,
            "period": "1Y",
        }
    ]


def test_render_comparison_contains_ranking_table():
    from mse_ai.strategy import compare_strategies, render_comparison

    payload = compare_strategies("apu", limit=60, client=_FakeFoundationClient())
    rendered = render_comparison(payload)

    assert "Strategy comparison: APU" in rendered
    assert "mean_reversion_bollinger" in rendered
    assert "buy_and_hold" in rendered
    assert "Best by final P&L: mean_reversion_bollinger" in rendered


def test_compare_strategies_rejects_empty_strategy_list():
    import pytest

    from mse_ai.strategy import compare_strategies

    with pytest.raises(ValueError):
        compare_strategies("apu", strategies=[], client=_FakeFoundationClient())


def test_main_compare_command_renders_default(monkeypatch, capsys):
    import mse_ai.main as cli

    monkeypatch.setattr(
        cli,
        "compare_strategies",
        lambda symbol, limit, period="1Y": {
            "schema_version": "strategy_comparison.v1",
            "symbol": symbol.upper(),
            "limit": limit,
            "period": period,
            "window": {"bar_count": 10, "first_date": "x", "last_date": "y"},
            "comparison": [
                {
                    "strategy": "buy_and_hold",
                    "final_pnl_pct": 5.0,
                    "max_drawdown_pct": 1.0,
                    "trade_count": 1,
                    "long_bar_count": 5,
                }
            ],
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
        lambda symbol, limit, period="1Y": {
            "schema_version": "strategy_comparison.v1",
            "symbol": symbol.upper(),
            "limit": limit,
            "best_strategy": "buy_and_hold",
        },
    )

    assert cli.main(["compare", "APU", "--json"]) == 0
    out = capsys.readouterr().out
    payload = jsonlib.loads(out)
    assert payload["best_strategy"] == "buy_and_hold"


def test_main_strategy_command_forwards_name(monkeypatch):
    import mse_ai.main as cli

    captured: dict = {}

    def fake_run(symbol, strategy, limit, **kwargs):  # noqa: ANN003
        captured["symbol"] = symbol
        captured["strategy"] = strategy
        captured["limit"] = limit
        captured["period"] = kwargs.get("period")
        return {"schema_version": "strategy_baseline.v1", "strategy": strategy}

    monkeypatch.setattr(cli, "run_strategy_backtest", fake_run)

    assert cli.main(["strategy", "apu", "--name", "momentum_ma_crossover", "--limit", "90"]) == 0
    assert captured == {"symbol": "apu", "strategy": "momentum_ma_crossover", "limit": 90, "period": "1Y"}


def test_main_rejects_invalid_limit_without_traceback(capsys):
    import mse_ai.main as cli

    assert cli.main(["signal", "APU", "--limit", "nope"]) == 2
    err = capsys.readouterr().err
    assert "must be an integer" in err
    assert "Traceback" not in err
