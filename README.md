# mse-ai

Deterministic ML + alpha research consumer built **on top of** the `mse-cli` foundation substrate.

## Architectural boundary

- `mse-ai` is a **downstream consumer** of `mse-cli`.
- `mse-ai` does **not** redefine foundation contracts.
- `mse-ai` imports canonical substrate from `mse_cli.core.*` via `substrate.py`:
  - **ML**: `feature_catalog`, `model_baselines`, `walk_forward_splits`
  - **Alpha/Signal**: `signal_engine`, `signal_alpha`, `signal_backtest`
  - **Data**: `OHLCVRecord` (canonical trade model)
- `mse-ai` produces models, predictions, evaluation reports, alpha signals, and backtest payloads.
- All outputs are **deterministic, credential-free, point-in-time safe** (inherited from `mse-cli` substrate).

## Install

```bash
pip install -e .
```

## Smoke test

```bash
pytest -q
```

## Run demos

```bash
mse-ai baseline          # Fit logistic baseline over demo training matrix
mse-ai signal             # Run signal backtest over synthetic OHLCV (APU)
mse-ai signal GOBI        # Same for a different symbol
```

## Boundary invariant

If you find yourself editing `mse_cli.core.*`, stop — that work belongs in the `mse-cli` repo, not here.
