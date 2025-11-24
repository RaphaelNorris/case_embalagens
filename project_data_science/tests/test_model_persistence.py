"""
Tests for model persistence module.

Tests saving and loading of ML models and artifacts.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler

from src.ml_artifacts.model_persistence import (
    save_model_artifacts,
    load_model_artifacts,
)


@pytest.fixture
def temp_model_dir():
    """Create temporary directory for models."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_classifier():
    """Create sample trained classifier."""
    X = np.random.rand(100, 5)
    y = np.random.randint(0, 2, 100)
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    return model


@pytest.fixture
def sample_regressor():
    """Create sample trained regressor."""
    X = np.random.rand(100, 5)
    y = np.random.rand(100)
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    model.fit(X, y)
    return model


@pytest.fixture
def sample_scaler():
    """Create sample fitted scaler."""
    X = np.random.rand(100, 5)
    scaler = StandardScaler()
    scaler.fit(X)
    return scaler


class TestSaveModelArtifacts:
    """Test saving model artifacts."""

    def test_save_classifier(self, temp_model_dir, sample_classifier):
        """Test saving a classifier model."""
        model_path = temp_model_dir / "test_classifier.pkl"

        selected_features = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']

        save_model_artifacts(
            model=sample_classifier,
            model_path=model_path,
            selected_features=selected_features,
            model_type='classification',
            task_type='classification',
        )

        # Check file was created
        assert model_path.exists()
        assert model_path.stat().st_size > 0

    def test_save_regressor(self, temp_model_dir, sample_regressor):
        """Test saving a regressor model."""
        model_path = temp_model_dir / "test_regressor.pkl"

        selected_features = ['feature1', 'feature2', 'feature3']

        save_model_artifacts(
            model=sample_regressor,
            model_path=model_path,
            selected_features=selected_features,
            model_type='regression',
            task_type='regression',
        )

        assert model_path.exists()

    def test_save_with_scaler(self, temp_model_dir, sample_classifier, sample_scaler):
        """Test saving model with scaler."""
        model_path = temp_model_dir / "test_with_scaler.pkl"

        selected_features = ['feature1', 'feature2']

        save_model_artifacts(
            model=sample_classifier,
            model_path=model_path,
            selected_features=selected_features,
            scaler=sample_scaler,
            model_type='classification',
            task_type='classification',
        )

        assert model_path.exists()

    def test_save_creates_directory(self, temp_model_dir, sample_classifier):
        """Test that save creates directory if it doesn't exist."""
        nested_path = temp_model_dir / "nested" / "dir" / "model.pkl"

        selected_features = ['feature1']

        save_model_artifacts(
            model=sample_classifier,
            model_path=nested_path,
            selected_features=selected_features,
            model_type='classification',
            task_type='classification',
        )

        assert nested_path.exists()
        assert nested_path.parent.exists()


class TestLoadModelArtifacts:
    """Test loading model artifacts."""

    def test_load_classifier(self, temp_model_dir, sample_classifier):
        """Test loading a saved classifier."""
        model_path = temp_model_dir / "classifier.pkl"
        selected_features = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']

        # Save first
        save_model_artifacts(
            model=sample_classifier,
            model_path=model_path,
            selected_features=selected_features,
            model_type='classification',
            task_type='classification',
        )

        # Load
        artifacts = load_model_artifacts(model_path)

        assert artifacts is not None
        assert 'model' in artifacts
        assert 'selected_features' in artifacts
        assert 'model_type' in artifacts
        assert artifacts['model_type'] == 'classification'
        assert len(artifacts['selected_features']) == 5

    def test_load_with_scaler(self, temp_model_dir, sample_classifier, sample_scaler):
        """Test loading model with scaler."""
        model_path = temp_model_dir / "with_scaler.pkl"
        selected_features = ['feature1', 'feature2']

        # Save with scaler
        save_model_artifacts(
            model=sample_classifier,
            model_path=model_path,
            selected_features=selected_features,
            scaler=sample_scaler,
            model_type='classification',
            task_type='classification',
        )

        # Load
        artifacts = load_model_artifacts(model_path)

        assert 'scaler' in artifacts
        assert artifacts['scaler'] is not None

    def test_load_nonexistent_file_raises_error(self, temp_model_dir):
        """Test that loading nonexistent file raises error."""
        nonexistent_path = temp_model_dir / "nonexistent.pkl"

        with pytest.raises(FileNotFoundError):
            load_model_artifacts(nonexistent_path)


class TestSaveLoadRoundtrip:
    """Test save-load roundtrip preserves model functionality."""

    def test_classifier_predictions_preserved(self, temp_model_dir, sample_classifier):
        """Test that classifier predictions are same after save/load."""
        model_path = temp_model_dir / "classifier.pkl"
        selected_features = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']

        # Get predictions before save
        X_test = np.random.rand(10, 5)
        predictions_before = sample_classifier.predict(X_test)

        # Save and load
        save_model_artifacts(
            model=sample_classifier,
            model_path=model_path,
            selected_features=selected_features,
            model_type='classification',
            task_type='classification',
        )

        artifacts = load_model_artifacts(model_path)
        loaded_model = artifacts['model']

        # Get predictions after load
        predictions_after = loaded_model.predict(X_test)

        # Should be identical
        assert np.array_equal(predictions_before, predictions_after)

    def test_regressor_predictions_preserved(self, temp_model_dir, sample_regressor):
        """Test that regressor predictions are same after save/load."""
        model_path = temp_model_dir / "regressor.pkl"
        selected_features = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']

        X_test = np.random.rand(10, 5)
        predictions_before = sample_regressor.predict(X_test)

        # Save and load
        save_model_artifacts(
            model=sample_regressor,
            model_path=model_path,
            selected_features=selected_features,
            model_type='regression',
            task_type='regression',
        )

        artifacts = load_model_artifacts(model_path)
        loaded_model = artifacts['model']

        predictions_after = loaded_model.predict(X_test)

        # Should be very close (accounting for floating point precision)
        assert np.allclose(predictions_before, predictions_after)

    def test_scaler_transform_preserved(self, temp_model_dir, sample_classifier, sample_scaler):
        """Test that scaler transform is preserved after save/load."""
        model_path = temp_model_dir / "with_scaler.pkl"
        selected_features = ['feature1', 'feature2']

        X_test = np.random.rand(10, 5)
        scaled_before = sample_scaler.transform(X_test)

        # Save and load
        save_model_artifacts(
            model=sample_classifier,
            model_path=model_path,
            selected_features=selected_features,
            scaler=sample_scaler,
            model_type='classification',
            task_type='classification',
        )

        artifacts = load_model_artifacts(model_path)
        loaded_scaler = artifacts['scaler']

        scaled_after = loaded_scaler.transform(X_test)

        # Should be identical
        assert np.allclose(scaled_before, scaled_after)


class TestMetadataStorage:
    """Test that metadata is correctly stored and retrieved."""

    def test_feature_names_preserved(self, temp_model_dir, sample_classifier):
        """Test that feature names are preserved."""
        model_path = temp_model_dir / "model.pkl"
        original_features = ['altura', 'largura', 'peso', 'volume', 'area']

        save_model_artifacts(
            model=sample_classifier,
            model_path=model_path,
            selected_features=original_features,
            model_type='classification',
            task_type='classification',
        )

        artifacts = load_model_artifacts(model_path)

        assert artifacts['selected_features'] == original_features

    def test_model_type_preserved(self, temp_model_dir, sample_regressor):
        """Test that model type is preserved."""
        model_path = temp_model_dir / "regressor.pkl"

        save_model_artifacts(
            model=sample_regressor,
            model_path=model_path,
            selected_features=['f1', 'f2'],
            model_type='random_forest',
            task_type='regression',
        )

        artifacts = load_model_artifacts(model_path)

        assert artifacts['model_type'] == 'random_forest'
        assert artifacts['task_type'] == 'regression'


# Performance tests
class TestPerformance:
    """Test performance characteristics."""

    def test_large_model_save_load(self, temp_model_dir):
        """Test saving/loading larger models is reasonably fast."""
        # Create larger random forest
        X = np.random.rand(1000, 50)
        y = np.random.randint(0, 2, 1000)
        large_model = RandomForestClassifier(n_estimators=100, random_state=42)
        large_model.fit(X, y)

        model_path = temp_model_dir / "large_model.pkl"
        features = [f'feature_{i}' for i in range(50)]

        import time

        # Test save performance
        start = time.time()
        save_model_artifacts(
            model=large_model,
            model_path=model_path,
            selected_features=features,
            model_type='classification',
            task_type='classification',
        )
        save_time = time.time() - start

        # Test load performance
        start = time.time()
        artifacts = load_model_artifacts(model_path)
        load_time = time.time() - start

        # Should be reasonably fast (< 5 seconds each)
        assert save_time < 5.0
        assert load_time < 5.0
