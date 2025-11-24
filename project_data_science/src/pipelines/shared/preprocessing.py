"""
Shared preprocessing logic for pedidos data.

This module implements DRY (Don't Repeat Yourself) principle by providing
a base class with common preprocessing logic and specific implementations
for training and inference contexts.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict
import pandas as pd
import numpy as np
from src.logger import get_logger

logger = get_logger(__name__)


class PedidosPreprocessor(ABC):
    """
    Base class for preprocessing pedidos data.

    Uses Template Method pattern to define common preprocessing steps
    while allowing subclasses to customize filtering logic.
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize preprocessor.

        Args:
            verbose: Whether to log processing steps
        """
        self.verbose = verbose

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Main preprocessing pipeline (Template Method).

        Args:
            df: Raw DataFrame with pedidos data

        Returns:
            Preprocessed DataFrame
        """
        if self.verbose:
            logger.info(f"Iniciando preprocessing", extra={"shape": df.shape})

        df = df.copy()

        # Template method steps (order matters!)
        df = self._create_operation_id(df)
        df = self._rename_columns(df)
        df = self._apply_filters(df)  # Abstract - varies by context
        df = self._convert_flags(df)
        df = self._create_derived_features(df)
        df = self._handle_missing_values(df)

        if self.verbose:
            logger.info(f"Preprocessing concluído", extra={"shape": df.shape})

        return df

    def _create_operation_id(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create CD_OP identifier if it doesn't exist."""
        if "CD_OP" not in df.columns:
            df["CD_OP"] = (
                df["CD_PEDIDO"].astype(str) + "/" + df["CD_ITEM"].astype(str)
            )
            if self.verbose:
                logger.info("CD_OP criado")
        return df

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename columns to standardized names."""
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

        # Only rename columns that exist
        existing_renames = {k: v for k, v in rename_map.items() if k in df.columns}
        if existing_renames:
            df = df.rename(columns=existing_renames)
            if self.verbose:
                logger.info(f"Colunas renomeadas", extra={"count": len(existing_renames)})

        return df

    @abstractmethod
    def _apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply context-specific filters.

        This is the key method that varies between training and inference.
        Subclasses must implement this method.
        """
        pass

    def _convert_flags(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert string flags to numeric (0/1)."""
        flag_columns = [col for col in df.columns if col.startswith("FL_")]

        for col in flag_columns:
            if col in df.columns and df[col].dtype == "object":
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

        if flag_columns and self.verbose:
            logger.info(f"Flags convertidas", extra={"count": len(flag_columns)})

        return df

    def _create_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived features common to all contexts."""
        # Example: Could add volume, area calculations, etc.
        # This is a placeholder for common feature engineering
        return df

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values with context-appropriate strategy."""
        # Log missing value summary
        missing_summary = df.isnull().sum()
        cols_with_missing = missing_summary[missing_summary > 0]

        if len(cols_with_missing) > 0 and self.verbose:
            logger.info(
                f"Valores faltantes encontrados",
                extra={"columns": len(cols_with_missing)}
            )

        return df


class TrainingPreprocessor(PedidosPreprocessor):
    """
    Preprocessor for training data.

    Applies STRICT filters to ensure data quality for model training.
    """

    def __init__(
        self,
        delivery_date_cutoff: Optional[str] = "2024-01-01",
        exclude_suspended: bool = True,
        verbose: bool = True
    ):
        """
        Initialize training preprocessor.

        Args:
            delivery_date_cutoff: Filter orders before this date
            exclude_suspended: Whether to exclude suspended/cancelled orders
            verbose: Whether to log processing steps
        """
        super().__init__(verbose)
        self.delivery_date_cutoff = delivery_date_cutoff
        self.exclude_suspended = exclude_suspended

    def _apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply STRICT filters for training data.

        Training data should be clean and representative of normal operations.
        """
        initial_count = len(df)

        # Filter by delivery date (if specified)
        if self.delivery_date_cutoff and "DT_ENTREGAORIGINAL" in df.columns:
            df = df[df["DT_ENTREGAORIGINAL"] >= self.delivery_date_cutoff]
            if self.verbose:
                logger.info(
                    f"Filtro de data aplicado",
                    extra={
                        "cutoff": self.delivery_date_cutoff,
                        "removed": initial_count - len(df)
                    }
                )

        # Exclude suspended/cancelled orders
        if self.exclude_suspended and "FL_SUSPOUCANCEL" in df.columns:
            before = len(df)
            df = df[df["FL_SUSPOUCANCEL"] == "0"]
            if self.verbose:
                logger.info(
                    f"Pedidos suspensos/cancelados removidos",
                    extra={"removed": before - len(df)}
                )

        # Additional training-specific filters could go here
        # Example: Exclude outliers, incomplete records, etc.

        if self.verbose:
            logger.info(
                f"Filtros de treino aplicados",
                extra={
                    "initial": initial_count,
                    "final": len(df),
                    "removed": initial_count - len(df)
                }
            )

        return df


class InferencePreprocessor(PedidosPreprocessor):
    """
    Preprocessor for inference data.

    Applies MINIMAL filters to accept production data as-is.
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize inference preprocessor.

        Args:
            verbose: Whether to log processing steps
        """
        super().__init__(verbose)

    def _apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply MINIMAL filters for inference data.

        In production, we want to make predictions on all data,
        even if it's incomplete or unusual.
        """
        initial_count = len(df)

        # Only filter completely invalid records (if any)
        # Example: Records with no CD_PEDIDO or CD_ITEM
        if "CD_PEDIDO" in df.columns and "CD_ITEM" in df.columns:
            df = df.dropna(subset=["CD_PEDIDO", "CD_ITEM"])
            removed = initial_count - len(df)
            if removed > 0 and self.verbose:
                logger.warning(
                    f"Registros sem CD_PEDIDO/CD_ITEM removidos",
                    extra={"removed": removed}
                )

        # NO filtering by date, status, or other business logic
        # We want to predict on ALL incoming data

        return df


# Convenience function for backward compatibility
def process_pedidos_for_training(
    df: pd.DataFrame,
    delivery_date_cutoff: str = "2024-01-01"
) -> pd.DataFrame:
    """
    Process pedidos for training (backward compatible function).

    Args:
        df: Raw DataFrame
        delivery_date_cutoff: Cutoff date for filtering

    Returns:
        Processed DataFrame
    """
    preprocessor = TrainingPreprocessor(delivery_date_cutoff=delivery_date_cutoff)
    return preprocessor.preprocess(df)


def process_pedidos_for_inference(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process pedidos for inference (backward compatible function).

    Args:
        df: Raw DataFrame

    Returns:
        Processed DataFrame
    """
    preprocessor = InferencePreprocessor()
    return preprocessor.preprocess(df)
