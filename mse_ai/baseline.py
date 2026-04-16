"""Baseline model training through the public mse-cli foundation SDK."""

from __future__ import annotations

from typing import Any

from .substrate import MSEClient


def _close_owned(client: Any, *, owned: bool) -> None:
    if owned:
        close = getattr(client, "close", None)
        if callable(close):
            close()


def run_baseline_fit(
    symbol: str,
    *,
    model_kind: str = "logistic_binary",
    limit: int = 120,
    client: MSEClient | None = None,
) -> dict[str, Any]:
    """Fit a baseline model via the canonical foundation SDK surface."""
    owned = client is None
    c = client or MSEClient()
    try:
        return c.research_baseline_model_fit(
            symbol=symbol,
            model_kind=model_kind,
            limit=limit,
            period="ALL",
        )
    finally:
        _close_owned(c, owned=owned)


__all__ = ["run_baseline_fit"]
