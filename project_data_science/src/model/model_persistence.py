"""
Model persistence utilities
============================
This module provides functions for saving and loading trained models and
associated artifacts (GMM, scaler, PCA, feature lists, etc.) to disk.
Models are saved using joblib for sklearn-compatible estimators and pickle
for general objects.
The save function creates a timestamped directory containing all pipeline
artifacts, enabling full reproducibility of predictions.
"""

import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import joblib
import pandas as pd


def save_model_artifacts(
    artifacts: Dict[str, Any],
    save_dir: Path,
    machine_type: str,
    model_name: Optional[str] = None,
) -> Path:
    """Save all model artifacts to disk.

    Parameters
    ----------
    artifacts : dict
        Dictionary containing all pipeline outputs from ``run_pipeline``.
        Expected keys: ``gmm``, ``classifier``, ``clustering_artifacts``,
        ``metrics``, ``feature_importance``, ``selected_features``,
        ``exclude_features``, ``cluster_k``, etc.
    save_dir : Path
        Base directory where models should be saved.
    machine_type : str
        Machine type (``"flexo"`` or ``"cv"``).
    model_name : str, optional
        Optional custom name for the model. If ``None`` a timestamp-based
        name will be generated.

    Returns
    -------
    Path
        Path to the created model directory.
    """
    # Create timestamp-based folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if model_name:
        folder_name = f"{machine_type}_{model_name}_{timestamp}"
    else:
        folder_name = f"{machine_type}_model_{timestamp}"

    model_dir = save_dir / folder_name
    model_dir.mkdir(parents=True, exist_ok=True)

    # Save GMM model
    if "gmm" in artifacts:
        joblib.dump(artifacts["gmm"], model_dir / "gmm.pkl")

    # Save classifier
    if "classifier" in artifacts:
        joblib.dump(artifacts["classifier"], model_dir / "classifier.pkl")
    if "regressor" in artifacts:
        joblib.dump(artifacts["regressor"], model_dir / "regressor.pkl")

    # Save clustering artifacts components individually (NOT the whole object)
    if "clustering_artifacts" in artifacts:
        clustering_artifacts = artifacts["clustering_artifacts"]

        # Save scaler
        if (
            hasattr(clustering_artifacts, "scaler")
            and clustering_artifacts.scaler is not None
        ):
            joblib.dump(clustering_artifacts.scaler, model_dir / "scaler.pkl")

        # Save PCA
        if (
            hasattr(clustering_artifacts, "pca")
            and clustering_artifacts.pca is not None
        ):
            joblib.dump(clustering_artifacts.pca, model_dir / "pca.pkl")

        # Save df_encoded columns if available
        if (
            hasattr(clustering_artifacts, "df_encoded")
            and clustering_artifacts.df_encoded is not None
        ):
            feature_cols = clustering_artifacts.df_encoded.columns.tolist()
            with open(model_dir / "feature_cols.json", "w") as f:
                json.dump(feature_cols, f, indent=2)

    # Save selected features
    if "selected_features" in artifacts and artifacts["selected_features"]:
        with open(model_dir / "selected_features.json", "w") as f:
            json.dump(artifacts["selected_features"], f, indent=2)

    # Save excluded features
    if "exclude_features" in artifacts and artifacts["exclude_features"]:
        with open(model_dir / "exclude_features.json", "w") as f:
            json.dump(artifacts["exclude_features"], f, indent=2)

    # Save metrics
    if "metrics" in artifacts:
        metrics = artifacts["metrics"].copy()
        # Convert classification report to serializable format
        if "classification_report" in metrics:
            # Already a dict, keep as is
            pass
        with open(model_dir / "metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)

    # Save feature importance
    if "feature_importance" in artifacts:
        importance_df = pd.DataFrame(
            {
                "feature": artifacts["feature_importance"].index,
                "importance": artifacts["feature_importance"].values,
            }
        )
        importance_df.to_csv(model_dir / "feature_importance.csv", index=False)

    # Save metadata
    metrics = artifacts.get("metrics", {})
    metadata = {
        "machine_type": machine_type,
        "timestamp": timestamp,
        "cluster_k": artifacts.get("cluster_k"),
        "model_type": artifacts.get("model_type", "unknown"),
        "task_type": artifacts.get("task_type", "classification"),
        "roc_auc": metrics.get("roc_auc"),
        "threshold": metrics.get("threshold"),
        "r2": metrics.get("r2"),
        "mae": metrics.get("mae"),
        "rmse": metrics.get("rmse"),
        "n_features": len(artifacts.get("selected_features", [])),
    }
    with open(model_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Save SHAP values if present
    if "shap_values" in artifacts and artifacts["shap_values"] is not None:
        with open(model_dir / "shap_values.pkl", "wb") as f:
            pickle.dump(artifacts["shap_values"], f)

    # Save top features per sample if present
    if "top_features" in artifacts and not artifacts["top_features"].empty:
        artifacts["top_features"].to_csv(model_dir / "top_features.csv", index=False)

    print(f"Model artifacts saved to: {model_dir}")

    # Create Streamlit-compatible pickle with ONLY the essential components
    streamlit_artifacts = {
        "gmm": artifacts.get("gmm"),
        "classifier": artifacts.get("classifier"),
        "regressor": artifacts.get("regressor"),
        "scaler": artifacts["clustering_artifacts"].scaler
        if "clustering_artifacts" in artifacts
        else None,
        "pca": artifacts["clustering_artifacts"].pca
        if "clustering_artifacts" in artifacts
        else None,
        "selected_features": artifacts.get("selected_features", []),
        "exclude_features": artifacts.get("exclude_features", []),
        "cluster_k": artifacts.get("cluster_k", 3),
        "metrics": artifacts.get("metrics", {}),
        "model_type": artifacts.get("model_type", "unknown"),
        "task_type": artifacts.get("task_type", "classification"),
    }

    # Add feature_cols if available
    if "clustering_artifacts" in artifacts:
        clustering_artifacts = artifacts["clustering_artifacts"]
        if (
            hasattr(clustering_artifacts, "df_encoded")
            and clustering_artifacts.df_encoded is not None
        ):
            streamlit_artifacts["feature_cols"] = (
                clustering_artifacts.df_encoded.columns.tolist()
            )

    # Add feature importance if available
    if "feature_importance" in artifacts:
        streamlit_artifacts["feature_importance"] = artifacts["feature_importance"]

    # Save streamlit-compatible version
    streamlit_path = save_dir / f"{machine_type}_model_artifacts.pkl"
    try:
        with open(streamlit_path, "wb") as f:
            pickle.dump(streamlit_artifacts, f)
        print(f"Streamlit-compatible model saved to: {streamlit_path}")
    except Exception as e:
        print(f"Warning: Could not save Streamlit-compatible model: {e}")
        # Try saving without problematic components
        minimal_artifacts = {
            "gmm": artifacts.get("gmm"),
            "classifier": artifacts.get("classifier"),
            "regressor": artifacts.get("regressor"),
            "selected_features": artifacts.get("selected_features", []),
            "cluster_k": artifacts.get("cluster_k", 3),
            "metrics": artifacts.get("metrics", {}),
            "task_type": artifacts.get("task_type", "classification"),
        }
        with open(streamlit_path, "wb") as f:
            pickle.dump(minimal_artifacts, f)
        print(f"Minimal Streamlit model saved to: {streamlit_path}")

    return model_dir


def load_model_artifacts(model_dir: Path) -> Dict[str, Any]:
    """Load all model artifacts from disk.

    Parameters
    ----------
    model_dir : Path
        Directory containing the saved model artifacts.

    Returns
    -------
    dict
        Dictionary containing loaded artifacts with keys: ``gmm``,
        ``classifier``, ``regressor``, ``scaler``, ``pca``, ``feature_cols``,
        ``selected_features``, ``exclude_features``, ``metrics``,
        ``feature_importance``, ``metadata``.
    """
    artifacts = {}

    # Load GMM
    gmm_path = model_dir / "gmm.pkl"
    if gmm_path.exists():
        artifacts["gmm"] = joblib.load(gmm_path)

    # Load classifier
    clf_path = model_dir / "classifier.pkl"
    if clf_path.exists():
        artifacts["classifier"] = joblib.load(clf_path)
    reg_path = model_dir / "regressor.pkl"
    if reg_path.exists():
        artifacts["regressor"] = joblib.load(reg_path)

    # Load scaler
    scaler_path = model_dir / "scaler.pkl"
    if scaler_path.exists():
        artifacts["scaler"] = joblib.load(scaler_path)

    # Load PCA
    pca_path = model_dir / "pca.pkl"
    if pca_path.exists():
        artifacts["pca"] = joblib.load(pca_path)

    # Load feature columns
    feature_cols_path = model_dir / "feature_cols.json"
    if feature_cols_path.exists():
        with open(feature_cols_path, "r") as f:
            artifacts["feature_cols"] = json.load(f)

    # Load selected features
    selected_path = model_dir / "selected_features.json"
    if selected_path.exists():
        with open(selected_path, "r") as f:
            artifacts["selected_features"] = json.load(f)

    # Load excluded features
    exclude_path = model_dir / "exclude_features.json"
    if exclude_path.exists():
        with open(exclude_path, "r") as f:
            artifacts["exclude_features"] = json.load(f)

    # Load metrics
    metrics_path = model_dir / "metrics.json"
    if metrics_path.exists():
        with open(metrics_path, "r") as f:
            artifacts["metrics"] = json.load(f)

    # Load feature importance
    importance_path = model_dir / "feature_importance.csv"
    if importance_path.exists():
        importance_df = pd.read_csv(importance_path)
        artifacts["feature_importance"] = pd.Series(
            importance_df["importance"].values,
            index=importance_df["feature"].values,
        )

    # Load metadata
    metadata_path = model_dir / "metadata.json"
    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            artifacts["metadata"] = json.load(f)

    # Load SHAP values if present
    shap_path = model_dir / "shap_values.pkl"
    if shap_path.exists():
        with open(shap_path, "rb") as f:
            artifacts["shap_values"] = pickle.load(f)

    # Load top features if present
    top_features_path = model_dir / "top_features.csv"
    if top_features_path.exists():
        artifacts["top_features"] = pd.read_csv(top_features_path)

    print(f"Model artifacts loaded from: {model_dir}")
    return artifacts


def create_dummy_model_artifacts(machine_type: str, save_dir: Path) -> Path:
    """Create dummy model artifacts for testing purposes.

    Parameters
    ----------
    machine_type : str
        Machine type ("flexo" or "cv")
    save_dir : Path
        Directory to save the dummy model

    Returns
    -------
    Path
        Path to the saved dummy model file
    """
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.mixture import GaussianMixture

    # Create dummy artifacts
    dummy_artifacts = {
        "classifier": RandomForestClassifier(n_estimators=10, random_state=42),
        "gmm": GaussianMixture(n_components=3, random_state=42),
        "scaler": StandardScaler(),
        "pca": PCA(n_components=5),
        "selected_features": [
            "VL_COMPRIMENTO",
            "VL_LARGURA",
            "VL_GRAMATURA",
            "QT_NRCORES",
            "QT_PEDIDA",
        ],
        "exclude_features": [],
        "feature_cols": [
            "VL_COMPRIMENTO",
            "VL_LARGURA",
            "VL_GRAMATURA",
            "QT_NRCORES",
            "QT_PEDIDA",
        ],
        "metrics": {
            "roc_auc": 0.85,
            "threshold": 0.5,
            "classification_report": {
                "weighted avg": {"precision": 0.82, "recall": 0.81, "f1-score": 0.81}
            },
        },
        "cluster_k": 3,
        "model_type": "RandomForest",
    }

    # Fit dummy models with sample data
    import numpy as np

    X_dummy = np.random.rand(100, 5)
    y_dummy = np.random.randint(0, 2, 100)

    dummy_artifacts["classifier"].fit(X_dummy, y_dummy)
    dummy_artifacts["scaler"].fit(X_dummy)
    dummy_artifacts["pca"].fit(X_dummy)
    dummy_artifacts["gmm"].fit(X_dummy)

    # Save dummy model
    save_dir.mkdir(parents=True, exist_ok=True)
    model_path = save_dir / f"{machine_type}_model_artifacts.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(dummy_artifacts, f)

    print(f"Dummy model created at: {model_path}")
    return model_path


__all__ = [
    "save_model_artifacts",
    "load_model_artifacts",
    "create_dummy_model_artifacts",
]
