"""Smoke test: mse-ai consumes mse-cli substrate cleanly."""

from __future__ import annotations

from mse_ai.baseline_demo import build_demo_training_matrix, run_demo_baseline
from mse_ai.substrate import (
    build_feature_catalog_surface,
    build_walk_forward_split_plan,
    fit_baseline_model,
)


def test_substrate_imports_resolve():
    assert callable(fit_baseline_model)
    assert callable(build_feature_catalog_surface)
    assert callable(build_walk_forward_split_plan)


def test_demo_training_matrix_is_canonical_shape():
    matrix = build_demo_training_matrix()
    assert matrix["schema_version"] == "training_matrix.v1"
    assert matrix["surface_id"] == "model.training_matrix"
    assert matrix["target_field"] == "fwd_return_5d"
    assert len(matrix["rows"]) == 8
    assert len(matrix["feature_columns"]) == 2


def test_demo_baseline_emits_canonical_fit_contract():
    fit = run_demo_baseline()
    assert fit["schema_version"] == "baseline_model_fit.v1"
    assert fit["surface_id"] == "model.baseline_fit"
    assert fit["model_kind"] == "logistic_binary"
    assert "model_params" in fit
    assert "evaluation" in fit
    assert "lineage" in fit
