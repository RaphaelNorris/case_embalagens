"""
Example: Load and Use Saved Model
==================================

This script demonstrates how to load a saved model and use it for predictions.
"""

import sys
from pathlib import Path

# Add src to path
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from model import load_model_artifacts
from pipelines.DS import inference


def load_and_predict_example():
    """Example of loading a saved model and making predictions."""

    # 1. Specify the model directory
    model_dir = Path(__file__).parent / "cv_catboost_v1_20251116_234515"

    if not model_dir.exists():
        print(f"Model directory not found: {model_dir}")
        print("Please run the pipeline with save_model=True first.")
        return

    # 2. Load the model artifacts
    print(f"Loading model from: {model_dir}")
    artifacts = load_model_artifacts(model_dir)

    # 3. Display model information
    print("\n=== Model Information ===")
    metadata = artifacts.get("metadata", {})
    print(f"Machine Type: {metadata.get('machine_type')}")
    print(f"Model Type: {metadata.get('model_type')}")
    print(f"Timestamp: {metadata.get('timestamp')}")
    print(f"Number of Clusters: {metadata.get('cluster_k')}")
    print(f"ROC AUC: {metadata.get('roc_auc'):.4f}")
    print(f"Threshold: {metadata.get('threshold')}")
    print(f"Number of Features: {metadata.get('n_features')}")

    # 4. Display selected features
    print("\n=== Selected Features ===")
    selected_features = artifacts.get("selected_features", [])
    print(f"Total: {len(selected_features)} features")
    for i, feat in enumerate(selected_features[:10], 1):
        print(f"  {i:2d}. {feat}")
    if len(selected_features) > 10:
        print(f"  ... and {len(selected_features) - 10} more")

    # 5. Display feature importance
    print("\n=== Top 10 Most Important Features ===")
    feature_importance = artifacts.get("feature_importance")
    if feature_importance is not None:
        for feat, imp in feature_importance.head(10).items():
            print(f"  {feat:30s}: {imp:.4f}")

    # 6. Reconstruct clustering artifacts for inference
    # Create a simple namespace to hold the required attributes
    from types import SimpleNamespace

    clustering_artifacts = SimpleNamespace(
        scaler=artifacts["scaler"],
        pca=artifacts["pca"],
    )

    # 7. Example: Make predictions on new data
    # In a real scenario, you would load actual new data here
    # For this example, we'll just show the structure

    print("\n=== Ready for Predictions ===")
    print("To make predictions, use:")
    print("  predictions = inference.predict_new_data(")
    print("      df_new=your_new_data,")
    print("      gmm=artifacts['gmm'],")
    print("      classifier=artifacts['classifier'],")
    print("      clustering_artifacts=clustering_artifacts,")
    print("      selected_features=artifacts['selected_features'],")
    print("      artefacts={'metrics': artifacts['metrics']},")
    print("  )")

    return artifacts


if __name__ == "__main__":
    artifacts = load_and_predict_example()
