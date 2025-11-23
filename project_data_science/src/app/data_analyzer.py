"""
Streamlit data exploration helpers.

Provides lightweight exploratory widgets so the Streamlit app can
summarise, filter and visualise the pedidos dataset without needing to
open notebooks.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
import streamlit as st
from pandas.api.types import is_datetime64_any_dtype


def _format_number(value: float | int) -> str:
    if value >= 1_000_000:
        return f"{value/1_000_000:,.1f}M"
    if value >= 1_000:
        return f"{value/1_000:,.1f}k"
    return f"{value:,}"


def _render_histogram(data: pd.Series, bins: int = 25) -> None:
    numeric = pd.to_numeric(data, errors="coerce").dropna()
    if numeric.empty:
        st.info("Não há valores numéricos suficientes para o histograma.")
        return
    hist, bin_edges = np.histogram(numeric, bins=bins)
    chart_df = pd.DataFrame({"bin": bin_edges[:-1], "freq": hist})
    st.bar_chart(chart_df.set_index("bin"))


def _render_bar_counts(data: pd.Series, top_k: int = 15) -> None:
    counts = data.value_counts(dropna=False).head(top_k)
    chart_df = counts.rename_axis("categoria").reset_index(name="freq")
    st.bar_chart(chart_df.set_index("categoria"))


def create_data_explorer_tab(df: pd.DataFrame) -> None:
    """Render the data explorer inside the Streamlit tab."""
    if df is None or df.empty:
        st.warning("Nenhum dado disponível para explorar.")
        return

    st.subheader("📊 Explorador de Dados")

    total_rows = len(df)
    total_columns = df.shape[1]
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()
    datetime_cols = [
        col for col in df.columns if is_datetime64_any_dtype(df[col])
    ]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Registros", _format_number(total_rows))
    with col2:
        st.metric("Colunas", total_columns)
    with col3:
        st.metric("Features numéricas", len(numeric_cols))

    if datetime_cols:
        min_date = df[datetime_cols[0]].min()
        max_date = df[datetime_cols[0]].max()
        st.info(
            f"Período disponível ({datetime_cols[0]}): {min_date:%Y-%m-%d} → {max_date:%Y-%m-%d}"
        )

    st.markdown("### 🔎 Pré-visualização")
    default_preview_cols: Iterable[str] = list(df.columns[:10])
    preview_cols = st.multiselect(
        "Selecione colunas para visualizar",
        options=df.columns.tolist(),
        default=[],
    )
    if preview_cols:
        st.dataframe(df[preview_cols].head(100))
    else:
        st.info("Selecione colunas acima para visualizar a prévia.")

    with st.expander("📈 Estatísticas Numéricas"):
        if numeric_cols:
            st.dataframe(df[numeric_cols].describe().T)
        else:
            st.write("Sem colunas numéricas disponíveis.")

    with st.expander("🔢 Distribuição de Variáveis"):
        tabs = st.tabs(["Numéricas", "Categóricas"])
        with tabs[0]:
            if numeric_cols:
                selected_num = st.selectbox(
                    "Escolha uma coluna numérica", options=numeric_cols
                )
                _render_histogram(df[selected_num])
            else:
                st.write("Não há colunas numéricas.")

        with tabs[1]:
            if categorical_cols:
                selected_cat = st.selectbox(
                    "Escolha uma coluna categórica", options=categorical_cols
                )
                _render_bar_counts(df[selected_cat])
            else:
                st.write("Não há colunas categóricas.")

    if len(numeric_cols) >= 2:
        with st.expander("🧮 Correlação (Pearson)"):
            corr_matrix = df[numeric_cols].corr()
            st.dataframe(corr_matrix.style.background_gradient(cmap="Blues"))


__all__ = ["create_data_explorer_tab"]
