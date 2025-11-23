"""
Utility functions for the Streamlit app
======================================

Helper functions for data processing, visualization, and model interaction.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
import streamlit as st

def validate_input_data(df: pd.DataFrame, machine_type: str) -> tuple[bool, List[str]]:
    """
    Validate input data for prediction.

    Parameters
    ----------
    df : pd.DataFrame
        Input data to validate
    machine_type : str
        Type of machine ('flexo' or 'cv')

    Returns
    -------
    tuple[bool, List[str]]
        (is_valid, list_of_errors)
    """
    errors = []

    # Required columns
    required_cols = [
        'CD_OP', 'CD_PEDIDO', 'CD_ITEM', 'VL_COMPRIMENTO', 'VL_LARGURA',
        'VL_GRAMATURA', 'QT_PEDIDA'
    ]

    # Check for missing required columns
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        errors.append(f"Colunas obrigatórias ausentes: {', '.join(missing_cols)}")

    # Check for negative values in numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col in df.columns and (df[col] < 0).any():
            errors.append(f"Valores negativos encontrados na coluna: {col}")

    # Check for zero dimensions
    dimension_cols = ['VL_COMPRIMENTO', 'VL_LARGURA']
    for col in dimension_cols:
        if col in df.columns and (df[col] <= 0).any():
            errors.append(f"Dimensões devem ser maiores que zero: {col}")

    return len(errors) == 0, errors

def create_prediction_gauge(probability: float, threshold: float = 0.7) -> go.Figure:
    """
    Create a gauge chart for prediction probability.

    Parameters
    ----------
    probability : float
        Prediction probability (0-1)
    threshold : float
        Threshold for high productivity classification

    Returns
    -------
    go.Figure
        Plotly gauge figure
    """
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = probability * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Probabilidade de Alta Produtividade (%)"},
        delta = {'reference': threshold * 100},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, threshold * 100], 'color': "yellow"},
                {'range': [threshold * 100, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': threshold * 100
            }
        }
    ))

    fig.update_layout(
        height=300,
        font={'color': "darkblue", 'family': "Arial"}
    )

    return fig

def create_feature_importance_chart(features: List[tuple], title: str = "Feature Importance") -> go.Figure:
    """
    Create a horizontal bar chart for feature importance.

    Parameters
    ----------
    features : List[tuple]
        List of (feature_name, importance_value) tuples
    title : str
        Chart title

    Returns
    -------
    go.Figure
        Plotly bar figure
    """
    if not features:
        return go.Figure()

    feature_names, importance_values = zip(*features)

    # Create color scale based on positive/negative values
    colors = ['red' if val < 0 else 'green' for val in importance_values]

    fig = go.Figure(go.Bar(
        x=list(importance_values),
        y=list(feature_names),
        orientation='h',
        marker_color=colors,
        text=[f'{val:.3f}' for val in importance_values],
        textposition='auto',
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Impacto na Predição",
        yaxis_title="Features",
        height=max(300, len(features) * 30),
        showlegend=False
    )

    return fig

def create_cluster_probability_chart(cluster_probs: List[float]) -> go.Figure:
    """
    Create a bar chart for cluster probabilities.

    Parameters
    ----------
    cluster_probs : List[float]
        List of cluster probabilities

    Returns
    -------
    go.Figure
        Plotly bar figure
    """
    cluster_names = [f"Cluster {i}" for i in range(len(cluster_probs))]

    fig = px.bar(
        x=cluster_names,
        y=cluster_probs,
        title="Probabilidade de Pertencimento aos Clusters",
        labels={'x': 'Cluster', 'y': 'Probabilidade'},
        color=cluster_probs,
        color_continuous_scale='viridis'
    )

    fig.update_layout(height=400)
    return fig

def format_prediction_summary(results: pd.DataFrame) -> Dict[str, Any]:
    """
    Create a summary of prediction results.

    Parameters
    ----------
    results : pd.DataFrame
        Prediction results dataframe

    Returns
    -------
    Dict[str, Any]
        Summary statistics
    """
    total_predictions = len(results)
    high_productivity = (results['classe_prevista'] == 1).sum()
    low_productivity = total_predictions - high_productivity
    avg_probability = results['prob_produtivo'].mean()

    return {
        'total_predictions': total_predictions,
        'high_productivity': high_productivity,
        'low_productivity': low_productivity,
        'high_productivity_pct': high_productivity / total_predictions * 100,
        'avg_probability': avg_probability,
        'avg_probability_pct': avg_probability * 100
    }

@st.cache_data
def load_sample_csv_template(machine_type: str) -> pd.DataFrame:
    """
    Create a sample CSV template for download.

    Parameters
    ----------
    machine_type : str
        Type of machine ('flexo' or 'cv')

    Returns
    -------
    pd.DataFrame
        Sample data template
    """
    from .config import DEFAULT_VALUES

    defaults = DEFAULT_VALUES[machine_type]

    # Create multiple sample rows
    sample_data = []
    for i in range(3):
        row = defaults.copy()
        row['CD_PEDIDO'] = defaults['CD_PEDIDO'] + i
        row['CD_OP'] = f"{row['CD_PEDIDO']}/{row['CD_ITEM']}"
        sample_data.append(row)

    return pd.DataFrame(sample_data)

def export_results_to_excel(results: pd.DataFrame, machine_type: str) -> bytes:
    """
    Export results to Excel format.

    Parameters
    ----------
    results : pd.DataFrame
        Prediction results
    machine_type : str
        Type of machine

    Returns
    -------
    bytes
        Excel file as bytes
    """
    from io import BytesIO
    import pandas as pd

    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Main results
        results.to_excel(writer, sheet_name='Predictions', index=False)

        # Summary sheet
        summary = format_prediction_summary(results)
        summary_df = pd.DataFrame([summary])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

    return output.getvalue()
