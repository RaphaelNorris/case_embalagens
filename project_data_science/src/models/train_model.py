"""
Model training and evaluation functions.
"""

from pathlib import Path
from typing import Any, Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from ..config import get_config
from ..logger import get_logger

logger = get_logger(__name__)


def train_production_model(
    X: pd.DataFrame,
    y: pd.Series,
    model_type: str = "random_forest",
    test_size: float = 0.2,
    random_state: int = 42,
    **model_params,
) -> Tuple[Any, Dict[str, float]]:
    """
    Train a production optimization model.

    Args:
        X: Feature matrix
        y: Target variable
        model_type: Type of model to train ('random_forest', 'xgboost', 'lightgbm')
        test_size: Proportion of data for testing
        random_state: Random seed
        **model_params: Additional parameters for the model

    Returns:
        Tuple of (trained_model, metrics_dict)
    """
    logger.info(f"Training {model_type} model with {len(X)} samples")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

    # Initialize model
    if model_type == "random_forest":
        model = RandomForestRegressor(
            n_estimators=model_params.get("n_estimators", 100),
            max_depth=model_params.get("max_depth", 10),
            random_state=random_state,
            n_jobs=-1,
        )
    elif model_type == "xgboost":
        from xgboost import XGBRegressor

        model = XGBRegressor(
            n_estimators=model_params.get("n_estimators", 100),
            max_depth=model_params.get("max_depth", 6),
            learning_rate=model_params.get("learning_rate", 0.1),
            random_state=random_state,
        )
    elif model_type == "lightgbm":
        from lightgbm import LGBMRegressor

        model = LGBMRegressor(
            n_estimators=model_params.get("n_estimators", 100),
            max_depth=model_params.get("max_depth", -1),
            learning_rate=model_params.get("learning_rate", 0.1),
            random_state=random_state,
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")

    # Train model
    logger.info("Training model...")
    model.fit(X_train, y_train)

    # Evaluate
    metrics = evaluate_model(model, X_test, y_test)

    logger.info(f"Model trained. R²: {metrics['r2']:.4f}, MAE: {metrics['mae']:.4f}")

    return model, metrics


def evaluate_model(model: Any, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
    """
    Evaluate a trained model.

    Args:
        model: Trained model
        X_test: Test features
        y_test: Test target

    Returns:
        Dictionary of evaluation metrics
    """
    y_pred = model.predict(X_test)

    metrics = {
        "mae": mean_absolute_error(y_test, y_pred),
        "mse": mean_squared_error(y_test, y_pred),
        "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
        "r2": r2_score(y_test, y_pred),
    }

    return metrics


def save_model(model: Any, model_name: str, metadata: Dict = None) -> Path:
    """
    Save a trained model to disk.

    Args:
        model: Trained model to save
        model_name: Name for the saved model
        metadata: Optional metadata dictionary

    Returns:
        Path to saved model
    """
    config = get_config()
    model_dir = config.ml.model_registry_path
    model_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / f"{model_name}.joblib"
    metadata_path = model_dir / f"{model_name}_metadata.joblib"

    # Save model
    joblib.dump(model, model_path)
    logger.info(f"Model saved to {model_path}")

    # Save metadata if provided
    if metadata:
        joblib.dump(metadata, metadata_path)
        logger.info(f"Metadata saved to {metadata_path}")

    return model_path


def load_model(model_name: str) -> Tuple[Any, Dict]:
    """
    Load a trained model from disk.

    Args:
        model_name: Name of the model to load

    Returns:
        Tuple of (model, metadata)
    """
    config = get_config()
    model_dir = config.ml.model_registry_path

    model_path = model_dir / f"{model_name}.joblib"
    metadata_path = model_dir / f"{model_name}_metadata.joblib"

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    model = joblib.load(model_path)
    logger.info(f"Model loaded from {model_path}")

    # Load metadata if exists
    metadata = {}
    if metadata_path.exists():
        metadata = joblib.load(metadata_path)
        logger.info(f"Metadata loaded from {metadata_path}")

    return model, metadata
