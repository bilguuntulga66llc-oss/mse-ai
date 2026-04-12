"""Signal backtest pipeline over real mse-cli trade data.

Fetches real OHLCV records from the SDK, runs the canonical detector
pipeline, and returns a `signal_backtest.v1` payload.
"""

from __future__ import annotations

from typing import Any

from .substrate import (
    MSEClient,
    build_signal_backtest_payload,
    detect_accumulation_distribution,
    detect_momentum,
    detect_price_anomalies,
    detect_volume_anomalies,
    detect_turnover_liquidity_shocks,
)


def run_signal_backtest(
    symbol: str,
    *,
    limit: int = 120,
    window: int = 20,
    threshold: float = 2.0,
    period: int = 20,
    std_floor: float = 0.0,
    adaptive_threshold: bool = False,
    range_threshold: float = 1.0,
    client: MSEClient | None = None,
) -> dict[str, Any]:
    """Fetch real trade data and run the full signal detector pipeline."""
    owned = client is None
    client = client or MSEClient()
    try:
        records = client.trade_history_typed(symbol=symbol, limit=limit)
    finally:
        if owned:
            client.close()

    volume_rows = detect_volume_anomalies(records, window=window, threshold=threshold, min_periods=window)
    price_rows = detect_price_anomalies(records, window=window, threshold=threshold, min_periods=window)
    momentum_rows = detect_momentum(records, period=period)
    accumulation_rows = detect_accumulation_distribution(
        records, window=window, threshold=threshold, min_periods=window,
    )
    turnover_rows = detect_turnover_liquidity_shocks(
        records, window=window, threshold=threshold, min_periods=window, range_threshold=range_threshold,
    )
    return build_signal_backtest_payload(
        symbol=symbol,
        records=records,
        volume_rows=volume_rows,
        price_rows=price_rows,
        momentum_rows=momentum_rows,
        accumulation_rows=accumulation_rows,
        turnover_rows=turnover_rows,
        limit=limit,
        window=window,
        threshold=threshold,
        period=period,
        std_floor=std_floor,
        adaptive_threshold=adaptive_threshold,
        range_threshold=range_threshold,
    )
