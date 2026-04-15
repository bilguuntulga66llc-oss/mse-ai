"""Deterministic strategy backtest pipeline over real mse-cli OHLCV data.

Runs the canonical strategy baselines (buy_and_hold, momentum_ma_crossover,
mean_reversion_bollinger) against live SDK trade history and produces a
ranked comparison payload.

Every run is deterministic, credential-free, and point-in-time safe —
those invariants come from the foundation; mse-ai just composes them.
"""

from __future__ import annotations

from typing import Any

from .substrate import MSEClient

COMPARISON_SCHEMA_VERSION = "mse_ai_strategy_comparison.v1"

CANONICAL_STRATEGIES: tuple[str, ...] = (
    "buy_and_hold",
    "momentum_ma_crossover",
    "mean_reversion_bollinger",
)


def run_strategy_backtest(
    symbol: str,
    *,
    strategy: str = "buy_and_hold",
    limit: int = 120,
    period: str = "1Y",
    short_window: int = 10,
    long_window: int = 30,
    bollinger_window: int = 20,
    bollinger_num_std: float = 2.0,
    client: MSEClient | None = None,
) -> dict[str, Any]:
    """Run a single named baseline strategy against live OHLCV data."""
    owned = client is None
    c = client or MSEClient()
    try:
        return c.research_strategy_baseline(
            symbol=symbol,
            strategy=strategy,
            limit=limit,
            period=period,
            short_window=short_window,
            long_window=long_window,
            bollinger_window=bollinger_window,
            bollinger_num_std=bollinger_num_std,
        )
    finally:
        if owned:
            close = getattr(c, "close", None)
            if callable(close):
                close()


def _summary_row(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    return {
        "strategy": payload.get("strategy"),
        "final_pnl_pct": summary.get("final_pnl_pct"),
        "max_pnl_pct": summary.get("max_pnl_pct"),
        "min_pnl_pct": summary.get("min_pnl_pct"),
        "max_drawdown_pct": summary.get("max_drawdown_pct"),
        "trade_count": summary.get("trade_count"),
        "long_bar_count": summary.get("long_bar_count"),
        "flat_bar_count": summary.get("flat_bar_count"),
        "bar_count": summary.get("bar_count"),
    }


def _sort_key(row: dict[str, Any]) -> float:
    value = row.get("final_pnl_pct")
    try:
        return float(value) if value is not None else float("-inf")
    except (TypeError, ValueError):
        return float("-inf")


def compare_strategies(
    symbol: str,
    *,
    strategies: tuple[str, ...] | list[str] | None = None,
    limit: int = 120,
    period: str = "1Y",
    client: MSEClient | None = None,
) -> dict[str, Any]:
    """Run every strategy in the catalog and rank by final P&L.

    Returns a `mse_ai_strategy_comparison.v1` payload:
    - comparison: rows sorted by final_pnl_pct descending
    - best_strategy / worst_strategy: convenience pointers
    - window: first/last date and bar_count from the underlying data
    """
    if strategies is None:
        chosen: tuple[str, ...] = CANONICAL_STRATEGIES
    else:
        chosen = tuple(strategies)
    if not chosen:
        raise ValueError("strategies must contain at least one baseline name")

    owned = client is None
    c = client or MSEClient()
    try:
        runs: list[dict[str, Any]] = [
            c.research_strategy_baseline(
                symbol=symbol,
                strategy=name,
                limit=limit,
                period=period,
            )
            for name in chosen
        ]
    finally:
        if owned:
            close = getattr(c, "close", None)
            if callable(close):
                close()

    rows = [_summary_row(r) for r in runs]
    ranked = sorted(rows, key=_sort_key, reverse=True)

    first_summary = runs[0].get("summary") if runs and isinstance(runs[0].get("summary"), dict) else {}
    window = {
        "bar_count": first_summary.get("bar_count"),
        "first_date": first_summary.get("first_date"),
        "last_date": first_summary.get("last_date"),
    }

    symbol_norm = str(symbol or "").strip().upper()
    return {
        "schema_version": COMPARISON_SCHEMA_VERSION,
        "symbol": symbol_norm,
        "limit": int(limit),
        "period": str(period or "1Y").strip().upper(),
        "window": window,
        "strategies_evaluated": list(chosen),
        "comparison": ranked,
        "best_strategy": ranked[0]["strategy"] if ranked else None,
        "worst_strategy": ranked[-1]["strategy"] if ranked else None,
        "summary": {
            "strategy_count": len(ranked),
            "positive_pnl_count": sum(1 for r in ranked if _sort_key(r) > 0),
            "negative_pnl_count": sum(1 for r in ranked if _sort_key(r) < 0),
        },
    }


def render_comparison(payload: dict[str, Any]) -> str:
    """Human-readable ranking table."""
    lines = [
        f"Strategy comparison: {payload.get('symbol')}  "
        f"(limit={payload.get('limit')}, period={payload.get('period')})",
    ]
    window = payload.get("window") if isinstance(payload.get("window"), dict) else {}
    lines.append(
        f"  window: {window.get('first_date')} -> {window.get('last_date')}  "
        f"bars={window.get('bar_count')}"
    )
    lines.append("")
    lines.append(
        f"  {'strategy':<28} {'final_pnl%':>11} {'max_dd%':>9} "
        f"{'trades':>7} {'long_bars':>10}"
    )
    lines.append("  " + "-" * 70)
    for row in payload.get("comparison", []):
        name = str(row.get("strategy") or "?")
        pnl = row.get("final_pnl_pct")
        mdd = row.get("max_drawdown_pct")
        trades = row.get("trade_count")
        long_bars = row.get("long_bar_count")
        pnl_str = f"{pnl:+.2f}" if isinstance(pnl, (int, float)) else "?"
        mdd_str = f"{mdd:.2f}" if isinstance(mdd, (int, float)) else "?"
        lines.append(
            f"  {name:<28} {pnl_str:>11} {mdd_str:>9} "
            f"{trades if trades is not None else '?':>7} "
            f"{long_bars if long_bars is not None else '?':>10}"
        )
    best = payload.get("best_strategy")
    if best:
        lines.append("")
        lines.append(f"Best by final P&L: {best}")
    return "\n".join(lines)


__all__ = [
    "COMPARISON_SCHEMA_VERSION",
    "CANONICAL_STRATEGIES",
    "run_strategy_backtest",
    "compare_strategies",
    "render_comparison",
]
