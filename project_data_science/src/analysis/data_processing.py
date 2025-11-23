"""
Data processing and transformation utilities.
"""

from typing import List, Tuple

import numpy as np
import pandas as pd

from ..logger import get_logger

logger = get_logger(__name__)


def clean_numeric_and_categorical(
    df: pd.DataFrame,
    numeric_threshold: float = 0.9,
    inplace: bool = False,
) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """
    Clean and categorize columns as numeric or categorical.

    Args:
        df: Input DataFrame
        numeric_threshold: Minimum proportion of numeric values to classify as numeric
        inplace: Whether to modify DataFrame in place

    Returns:
        Tuple of (cleaned_df, numeric_columns, categorical_columns)
    """
    if not inplace:
        df = df.copy()

    # Replace empty strings with NaN
    df = df.replace(r"^\s*$", np.nan, regex=True)

    # Start with already numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    other_cols = [c for c in df.columns if c not in numeric_cols]

    categorical_cols = []

    # Try coercion for non-numeric columns
    for col in other_cols:
        coerced = pd.to_numeric(df[col], errors="coerce")
        prop_numeric = coerced.notna().sum() / len(df)

        if prop_numeric >= numeric_threshold:
            df[col] = coerced
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)

    # Fill missing values
    if numeric_cols:
        df[numeric_cols] = df[numeric_cols].fillna(0)
    if categorical_cols:
        df[categorical_cols] = df[categorical_cols].fillna("NA")

    logger.info(
        f"Processed {len(numeric_cols)} numeric and {len(categorical_cols)} categorical columns"
    )

    return df, numeric_cols, categorical_cols


def get_common_numeric_columns(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    exclude_ids: List[str] = None,
) -> List[str]:
    """
    Identify common numeric columns between two DataFrames.

    Args:
        df1: First DataFrame
        df2: Second DataFrame
        exclude_ids: List of ID column names to exclude

    Returns:
        List of common numeric column names
    """
    if exclude_ids is None:
        exclude_ids = ["ID_ITEM", "ID_PEDIDO", "ID_IDCLIENTE"]

    common = set(df1.columns).intersection(df2.columns)
    numeric_common = []

    for col in common:
        s1 = pd.to_numeric(df1[col], errors="coerce")
        s2 = pd.to_numeric(df2[col], errors="coerce")

        if s1.notna().any() and s2.notna().any():
            if col not in exclude_ids:
                numeric_common.append(col)

    return sorted(numeric_common)


def calculate_differences(
    df_left: pd.DataFrame,
    df_right: pd.DataFrame,
    join_key: str,
    value_columns: List[str],
    id_columns: List[str] = None,
) -> pd.DataFrame:
    """
    Calculate absolute and percentage differences between two DataFrames.

    Args:
        df_left: Left DataFrame (e.g., orders)
        df_right: Right DataFrame (e.g., items catalog)
        join_key: Column to join on
        value_columns: Columns to calculate differences for
        id_columns: Additional ID columns to include

    Returns:
        DataFrame with differences
    """
    if id_columns is None:
        id_columns = [join_key]

    # Ensure join key is string
    df_left = df_left.copy()
    df_right = df_right.copy()

    if join_key in df_left.columns:
        df_left[join_key] = df_left[join_key].astype(str)
    if join_key in df_right.columns:
        df_right[join_key] = df_right[join_key].astype(str)

    # Select columns
    left_cols = list(set(id_columns + value_columns))
    right_cols = list(set([join_key] + value_columns))

    df_l = df_left[left_cols].copy()
    df_r = df_right[right_cols].copy().drop_duplicates(join_key)

    # Coerce to numeric
    for col in value_columns:
        df_l[col] = pd.to_numeric(df_l[col], errors="coerce")
        df_r[col] = pd.to_numeric(df_r[col], errors="coerce")

    # Merge
    merged = df_l.merge(df_r, on=join_key, how="left", suffixes=("_left", "_right"))

    # Calculate differences
    result = merged[id_columns].copy()

    for col in value_columns:
        col_left = f"{col}_left" if f"{col}_left" in merged.columns else col
        col_right = f"{col}_right" if f"{col}_right" in merged.columns else col

        if col_left in merged.columns and col_right in merged.columns:
            # Absolute difference
            diff = merged[col_left] - merged[col_right]

            # Percentage difference (with zero protection)
            base = merged[col_right].replace(0, np.nan)
            diff_pct = (diff / base) * 100

            result[f"{col}_diff"] = diff
            result[f"{col}_diff_pct"] = diff_pct

    logger.info(f"Calculated differences for {len(result)} records")

    return result


def create_temporal_aggregation(
    df: pd.DataFrame,
    date_col: str,
    freq: str = "M",
    agg_col: str = None,
    agg_func: str = "count",
) -> pd.DataFrame:
    """
    Create temporal aggregations from datetime column.

    Args:
        df: Input DataFrame
        date_col: Date column name
        freq: Frequency ('D', 'W', 'M', 'Q', 'Y')
        agg_col: Column to aggregate (if None, counts records)
        agg_func: Aggregation function ('count', 'sum', 'mean', etc.)

    Returns:
        Aggregated DataFrame
    """
    df = df.copy()

    # Ensure datetime
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    # Create period column
    df["period"] = df[date_col].dt.to_period(freq)

    # Aggregate
    if agg_col is None:
        result = df.groupby("period").size().reset_index(name="count")
    else:
        result = (
            df.groupby("period")[agg_col]
            .agg(agg_func)
            .reset_index(name=f"{agg_col}_{agg_func}")
        )

    # Convert period to string for plotting
    result["period_str"] = result["period"].astype(str)

    return result


def abc_classification(
    values: pd.Series,
    thresholds: Tuple[float, float] = (80, 95),
) -> pd.DataFrame:
    """
    Perform ABC classification on a series of values.

    Args:
        values: Series of values (will be sorted descending)
        thresholds: Tuple of (A_threshold, B_threshold) percentages

    Returns:
        DataFrame with ABC classification
    """
    # Sort descending
    values_sorted = values.sort_values(ascending=False)

    # Calculate cumulative percentage
    total = values_sorted.sum()
    cumulative_pct = (values_sorted.cumsum() / total * 100)

    # Create classification
    result = pd.DataFrame(
        {
            "value": values_sorted,
            "percentage": values_sorted / total * 100,
            "cumulative": cumulative_pct,
        }
    )

    # Assign class
    result["class"] = "C"
    result.loc[result["cumulative"] <= thresholds[0], "class"] = "A"
    result.loc[
        (result["cumulative"] > thresholds[0]) & (result["cumulative"] <= thresholds[1]),
        "class",
    ] = "B"

    return result
