"""
Visualization utilities for dashboards.
Contains reusable plotting functions.
"""

from typing import List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_status_distribution(
    df: pd.DataFrame,
    status_col: str = "STATUS_CODE",
    label_col: str = "STATUS_LABEL",
    title: str = "Distribuição por Status",
) -> go.Figure:
    """
    Create a bar plot for status distribution.

    Args:
        df: DataFrame with status data
        status_col: Column with status codes
        label_col: Column with status labels
        title: Plot title

    Returns:
        Plotly figure
    """
    status_counts = (
        df[status_col]
        .value_counts()
        .rename_axis(status_col)
        .reset_index(name="COUNT")
    )

    if label_col in df.columns:
        status_counts[label_col] = status_counts[status_col].map(
            df.set_index(status_col)[label_col].to_dict()
        )
        x_col = label_col
    else:
        x_col = status_col

    status_counts = status_counts.sort_values(by="COUNT", ascending=False)

    fig = px.bar(
        status_counts,
        x=x_col,
        y="COUNT",
        color=x_col,
        text="COUNT",
        title=title,
        labels={x_col: "Status", "COUNT": "Quantidade"},
    )
    fig.update_layout(
        template="plotly_white",
        height=450,
        xaxis={"categoryorder": "total descending"},
        showlegend=False,
    )
    fig.update_traces(textposition="outside")

    return fig


def plot_histogram(
    df: pd.DataFrame,
    column: str,
    title: str,
    xlabel: str = None,
    nbins: int = 50,
    marginal: Optional[str] = None,
) -> go.Figure:
    """
    Create a histogram with optional marginal plot.

    Args:
        df: DataFrame
        column: Column to plot
        title: Plot title
        xlabel: X-axis label
        nbins: Number of bins
        marginal: Type of marginal plot ('box', 'violin', 'rug')

    Returns:
        Plotly figure
    """
    fig = px.histogram(
        df,
        x=column,
        nbins=nbins,
        marginal=marginal,
        title=title,
        labels={column: xlabel or column},
        opacity=0.85,
    )
    fig.update_layout(template="plotly_white", height=450)
    fig.update_yaxes(title_text="Frequência")

    return fig


def plot_box_by_category(
    df: pd.DataFrame,
    category_col: str,
    value_col: str,
    title: str,
    xlabel: str = None,
    ylabel: str = None,
) -> go.Figure:
    """
    Create a box plot grouped by category.

    Args:
        df: DataFrame
        category_col: Column with categories
        value_col: Column with values
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label

    Returns:
        Plotly figure
    """
    fig = px.box(
        df,
        x=category_col,
        y=value_col,
        color=category_col,
        title=title,
        labels={
            category_col: xlabel or category_col,
            value_col: ylabel or value_col,
        },
    )
    fig.update_layout(template="plotly_white", height=450, showlegend=False)

    return fig


def plot_time_series(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    xlabel: str = None,
    ylabel: str = None,
) -> go.Figure:
    """
    Create a time series line plot with markers.

    Args:
        df: DataFrame
        x_col: X-axis column (time)
        y_col: Y-axis column (values)
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label

    Returns:
        Plotly figure
    """
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        markers=True,
        title=title,
        labels={x_col: xlabel or x_col, y_col: ylabel or y_col},
    )
    fig.update_layout(xaxis_tickangle=45, height=400, template="plotly_white")

    return fig


def plot_pareto(
    values: pd.Series,
    title: str,
    top_n: int = 50,
    cumsum_lines: List[int] = None,
) -> go.Figure:
    """
    Create a Pareto chart (bar + cumulative line).

    Args:
        values: Series with values (sorted descending)
        title: Plot title
        top_n: Number of top items to show
        cumsum_lines: List of cumulative percentages for reference lines

    Returns:
        Plotly figure
    """
    if cumsum_lines is None:
        cumsum_lines = [80, 95]

    # Calculate cumulative percentage
    total = values.sum()
    cumulative_pct = (values.cumsum() / total * 100)

    # Take top N
    values_top = values.head(top_n)
    cumulative_top = cumulative_pct.head(top_n)

    # Create subplot with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add bar chart
    fig.add_trace(
        go.Bar(
            x=values_top.index.astype(str),
            y=values_top.values,
            name="Count",
        ),
        secondary_y=False,
    )

    # Add cumulative line
    fig.add_trace(
        go.Scatter(
            x=values_top.index.astype(str),
            y=cumulative_top.values,
            name="% Cumulativo",
            mode="lines+markers",
            line=dict(color="red", width=2),
        ),
        secondary_y=True,
    )

    # Add reference lines
    for threshold in cumsum_lines:
        fig.add_shape(
            type="line",
            x0=values_top.index[0],
            y0=threshold,
            x1=values_top.index[-1],
            y1=threshold,
            line=dict(color="green", width=2, dash="dash"),
            yref="y2",
        )

    fig.update_layout(
        title=title,
        height=500,
        template="plotly_white",
        legend=dict(x=0.01, y=0.99),
    )

    fig.update_yaxes(title_text="Contagem", secondary_y=False)
    fig.update_yaxes(title_text="% Cumulativo", range=[0, 100], secondary_y=True)

    return fig


def plot_pie(
    values: List,
    names: List,
    title: str,
    hole: float = 0.4,
) -> go.Figure:
    """
    Create a pie/donut chart.

    Args:
        values: List of values
        names: List of labels
        title: Plot title
        hole: Size of hole (0 for pie, >0 for donut)

    Returns:
        Plotly figure
    """
    fig = px.pie(
        values=values,
        names=names,
        title=title,
        hole=hole,
    )
    fig.update_layout(height=400, template="plotly_white")

    return fig


def plot_3d_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    z_col: str,
    color_col: str = None,
    title: str = "3D Scatter Plot",
    sample_size: int = 1000,
) -> go.Figure:
    """
    Create a 3D scatter plot.

    Args:
        df: DataFrame
        x_col: X-axis column
        y_col: Y-axis column
        z_col: Z-axis column
        color_col: Column for color grouping
        title: Plot title
        sample_size: Max number of points to plot

    Returns:
        Plotly figure
    """
    # Sample if too large
    if len(df) > sample_size:
        df_plot = df.sample(sample_size)
    else:
        df_plot = df

    fig = px.scatter_3d(
        df_plot,
        x=x_col,
        y=y_col,
        z=z_col,
        color=color_col,
        title=title,
    )
    fig.update_layout(height=600, template="plotly_white")

    return fig
