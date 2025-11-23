"""
Modelling utilities
===================

This module defines functions for creating targets used in both classification
and regression tasks and provides helper routines for model diagnostics.  The
classification target measures productivity (pieces per hour) whereas the
regression target measures the amount produced per cubic metre.
"""

from typing import Tuple, Optional, Iterable, Any

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance


def compute_productivity_target(
    df: pd.DataFrame,
    produced_col: str = "QT_PRODUZIDA",
    duration_col: str = "VL_DURACAO_PRODUCAO",
    quantile: float = 0.6,
    min_duration: float = 1e-3,
) -> pd.Series:
    """Compute a binary productivity target based on production rate.

    The production rate is defined as the quantity produced divided by the
    duration of production in minutes.  Operations with production
    durations below ``min_duration`` minutes are excluded by returning NaN.
    A threshold is computed as the ``quantile`` of the production rate in
    the provided DataFrame; rates above or equal to this threshold are
    labelled as 1 (productive) and below the threshold as 0 (non‑productive).

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the production and duration columns.
    produced_col : str, optional
        Name of the column containing the number of pieces produced.  Defaults to ``QT_PRODUZIDA``.
    duration_col : str, optional
        Name of the column containing the production duration in minutes.  Defaults to ``VL_DURACAO_PRODUCAO``.
    quantile : float, optional
        Quantile used as the threshold between productive and non‑productive.  Defaults to 0.6 (60th percentile).
    min_duration : float, optional
        Minimum non‑zero duration (in minutes) required to compute a rate.
        Durations equal to zero or below this value will result in NaN for the
        target.  Defaults to 1e-3.

    Returns
    -------
    pd.Series
        Binary target series of the same length as ``df`` with values 1 for
        productive, 0 for non‑productive and NaN for rows where the rate
        could not be computed.
    """
    # Calculate production rate (pieces per hour)
    rate = df[produced_col] / (df[duration_col] / 60.0)

    # Filter out invalid durations (too small)
    rate = rate.where(df[duration_col] > min_duration)

    # Calculate threshold based on quantile of VALID rates only
    threshold = rate.quantile(quantile)

    # Create target: 1 if rate >= threshold, 0 otherwise
    # NaN rates will become NaN targets
    target = (rate >= threshold).astype(float)
    target.loc[rate.isna()] = np.nan

    return target


def compute_quantity_per_volume_target(
    df: pd.DataFrame,
    produced_col: str = "QT_PRODUZIDA",
    length_col: str = "VL_COMPRIMENTOINTERNO",
    width_col: str = "VL_LARGURAINTERNA",
    height_col: str = "VL_ALTURAINTERNA",
    volume_col: Optional[str] = "VOLUME_INTERNO",
    additional_volume_cols: Iterable[str] = (
        "VL_VOLUMEFECHADOPEDIDO",
        "VL_VOLUMEPACOTEFECHADOM3",
        "VL_VOLUMEPALETEFECHADOM3",
    ),
    min_volume: float = 1e-6,
) -> pd.Series:
    """Compute quantity produced per cubic metre for regression tasks.

    The function tries to derive the physical volume of the order in cubic
    metres by prioritising geometric measurements (length, width, height).
    When those dimensions are missing it falls back to pre-computed volume
    columns.  The returned series aligns with ``df`` and contains NaN for
    rows where the volume is unknown or below ``min_volume``.
    """

    qty = pd.to_numeric(df[produced_col], errors="coerce")
    volume_m3 = pd.Series(np.nan, index=df.index, dtype=float)

    dims_available = {length_col, width_col, height_col}.issubset(df.columns)
    if dims_available:
        dims = (
            pd.to_numeric(df[length_col], errors="coerce")
            * pd.to_numeric(df[width_col], errors="coerce")
            * pd.to_numeric(df[height_col], errors="coerce")
        )
        dims = dims.replace({0: np.nan})
        volume_m3 = dims / 1_000_000_000.0  # mm³ to m³

    if volume_col and volume_col in df.columns:
        vol_raw = pd.to_numeric(df[volume_col], errors="coerce")
        vol_raw = vol_raw.where(vol_raw > 0)
        median_val = vol_raw.dropna().median()
        if np.isfinite(median_val):
            if median_val > 1e6:
                vol_converted = vol_raw / 1_000_000_000.0
            elif median_val > 1e3:
                vol_converted = vol_raw / 1_000.0
            else:
                vol_converted = vol_raw
        else:
            vol_converted = vol_raw
        volume_m3 = volume_m3.fillna(vol_converted)

    for col in additional_volume_cols:
        if col in df.columns:
            vol_alt = pd.to_numeric(df[col], errors="coerce")
            vol_alt = vol_alt.where(vol_alt > 0)
            volume_m3 = volume_m3.fillna(vol_alt)

    volume_m3 = volume_m3.where(volume_m3 >= min_volume)
    target = qty / volume_m3
    target[volume_m3.isna()] = np.nan
    return target


def compute_volume_per_hour_target(
    df: pd.DataFrame,
    produced_col: str = "QT_PRODUZIDA",
    duration_col: str = "VL_DURACAO_PRODUCAO",
    length_col: str = "VL_COMPRIMENTOINTERNO",
    width_col: str = "VL_LARGURAINTERNA",
    height_col: str = "VL_ALTURAINTERNA",
    volume_col: Optional[str] = "VOLUME_INTERNO",
    additional_volume_cols: Iterable[str] = (
        "VL_VOLUMEFECHADOPEDIDO",
        "VL_VOLUMEPACOTEFECHADOM3",
        "VL_VOLUMEPALETEFECHADOM3",
    ),
    min_volume: float = 1e-9,
    min_duration_minutes: float = 0.1,
) -> pd.Series:
    """Compute throughput em volume físico (m³) por hora."""

    qty = pd.to_numeric(df[produced_col], errors="coerce")
    duration_minutes = pd.to_numeric(df[duration_col], errors="coerce")
    hours = duration_minutes / 60.0
    hours = hours.where(hours > (min_duration_minutes / 60.0))

    piece_volume_m3 = pd.Series(np.nan, index=df.index, dtype=float)
    dims_available = {length_col, width_col, height_col}.issubset(df.columns)
    if dims_available:
        dims = (
            pd.to_numeric(df[length_col], errors="coerce")
            * pd.to_numeric(df[width_col], errors="coerce")
            * pd.to_numeric(df[height_col], errors="coerce")
        )
        dims = dims.replace({0: np.nan})
        piece_volume_m3 = dims / 1_000_000_000.0

    if volume_col and volume_col in df.columns:
        vol_raw = pd.to_numeric(df[volume_col], errors="coerce").where(lambda v: v > 0)
        if vol_raw.notna().any():
            # convert heuristically the same way as compute_quantity_per_volume_target
            median_val = vol_raw.dropna().median()
            if np.isfinite(median_val):
                if median_val > 1e6:
                    vol_converted = vol_raw / 1_000_000_000.0
                elif median_val > 1e3:
                    vol_converted = vol_raw / 1_000.0
                else:
                    vol_converted = vol_raw
            else:
                vol_converted = vol_raw
            piece_volume_m3 = piece_volume_m3.fillna(vol_converted)

    for col in additional_volume_cols:
        if col in df.columns:
            vol_alt = pd.to_numeric(df[col], errors="coerce")
            vol_alt = vol_alt.where(vol_alt > 0)
            piece_volume_m3 = piece_volume_m3.fillna(vol_alt)

    piece_volume_m3 = piece_volume_m3.where(piece_volume_m3 >= min_volume)
    total_volume_m3 = piece_volume_m3 * qty
    throughput = total_volume_m3 / hours
    throughput[piece_volume_m3.isna() | hours.isna()] = np.nan
    throughput[~np.isfinite(throughput)] = np.nan
    return throughput


def train_classifier(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2,
    random_state: int = 42,
    threshold: float = 0.7,
) -> Tuple[HistGradientBoostingClassifier, dict]:
    """Train a HistGradientBoostingClassifier and evaluate on a hold‑out set.

    Parameters
    ----------
    X : pd.DataFrame
        Feature matrix.
    y : pd.Series
        Binary target variable.
    test_size : float, optional
        Fraction of the data to reserve for evaluation.  Defaults to 0.2.
    random_state : int, optional
        Random seed for the train/test split.  Defaults to 42.
    threshold : float, optional
        Probability threshold for classifying a sample as positive.  Defaults to 0.7.

    Returns
    -------
    tuple
        ``(clf, metrics)`` where ``clf`` is the fitted classifier and
        ``metrics`` is a dictionary containing ``roc_auc``, ``classification_report``
        and the ``threshold`` used.  The classification report is produced
        using the threshold to binarise predicted probabilities.
    """
    # Drop rows with NaN target
    mask_valid = y.notna()
    X_valid = X.loc[mask_valid]
    y_valid = y[mask_valid].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X_valid, y_valid, test_size=test_size, random_state=random_state, stratify=y_valid
    )
    clf = HistGradientBoostingClassifier(random_state=random_state)
    clf.fit(X_train, y_train)
    # Probabilities of the positive class
    y_proba = clf.predict_proba(X_test)[:, 1]
    # Threshold predictions
    y_pred = (y_proba >= threshold).astype(int)
    # Metrics
    roc_auc = roc_auc_score(y_test, y_proba)
    report = classification_report(y_test, y_pred, output_dict=True)
    metrics = {
        "roc_auc": roc_auc,
        "classification_report": report,
        "threshold": threshold,
    }
    return clf, metrics


def compute_permutation_importance(
    estimator: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    n_repeats: int = 10,
    random_state: int = 42,
    scoring: Optional[str] = "roc_auc",
) -> pd.Series:
    """Compute permutation feature importance on a held‑out set.

    Parameters
    ----------
    estimator : sklearn estimator
        Fitted estimator implementing ``predict``/``predict_proba``.
    X_test : pd.DataFrame
        Feature matrix of the test set.
    y_test : pd.Series
        True labels for the test set.
    n_repeats : int, optional
        Number of shuffling rounds.  Defaults to 10.
    random_state : int, optional
        Random seed used to draw permutations.  Defaults to 42.

    Returns
    -------
    pd.Series
        Mean decrease in accuracy for each feature, sorted descending.
    """
    r = permutation_importance(
        estimator,
        X_test,
        y_test,
        n_repeats=n_repeats,
        random_state=random_state,
        scoring=scoring,
    )
    importance = pd.Series(r.importances_mean, index=X_test.columns)
    return importance.sort_values(ascending=False)


__all__ = [
    "compute_productivity_target",
    "compute_quantity_per_volume_target",
    "compute_volume_per_hour_target",
    "train_classifier",
    "compute_permutation_importance",
]
