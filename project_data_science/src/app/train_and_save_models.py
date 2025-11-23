"""
Model Training and Persistence Script
====================================

This script trains the production productivity models for both Flexo and
Corte/Vinco machines and saves them as pickle files for use in the Streamlit app.
"""

import pickle
from pathlib import Path
import sys

# Add src to path for imports
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pipelines.DS import pipelines

def train_and_save_models():
    """Train models for both machine types and save artifacts."""

    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    # Train Flexo model
    print("Training Flexo model...")
    try:
        flexo_artifacts = pipelines.run_flexo_pipeline(
            cluster_k=None,  # Auto-select best k
            productivity_quantile=0.6,
            classification_threshold=0.7,
            feature_selection_method="tree",
            feature_selection_params={"importance_threshold": 0.01},
            shap_sample_size=100,
            random_state=42
        )

        # Save Flexo model
        flexo_path = models_dir / "flexo_model_artifacts.pkl"
        with open(flexo_path, 'wb') as f:
            pickle.dump(flexo_artifacts, f)
        print(f"✅ Flexo model saved to {flexo_path}")

    except Exception as e:
        print(f"❌ Error training Flexo model: {e}")

    # Train Corte/Vinco model
    print("Training Corte/Vinco model...")
    try:
        cv_artifacts = pipelines.run_corte_pipeline(
            cluster_k=None,  # Auto-select best k
            productivity_quantile=0.6,
            classification_threshold=0.7,
            feature_selection_method="tree",
            feature_selection_params={"importance_threshold": 0.01},
            shap_sample_size=100,
            random_state=42
        )

        # Save CV model
        cv_path = models_dir / "cv_model_artifacts.pkl"
        with open(cv_path, 'wb') as f:
            pickle.dump(cv_artifacts, f)
        print(f"✅ Corte/Vinco model saved to {cv_path}")

    except Exception as e:
        print(f"❌ Error training Corte/Vinco model: {e}")

if __name__ == "__main__":
    train_and_save_models()
