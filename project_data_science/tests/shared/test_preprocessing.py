"""
Tests for shared preprocessing module.

Tests the DRY preprocessing classes: TrainingPreprocessor and InferencePreprocessor.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.pipelines.shared.preprocessing import (
    TrainingPreprocessor,
    InferencePreprocessor,
    process_pedidos_for_training,
    process_pedidos_for_inference,
)


@pytest.fixture
def sample_pedidos():
    """Create sample pedidos data for testing."""
    return pd.DataFrame({
        'CD_PEDIDO': ['P001', 'P002', 'P003', 'P004', 'P005'],
        'CD_ITEM': ['1', '2', '1', '3', '1'],
        'DT_ENTREGAORIGINAL': [
            '2024-01-15',
            '2023-12-01',  # Old date - should be filtered in training
            '2024-02-01',
            '2024-03-01',
            '2023-11-01',  # Old date
        ],
        'FL_SUSPOUCANCEL': ['0', '1', '0', '0', '0'],  # P002 suspended
        'FL_EXIGELAUDO': ['1', '0', '1', '0', '1'],
        'VL_GRAMATURA': [150.5, 200.0, 180.0, 160.0, 190.0],
        'QT_COBBINTMAXIMO': [10, 20, 15, 25, 30],
    })


class TestTrainingPreprocessor:
    """Test TrainingPreprocessor class."""

    def test_initialization(self):
        """Test preprocessor can be initialized."""
        prep = TrainingPreprocessor()
        assert prep.delivery_date_cutoff == "2024-01-01"
        assert prep.exclude_suspended is True

    def test_filters_old_dates(self, sample_pedidos):
        """Test that old dates are filtered out."""
        prep = TrainingPreprocessor(delivery_date_cutoff='2024-01-01', verbose=False)
        result = prep.preprocess(sample_pedidos)

        # Should filter out P002 (2023-12-01) and P005 (2023-11-01)
        assert len(result) == 3
        assert 'P002' not in result['CD_PEDIDO'].values
        assert 'P005' not in result['CD_PEDIDO'].values

    def test_excludes_suspended_orders(self, sample_pedidos):
        """Test that suspended/cancelled orders are excluded."""
        prep = TrainingPreprocessor(delivery_date_cutoff=None, verbose=False)
        result = prep.preprocess(sample_pedidos)

        # Should filter out P002 (FL_SUSPOUCANCEL = '1')
        assert 'P002' not in result['CD_PEDIDO'].values

    def test_creates_operation_id(self, sample_pedidos):
        """Test that CD_OP is created correctly."""
        # Remove CD_OP if exists
        df = sample_pedidos.copy()
        if 'CD_OP' in df.columns:
            df = df.drop(columns=['CD_OP'])

        prep = TrainingPreprocessor(verbose=False)
        result = prep.preprocess(df)

        assert 'CD_OP' in result.columns
        assert result.iloc[0]['CD_OP'] == 'P001/1'
        assert result.iloc[2]['CD_OP'] == 'P003/1'

    def test_renames_columns(self, sample_pedidos):
        """Test that columns are renamed correctly."""
        prep = TrainingPreprocessor(verbose=False)
        result = prep.preprocess(sample_pedidos)

        # FL_EXIGELAUDO should be renamed to FL_TESTE_EXIGELAUDO
        assert 'FL_TESTE_EXIGELAUDO' in result.columns
        assert 'FL_EXIGELAUDO' not in result.columns

    def test_converts_flags(self, sample_pedidos):
        """Test that flag columns are converted to numeric."""
        prep = TrainingPreprocessor(verbose=False)
        result = prep.preprocess(sample_pedidos)

        # All FL_ columns should be numeric
        flag_cols = [col for col in result.columns if col.startswith('FL_')]
        for col in flag_cols:
            assert pd.api.types.is_numeric_dtype(result[col])

    def test_backward_compatible_function(self, sample_pedidos):
        """Test backward compatible function works."""
        result = process_pedidos_for_training(sample_pedidos, delivery_date_cutoff='2024-01-01')

        assert isinstance(result, pd.DataFrame)
        assert len(result) < len(sample_pedidos)  # Some should be filtered


class TestInferencePreprocessor:
    """Test InferencePreprocessor class."""

    def test_initialization(self):
        """Test preprocessor can be initialized."""
        prep = InferencePreprocessor()
        assert prep.verbose is True

    def test_keeps_all_data(self, sample_pedidos):
        """Test that inference keeps all valid data (no date/status filters)."""
        prep = InferencePreprocessor(verbose=False)
        result = prep.preprocess(sample_pedidos)

        # Should keep all records (no date or status filtering)
        assert len(result) == len(sample_pedidos)

    def test_creates_operation_id(self, sample_pedidos):
        """Test that CD_OP is created correctly."""
        df = sample_pedidos.copy()
        if 'CD_OP' in df.columns:
            df = df.drop(columns=['CD_OP'])

        prep = InferencePreprocessor(verbose=False)
        result = prep.preprocess(df)

        assert 'CD_OP' in result.columns
        assert result.iloc[0]['CD_OP'] == 'P001/1'

    def test_handles_missing_pedido(self, sample_pedidos):
        """Test that records without CD_PEDIDO are dropped."""
        df = sample_pedidos.copy()
        df.loc[0, 'CD_PEDIDO'] = None

        prep = InferencePreprocessor(verbose=False)
        result = prep.preprocess(df)

        # Should drop record with missing CD_PEDIDO
        assert len(result) == len(sample_pedidos) - 1

    def test_renames_columns(self, sample_pedidos):
        """Test that columns are renamed correctly."""
        prep = InferencePreprocessor(verbose=False)
        result = prep.preprocess(sample_pedidos)

        # Check renamed column
        assert 'VL_COBBINTMAXIMO' in result.columns
        assert 'QT_COBBINTMAXIMO' not in result.columns

    def test_backward_compatible_function(self, sample_pedidos):
        """Test backward compatible function works."""
        result = process_pedidos_for_inference(sample_pedidos)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_pedidos)  # Should keep all


class TestPreprocessorComparison:
    """Test differences between Training and Inference preprocessors."""

    def test_training_vs_inference_filtering(self, sample_pedidos):
        """Test that training filters more strictly than inference."""
        training_prep = TrainingPreprocessor(verbose=False)
        inference_prep = InferencePreprocessor(verbose=False)

        training_result = training_prep.preprocess(sample_pedidos)
        inference_result = inference_prep.preprocess(sample_pedidos)

        # Training should have fewer records due to filters
        assert len(training_result) < len(inference_result)

    def test_column_transformations_consistent(self, sample_pedidos):
        """Test that column transformations are consistent across both."""
        training_prep = TrainingPreprocessor(verbose=False)
        inference_prep = InferencePreprocessor(verbose=False)

        training_result = training_prep.preprocess(sample_pedidos)
        inference_result = inference_prep.preprocess(sample_pedidos)

        # Both should create CD_OP
        assert 'CD_OP' in training_result.columns
        assert 'CD_OP' in inference_result.columns

        # Both should rename columns the same way
        assert set(training_result.columns) == set(inference_result.columns)


# Integration tests
class TestPreprocessingIntegration:
    """Integration tests for real-world scenarios."""

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        df = pd.DataFrame()
        prep = InferencePreprocessor(verbose=False)

        # Should not crash
        result = prep.preprocess(df)
        assert len(result) == 0

    def test_large_dataset_performance(self):
        """Test preprocessing on larger dataset."""
        # Create large dataset
        n_records = 10000
        df = pd.DataFrame({
            'CD_PEDIDO': [f'P{i:06d}' for i in range(n_records)],
            'CD_ITEM': ['1'] * n_records,
            'DT_ENTREGAORIGINAL': ['2024-01-01'] * n_records,
            'FL_SUSPOUCANCEL': ['0'] * n_records,
        })

        prep = TrainingPreprocessor(verbose=False)

        import time
        start = time.time()
        result = prep.preprocess(df)
        elapsed = time.time() - start

        # Should process reasonably fast (< 1 second for 10k records)
        assert elapsed < 1.0
        assert len(result) == n_records

    def test_missing_columns_handled_gracefully(self):
        """Test that missing columns don't cause errors."""
        df = pd.DataFrame({
            'CD_PEDIDO': ['P001', 'P002'],
            'CD_ITEM': ['1', '2'],
            # Missing many columns
        })

        prep = InferencePreprocessor(verbose=False)
        result = prep.preprocess(df)

        # Should not crash and should create CD_OP
        assert 'CD_OP' in result.columns
        assert len(result) == 2
