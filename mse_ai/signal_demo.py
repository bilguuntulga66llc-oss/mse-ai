"""Minimal alpha signal demo: build a deterministic signal_backtest.v1 payload.

Demonstrates architectural boundary: mse-alpha imports the foundation
detectors/backtest via `substrate`, composes them over a synthetic
OHLCV sequence, and returns a canonical `signal_backtest.v1` payload.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from .substrate import (
    OHLCVRecord,
    build_signal_backtest_payload,
    detect_accumulation_distribution,
    detect_momentum,
    detect_price_anomalies,
    detect_turnover_liquidity_shocks,
    detect_volume_anomalies,
)


def build_demo_records(symbol: str = "APU", n: int = 20) -> list[OHLCVRecord]:
    """Return a synthetic `n+1`-row OHLCV sequence with a spike on the last day."""
    records: list[OHLCVRecord] = []
    for i in range(n):
        close = 100.0 + (i % 5)
        volume = 100 + (i % 3) * 10
        turnover = 10_000.0 + i * 100
        records.append(
            OHLCVRecord(
                trading_date=date(2024, 1, 1) + timedelta(days=i),
                symbol=symbol,
                open_price=Decimal("100"),
                high_price=Decimal("105"),
                low_price=Decimal("95"),
                close_price=Decimal(str(close)),
                vwap=None,
                volume=volume,
                turnover=Decimal(str(turnover)),
                trades=None,
                price_change=None,
                price_change_pct=None,
            )
        )
    # inject a liquidity + price spike on the last day
    records.append(
        OHLCVRecord(
            trading_date=date(2024, 1, 1) + timedelta(days=n),
            symbol=symbol,
            open_price=Decimal("100"),
            high_price=Decimal("113"),
            low_price=Decimal("99"),
            close_price=Decimal("112"),
            vwap=None,
            volume=5_000,
            turnover=Decimal("90000"),
            trades=None,
            price_change=None,
            price_change_pct=None,
        )
    )
    return records


def run_demo_signal_backtest(symbol: str = "APU") -> dict[str, Any]:
    """Run the full detector pipeline and emit a `signal_backtest.v1` payload."""
    records = build_demo_records(symbol=symbol)
    volume_rows = detect_volume_anomalies(records, window=5, threshold=2.0, min_periods=5)
    price_rows = detect_price_anomalies(records, window=5, threshold=1.5, min_periods=5)
    momentum_rows = detect_momentum(records, period=5)
    accumulation_rows = detect_accumulation_distribution(
        records, window=5, threshold=1.5, min_periods=5
    )
    turnover_rows = detect_turnover_liquidity_shocks(
        records,
        window=5,
        threshold=1.5,
        min_periods=5,
        range_threshold=1.0,
    )
    return build_signal_backtest_payload(
        symbol=symbol,
        records=records,
        volume_rows=volume_rows,
        price_rows=price_rows,
        momentum_rows=momentum_rows,
        accumulation_rows=accumulation_rows,
        turnover_rows=turnover_rows,
        limit=120,
        window=5,
        threshold=1.5,
        period=5,
        std_floor=0.0,
        adaptive_threshold=False,
        range_threshold=1.0,
    )
