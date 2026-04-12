"""Baseline model training over real mse-cli substrate data.

Uses the SDK to build a real training matrix from live feature/label
surfaces and fits the canonical deterministic baseline.
"""

from __future__ import annotations

from typing import Any

from .substrate import MSEClient, fit_baseline_model


def run_baseline_fit(
    symbol: str,
    *,
    model_kind: str = "logistic_binary",
    limit: int = 120,
    client: MSEClient | None = None,
) -> dict[str, Any]:
    """Build a real training matrix from the SDK and fit a baseline model."""
    owned = client is None
    client = client or MSEClient()
    try:
        matrix = client.research_training_matrix(
            symbol=symbol,
            limit=limit,
        )
    finally:
        if owned:
            client.close()
    return fit_baseline_model(matrix, model_kind=model_kind)
