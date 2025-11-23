"""
Feature engineering functions for the packaging manufacturing domain.
"""

from typing import List

import numpy as np
import pandas as pd

from ..logger import get_logger

logger = get_logger(__name__)


def create_temporal_features(df: pd.DataFrame, datetime_col: str = "data") -> pd.DataFrame:
    """
    Create temporal features from a datetime column.

    Args:
        df: Input DataFrame
        datetime_col: Name of the datetime column

    Returns:
        DataFrame with added temporal features
    """
    df = df.copy()

    if datetime_col not in df.columns:
        logger.warning(f"Column {datetime_col} not found in DataFrame")
        return df

    # Convert to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(df[datetime_col]):
        df[datetime_col] = pd.to_datetime(df[datetime_col], errors="coerce")

    # Extract temporal components
    df["year"] = df[datetime_col].dt.year
    df["month"] = df[datetime_col].dt.month
    df["day"] = df[datetime_col].dt.day
    df["day_of_week"] = df[datetime_col].dt.dayofweek
    df["day_of_year"] = df[datetime_col].dt.dayofyear
    df["week_of_year"] = df[datetime_col].dt.isocalendar().week
    df["quarter"] = df[datetime_col].dt.quarter
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["is_month_start"] = df[datetime_col].dt.is_month_start.astype(int)
    df["is_month_end"] = df[datetime_col].dt.is_month_end.astype(int)

    # Time-based features
    if hasattr(df[datetime_col].dt, "hour"):
        df["hour"] = df[datetime_col].dt.hour
        df["is_business_hours"] = df["hour"].between(8, 18).astype(int)

    logger.info(f"Created {10} temporal features from {datetime_col}")
    return df


def create_production_features(
    df: pd.DataFrame,
    group_cols: List[str] = None,
    value_col: str = "quantidade",
) -> pd.DataFrame:
    """
    Create production-related features with aggregations.

    Args:
        df: Input DataFrame
        group_cols: Columns to group by for aggregations
        value_col: Value column for aggregations

    Returns:
        DataFrame with production features
    """
    df = df.copy()

    if group_cols is None:
        group_cols = ["cod_maquina", "year", "month"]

    if value_col not in df.columns:
        logger.warning(f"Value column {value_col} not found")
        return df

    # Rolling statistics
    if all(col in df.columns for col in group_cols):
        for window in [7, 14, 30]:
            df[f"{value_col}_rolling_mean_{window}d"] = (
                df.groupby(group_cols)[value_col].transform(lambda x: x.rolling(window, min_periods=1).mean())
            )
            df[f"{value_col}_rolling_std_{window}d"] = (
                df.groupby(group_cols)[value_col].transform(lambda x: x.rolling(window, min_periods=1).std())
            )

        # Lag features
        for lag in [1, 7, 30]:
            df[f"{value_col}_lag_{lag}"] = df.groupby(group_cols)[value_col].shift(lag)

        logger.info("Created production rolling and lag features")

    return df


def create_stoppage_features(
    df_paradas: pd.DataFrame,
    df_tarefcon: pd.DataFrame = None,
) -> pd.DataFrame:
    """
    Create features from machine stoppage data.

    Args:
        df_paradas: DataFrame with machine stoppage data
        df_tarefcon: Optional DataFrame with production tasks

    Returns:
        DataFrame with stoppage features
    """
    df = df_paradas.copy()

    # Duration features
    if "inicio" in df.columns and "fim" in df.columns:
        df["inicio"] = pd.to_datetime(df["inicio"], errors="coerce")
        df["fim"] = pd.to_datetime(df["fim"], errors="coerce")

        df["duracao_minutos"] = (df["fim"] - df["inicio"]).dt.total_seconds() / 60
        df["duracao_horas"] = df["duracao_minutos"] / 60

        # Categorize stoppage duration
        df["duracao_categoria"] = pd.cut(
            df["duracao_minutos"],
            bins=[0, 15, 60, 240, float("inf")],
            labels=["curta", "media", "longa", "muito_longa"],
        )

    # Stoppage frequency by machine
    if "cod_maquina" in df.columns:
        df["paradas_por_maquina"] = df.groupby("cod_maquina")["cod_maquina"].transform("count")

    # Time between stoppages
    if "cod_maquina" in df.columns and "inicio" in df.columns:
        df = df.sort_values(["cod_maquina", "inicio"])
        df["tempo_ate_proxima_parada"] = (
            df.groupby("cod_maquina")["inicio"].shift(-1) - df["inicio"]
        ).dt.total_seconds() / 60

    logger.info("Created stoppage features")
    return df


def create_knife_blade_features(df_facas: pd.DataFrame) -> pd.DataFrame:
    """
    Create features specific to knife/blade (facas) data.

    Args:
        df_facas: DataFrame with knife/blade data

    Returns:
        DataFrame with knife features
    """
    df = df_facas.copy()

    # Normalize blade length to meters if in millimeters
    if "COMPLAMINA" in df.columns:
        df["comp_lamina_metros"] = df["COMPLAMINA"] / 1000.0

    # Status encoding
    if "STATUS" in df.columns:
        status_map = {
            "0": "N/A",
            "1": "Ativo",
            "2": "Suspenso",
            "4": "Reparo",
            "5": "Desmanchadas",
            "6": "Alteração",
            "7": "Alt. Não Realizada",
        }
        df["status_descricao"] = df["STATUS"].astype(str).map(status_map)
        df["is_ativo"] = (df["STATUS"] == "1").astype(int)

    logger.info("Created knife/blade features")
    return df


def merge_temporal_production_data(
    df_tarefcon: pd.DataFrame,
    df_paradas: pd.DataFrame,
    tolerance_minutes: int = 30,
) -> pd.DataFrame:
    """
    Merge production tasks with stoppages using temporal proximity.

    Args:
        df_tarefcon: Production tasks DataFrame
        df_paradas: Machine stoppages DataFrame
        tolerance_minutes: Time tolerance for matching (minutes)

    Returns:
        Merged DataFrame
    """
    logger.info(f"Merging production data with {tolerance_minutes} minute tolerance")

    # Ensure datetime columns
    df_tarefcon = df_tarefcon.copy()
    df_paradas = df_paradas.copy()

    # Convert datetime columns
    for col in ["inicio", "fim"]:
        if col in df_tarefcon.columns:
            df_tarefcon[col] = pd.to_datetime(df_tarefcon[col], errors="coerce")
        if col in df_paradas.columns:
            df_paradas[col] = pd.to_datetime(df_paradas[col], errors="coerce")

    # Merge using pd.merge_asof for temporal join
    merged = pd.merge_asof(
        df_tarefcon.sort_values("inicio"),
        df_paradas.sort_values("inicio"),
        on="inicio",
        by="cod_maquina" if "cod_maquina" in df_tarefcon.columns and "cod_maquina" in df_paradas.columns else None,
        tolerance=pd.Timedelta(minutes=tolerance_minutes),
        direction="nearest",
        suffixes=("_tarefa", "_parada"),
    )

    logger.info(f"Merged {len(merged)} records")
    return merged
