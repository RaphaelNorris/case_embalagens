"""
Tests for feature engineering module.
"""

import pandas as pd
import pytest
from src.features.build_features import (
    create_temporal_features,
    create_production_features,
    create_knife_blade_features,
)


@pytest.fixture
def sample_datetime_df():
    """Create a sample DataFrame with datetime column."""
    return pd.DataFrame(
        {
            "data": pd.date_range("2024-01-01", periods=100, freq="h"),
            "value": range(100),
        }
    )


@pytest.fixture
def sample_production_df():
    """Create a sample DataFrame with production data."""
    return pd.DataFrame(
        {
            "cod_maquina": ["M1", "M1", "M2", "M2"] * 25,
            "quantidade": [100, 150, 200, 120] * 25,
            "year": [2024] * 100,
            "month": [1] * 100,
        }
    )


def test_create_temporal_features(sample_datetime_df):
    """Test temporal feature creation."""
    result = create_temporal_features(sample_datetime_df, datetime_col="data")

    # Check that temporal features were added
    assert "year" in result.columns
    assert "month" in result.columns
    assert "day" in result.columns
    assert "day_of_week" in result.columns
    assert "is_weekend" in result.columns
    assert "quarter" in result.columns

    # Check values
    assert result["year"].iloc[0] == 2024
    assert result["month"].iloc[0] == 1


def test_create_temporal_features_missing_column():
    """Test temporal features with missing column."""
    df = pd.DataFrame({"value": [1, 2, 3]})
    result = create_temporal_features(df, datetime_col="nonexistent")

    # Should return original DataFrame
    assert len(result.columns) == len(df.columns)


def test_create_production_features(sample_production_df):
    """Test production feature creation."""
    result = create_production_features(
        sample_production_df,
        group_cols=["cod_maquina", "year", "month"],
        value_col="quantidade",
    )

    # Check that features were added
    assert any("rolling_mean" in col for col in result.columns)
    assert any("lag" in col for col in result.columns)


def test_create_knife_blade_features():
    """Test knife/blade feature creation."""
    df = pd.DataFrame(
        {
            "CODFACA": [1, 2, 3],
            "COMPLAMINA": [1000, 2000, 1500],
            "STATUS": ["1", "2", "4"],
        }
    )

    result = create_knife_blade_features(df)

    assert "comp_lamina_metros" in result.columns
    assert "status_descricao" in result.columns
    assert "is_ativo" in result.columns
    assert result["comp_lamina_metros"].iloc[0] == 1.0
    assert result["is_ativo"].iloc[0] == 1
