"""
Centralized configuration management for the project.
Uses pydantic-settings for type-safe environment variable handling.
"""

import os
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OracleConfig(BaseSettings):
    """Oracle database configuration."""

    model_config = SettingsConfigDict(env_prefix="ORACLE_", case_sensitive=False)

    host: str
    port: int = 1521
    service_name: str

    # Layer-specific users
    raw_user: str
    raw_password: str
    trusted_user: str
    trusted_password: str
    refined_user: str
    refined_password: str


class SQLServerConfig(BaseSettings):
    """SQL Server database configuration."""

    model_config = SettingsConfigDict(env_prefix="SQLSERVER_", case_sensitive=False)

    host: str
    port: int = 1433
    database: str
    user: str
    password: str


class DataPathsConfig(BaseSettings):
    """Data layer paths configuration."""

    model_config = SettingsConfigDict(env_prefix="DATA_", case_sensitive=False)

    raw_path: Path = Path("project_data_science/data/01 - raw")
    trusted_path: Path = Path("project_data_science/data/02 - trusted")
    ml_path: Path = Path("project_data_science/data/03 - ml")
    refined_path: Path = Path("project_data_science/data/04 - refined")

    def get_raw_path(self) -> Path:
        """Get absolute path to raw data layer."""
        return self.raw_path.resolve()

    def get_trusted_path(self) -> Path:
        """Get absolute path to trusted data layer."""
        return self.trusted_path.resolve()

    def get_ml_path(self) -> Path:
        """Get absolute path to ML data layer."""
        return self.ml_path.resolve()

    def get_refined_path(self) -> Path:
        """Get absolute path to refined data layer."""
        return self.refined_path.resolve()


class MLConfig(BaseSettings):
    """Machine Learning configuration."""

    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)

    model_registry_path: Path = Path("project_data_science/models")
    mlflow_tracking_uri: str = "sqlite:///mlflow.db"
    mlflow_experiment_name: str = "adami_production_optimization"


class AppConfig(BaseSettings):
    """Main application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: Literal["development", "staging", "production"] = "development"

    # Logging
    log_level: str = "INFO"
    log_format: Literal["json", "text"] = "text"

    # Feature flags
    enable_monitoring: bool = True
    enable_data_validation: bool = True

    # Sub-configurations
    oracle: OracleConfig = Field(default_factory=OracleConfig)
    sqlserver: SQLServerConfig = Field(default_factory=SQLServerConfig)
    data_paths: DataPathsConfig = Field(default_factory=DataPathsConfig)
    ml: MLConfig = Field(default_factory=MLConfig)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


# Global configuration instance
config = AppConfig()


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    return config
