"""
Feature engineering utilities
============================

This module defines helper functions for deriving new features from the
merged production/order dataset.  The functions are stateless: they take a
DataFrame as input and return a new DataFrame with additional columns.

The core feature engineering steps performed in the original notebooks
included ratios of dimensions, volumes, surface areas, counts of pieces per
sheet and sums of refilo lengths.  These functions encapsulate those
operations so they can be reused in both flexo and corte/vinco pipelines.
"""
from __future__ import annotations

import pandas as pd
import numpy as np
from typing import List, Iterable


def create_geometric_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create geometric features such as ratios, volumes, areas and piece counts.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the raw geometric columns.  Columns used include
        ``VL_COMPRIMENTO``, ``VL_LARGURA``, ``VL_COMPRIMENTOINTERNO``,
        ``VL_LARGURAINTERNA``, ``VL_ALTURAINTERNA``, ``VL_COMPRIMENTOINTERNO``,
        ``VL_LARGURAINTERNA``, ``VL_ALTURAINTERNA``, ``VL_MULTCOMP``,
        ``VL_MULTLARG``, ``VL_REFILOCOMPRIMENTO`` and ``VL_REFILOLARGURA``.

    Returns
    -------
    pd.DataFrame
        A new DataFrame with additional columns:

        - ``RAZAO_COMP_LARG``: ratio of length to width of the external box.
        - ``RAZAO_INTERNA``: ratio of internal length to internal width.
        - ``VOLUME_INTERNO``: internal volume in cubic millimetres (mm³).
        - ``AREA_CHAPA``: area of the sheet (mm²).
        - ``PECAS_POR_CHAPA``: number of pieces per sheet (multiplicative).
        - ``REFILO_TOTAL``: total refilo length (mm) across both dimensions.
    """
    result = df.copy()
    # Avoid division by zero by replacing zeros with NaN
    if {'VL_COMPRIMENTO', 'VL_LARGURA'}.issubset(result.columns):
        denom = result['VL_LARGURA'].replace({0: np.nan})
        result['RAZAO_COMP_LARG'] = result['VL_COMPRIMENTO'] / denom
    if {'VL_COMPRIMENTOINTERNO', 'VL_LARGURAINTERNA'}.issubset(result.columns):
        denom_int = result['VL_LARGURAINTERNA'].replace({0: np.nan})
        result['RAZAO_INTERNA'] = result['VL_COMPRIMENTOINTERNO'] / denom_int
    # Volume interno (no division by 1e6 here – keep units consistent in mm³)
    vol_cols = {'VL_COMPRIMENTOINTERNO', 'VL_LARGURAINTERNA', 'VL_ALTURAINTERNA'}
    if vol_cols.issubset(result.columns):
        result['VOLUME_INTERNO'] = (
            result['VL_COMPRIMENTOINTERNO'] * result['VL_LARGURAINTERNA'] * result['VL_ALTURAINTERNA']
        )
    # Area da chapa
    if {'VL_COMPRIMENTO', 'VL_LARGURA'}.issubset(result.columns):
        result['AREA_CHAPA'] = result['VL_COMPRIMENTO'] * result['VL_LARGURA']
    # Peças por chapa
    if {'VL_MULTCOMP', 'VL_MULTLARG'}.issubset(result.columns):
        result['PECAS_POR_CHAPA'] = result['VL_MULTCOMP'] * result['VL_MULTLARG']
    # Total de refilo
    if {'VL_REFILOCOMPRIMENTO', 'VL_REFILOLARGURA'}.issubset(result.columns):
        result['REFILO_TOTAL'] = result['VL_REFILOCOMPRIMENTO'] + result['VL_REFILOLARGURA']
    return result


def drop_correlated_features(df: pd.DataFrame, threshold: float = 0.99) -> pd.DataFrame:
    """Remove highly correlated numeric features from a DataFrame.

    This function computes the absolute Pearson correlation matrix for all
    numeric columns and drops one of each pair of features with correlation
    above the given threshold.  It is deterministic: the feature that
    appears later in the DataFrame columns order is dropped.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame.
    threshold : float, optional
        Correlation coefficient above which to drop one of the two features.
        Defaults to 0.99, corresponding to almost perfectly collinear
        variables.

    Returns
    -------
    pd.DataFrame
        DataFrame with correlated features removed.
    """
    result = df.copy()
    numeric_cols = result.select_dtypes(include=[np.number]).columns.tolist()
    corr_matrix = result[numeric_cols].corr().abs()
    # Only consider the upper triangular portion to avoid duplicate pairs
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    to_drop: List[str] = []
    for col in upper.columns:
        if (upper[col] > threshold).any():
            # Drop this column if it is highly correlated with any previous column
            to_drop.append(col)
    return result.drop(columns=to_drop)


def select_features(df: pd.DataFrame, exclude: Iterable[str]) -> List[str]:
    """Return a list of column names to use as features after excluding some columns.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame whose columns are to be filtered.
    exclude : Iterable[str]
        Names of columns to remove from the feature list.  Non‑existent
        columns are ignored.

    Returns
    -------
    List[str]
        List of remaining column names suitable for modelling.
    """
    exclude_set = set(exclude)
    return [c for c in df.columns if c not in exclude_set]

__all__ = [
    "create_geometric_features",
    "drop_correlated_features",
    "select_features",
]