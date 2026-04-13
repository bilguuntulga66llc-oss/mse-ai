# mse-ai

Deterministic ML and signal research for the Mongolian Stock Exchange — built on `mse-cli`.

All outputs are **deterministic, credential-free, and point-in-time safe**.

## Install

```bash
pip install mse-ai
```

## Commands

```bash
mse-ai signal APU              # 5-detector signal backtest on APU
mse-ai signal GOBI             # Same for GOBI
mse-ai baseline APU            # Fit logistic baseline model on APU
```

## Capabilities

| Command | What it does |
|---------|-------------|
| `signal` | Runs 5 detectors (volume anomaly, price anomaly, momentum, accumulation/distribution, turnover liquidity) on real trade history |
| `baseline` | Fits a logistic binary baseline model on real training matrix from mse-cli |

## Architecture

`mse-ai` is a downstream consumer of [`mse-cli`](https://pypi.org/project/mse-cli/). It imports canonical ML substrate:

- `fit_baseline_model` — deterministic model fitting
- `build_signal_backtest_payload` — signal evaluation
- `detect_*` — 5 signal detectors
- `build_walk_forward_split_plan` — walk-forward cross-validation
- `MSEClient` — real market data (no demo data)

## Development

```bash
pip install -e ".[dev]"
pytest -q
```
