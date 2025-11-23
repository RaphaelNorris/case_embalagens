"""
Convenience exports for the DS pipelines so notebooks/apps can simply import
from :mod:`src.pipelines` instead of navigating through internal packages.
"""

from .DS.feature_pipeline import (
    FlexoDataSources,
    cluster_profile,
    compute_productivity_target,
    engineer_features,
    get_clustering_dataset,
    load_raw_sources,
)
from .DS.pipelines import (
    run_corte_pipeline,
    run_flexo_pipeline,
    run_pipeline,
)
from .DS.inference_pipeline import (
    InferenceArtifacts,
    predict_from_engineered_data,
    run_end_to_end_inference,
)
from .DS.training_pipeline import (
    ClassificationConfig,
    ClusteringConfig,
    TrainingArtifacts,
    run_training_pipeline,
)

__all__ = [
    "FlexoDataSources",
    "load_raw_sources",
    "engineer_features",
    "cluster_profile",
    "compute_productivity_target",
    "get_clustering_dataset",
    "ClusteringConfig",
    "ClassificationConfig",
    "TrainingArtifacts",
    "run_training_pipeline",
    "run_pipeline",
    "run_flexo_pipeline",
    "run_corte_pipeline",
    "InferenceArtifacts",
    "predict_from_engineered_data",
    "run_end_to_end_inference",
]
