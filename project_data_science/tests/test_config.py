"""
Tests for configuration module.
"""

import pytest
from src.config import AppConfig, get_config


def test_config_singleton():
    """Test that get_config returns the same instance."""
    config1 = get_config()
    config2 = get_config()
    assert config1 is config2


def test_config_environment_defaults():
    """Test default configuration values."""
    config = get_config()
    assert config.environment in ["development", "staging", "production"]
    assert config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def test_config_is_development():
    """Test environment check methods."""
    config = get_config()
    if config.environment == "development":
        assert config.is_development is True
        assert config.is_production is False


def test_data_paths_config():
    """Test data paths configuration."""
    config = get_config()
    assert config.data_paths.raw_path is not None
    assert config.data_paths.trusted_path is not None
    assert config.data_paths.ml_path is not None
    assert config.data_paths.refined_path is not None
