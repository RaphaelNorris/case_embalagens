"""
Explainability utilities
=======================

This module provides functions for computing SHAP values for tree‑based
classifiers and extracting the most influential features per observation.
It mirrors the SHAP workflow used in the original notebooks but wraps the
logic into reusable functions with clear signatures.
"""
from __future__ import annotations

from typing import List, Tuple, Callable, Optional, Any

import numpy as np
import pandas as pd
try:
    import shap  # type: ignore
except ImportError:  # pragma: no cover
    # SHAP is an optional dependency.  If it is not installed the
    # functions below will raise a clear error when called.
    shap = None  # type: ignore


def compute_shap_values(
    model: Any,
    X_background: pd.DataFrame,
    X_explain: pd.DataFrame,
    nsamples: int | str | None = "auto",
) -> Any:
    """Compute SHAP values for a subset of the data.

    Parameters
    ----------
    model : any
        The fitted model with a ``predict_proba`` method.  SHAP will
        automatically select the appropriate explainer for tree‑based models.
    X_background : pd.DataFrame
        Background dataset used to estimate the expected value of the model.
        It is recommended to pass a subset of the training data.
    X_explain : pd.DataFrame
        Dataset for which SHAP values are computed.  SHAP values are
        returned in the same order as ``X_explain``.
    nsamples : int or str, optional
        Number of samples to draw when approximating the SHAP kernel explainer
        (ignored for tree explainers).  Defaults to ``"auto"``.

    Returns
    -------
    shap.Explanation
        An object containing the SHAP values with shape
        ``(n_samples, n_features)``.
    """
    if shap is None:
        raise RuntimeError(
            "SHAP is not installed.  Install it with 'pip install shap' to compute explanations."
        )
    explainer = shap.Explainer(model, X_background)
    shap_values = explainer(X_explain, nsamples=nsamples)
    return shap_values


def top_k_features_per_sample(
    X_explain: pd.DataFrame,
    shap_values: Any,
    predict_proba_fn: Callable[[pd.DataFrame], np.ndarray],
    k: int = 5,
    id_col: Optional[str] = None,
) -> pd.DataFrame:
    """Return the top‑``k`` most impactful features for each observation.

    Parameters
    ----------
    X_explain : pd.DataFrame
        Feature matrix for which SHAP values have been computed.
    shap_values : shap.Explanation
        SHAP values for each observation in ``X_explain``.
    predict_proba_fn : callable
        A function that accepts ``X_explain.iloc[[i]]`` and returns the
        probability of the positive class (``shape (1,)``).  Typically
        ``clf.predict_proba`` for a binary classifier.
    k : int, optional
        Number of top features to return per observation.  Defaults to 5.
    id_col : str, optional
        Name of a column in ``X_explain`` to use as an identifier.  If
        provided, its values are included in the result to help map
        explanations back to original entities.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ``id`` (if ``id_col`` provided),
        ``probability`` (predicted positive class probability),
        ``predicted_class`` (binary prediction) and ``top_features``
        (list of tuples ``(feature_name, shap_value)``) for each sample.
    """
    results: List[dict] = []
    shap_array = shap_values.values
    for i in range(X_explain.shape[0]):
        feature_impacts = pd.DataFrame({
            "feature": X_explain.columns,
            "shap_value": shap_array[i],
        })
        feature_impacts["impact_abs"] = feature_impacts["shap_value"].abs()
        topk = feature_impacts.sort_values("impact_abs", ascending=False).head(k)
        prob = float(predict_proba_fn(X_explain.iloc[[i]])[0, 1])
        pred = int(prob >= 0.5)
        row = {
            "probability": prob,
            "predicted_class": pred,
            "top_features": list(zip(topk["feature"], topk["shap_value"])),
        }
        if id_col and id_col in X_explain.columns:
            row["id"] = X_explain.iloc[i][id_col]
        results.append(row)
    return pd.DataFrame(results)


__all__ = [
    "compute_shap_values",
    "top_k_features_per_sample",
]