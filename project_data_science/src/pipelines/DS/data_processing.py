"""
Data loading and pre‑processing utilities
========================================

This module contains helper functions for reading parquet files and
pre‑processing the order table (pedidos).  The functions are written with
type hints and clear docstrings to encourage reuse.  Downstream code should
avoid loading the same file multiple times – instead load it once here and
pass the resulting DataFrame to other functions.

Most functions take ``Path`` objects as inputs rather than raw strings;
however convenient defaults referencing ``ml_pipeline.config`` are provided.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional

if __package__ in (None, ""):
    import sys

    SRC_DIR = Path(__file__).resolve().parents[2]
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))

    from pipelines.DS import config
else:
    from . import config

def load_parquet(file_path: Path) -> pd.DataFrame:
    """Load a parquet file into a DataFrame.

    Parameters
    ----------
    file_path: Path
        Absolute or project‑relative path to the parquet file.

    Returns
    -------
    pd.DataFrame
        The loaded DataFrame.
    """
    return pd.read_parquet(file_path)


def load_raw_table(filename: str, raw_dir: Path | None = None) -> pd.DataFrame:
    """Load a raw parquet table from the ``data/raw`` directory.

    Parameters
    ----------
    filename: str
        Name of the parquet file (e.g., ``"tb_paradas.parquet"``).
    raw_dir: Path, optional
        Directory containing the raw files.  Defaults to
        ``ml_pipeline.config.RAW_DIR``.

    Returns
    -------
    pd.DataFrame
        The loaded DataFrame.
    """
    raw_dir = raw_dir or config.RAW_DIR
    file_path = raw_dir / filename
    return load_parquet(file_path)


def load_final_table(machine_type: str, ml_dir: Path | None = None) -> pd.DataFrame:
    """Load the pre‑aggregated table of production metrics for a given machine type.

    The pipeline that created this package produces two aggregated tables
    (``table_final_flexo.parquet`` and ``table_final_cv.parquet``) via the
    ``pipeline_ops_paradas`` notebook.  These files summarise per‑operation
    statistics such as production quantity, duration of production, total
    duration of stops and number of stops.  Use this function to load the
    appropriate table for a given machine type.

    Parameters
    ----------
    machine_type: str
        Either ``"flexo"`` or ``"cv"`` (case insensitive).  Other values will
        raise a ``ValueError``.
    ml_dir: Path, optional
        Directory containing the machine learning tables.  Defaults to
        ``ml_pipeline.config.ML_DIR``.

    Returns
    -------
    pd.DataFrame
        The aggregated table filtered to the specified machine type.
    """
    ml_dir = ml_dir or config.ML_DIR
    machine_type = machine_type.lower()
    if machine_type == "flexo":
        filename = config.FINAL_TABLE_FLEXO
    elif machine_type in {"cv", "corte", "corte_vinco"}:
        # Accept multiple aliases for corte/vinco
        filename = config.FINAL_TABLE_CV
    else:
        raise ValueError(f"Unknown machine_type '{machine_type}'. Use 'flexo' or 'cv'.")
    file_path = ml_dir / filename
    return load_parquet(file_path)


def process_pedidos(
    df_pedidos: Optional[pd.DataFrame] = None,
    raw_file: Optional[Path] = None,
    delivery_date_cutoff: str = "2024-01-01",
) -> pd.DataFrame:
    """Filter and engineer features for the order (pedido) dataset.

    This function reproduces the processing steps implemented in the
    ``nb_pedidos_process.ipynb`` notebook.  It performs date filtering,
    removal of cancelled/suspended orders, creation of a composite operation
    identifier (``CD_OP``), renaming of columns for clarity, conversion of
    flags to binary format and creation of several derived numerical
    features.

    Parameters
    ----------
    df_pedidos: pd.DataFrame, optional
        If provided, this DataFrame is processed directly.  Otherwise the
        function loads the raw order table from ``raw_file``.  If both are
        provided ``df_pedidos`` takes precedence.
    raw_file: Path, optional
        Parquet file path for the raw orders table.  Defaults to
        ``ml_pipeline.config.RAW_DIR / ml_pipeline.config.TB_PEDIDOS``.
    delivery_date_cutoff: str, optional
        Only orders with ``DT_ENTREGAORIGINAL`` on or after this ISO date
        string are retained.  Defaults to "2024-01-01".

    Returns
    -------
    pd.DataFrame
        A new DataFrame containing the processed orders with derived
        features.  The original input is not modified.
    """
    if df_pedidos is None:
        raw_file = raw_file or (config.RAW_DIR / config.TB_PEDIDOS)
        df_pedidos = pd.read_parquet(raw_file)
    df = df_pedidos.copy()

    # Create composite operation ID
    df["CD_OP"] = df["CD_PEDIDO"].astype(str) + "/" + df["CD_ITEM"].astype(str)

    # Filter by delivery date
    df = df[df["DT_ENTREGAORIGINAL"] >= delivery_date_cutoff]

    # Remove cancelled/suspended orders
    df = df[df["FL_SUSPOUCANCEL"] == "0"]
    df = df[df["ST_PEDIDO"] != "4"]
    df = df[df["FL_SUSPENSO"] == "0"]

    # Compute percentage variation between min and max ordered quantities
    df["PERC_VAR_PEDIDA"] = (
        (df["QT_PEDIDAMAX"] - df["QT_PEDIDA"]) / df["QT_PEDIDA"] * 100
    )

    # Remove plates (FL_CHAPA == 1)
    df = df[df["FL_CHAPA"] != "1"]

    # Drop high cardinality or uninformative columns
    cols_drop = [
        "ID_CLIENTE",
        "FL_CHAPA",
        "VL_ALTURAPACOTE",
        "VL_ALTURAPALETEFECHADO",
        "VL_COMPPALETEFECHADO",
        "VL_COMPPACOTE",
        "VL_LARGPACOTE",
        "VL_LARGPALETEFECHADO",
        "VL_PACOTESCOMPRIMENTO",
        "VL_PACOTESLARGURA",
        "VL_PACOTESALTURA",
        "TX_DESCRTIPODOPEDIDO",
        "TX_DESCRSTATUSPEDIDO",
        "TX_DESCTIPOENTREGA",
        "DT_ENTREGA2",
        "DT_ENTREGAORIGINAL",
        "CD_REFERENCIA",
        "CD_PALETE",
        "FL_PALETIZADO",
        "FL_TIPOENTREGA",
        "FL_SUSPOUCANCEL",
        "ST_PEDIDO",
        "FL_SUSPENSO",
        "QT_PECASPORPACOTE",
        "QT_PECASPORPALETE",
        "QT_UNIDADESPORPALETE",
        "QT_PACOTESPORPALETE",
        "VL_VOLUMEPACOTEFECHADOM3",
        "VL_VOLUMEPALETEFECHADOM3",
        "VL_VOLUMEFECHADOPEDIDO",
        "QT_PEDIDAMAX",
        "QT_PEDIDAMIN",
    ]
    # Keep only existing columns from the list
    df = df.drop(columns=[c for c in cols_drop if c in df.columns])

    # Rename columns for clarity
    rename_map = {
        "FL_EXIGELAUDO": "FL_TESTE_EXIGELAUDO",
        "VL_COLUNAMINIMO": "VL_COLUNAMINIMO",
        "QT_COBBINTMAXIMO": "VL_COBBINTMAXIMO",
        "VL_COMPRESSAO": "VL_COMPRESSAO",
        "VL_GRAMATURA": "VL_GRAMATURA",
        "CD_ESPELHO": "CAT_ESPELHO",
        "CD_FILME": "CAT_FILME",
        "CD_TIPOFT2": "FL_CONTROLE_ESPECIAL_IMPRESSAO",
        "VL_LAPINTERNO": "FL_LAP_INTERNO",
        "VL_LAPNOCOMP": "FL_LAP_NO_COMPR",
        "TX_COMPOSICAO": "CAT_COMPOSICAO",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Convert LAP flags to binary (replace -1 with 0)
    for col in ["FL_LAP_INTERNO", "FL_LAP_NO_COMPR"]:
        if col in df.columns:
            df[col] = df[col].replace(-1, 0).astype(int)

    # Binary flag for FL_PROLONG_LAP
    if "FL_PROLONG_LAP" in df.columns:
        df["FL_PROLONG_LAP"] = (df["FL_PROLONG_LAP"] > 0).astype(int)

    # Padronise FL_CONTROLE_ESPECIAL_IMPRESSAO: convert -1/2 into 0/1
    if "FL_CONTROLE_ESPECIAL_IMPRESSAO" in df.columns:
        df["FL_CONTROLE_ESPECIAL_IMPRESSAO"] = (
            df["FL_CONTROLE_ESPECIAL_IMPRESSAO"].astype(str).replace({"-1": "0", "2": "1"}).astype(int)
        )

    # Convert selected numeric columns to integers where appropriate
    for col in ["FL_LAP_INTERNO", "FL_LAP_NO_COMPR", "FL_PROLONG_LAP", "QT_ARRANJO", "QT_NRCORES"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Aggregate colour consumption into a single column and drop individual colours
    col_corr = ["QT_CONSUMOCOR1", "QT_CONSUMOCOR2", "QT_CONSUMOCOR3", "QT_CONSUMOCOR4"]
    if any(c in df.columns for c in col_corr):
        df["VL_CONSUMO_COR_TOTAL"] = df[col_corr].sum(axis=1)
        df.drop(columns=[c for c in col_corr if c in df.columns], inplace=True)

    # Map QT_PROLONGLAP values into a binary flag FL_PROLONGLAP
    if "QT_PROLONGLAP" in df.columns:
        df["FL_PROLONGLAP"] = df["QT_PROLONGLAP"].replace({50: 1, 30: 1}).fillna(0).astype(int)
        df.drop(columns=["QT_PROLONGLAP"], inplace=True)

    # Create aggregated vinyl feature: sum of all VINCO lengths
    vinco_comp_cols = [c for c in df.columns if c.startswith("VL_VINCOCOMP")]
    vinco_larg_cols = [c for c in df.columns if c.startswith("VL_VINCOLARG")]
    if vinco_comp_cols or vinco_larg_cols:
        df["VL_VINCOS_TOTAL_MM"] = df[vinco_comp_cols].sum(axis=1) + df[vinco_larg_cols].sum(axis=1)
        # It is up to the caller to drop the individual vinco columns if desired

    # Dimension ratios of the sheet and unfolded piece
    if {"VL_COMPRIMENTO", "VL_LARGURA"}.issubset(df.columns):
        df["RAZAO_CHAPA_COMP_LARG"] = df["VL_COMPRIMENTO"] / df["VL_LARGURA"].replace(0, np.nan)
        df["RAZAO_CHAPA_COMP_LARG"] = df["RAZAO_CHAPA_COMP_LARG"].replace([np.inf, -np.inf], np.nan)
    if {"VL_COMPPECA", "VL_LARGPECA"}.issubset(df.columns):
        df["RAZAO_PECA_COMP_LARG"] = df["VL_COMPPECA"] / df["VL_LARGPECA"].replace(0, np.nan)
        df["RAZAO_PECA_COMP_LARG"] = df["RAZAO_PECA_COMP_LARG"].replace([np.inf, -np.inf], np.nan)

    # Internal volume in cubic decimetres (litres).  Note: the original notebook
    # divides by 1,000,000 to convert mm³ into litres (1 dm³ = 1,000,000 mm³).
    vol_cols = {"VL_COMPRIMENTOINTERNO", "VL_LARGURAINTERNA", "VL_ALTURAINTERNA"}
    if vol_cols.issubset(df.columns):
        df["VOLUME_INTERNO"] = (
            df["VL_COMPRIMENTOINTERNO"] * df["VL_LARGURAINTERNA"] * df["VL_ALTURAINTERNA"]
        ) / 1_000_000.0

    # Drop other redundant area columns if present
    cols_remove = [
        "VL_ALTURAINTERNA_REAL",
        "VL_AREABRUTACHAPA",
        "VL_AREABRUTAPECA",
        "VL_AREABRUTAPECACOMREFILOS",
        "VL_AREALIQUIDACHAPA",
    ]
    df = df.drop(columns=[c for c in cols_remove if c in df.columns])

    return df

__all__ = [
    "load_parquet",
    "load_raw_table",
    "load_final_table",
    "process_pedidos",
]
