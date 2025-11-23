"""
Tests for model training and prediction.
"""

import numpy as np
import pandas as pd
import pytest
from sklearn.datasets import make_regression

from src.models.train_model import train_production_model, evaluate_model
from src.models.predict_model import predict_production


@pytest.fixture
def sample_regression_data():
    """Create sample regression data."""
    X, y = make_regression(n_samples=100, n_features=5, noise=0.1, random_state=42)
    X_df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(5)])
    y_series = pd.Series(y, name="target")
    return X_df, y_series


def test_train_production_model(sample_regression_data):
    """Test model training."""
    X, y = sample_regression_data

    model, metrics = train_production_model(
        X, y, model_type="random_forest", test_size=0.2, random_state=42
    )

    # Check that model was trained
    assert model is not None
    assert hasattr(model, "predict")

    # Check metrics
    assert "mae" in metrics
    assert "mse" in metrics
    assert "rmse" in metrics
    assert "r2" in metrics

    # Check metric values are reasonable
    assert metrics["r2"] > 0.5  # Should have decent R²
    assert metrics["mae"] >= 0
    assert metrics["mse"] >= 0


def test_evaluate_model(sample_regression_data):
    """Test model evaluation."""
    X, y = sample_regression_data

    model, _ = train_production_model(X, y, model_type="random_forest", test_size=0.2)

    # Evaluate on full data
    metrics = evaluate_model(model, X, y)

    assert all(key in metrics for key in ["mae", "mse", "rmse", "r2"])
    assert all(isinstance(val, float) for val in metrics.values())


def test_predict_production(sample_regression_data):
    """Test making predictions."""
    X, y = sample_regression_data

    model, _ = train_production_model(X, y, model_type="random_forest", test_size=0.2)

    predictions = predict_production(model, X)

    assert len(predictions) == len(X)
    assert isinstance(predictions, pd.Series)
    assert predictions.name == "predictions"
