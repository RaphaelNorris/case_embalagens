"""
Model training utilities
=======================

This module provides flexible interfaces for training both classification
and regression models on tabular data.  It detects the requested model
type by name and instantiates the appropriate estimator using sensible
default hyperparameters.  Supported models include RandomForest, ExtraTrees,
GradientBoosting, HistGradientBoosting and, if installed, CatBoost and
LightGBM counterparts.
"""

from typing import Tuple, Dict, Any, List

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score,
    classification_report,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
)

try:
    from lightgbm import LGBMClassifier  # type: ignore
except ImportError:
    LGBMClassifier = None  # type: ignore

try:
    from catboost import CatBoostClassifier  # type: ignore
except ImportError:
    CatBoostClassifier = None  # type: ignore

try:
    from lightgbm import LGBMRegressor  # type: ignore
except ImportError:
    LGBMRegressor = None  # type: ignore

try:
    from catboost import CatBoostRegressor  # type: ignore
except ImportError:
    CatBoostRegressor = None  # type: ignore


def identify_categorical_features(X: pd.DataFrame) -> List[str]:
    """
    Identify categorical features in the dataset.
    
    Parameters
    ----------
    X : pd.DataFrame
        Feature matrix
        
    Returns
    -------
    List[str]
        List of column names that are categorical
    """
    categorical_features = []
    
    for col in X.columns:
        # Check if column is object/string type
        if X[col].dtype == 'object':
            categorical_features.append(col)
        # Check if column has string values (even if dtype is not object)
        elif X[col].dtype != 'object':
            # Sample a few non-null values to check if they're strings
            sample_values = X[col].dropna().head(10)
            if len(sample_values) > 0:
                # Check if any value is a string
                if any(isinstance(val, str) for val in sample_values):
                    categorical_features.append(col)
    
    return categorical_features


def train_model(
    X: pd.DataFrame,
    y: pd.Series,
    model_type: str = "random_forest",
    test_size: float = 0.2,
    random_state: int = 42,
    threshold: float = 0.5,
    **model_params: Any,
) -> Tuple[Any, Dict[str, Any]]:
    """Train a classification model and return metrics.

    Parameters
    ----------
    X : pd.DataFrame
        Feature matrix.
    y : pd.Series
        Binary target variable.  NaNs are dropped.
    model_type : str, optional
        Name of the model to train.  Supported values:
        ``"random_forest"``, ``"extra_trees"``, ``"gradient_boosting"``,
        ``"hist_gradient_boosting"``, ``"lightgbm"``, ``"catboost"``.  Defaults
        to ``"random_forest"``.
    test_size : float, optional
        Fraction of samples to use as the test set.  Defaults to 0.2.
    random_state : int, optional
        Random seed for reproducibility.  Defaults to 42.
    threshold : float, optional
        Probability threshold used to convert probabilities into binary
        predictions.  Defaults to 0.5.
    **model_params : dict
        Additional keyword arguments passed to the model constructor.  Use
        this to tune hyperparameters.

    Returns
    -------
    tuple
        A tuple ``(model, metrics)`` where ``model`` is the fitted estimator
        and ``metrics`` contains ``roc_auc``, ``classification_report`` and
        ``threshold``.
    """
    # Drop NaN labels
    mask = y.notna()
    X_valid = X.loc[mask]
    y_valid = y.loc[mask].astype(int)
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_valid,
        y_valid,
        test_size=test_size,
        random_state=random_state,
        stratify=y_valid,
    )
    
    model_type = model_type.lower()
    
    # Identify categorical features for CatBoost
    cat_features = identify_categorical_features(X_train)
    
    # Instantiate model
    if model_type == "random_forest":
        model_cls = RandomForestClassifier
    elif model_type == "extra_trees":
        model_cls = ExtraTreesClassifier
    elif model_type == "gradient_boosting":
        model_cls = GradientBoostingClassifier
    elif model_type in {"hist_gradient_boosting", "histgb"}:
        model_cls = HistGradientBoostingClassifier
    elif model_type == "lightgbm":
        if LGBMClassifier is None:
            raise ImportError("LightGBM is not installed.  Please install lightgbm to use this model.")
        model_cls = LGBMClassifier
    elif model_type == "catboost":
        if CatBoostClassifier is None:
            raise ImportError("CatBoost is not installed.  Please install catboost to use this model.")
        model_cls = CatBoostClassifier
    else:
        raise ValueError(f"Unsupported model_type '{model_type}'.")

    # Default parameters for some models
    default_params = {}
    if model_type == "random_forest":
        default_params = {"n_estimators": 300, "max_depth": None, "n_jobs": -1, "random_state": random_state}
    elif model_type == "extra_trees":
        default_params = {"n_estimators": 300, "max_depth": None, "n_jobs": -1, "random_state": random_state}
    elif model_type == "gradient_boosting":
        default_params = {"n_estimators": 200, "learning_rate": 0.1, "random_state": random_state}
    elif model_type in {"hist_gradient_boosting", "histgb"}:
        default_params = {"max_depth": None, "learning_rate": 0.05, "random_state": random_state}
    elif model_type == "lightgbm":
        default_params = {"n_estimators": 300, "learning_rate": 0.05, "random_state": random_state, "n_jobs": -1}
    elif model_type == "catboost":
        default_params = {
            "iterations": 300, 
            "learning_rate": 0.05, 
            "depth": 6, 
            "verbose": False, 
            "random_seed": random_state
        }
        # Add categorical features if any exist
        if cat_features:
            default_params["cat_features"] = cat_features
    
    # Merge default and user provided params
    params = {**default_params, **model_params}
    model = model_cls(**params)
    
    # Fit
    model.fit(X_train, y_train)
    
    # Predict probabilities
    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= threshold).astype(int)
    
    # Compute metrics
    roc_auc = roc_auc_score(y_test, y_proba)
    report = classification_report(y_test, y_pred, output_dict=True)
    metrics = {
        "roc_auc": roc_auc,
        "classification_report": report,
        "threshold": threshold,
    }
    return model, metrics


def train_regressor(
    X: pd.DataFrame,
    y: pd.Series,
    model_type: str = "random_forest",
    test_size: float = 0.2,
    random_state: int = 42,
    **model_params: Any,
) -> Tuple[Any, Dict[str, float]]:
    """Train a regression model and compute standard regression metrics."""

    mask = y.notna()
    X_valid = X.loc[mask]
    y_valid = pd.to_numeric(y.loc[mask], errors="coerce")
    mask = y_valid.notna()
    X_valid = X_valid.loc[mask]
    y_valid = y_valid.loc[mask]

    X_train, X_test, y_train, y_test = train_test_split(
        X_valid,
        y_valid,
        test_size=test_size,
        random_state=random_state,
    )

    model_type = model_type.lower()
    
    # Identify categorical features for CatBoost
    cat_features = identify_categorical_features(X_train)
    
    if model_type == "random_forest":
        model_cls = RandomForestRegressor
    elif model_type == "extra_trees":
        model_cls = ExtraTreesRegressor
    elif model_type == "gradient_boosting":
        model_cls = GradientBoostingRegressor
    elif model_type in {"hist_gradient_boosting", "histgb"}:
        model_cls = HistGradientBoostingRegressor
    elif model_type == "lightgbm":
        if LGBMRegressor is None:
            raise ImportError("LightGBM is not installed. Please install lightgbm to use this model.")
        model_cls = LGBMRegressor
    elif model_type == "catboost":
        if CatBoostRegressor is None:
            raise ImportError("CatBoost is not installed. Please install catboost to use this model.")
        model_cls = CatBoostRegressor
    else:
        raise ValueError(f"Unsupported model_type '{model_type}'.")

    default_params: Dict[str, Any] = {}
    if model_type in {"random_forest", "extra_trees"}:
        default_params = {"n_estimators": 300, "max_depth": None, "n_jobs": -1, "random_state": random_state}
    elif model_type == "gradient_boosting":
        default_params = {"n_estimators": 200, "learning_rate": 0.1, "random_state": random_state}
    elif model_type in {"hist_gradient_boosting", "histgb"}:
        default_params = {"max_depth": None, "learning_rate": 0.05, "random_state": random_state}
    elif model_type == "lightgbm":
        default_params = {"n_estimators": 300, "learning_rate": 0.05, "random_state": random_state, "n_jobs": -1}
    elif model_type == "catboost":
        default_params = {
            "iterations": 300, 
            "learning_rate": 0.05, 
            "depth": 6, 
            "verbose": False, 
            "random_seed": random_state
        }
        # Add categorical features if any exist
        if cat_features:
            default_params["cat_features"] = cat_features

    params = {**default_params, **model_params}
    model = model_cls(**params)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    r2 = r2_score(y_test, y_pred)
    metrics = {
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
    }
    return model, metrics


__all__ = [
    "train_model",
    "train_regressor",
    "identify_categorical_features",
]