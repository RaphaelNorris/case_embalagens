"""
Clustering utilities
====================

This module encapsulates the clustering workflow applied to the product
features.  The primary clustering algorithm used in the original notebook is
a Gaussian Mixture Model (GMM).  The functions here prepare the data for
clustering (encoding, scaling and dimensionality reduction), test multiple
numbers of clusters and fit the final GMM.  They return not only the
cluster labels but also the probabilities of belonging to each cluster,
which can be used downstream as additional features for classification.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Iterable

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler


@dataclass
class ClusteringArtifacts:
    """Container for artefacts produced during clustering.

    Attributes
    ----------
    X_pca : np.ndarray
        Data matrix after encoding, scaling and PCA.
    df_encoded : pd.DataFrame
        One‑hot encoded DataFrame corresponding to the original features.
    scaler : StandardScaler
        Fitted standard scaler for normalising numeric features.
    pca : PCA
        Fitted PCA reducer used for dimensionality reduction.
    gmm : Optional[GaussianMixture]
        Fitted GMM model.  Populated only after calling ``train_gmm``.
    labels : Optional[np.ndarray]
        Integer cluster labels for each sample.  Populated only after training.
    probabilities : Optional[np.ndarray]
        Cluster membership probabilities.  Populated only after training.
    """
    X_pca: np.ndarray
    df_encoded: pd.DataFrame
    scaler: StandardScaler
    pca: PCA
    gmm: Optional[GaussianMixture] = None
    labels: Optional[np.ndarray] = None
    probabilities: Optional[np.ndarray] = None


def prepare_dataset_for_clustering(
    df: pd.DataFrame,
    exclude_cols: List[str] | None = None,
    fill_numeric: bool = True,
    drop_na: bool = False,
    scaler: Optional[StandardScaler] = None,
    pca: Optional[PCA] = None,
    variance_ratio: float = 0.95,
) -> ClusteringArtifacts:
    """Prepare a DataFrame for clustering by encoding, scaling and reducing dimensions.

    The function performs the following steps:

    1. Drop columns specified in ``exclude_cols``.
    2. Identify numeric and categorical features.
    3. Optionally fill missing numeric values with the median of each column.
    4. One‑hot encode categorical features (drop_first=True to reduce
       redundancy).
    5. Fit or apply a ``StandardScaler`` to numeric columns.
    6. Fit or apply a ``PCA`` transformer to retain the specified fraction
       of explained variance.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing engineered features.
    exclude_cols : list of str, optional
        Columns to drop prior to encoding and scaling.  Use this to remove
        identifiers, target variables or columns you know should not be used
        for clustering.  Defaults to ``None``.
    fill_numeric : bool, optional
        Whether to fill missing values in numeric features with the median of
        the respective column.  Defaults to ``True``.
    drop_na : bool, optional
        If ``True``, drop rows with any missing value after encoding.  If
        ``False``, leave missing values as NaN (some algorithms handle this).
        Defaults to ``False``.
    scaler : StandardScaler, optional
        Pre‑fitted scaler to apply.  If ``None`` a new scaler will be
        instantiated and fitted on the numeric features.
    pca : PCA, optional
        Pre‑fitted PCA transformer.  If ``None`` a new PCA will be fitted
        using the specified ``variance_ratio``.
    variance_ratio : float, optional
        Fraction of variance to retain when fitting PCA.  Defaults to 0.95
        (i.e. retain 95% of variance).

    Returns
    -------
    ClusteringArtifacts
        A data class holding the processed matrix, encoded DataFrame, scaler
        and PCA objects.  Cluster labels and probabilities will be ``None``
        until a GMM is trained via ``train_gmm``.
    """
    # Drop specified columns
    if exclude_cols:
        df_proc = df.drop(columns=[c for c in exclude_cols if c in df.columns]).copy()
    else:
        df_proc = df.copy()

    # Identify numeric and categorical columns
    numeric_cols = df_proc.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df_proc.select_dtypes(include=["object", "category", "string"]).columns.tolist()

    # Fill missing numeric values
    if fill_numeric and numeric_cols:
        for col in numeric_cols:
            if df_proc[col].isnull().any():
                median = df_proc[col].median()
                df_proc[col] = df_proc[col].fillna(median)

    # One-hot encode categoricals
    if categorical_cols:
        df_encoded = pd.get_dummies(df_proc, columns=categorical_cols, drop_first=True)
    else:
        df_encoded = df_proc.copy()

    if drop_na:
        df_encoded = df_encoded.dropna()

    # Scale numeric features
    X_numeric = df_encoded.values.astype(float)
    if scaler is None:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_numeric)
    else:
        X_scaled = scaler.transform(X_numeric)

    # Apply PCA
    if pca is None:
        pca = PCA(n_components=variance_ratio, random_state=42)
        X_pca = pca.fit_transform(X_scaled)
    else:
        X_pca = pca.transform(X_scaled)

    return ClusteringArtifacts(
        X_pca=X_pca,
        df_encoded=df_encoded,
        scaler=scaler,
        pca=pca,
    )


def evaluate_gmm_models(
    X: np.ndarray,
    k_range: Iterable[int] = range(2, 11),
    random_state: int = 42,
    max_iter: int = 100,
    n_init: int = 3,
) -> List[Dict[str, float]]:
    """Test multiple GMM models and return their evaluation metrics.

    Parameters
    ----------
    X : np.ndarray
        Matrix of features after PCA (rows = samples, columns = components).
    k_range : iterable of int, optional
        Range of ``K`` values (number of mixture components) to test.  Defaults
        to ``range(2, 11)``, corresponding to cluster counts from 2 to 10.
    random_state : int, optional
        Random seed for GMM initialisation.  Defaults to 42.
    max_iter : int, optional
        Maximum number of EM iterations.  Defaults to 100.
    n_init : int, optional
        Number of initialisations to perform.  Defaults to 3.

    Returns
    -------
    list of dict
        Each dictionary contains the keys ``k``, ``bic``, ``aic`` and
        ``silhouette`` for the tested models.  You can select the best model
        according to your preferred criterion (e.g. lowest BIC).
    """
    results: List[Dict[str, float]] = []
    for k in k_range:
        gmm = GaussianMixture(
            n_components=k,
            covariance_type="full",
            random_state=random_state,
            n_init=n_init,
            max_iter=max_iter,
        )
        gmm.fit(X)
        labels = gmm.predict(X)
        bic = gmm.bic(X)
        aic = gmm.aic(X)
        sil = silhouette_score(X, labels)
        results.append({"k": k, "bic": bic, "aic": aic, "silhouette": sil})
    return results


def train_gmm(
    X: np.ndarray,
    n_components: int,
    random_state: int = 42,
    n_init: int = 10,
    max_iter: int = 100,
) -> Tuple[GaussianMixture, np.ndarray, np.ndarray]:
    """Fit a Gaussian Mixture Model to the provided data and compute labels and probabilities.

    Parameters
    ----------
    X : np.ndarray
        Matrix of features after PCA.
    n_components : int
        Number of mixture components to fit.
    random_state : int, optional
        Random seed for reproducibility.  Defaults to 42.
    n_init : int, optional
        Number of initialisations for the EM algorithm.  Defaults to 10.
    max_iter : int, optional
        Maximum number of EM iterations.  Defaults to 100.

    Returns
    -------
    tuple
        A tuple ``(gmm, labels, probabilities)`` where ``gmm`` is the fitted
        GMM instance, ``labels`` is a 1D integer array of cluster labels and
        ``probabilities`` is a 2D array of membership probabilities (rows =
        samples, columns = components).
    """
    gmm = GaussianMixture(
        n_components=n_components,
        covariance_type="full",
        random_state=random_state,
        n_init=n_init,
        max_iter=max_iter,
    )
    gmm.fit(X)
    labels = gmm.predict(X)
    probs = gmm.predict_proba(X)
    return gmm, labels, probs


__all__ = [
    "ClusteringArtifacts",
    "prepare_dataset_for_clustering",
    "evaluate_gmm_models",
    "train_gmm",
]
