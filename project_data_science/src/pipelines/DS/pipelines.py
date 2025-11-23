"""
High level pipelines
====================

This module defines high level functions that orchestrate the entire
workflow for a given machine type.  They tie together data loading,
feature engineering, clustering, modelling and explainability into a single
callable.  The functions return dictionaries containing the fitted models
and data frames, enabling users to inspect the intermediate results or
persist them to disk.

Two convenience wrappers are provided for the flexo and corte/vinco
machines.  Both call the generic ``run_pipeline`` function with the
appropriate machine type.  You can customise the behaviour of the pipeline
via keyword arguments, such as the cluster range, number of clusters,
feature exclusions and productivity threshold.
"""

from pathlib import Path
from typing import List, Dict, Optional, Iterable, Any

import numpy as np
import pandas as pd

if __package__ in (None, ""):
    # Support running the module directly (e.g. inside notebooks) by ensuring
    # the project ``src`` directory is on ``sys.path`` before importing using
    # absolute package names.
    import sys

    SRC_DIR = Path(__file__).resolve().parents[2]
    if str(SRC_DIR) not in sys.path:
        sys.path.append(str(SRC_DIR))

from pipelines.DS import clustering
from pipelines.DS import config
from pipelines.DS import data_processing
from pipelines.DS import explainability
from pipelines.DS import feature_engineering
from pipelines.DS import modeling

from sklearn.model_selection import train_test_split


def run_pipeline(
    machine_type: str,
    raw_dir: Path | None = None,
    ml_dir: Path | None = None,
    pedidos_df: Optional[pd.DataFrame] = None,
    pedidos_cutoff: str = "2024-01-01",
    cluster_k: Optional[int] = None,
    cluster_range: Iterable[int] = range(2, 11),
    exclude_features: Optional[List[str]] = None,
    productivity_quantile: float = 0.6,
    classification_threshold: float = 0.7,
    feature_selection_method: Optional[str] = None,
    feature_selection_params: Optional[Dict[str, Any]] = None,
    model_type: str = "hist_gradient_boosting",
    task_type: str = "classification",
    shap_sample_size: int = 100,
    random_state: int = 42,
    save_model: bool = False,
    model_dir: Optional[Path] = None,
    model_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Run the complete clustering and modelling pipeline for a given machine type.

    Parameters
    ----------
    machine_type : str
        Either ``"flexo"`` or ``"cv"``.  Determines which aggregated
        production table to load.
    raw_dir : Path, optional
        Directory containing raw parquet files.  Defaults to
        ``ml_pipeline.config.RAW_DIR``.
    ml_dir : Path, optional
        Directory containing machine learning tables.  Defaults to
        ``ml_pipeline.config.ML_DIR``.
    pedidos_df : pd.DataFrame, optional
        Pre‑processed orders DataFrame.  If ``None`` the raw orders table
        will be loaded and processed via ``data_processing.process_pedidos``.
    pedidos_cutoff : str, optional
        Date cutoff (inclusive) for orders used in ``process_pedidos``.
    cluster_k : int, optional
        Number of GMM components to fit.  If ``None`` the function will
        evaluate the models in ``cluster_range`` and choose the one with the
        lowest BIC.
    cluster_range : iterable of int, optional
        Range of candidate cluster counts to evaluate when ``cluster_k`` is
        ``None``.  Defaults to 2–10.
    exclude_features : list of str, optional
        Columns to remove from the feature set prior to clustering.  If
        ``None`` a sensible default list derived from the original
        notebook is used.
    productivity_quantile : float, optional
        Quantile threshold for labelling operations as productive.  See
        ``modeling.compute_productivity_target``.  Defaults to 0.6.
    classification_threshold : float, optional
        Probability threshold used when converting predicted probabilities
        into a binary class.  Defaults to 0.7.
    model_type : str, optional
        Estimator identifier passed to the training utilities. Defaults to
        ``"hist_gradient_boosting"``.
    task_type : str, optional
        ``"classification"`` for productivity modelling or ``"regression"``
        to predict quantity produced por m³. Defaults to ``"classification"``.
    shap_sample_size : int, optional
        Number of samples to use when computing SHAP values.  A subset of
        ``X_test`` will be drawn.  Defaults to 100.
    random_state : int, optional
        Random seed used in clustering and modelling.  Defaults to 42.
    save_model : bool, optional
        If ``True``, save all model artifacts to disk.  Defaults to ``False``.
    model_dir : Path, optional
        Directory where models should be saved.  If ``None`` and
        ``save_model`` is ``True``, uses ``src/model`` directory.  Defaults to ``None``.
    model_name : str, optional
        Optional custom name for the saved model.  If ``None`` a timestamp-based
        name will be generated.  Defaults to ``None``.

    Returns
    -------
    dict
        A dictionary containing the key intermediate objects: ``df``,
        ``clustering_artifacts``, ``gmm``, ``classifier``, ``metrics``,
        ``feature_importance``, ``shap_values``, ``top_features``,
        ``cluster_k``, ``model_type`` and (if feature selection was performed) ``selected_features``.
        If ``save_model`` is ``True``, also includes ``model_save_path``.
    """
    raw_dir = raw_dir or config.RAW_DIR
    ml_dir = ml_dir or config.ML_DIR
    task_type = task_type.lower()
    if task_type not in {"classification", "regression"}:
        raise ValueError("task_type must be either 'classification' or 'regression'.")

    # 1. Load aggregated production table for the specified machine type
    df_ml = data_processing.load_final_table(machine_type, ml_dir=ml_dir)

    # 2. Load and process the orders (pedidos) table
    if pedidos_df is None:
        pedidos_df = data_processing.process_pedidos(raw_file=raw_dir / config.TB_PEDIDOS, delivery_date_cutoff=pedidos_cutoff)
    else:
        # Ensure we don't modify user supplied DataFrame
        pedidos_df = pedidos_df.copy()

    # 3. Load facas table to get VL_COMPLAMINA
    df_facas = data_processing.load_raw_table(config.TB_FACAS, raw_dir=raw_dir)
    facas_cols = [c for c in ["CD_FACA", "VL_COMPLAMINA"] if c in df_facas.columns]
    df_facas = df_facas[facas_cols] if facas_cols else pd.DataFrame()

    # 4. Merge tables: aggregated ml table → pedidos → facas
    df = df_ml.merge(pedidos_df, on=["CD_OP"], how="inner")
    if not df_facas.empty:
        df = df.merge(df_facas, on="CD_FACA", how="left")

    # Drop TX_TIPO_MAQUINA column if present (it has no predictive value beyond specifying machine type)
    df = df.drop(columns=[c for c in ["TX_TIPO_MAQUINA"] if c in df.columns])

    # 5. Feature engineering: geometric features derived from dimensions
    df = feature_engineering.create_geometric_features(df)

    # 6. Determine columns to exclude if not provided
    if exclude_features is None:
        # Exclude identifiers and known targets/operational metrics
        exclude_features = [
            # Identifiers
            "CD_OP", "CD_ITEM", "CD_PEDIDO", "CD_FACA",
            # Target variables (dependent)
            "QT_PRODUZIDA", "QT_CHAPASALIMENTADAS", "VL_DURACAO_PRODUCAO", "QT_PROGRAMADA",
            "VL_DURACAO_PARADAS", "QT_PARADAS",
            # Derived target for classification
            "PROD_HORA", "y_produtivo", "y_quantidade_por_m3", "y_volume_por_hora",
            # High cardinality categoricals (exclude from clustering, analyze separately)
            "CAT_COMPOSICAO", "TX_TIPOABNT",
        ]
        # Remove duplicates but keep order
        exclude_features = list(dict.fromkeys([c for c in exclude_features if c in df.columns]))

    # 7. Prepare data for clustering
    clustering_artifacts = clustering.prepare_dataset_for_clustering(
        df,
        exclude_cols=exclude_features,
        fill_numeric=True,
        drop_na=False,
    )

    # 8. Choose number of clusters if not provided
    if cluster_k is None:
        results = clustering.evaluate_gmm_models(
            clustering_artifacts.X_pca,
            k_range=cluster_range,
            random_state=random_state,
        )
        # Select the model with the lowest BIC
        best = min(results, key=lambda d: d["bic"])
        cluster_k = best["k"]

    # 9. Train final GMM
    gmm, labels, probs = clustering.train_gmm(
        clustering_artifacts.X_pca,
        n_components=cluster_k,
        random_state=random_state,
    )
    clustering_artifacts.gmm = gmm
    clustering_artifacts.labels = labels
    clustering_artifacts.probabilities = probs

    # Append cluster labels to the DataFrame (not probabilities yet)
    df_clusters = df.copy().reset_index(drop=True)
    df_clusters["CLUSTER_ID"] = labels

    # 10. Compute target variable according to the requested task type
    if task_type == "classification":
        target_column = "y_produtivo"
        df_clusters[target_column] = modeling.compute_productivity_target(
            df_clusters,
            produced_col="QT_PRODUZIDA",
            duration_col="VL_DURACAO_PRODUCAO",
            quantile=productivity_quantile,
        )
    else:
        target_column = "y_volume_por_hora"
        df_clusters[target_column] = modeling.compute_volume_per_hour_target(
            df_clusters,
            produced_col="QT_PRODUZIDA",
            duration_col="VL_DURACAO_PRODUCAO",
        )

    # 11. Build feature matrix and target
    # First, select non-target features (excluding cluster-related columns we'll add separately)
    feature_cols = [
        c for c in df_clusters.columns
        if c not in exclude_features and c not in ["CLUSTER_ID", target_column]
    ]

    # Create feature matrix from selected columns
    X = df_clusters[feature_cols].copy()

    # Add cluster probabilities as features
    prob_cols = [f"PROB_CLUSTER_{i}" for i in range(cluster_k)]
    for i in range(cluster_k):
        X[f"PROB_CLUSTER_{i}"] = probs[:, i]

    # Add back categorical features from original df (before clustering exclusion)
    # These were excluded from clustering but should be included in the model
    categorical_features_to_add = ["CAT_COMPOSICAO", "TX_TIPOABNT"]

    # Determine if we need to one-hot encode categorical features
    # CatBoost and LightGBM can handle categorical strings natively
    # But tree-based feature selection uses Random Forest which cannot
    needs_encoding = (
        model_type.lower() not in ["catboost", "lightgbm"] or
        (feature_selection_method and feature_selection_method.lower() == "tree")
    )

    for cat_col in categorical_features_to_add:
        if cat_col in df.columns and cat_col not in X.columns:
            if needs_encoding:
                # One-hot encode for models/methods that don't handle strings
                dummies = pd.get_dummies(df[cat_col], prefix=cat_col, drop_first=True)
                for dummy_col in dummies.columns:
                    X[dummy_col] = dummies[dummy_col].values
            else:
                # Keep as string for CatBoost/LightGBM (when not using tree feature selection)
                X[cat_col] = df[cat_col].values

    y = df_clusters[target_column]

    # Also add probabilities to df_clusters for later use
    for i in range(cluster_k):
        df_clusters[f"PROB_CLUSTER_{i}"] = probs[:, i]

    # 12. Optional feature selection
    # IMPORTANT: Remove NaN from target before feature selection
    # Some feature selection methods (like tree-based) don't accept NaN in y
    mask_valid = y.notna()
    X_for_selection = X.loc[mask_valid]
    y_for_selection = y.loc[mask_valid]

    selection_method = feature_selection_method.lower() if feature_selection_method else None
    if selection_method and task_type == "regression" and selection_method != "correlation":
        raise ValueError("Only 'correlation' feature selection is supported for regression tasks.")

    selected_features: Optional[List[str]] = None
    if selection_method:
        from pipelines.DS.feature_selection import select_features  # local import to avoid circular
        y_selection = y_for_selection.astype(int) if task_type == "classification" else y_for_selection
        X_selected, selected_features = select_features(
            X_for_selection, y_selection,
            method=selection_method,
            **(feature_selection_params or {})
        )
        # Apply selection to full X (including rows with NaN in y)
        X_train_final = X[selected_features]
    else:
        X_train_final = X
        selected_features = X_train_final.columns.tolist()

    # 13. Train classifier using user chosen model
    if task_type == "classification":
        from pipelines.DS.training import train_model

        estimator, metrics = train_model(
            X=X_train_final,
            y=y,
            model_type=model_type,
            test_size=0.2,
            random_state=random_state,
            threshold=classification_threshold,
        )
        model_key = "classifier"
    else:
        from pipelines.DS.training import train_regressor

        estimator, metrics = train_regressor(
            X=X_train_final,
            y=y,
            model_type=model_type,
            test_size=0.2,
            random_state=random_state,
        )
        model_key = "regressor"

    # 14. Compute permutation importance on the held‑out set
    # Reproduce the train/test split used inside train_model
    mask_valid = y.notna()
    X_valid = X_train_final.loc[mask_valid]
    y_valid = y.loc[mask_valid]
    split_kwargs: Dict[str, Any] = {
        "test_size": 0.2,
        "random_state": random_state,
    }
    if task_type == "classification":
        y_split = y_valid.astype(int)
        split_kwargs["stratify"] = y_split
        perm_scoring = "roc_auc"
    else:
        y_split = pd.to_numeric(y_valid, errors="coerce")
        perm_scoring = "neg_mean_absolute_error"
    _, X_test, _, y_test = train_test_split(
        X_valid,
        y_split,
        **split_kwargs,
    )
    feature_importance = modeling.compute_permutation_importance(
        estimator, X_test, y_test, n_repeats=10, random_state=random_state, scoring=perm_scoring
    )

    # 15. SHAP explainability on a random subset of the test set (if SHAP is installed)
    if shap_sample_size > 0 and X_test.shape[0] > 0 and task_type == "classification":
        try:
            sample_size = min(shap_sample_size, X_test.shape[0])
            idx = np.random.RandomState(random_state).choice(X_test.index, size=sample_size, replace=False)
            X_bg = X_valid.sample(n=min(100, len(X_valid)), random_state=random_state)
            shap_values = explainability.compute_shap_values(estimator, X_bg, X_test.loc[idx])
            top_features = explainability.top_k_features_per_sample(
                X_test.loc[idx],
                shap_values,
                predict_proba_fn=estimator.predict_proba,
                k=5,
                id_col=None,
            )
        except RuntimeError:
            shap_values = None
            top_features = pd.DataFrame()
    else:
        shap_values = None
        top_features = pd.DataFrame()

    # Build results dictionary
    results: Dict[str, Any] = {
        "df": df_clusters,
        "clustering_artifacts": clustering_artifacts,
        "gmm": gmm,
        "metrics": metrics,
        "feature_importance": feature_importance,
        "shap_values": shap_values,
        "top_features": top_features,
        "cluster_k": cluster_k,
        "selected_features": selected_features,
        "exclude_features": exclude_features,
        "model_type": model_type,
        "task_type": task_type,
        "target_column": target_column,
        "estimator": estimator,
    }
    results[model_key] = estimator

    # 16. Save model artifacts if requested
    if save_model:
        if model_dir is None:
            # Default to src/model directory
            model_dir = Path(__file__).resolve().parents[2] / "model"

        from model import save_model_artifacts

        save_path = save_model_artifacts(
            results,
            save_dir=model_dir,
            machine_type=machine_type,
            model_name=model_name,
        )
        results["model_save_path"] = save_path

    # Return all relevant artefacts
    return results


def run_flexo_pipeline(**kwargs) -> Dict[str, Any]:
    """Convenience wrapper to run the pipeline for Flexo machines."""
    return run_pipeline(machine_type="flexo", **kwargs)


def run_corte_pipeline(**kwargs) -> Dict[str, Any]:
    """Convenience wrapper to run the pipeline for Corte/Vinco machines."""
    return run_pipeline(machine_type="cv", **kwargs)


__all__ = [
    "run_pipeline",
    "run_flexo_pipeline",
    "run_corte_pipeline",
]
