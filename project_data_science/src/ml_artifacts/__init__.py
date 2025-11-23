"""
Model persistence module
=========================

This module provides utilities for saving and loading trained models.
"""

from .model_persistence import save_model_artifacts, load_model_artifacts

__all__ = [
    "save_model_artifacts",
    "load_model_artifacts",
]
