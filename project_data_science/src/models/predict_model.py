"""
Model prediction functions.
"""

from typing import Any

import pandas as pd

from ..logger import get_logger

logger = get_logger(__name__)


def predict_production(model: Any, X: pd.DataFrame) -> pd.Series:
    """
    Make predictions using a trained model.

    Args:
        model: Trained model
        X: Feature matrix

    Returns:
        Series of predictions
    """
    logger.info(f"Making predictions for {len(X)} samples")

    predictions = model.predict(X)

    return pd.Series(predictions, index=X.index, name="predictions")


def predict_with_confidence(model: Any, X: pd.DataFrame) -> pd.DataFrame:
    """
    Make predictions with confidence intervals (for models that support it).

    Args:
        model: Trained model (must have predict method and optionally estimators_)
        X: Feature matrix

    Returns:
        DataFrame with predictions and confidence bounds
    """
    predictions = predict_production(model, X)

    results = pd.DataFrame({"prediction": predictions}, index=X.index)

    # For ensemble models, calculate prediction intervals
    if hasattr(model, "estimators_"):
        all_predictions = np.array([tree.predict(X) for tree in model.estimators_])
        results["prediction_std"] = all_predictions.std(axis=0)
        results["prediction_lower"] = all_predictions.quantile(0.025, axis=0)
        results["prediction_upper"] = all_predictions.quantile(0.975, axis=0)

        logger.info("Calculated prediction intervals")

    return results
