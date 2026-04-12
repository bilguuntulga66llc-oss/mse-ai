# mse-ai

Deterministic ML consumer built **on top of** the `mse-cli` foundation substrate.

## Architectural boundary

- `mse-ai` is a **downstream consumer** of `mse-cli`.
- `mse-ai` does **not** redefine foundation contracts.
- `mse-ai` imports canonical substrate from `mse_cli.core.*`:
  - `feature_store`, `feature_catalog`, `feature_rows`
  - `label_catalog`, `forward_return_labels`
  - `training_dataset_manifest`, `event_dataset_manifest`
  - `walk_forward_splits` (purge/embargo split policy)
  - `model_registry`, `model_baselines`
  - `evaluation_report`, `benchmark_evaluation`
- `mse-ai` produces models, predictions, and evaluation reports.
- `mse-ai` is **deterministic, credential-free, point-in-time safe** (inherits from `mse-cli` substrate).

## Install

```bash
pip install -e .
```

## Smoke test

```bash
pytest -q
```

## Run baseline

```bash
mse-ai baseline --help
```

## Boundary invariant

If you find yourself editing `mse_cli.core.*`, stop — that work belongs in the `mse-cli` repo, not here.
