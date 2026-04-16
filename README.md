# mse-ai

Deterministic ML and signal research for the Mongolian Stock Exchange — built on `mse-cli`.

All outputs are **deterministic, credential-free, and point-in-time safe**.

## Install

```bash
pip install mse-ai
```

Requires `mse-cli>=2.0.0`; earlier `mse-cli` releases do not expose the foundation SDK surfaces used by this product.

## Commands

```bash
mse-ai signal APU              # 5-detector signal backtest on APU
mse-ai signal GOBI             # Same for GOBI
mse-ai baseline APU            # Fit logistic baseline model on APU
```

## Capabilities

| Command | What it does |
|---------|-------------|
| `signal` | Calls `MSEClient.research_signal_backtest(...)` for canonical `signal_backtest.v1` |
| `baseline` | Calls `MSEClient.research_baseline_model_fit(...)` for canonical `baseline_model_fit.v1` |
| `strategy` | Calls `MSEClient.research_strategy_baseline(...)` for one strategy baseline |
| `compare` | Calls `MSEClient.research_strategy_comparison(...)` for canonical strategy ranking |

## Architecture

`mse-ai` is a downstream product built on [`mse-cli`](https://pypi.org/project/mse-cli/). It has one substrate boundary:

- Product code imports only `MSEClient` from `mse_cli.sdk`.
- Core detectors, model fitting, strategy ranking, schemas, and market-data adapters stay in `mse-cli`.
- This repo owns product CLI composition only; it must not re-own `mse_cli.core.*` primitives.

## Development

```bash
pip install -e ".[dev]"
pytest -q
```
