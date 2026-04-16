"""Signal backtest pipeline through the public mse-cli foundation SDK."""

from __future__ import annotations

from typing import Any

from .substrate import MSEClient


def _close_owned(client: Any, *, owned: bool) -> None:
    if owned:
        close = getattr(client, "close", None)
        if callable(close):
            close()


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
    """Run canonical signal backtest through the foundation SDK."""
    owned = client is None
    c = client or MSEClient()
    try:
        return c.research_signal_backtest(
            symbol=symbol,
            limit=limit,
            window=window,
            threshold=threshold,
            period=period,
            std_floor=std_floor,
            adaptive_threshold=adaptive_threshold,
            range_threshold=range_threshold,
        )
    finally:
        _close_owned(c, owned=owned)
