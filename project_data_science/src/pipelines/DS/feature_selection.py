"""
Feature selection utilities
==========================

This module defines general purpose feature selection helpers.  Feature
selection can reduce the dimensionality of your dataset, improve
interpretability and mitigate overfitting.  Three selection strategies are
implemented:

* Correlation filter: removes features that are highly correlated with others
  above a specified threshold (wrapper around ``drop_correlated_features`` in
  ``feature_engineering``).
* Univariate selection: ranks features using a univariate statistical test
  (e.g. ANOVA F score or mutual information) and retains the top ``k``.
* Tree‑based selection: trains a RandomForest (or similar) classifier and
  keeps features whose importance exceeds a threshold.

The entry point is ``select_features`` which dispatches to the appropriate
strategy based on the ``method`` argument.
"""
from __future__ import annotations

from typing import List, Tuple, Optional, Dict, Any

import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.ensemble import RandomForestClassifier

from .feature_engineering import drop_correlated_features


def select_features(
    X: pd.DataFrame,
    y: pd.Series,
    method: str,
    **kwargs: Any,
) -> Tuple[pd.DataFrame, List[str]]:
    """Select a subset of features according to a specified method.

    Parameters
    ----------
    X : pd.DataFrame
        Feature matrix.
    y : pd.Series
        Target variable (used for supervised methods).  Can be ignored for
        correlation filtering.
    method : str
        Selection strategy.  One of ``"correlation"``, ``"kbest"`` or
        ``"tree"``.
    **kwargs : dict
        Additional parameters passed to the specific selector.  See below
        for details.

    Returns
    -------
    tuple
        A tuple ``(X_selected, selected_columns)`` where ``X_selected`` is the
        reduced DataFrame containing only the selected columns and
        ``selected_columns`` is the list of retained column names.

    Notes
    -----
    * **Correlation filter**: specify ``threshold`` (float, default 0.95)
      to remove one of each pair of features whose absolute Pearson
      correlation exceeds ``threshold``.
    * **K‑best**: specify ``k`` (int, number of features to keep) and
      optionally ``score_func`` (str, either ``"f_classif"`` or
      ``"mutual_info"``).  Defaults to ``f_classif``.
    * **Tree‑based**: specify ``n_estimators`` (int, default 100) and
      ``importance_threshold`` (float, default 0.01).  Uses a RandomForest
      classifier to compute feature importances.
    """
    method = method.lower()
    if method == "correlation":
        threshold = float(kwargs.get("threshold", 0.95))
        X_filtered = drop_correlated_features(X, threshold=threshold)
        return X_filtered, X_filtered.columns.tolist()
    elif method == "kbest":
        k = int(kwargs.get("k", min(10, X.shape[1])))
        score_func_name = kwargs.get("score_func", "f_classif")
        if score_func_name == "f_classif":
            score_func = f_classif
        elif score_func_name == "mutual_info":
            score_func = mutual_info_classif
        else:
            raise ValueError(f"Unknown score_func '{score_func_name}'. Use 'f_classif' or 'mutual_info'.")
        selector = SelectKBest(score_func, k=k)
        selector.fit(X, y)
        mask = selector.get_support()
        selected_columns = X.columns[mask].tolist()
        X_selected = X[selected_columns]
        return X_selected, selected_columns
    elif method == "tree":
        n_estimators = int(kwargs.get("n_estimators", 100))
        importance_threshold = float(kwargs.get("importance_threshold", 0.01))
        rf = RandomForestClassifier(n_estimators=n_estimators, random_state=42, n_jobs=-1)
        rf.fit(X, y)
        importances = rf.feature_importances_
        selected_columns = [col for col, imp in zip(X.columns, importances) if imp >= importance_threshold]
        if not selected_columns:
            # Fallback: keep at least the top 5 features
            idx_sorted = np.argsort(importances)[::-1]
            selected_columns = [X.columns[i] for i in idx_sorted[: min(5, len(idx_sorted))]]
        X_selected = X[selected_columns]
        return X_selected, selected_columns
    else:
        raise ValueError(f"Unknown feature selection method '{method}'.")


__all__ = [
    "select_features",
]