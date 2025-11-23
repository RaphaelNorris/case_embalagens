# Add this function to handle categorical encoding if needed
def preprocess_categorical_features(df, categorical_columns=None):
    """
    Preprocess categorical features by ensuring they're properly formatted for CatBoost.
    CatBoost can handle categorical features natively, but they need to be identified.
    """
    df_processed = df.copy()
    
    if categorical_columns is None:
        # Auto-detect categorical columns
        categorical_columns = []
        for col in df.columns:
            if df[col].dtype == 'object':
                categorical_columns.append(col)
            elif df[col].dtype in ['int64', 'float64']:
                # Check for mixed types that might be categorical
                sample_values = df[col].dropna().astype(str).head(100)
                if any(val.replace('.', '').replace('-', '').replace('+', '').isalpha() 
                       for val in sample_values if isinstance(val, str)):
                    categorical_columns.append(col)
    
    # Convert categorical columns to string type for CatBoost
    for col in categorical_columns:
        if col in df_processed.columns:
            df_processed[col] = df_processed[col].astype(str)
    
    return df_processed, categorical_columns
