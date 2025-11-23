"""
Configuration and constants
==========================

This module centralises configuration variables used throughout the pipeline.
Defining paths in one place makes it easier to adapt the code to different
environments (e.g. training locally versus on a cloud server).  Change the
constants below to point at your actual data locations.  All paths are
relative to the project root unless explicitly marked as absolute.
"""
from pathlib import Path

# Base directory for data.  By default we assume the notebooks live in a
# ``notebooks/`` directory three levels deeper than the project root and
# therefore the raw data is located in ``data/raw`` relative to the project
# root.  Adjust ``DATA_DIR`` if your folder layout differs.
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]

# Allow the user to override DATA_DIR by editing this constant.  Set the
# string to "" to fall back to the default ``PROJECT_ROOT / "data"``.
_DATA_DIR_DEFAULT = PROJECT_ROOT / "data"
DATA_DIR_CONFIG = "/home/adami/Documentos/Projeto_IA_AMCOM/project_data_science/data/"
if DATA_DIR_CONFIG:
    DATA_DIR: Path = Path(DATA_DIR_CONFIG).expanduser()
else:
    DATA_DIR = _DATA_DIR_DEFAULT

# Subdirectories for raw and processed data.  Raw data should contain the
# parquet files provided by the manufacturing systems.  Processed data
# produced by these pipelines is saved into ``ML_DIR``.  You can override
# these values when calling the pipeline functions.

RAW_DIR: Path = DATA_DIR / "raw"
ML_DIR: Path = DATA_DIR / "ml"

# Filenames for key tables.  These match the naming conventions used in the
# original notebooks.  If your raw data files live elsewhere or have
# different names then update these constants accordingly.
TB_PARADAS: str = "tb_paradas.parquet"
TB_FACAS: str = "tb_facas.parquet"
TB_MAQUINAS: str = "tb_maquina.parquet"
TB_TAREFCON: str = "tb_tarefcon.parquet"
TB_PEDIDOS: str = "tb_pedidos.parquet"

# Names of the final aggregated tables produced by ``pipeline_ops_paradas``.
FINAL_TABLE_FLEXO: str = "table_final_flexo.parquet"
FINAL_TABLE_CV: str = "table_final_cv.parquet"

__all__ = [
    "PROJECT_ROOT",
    "DATA_DIR",
    "RAW_DIR",
    "ML_DIR",
    "TB_PARADAS",
    "TB_FACAS",
    "TB_MAQUINAS",
    "TB_TAREFCON",
    "TB_PEDIDOS",
    "FINAL_TABLE_FLEXO",
    "FINAL_TABLE_CV",
]
