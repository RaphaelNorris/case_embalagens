# Add this import at the top
from .preprocessing import preprocess_categorical_features

# Modify the run_pipeline function around line 280-320
def run_pipeline(
    machine_type="flexo",
    raw_dir=None,
    ml_dir=None,
    pedidos_df=None,
    pedidos_cutoff=None,
    cluster_k=None,
    cluster_range=None,
    exclude_features=None,
    productivity_quantile=0.8,
    classification_threshold=0.7,
    feature_selection_method="mutual_info",
    feature_selection_params=None,
    model_type="catboost",
    task_type="regression",
    shap_sample_size=100,
    random_state=42,
    save_model=False,
    model_dir=None,
    model_name=None,
):
    # ... existing code until feature selection ...
    
    # After feature selection and before model training, add:
    
    # 13. Preprocess categorical features
    X_train_processed, categorical_features = preprocess_categorical_features(X_train_final)
    
    # 14. Train model
    if task_type == "classification":
        from pipelines.DS.training import train_classifier
        estimator, metrics = train_classifier(
            X=X_train_processed,
            y=y_binary,
            model_type=model_type,
            test_size=0.2,
            random_state=random_state,
        )
        model_key = "classifier"
    else:
        from pipelines.DS.training import train_regressor
        estimator, metrics = train_regressor(
            X=X_train_processed,
            y=y,
            model_type=model_type,
            test_size=0.2,
            random_state=random_state,
        )
        model_key = "regressor"
    
    # ... rest of the function ...
    
    # Update the results dictionary to include processed data
    results = {
        "df": df_model,
        "X_train": X_train_processed,  # Use processed data
        "y": y,
        "selected_features": selected_features,
        "categorical_features": categorical_features,  # Add this
        model_key: estimator,
        "metrics": metrics,
        "feature_importance": feature_importance_df,
        "shap_values": shap_values,
        "shap_expected_value": shap_expected_value,
    }
    
    return results
