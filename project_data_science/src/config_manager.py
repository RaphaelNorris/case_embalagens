"""
Centralized configuration manager with path validation.

Provides simplified access to configuration and ensures all paths exist.
"""
from pathlib import Path
from typing import Optional
import logging

from src.config import get_config, AppConfig

logger = logging.getLogger(__name__)


class ConfigManager:
    """Centralized configuration with path validation and helpers."""

    def __init__(self, config: Optional[AppConfig] = None):
        """Initialize config manager.

        Args:
            config: Optional config instance. If None, loads from environment.
        """
        self.config = config or get_config()
        self._validate_and_create_paths()

    def _validate_and_create_paths(self):
        """Ensure all data paths exist, creating them if necessary."""
        paths_to_check = [
            self.raw_path,
            self.trusted_path,
            self.ml_path,
            self.refined_path,
        ]

        for path in paths_to_check:
            if not path.exists():
                logger.warning(f"Path does not exist, creating: {path}")
                path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"✓ Path validated: {path}")

    # Data paths properties
    @property
    def raw_path(self) -> Path:
        """Bronze layer - raw data."""
        return Path(self.config.data_paths.raw_path)

    @property
    def trusted_path(self) -> Path:
        """Silver layer - cleaned/validated data."""
        return Path(self.config.data_paths.trusted_path)

    @property
    def ml_path(self) -> Path:
        """ML features layer."""
        return Path(self.config.data_paths.ml_path)

    @property
    def refined_path(self) -> Path:
        """Gold layer - aggregated/analytical data."""
        return Path(self.config.data_paths.refined_path)

    @property
    def data_dir(self) -> Path:
        """Base data directory (parent of all layers)."""
        return self.raw_path.parent

    # Model paths
    @property
    def models_dir(self) -> Path:
        """Directory for saved models."""
        models_path = self.data_dir.parent / "models"
        models_path.mkdir(parents=True, exist_ok=True)
        return models_path

    @property
    def artifacts_dir(self) -> Path:
        """Directory for ML artifacts (scalers, encoders, etc)."""
        artifacts_path = self.data_dir.parent / "artifacts"
        artifacts_path.mkdir(parents=True, exist_ok=True)
        return artifacts_path

    # Documentation paths
    @property
    def docs_dir(self) -> Path:
        """Documentation directory."""
        docs_path = self.data_dir.parent / "docs"
        docs_path.mkdir(parents=True, exist_ok=True)
        return docs_path

    @property
    def data_quality_dir(self) -> Path:
        """Data quality reports directory."""
        dq_path = self.docs_dir / "data_quality"
        dq_path.mkdir(parents=True, exist_ok=True)
        return dq_path

    # Helper methods
    def get_table_path(self, table_name: str, layer: str = "trusted", ext: str = "parquet") -> Path:
        """Get path to a specific table in a data layer.

        Args:
            table_name: Name of the table (e.g., 'tb_pedidos')
            layer: Data layer ('raw', 'trusted', 'ml', 'refined')
            ext: File extension (default: 'parquet')

        Returns:
            Full path to the table file

        Example:
            >>> cm = ConfigManager()
            >>> path = cm.get_table_path('tb_pedidos', 'trusted')
            >>> # Returns: Path('data/02 - trusted/parquet/tb_pedidos.parquet')
        """
        layer_map = {
            "raw": self.raw_path,
            "trusted": self.trusted_path,
            "ml": self.ml_path,
            "refined": self.refined_path,
        }

        base_path = layer_map.get(layer)
        if base_path is None:
            raise ValueError(f"Invalid layer: {layer}. Must be one of: {list(layer_map.keys())}")

        # Check for parquet subdirectory (common pattern)
        parquet_dir = base_path / "parquet"
        if ext == "parquet" and parquet_dir.exists():
            return parquet_dir / f"{table_name}.{ext}"

        return base_path / f"{table_name}.{ext}"

    def get_model_path(self, model_name: str, version: Optional[str] = None) -> Path:
        """Get path to a saved model.

        Args:
            model_name: Name of the model (e.g., 'cv_model', 'flexo_model')
            version: Optional version string (e.g., '20241123', 'v1.0')

        Returns:
            Full path to the model file
        """
        if version:
            return self.models_dir / f"{model_name}_{version}.pkl"
        return self.models_dir / f"{model_name}.pkl"

    def __repr__(self) -> str:
        return f"ConfigManager(environment={self.config.environment})"


# Global singleton instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get or create the global ConfigManager instance.

    Returns:
        Singleton ConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


# Convenience alias
cm = get_config_manager


if __name__ == "__main__":
    # Demo usage
    config_mgr = get_config_manager()
    print(f"ConfigManager initialized: {config_mgr}")
    print(f"Raw path: {config_mgr.raw_path}")
    print(f"Trusted path: {config_mgr.trusted_path}")
    print(f"Models dir: {config_mgr.models_dir}")
    print(f"Table path example: {config_mgr.get_table_path('tb_pedidos', 'trusted')}")
