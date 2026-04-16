"""Strategy backtest pipeline through the public mse-cli foundation SDK."""

from __future__ import annotations

from typing import Any

from .substrate import MSEClient

CANONICAL_STRATEGIES: tuple[str, ...] = (
    "buy_and_hold",
    "momentum_ma_crossover",
    "mean_reversion_bollinger",
)


def _close_owned(client: Any, *, owned: bool) -> None:
    if owned:
        close = getattr(client, "close", None)
        if callable(close):
            close()


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
    """Run a single named baseline strategy through the foundation SDK."""
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
        _close_owned(c, owned=owned)


def compare_strategies(
    symbol: str,
    *,
    strategies: tuple[str, ...] | list[str] | None = None,
    limit: int = 120,
    period: str = "1Y",
    client: MSEClient | None = None,
) -> dict[str, Any]:
    """Run foundation-owned strategy comparison."""
    chosen = (
        ()
        if strategies is None
        else tuple(str(item or "").strip().lower() for item in strategies if str(item or "").strip())
    )
    if strategies is not None and not chosen:
        raise ValueError("strategies must contain at least one baseline name")

    owned = client is None
    c = client or MSEClient()
    try:
        return c.research_strategy_comparison(
            symbol=symbol,
            strategies=chosen,
            limit=limit,
            period=period,
        )
    finally:
        _close_owned(c, owned=owned)


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
    "CANONICAL_STRATEGIES",
    "run_strategy_backtest",
    "compare_strategies",
    "render_comparison",
]
