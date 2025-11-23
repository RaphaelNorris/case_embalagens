"""
Configuration and constants
==========================

This module centralises configuration variables used throughout the pipeline.
Defining paths in one place makes it easier to adapt the code to different
environments (e.g. training locally versus on a cloud server).

All paths are now managed via the centralized ConfigManager which uses
environment variables and the src/config.py Pydantic settings.
"""
from pathlib import Path

# Import centralized config manager
import sys
SRC_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SRC_DIR))

from src.config_manager import get_config_manager

# Initialize config manager
_cm = get_config_manager()

# Project root and data directories
PROJECT_ROOT: Path = SRC_DIR
DATA_DIR: Path = _cm.data_dir
RAW_DIR: Path = _cm.raw_path
ML_DIR: Path = _cm.ml_path

# Additional directories
TRUSTED_DIR: Path = _cm.trusted_path
REFINED_DIR: Path = _cm.refined_path
MODELS_DIR: Path = _cm.models_dir

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
