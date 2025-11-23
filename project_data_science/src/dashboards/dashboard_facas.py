import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------
# Configuração da página
# ---------------------------
st.set_page_config(
    page_title="Análise de Facas | Embalagens",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------
# Utilitários e constantes
# ---------------------------
DEFAULT_DATA_PATH = "../data/02 - trusted/parquet/tb_facas.parquet"

# Mapeamento segundo a documentação fornecida
STATUS_MAP = {
    "0": "N/A",
    "1": "Ativo",
    "2": "Suspenso",
    "4": "Reparo",
    "5": "Desmanchadas",
    "6": "Alteração",
    "7": "Alt. Não Realizada",
}

DESATIVADOSN_NORMALIZATION = {
    "Y": "Y", "Yes": "Y", "SIM": "Y", "Sim": "Y", "S": "Y",
    "N": "N", "No": "N", "NAO": "N", "Não": "N", "Nao": "N"
}

NUM_FMT = "{:,.0f}".format


def normalize_desativadosn(x):
    if pd.isna(x):
        return x
    x_str = str(x).strip()
    return DESATIVADOSN_NORMALIZATION.get(x_str, x_str)


def canonical_status_code(value):
    # Converte códigos como "5.0" ou 5.0 para "5" (string)
    if pd.isna(value):
        return "0"
    s = str(value).strip()
    try:
        f = float(s)
        i = int(f)
        return str(i)
    except Exception:
        # Mantém como string original, se não for numérico
        return s


def label_status(code):
    c = canonical_status_code(code)
    return STATUS_MAP.get(c, f"Código {c}")


def as_meters(series_mm):
    # Conversão mm -> m
    return series_mm / 1000.0


@st.cache_data(show_spinner=False)
def load_parquet(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    return df


@st.cache_data(show_spinner=False)
def load_parquet_from_bytes(_bytes: bytes) -> pd.DataFrame:
    buff = io.BytesIO(_bytes)
    df = pd.read_parquet(buff)
    return df


def preprocess_df(
    df: pd.DataFrame,
    fill_status_to_zero: bool = True,
    fill_complamina_to_zero: bool = True,
    convert_to_meters: bool = True,
):
    df = df.copy()

    # Colunas esperadas
    expected_cols = ["CODFACA", "STATUS", "COMPLAMINA", "DESATIVADOSN"]
    missing_cols = [c for c in expected_cols if c not in df.columns]
    if missing_cols:
        st.warning(f"Colunas ausentes no dataset: {missing_cols}. O app tentará funcionar com o que está disponível.")
        for c in missing_cols:
            df[c] = np.nan

    # STATUS: preencher NaN com 0 (opcional) e converter para string
    if fill_status_to_zero:
        df["STATUS"] = df["STATUS"].fillna(0)
    df["STATUS"] = df["STATUS"].astype(str)

    # Códigos e rótulos normalizados
    df["STATUS_CODE"] = df["STATUS"].apply(canonical_status_code)
    df["STATUS_LABEL"] = df["STATUS_CODE"].apply(lambda c: STATUS_MAP.get(c, f"Código {c}"))

    # DESATIVADOSN: normalização
    df["DESATIVADOSN"] = df["DESATIVADOSN"].apply(normalize_desativadosn)

    # COMPLAMINA: manter original, criar versão em metros
    df["COMPLAMINA_raw_mm"] = df["COMPLAMINA"]
    if fill_complamina_to_zero:
        df["COMPLAMINA"] = df["COMPLAMINA"].fillna(0)

    if convert_to_meters:
        df["COMPLAMINA_m"] = as_meters(df["COMPLAMINA"])
        df["COMPLAMINA_raw_m"] = as_meters(df["COMPLAMINA_raw_mm"])
    else:
        df["COMPLAMINA_m"] = df["COMPLAMINA"]
        df["COMPLAMINA_raw_m"] = df["COMPLAMINA_raw_mm"]

    # Flags de inconsistência segundo a documentação:
    # - Desmanchadas (5) deveriam estar desativadas (DESATIVADOSN = Y)
    # - Ativo (1) deveria estar ativo (DESATIVADOSN = N)
    df["flag_desmanchadas_com_N"] = (df["STATUS_CODE"] == "5") & (df["DESATIVADOSN"] != "Y")
    df["flag_ativo_com_Y"] = (df["STATUS_CODE"] == "1") & (df["DESATIVADOSN"] == "Y")

    return df


def kpi_metric(label, value, help_text=None):
    st.metric(label, value, help=help_text)


def build_status_distribution(df: pd.DataFrame):
    status_counts = df["STATUS_CODE"].value_counts().rename_axis("STATUS_CODE").reset_index(name="COUNT")
    status_counts["STATUS_LABEL"] = status_counts["STATUS_CODE"].apply(lambda c: STATUS_MAP.get(c, f"Código {c}"))
    status_counts = status_counts.sort_values(by="COUNT", ascending=False)

    fig = px.bar(
        status_counts,
        x="STATUS_LABEL",
        y="COUNT",
        color="STATUS_LABEL",
        text="COUNT",
        title="Distribuição por Status de Facas",
        labels={"STATUS_LABEL": "Status", "COUNT": "Quantidade"},
    )
    fig.update_layout(template="plotly_white", height=450, xaxis={"categoryorder": "total descending"})
    fig.update_traces(textposition="outside")
    return fig


def build_hist_length(df: pd.DataFrame, length_col: str, title: str = "Distribuição Geral do Comprimento da Lâmina"):
    fig = px.histogram(
        df,
        x=length_col,
        nbins=50,
        marginal="box",
        title=title,
        labels={length_col: "Comprimento da Lâmina"},
        opacity=0.85,
    )
    fig.update_layout(template="plotly_white", height=450)
    fig.update_xaxes(title_text="Comprimento da Lâmina")
    fig.update_yaxes(title_text="Frequência")
    return fig


def build_box_by_status(df: pd.DataFrame, length_col: str):
    fig = px.box(
        df,
        x="STATUS_LABEL",
        y=length_col,
        color="STATUS_LABEL",
        title="Distribuição do Comprimento da Lâmina por Status",
        labels={"STATUS_LABEL": "Status", length_col: "Comprimento da Lâmina"},
    )
    fig.update_layout(template="plotly_white", height=450)
    fig.update_xaxes(title_text="Status")
    fig.update_yaxes(title_text="Comprimento da Lâmina")
    return fig


def build_hist_by_status(df: pd.DataFrame, length_col: str):
    fig = px.histogram(
        df,
        x=length_col,
        color="STATUS_LABEL",
        nbins=50,
        opacity=0.7,
        title="Histograma do Comprimento da Lâmina por Status",
        labels={length_col: "Comprimento da Lâmina", "STATUS_LABEL": "Status"},
    )
    fig.update_layout(template="plotly_white", height=450, barmode="overlay")
    return fig


def build_box_by_desativado(df: pd.DataFrame, length_col: str):
    fig = px.box(
        df,
        x="DESATIVADOSN",
        y=length_col,
        color="DESATIVADOSN",
        title="Distribuição do Comprimento da Lâmina por Status de Desativação",
        labels={"DESATIVADOSN": "Desativado (S/N)", length_col: "Comprimento da Lâmina"},
    )
    fig.update_layout(template="plotly_white", height=450)
    fig.update_xaxes(title_text="Desativado (S/N)")
    fig.update_yaxes(title_text="Comprimento da Lâmina")
    return fig


def build_hist_by_desativado(df: pd.DataFrame, length_col: str):
    fig = px.histogram(
        df,
        x=length_col,
        color="DESATIVADOSN",
        nbins=50,
        opacity=0.7,
        title="Histograma do Comprimento da Lâmina por Status de Desativação",
        labels={length_col: "Comprimento da Lâmina", "DESATIVADOSN": "Desativado (S/N)"},
    )
    fig.update_layout(template="plotly_white", height=450, barmode="overlay")
    return fig


def build_box_status_desativado(df: pd.DataFrame, length_col: str):
    fig = px.box(
        df,
        x="STATUS_LABEL",
        y=length_col,
        color="DESATIVADOSN",
        title="Distribuição do Comprimento da Lâmina por Status e Desativação",
        labels={"STATUS_LABEL": "Status", length_col: "Comprimento da Lâmina", "DESATIVADOSN": "Desativado (S/N)"},
    )
    fig.update_layout(template="plotly_white", height=500, boxmode="group")
    fig.update_xaxes(title_text="Status")
    fig.update_yaxes(title_text="Comprimento da Lâmina")
    return fig


def stats_by_groups(df: pd.DataFrame, length_col: str):
    stats_status = df.groupby("STATUS_LABEL")[length_col].describe().reset_index()
    stats_desativado = df.groupby("DESATIVADOSN")[length_col].describe().reset_index()
    stats_combined = df.groupby(["STATUS_LABEL", "DESATIVADOSN"])[length_col].describe().reset_index()
    return stats_status, stats_desativado, stats_combined


def build_inconsistency_tables(df: pd.DataFrame):
    inco_desmanchadas_N = df.loc[df["flag_desmanchadas_com_N"], ["CODFACA", "STATUS", "STATUS_CODE", "STATUS_LABEL", "DESATIVADOSN", "COMPLAMINA_raw_mm", "COMPLAMINA_raw_m"]]
    inco_ativo_Y = df.loc[df["flag_ativo_com_Y"], ["CODFACA", "STATUS", "STATUS_CODE", "STATUS_LABEL", "DESATIVADOSN",
                                                   "COMPLAMINA_raw_mm", "COMPLAMINA_raw_m"]]
    return inco_desmanchadas_N, inco_ativo_Y


def filter_df(
    df: pd.DataFrame,
    statuses: list,
    desativadosn_values: list,
    length_col: str,
    length_range: tuple,
    codfaca_query: str,
):
    filtered = df.copy()
    if statuses:
        filtered = filtered[filtered["STATUS_LABEL"].isin(statuses)]
    if desativadosn_values:
        filtered = filtered[filtered["DESATIVADOSN"].isin(desativadosn_values)]
    if length_range and length_col in filtered.columns:
        min_len, max_len = length_range
        filtered = filtered[(filtered[length_col] >= min_len) & (filtered[length_col] <= max_len)]
    if codfaca_query:
        q = codfaca_query.strip().lower()
        filtered = filtered[filtered["CODFACA"].astype(str).str.lower().str.contains(q)]
    return filtered


def main():
    st.title("Análise de Facas | Embalagens de Grande Porte")
    st.caption("App interativo baseado na EDA do notebook 03.nb_eda_facas.ipynb, com mapeamento de status atualizado.")

    # Sidebar: fonte de dados
    st.sidebar.header("Fonte de Dados")
    data_source = st.sidebar.radio(
        "Selecione a origem dos dados",
        options=["Caminho padrão", "Upload de arquivo (parquet)"],
        index=0,
    )

    df_raw = None
    if data_source == "Caminho padrão":
        st.sidebar.text_input("Caminho do parquet", value=DEFAULT_DATA_PATH, key="data_path")
        try:
            df_raw = load_parquet(st.session_state.get("data_path", DEFAULT_DATA_PATH))
            st.sidebar.success("Parquet carregado com sucesso.")
        except Exception as e:
            st.sidebar.error(f"Erro ao carregar parquet: {e}")
    else:
        uploaded = st.sidebar.file_uploader("Enviar arquivo .parquet", type=["parquet"])
        if uploaded is not None:
            try:
                df_raw = load_parquet_from_bytes(uploaded.getvalue())
                st.sidebar.success("Parquet carregado com sucesso.")
            except Exception as e:
                st.sidebar.error(f"Erro ao ler arquivo enviado: {e}")

    if df_raw is None or df_raw.empty:
        st.warning("Nenhum dado carregado. Selecione uma fonte válida de dados.")
        st.stop()

    # Sidebar: opções de pré-processamento
    st.sidebar.header("Pré-processamento")
    opt_fill_status_zero = st.sidebar.checkbox("Preencher STATUS ausente com 0 (N/A)", value=True)
    opt_fill_complamina_zero = st.sidebar.checkbox("Preencher COMPLAMINA ausente com 0 (apenas coluna tratada)", value=True)
    opt_convert_meters = st.sidebar.checkbox("Converter comprimento de mm para m", value=True)

    # Preprocessamento
    df = preprocess_df(
        df_raw,
        fill_status_to_zero=opt_fill_status_zero,
        fill_complamina_to_zero=opt_fill_complamina_zero,
        convert_to_meters=opt_convert_meters,
    )

    # Seleção da coluna de comprimento para análises
    st.sidebar.header("Configuração de Medida")
    length_col_option = st.sidebar.selectbox(
        "Coluna de comprimento",
        options=[
            ("COMPLAMINA_m", "Comprimento (m) tratado"),
            ("COMPLAMINA_raw_m", "Comprimento (m) original"),
            ("COMPLAMINA", "Comprimento (mm) tratado"),
            ("COMPLAMINA_raw_mm", "Comprimento (mm) original"),
        ],
        format_func=lambda x: x[1],
        index=0 if opt_convert_meters else 2,
    )
    length_col = length_col_option[0]

    # KPIs iniciais
    total_registros = df.shape[0]
    facas_unicas = df["CODFACA"].astype(str).nunique()
    status_unicos = df["STATUS_LABEL"].nunique()
    desativados_unicos = df["DESATIVADOSN"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_metric("Total de registros", NUM_FMT(total_registros))
    with col2:
        kpi_metric("Facas únicas", NUM_FMT(facas_unicas))
    with col3:
        kpi_metric("Status únicos", NUM_FMT(status_unicos))
    with col4:
        kpi_metric("Valores distintos de DESATIVADOSN", NUM_FMT(desativados_unicos))

    inco_desmanchadas_N_df, inco_ativo_Y_df = build_inconsistency_tables(df)
    n_inco_desmanchadas_N = inco_desmanchadas_N_df.shape[0]
    n_inco_ativo_Y = inco_ativo_Y_df.shape[0]

    if n_inco_desmanchadas_N > 0 or n_inco_ativo_Y > 0:
        st.info(
            f"Inconsistências detectadas: Desmanchadas com N = {n_inco_desmanchadas_N} | Ativo com Y = {n_inco_ativo_Y}. "
            "Revise os registros abaixo na seção 'Qualidade de Dados'."
        )

    # Filtros
    st.subheader("Filtros")
    col_f1, col_f2, col_f3, col_f4 = st.columns([1.2, 1.2, 2, 1.2])

    with col_f1:
        status_opts = sorted(df["STATUS_LABEL"].dropna().unique().tolist())
        selected_status = st.multiselect("Status", status_opts, default=[])
    with col_f2:
        desat_opts = sorted(df["DESATIVADOSN"].dropna().unique().tolist())
        selected_desat = st.multiselect("Desativado (S/N)", desat_opts, default=[])
    with col_f3:
        # Trata min/max sem falhar caso haja NaN
        valid_vals = df[length_col].dropna()
        if valid_vals.empty:
            min_len, max_len = 0.0, 0.0
        else:
            min_len = float(np.nanmin(valid_vals))
            max_len = float(np.nanmax(valid_vals))
        step_val = 0.001 if ("_m" in length_col) else 1.0
        selected_range = st.slider(
            "Faixa de comprimento",
            min_value=min_len,
            max_value=max_len,
            value=(min_len, max_len),
            step=step_val,
        )
    with col_f4:
        codfaca_query = st.text_input("Buscar CODFACA (contém)")

    df_filtered = filter_df(
        df,
        statuses=selected_status,
        desativadosn_values=selected_desat,
        length_col=length_col,
        length_range=selected_range,
        codfaca_query=codfaca_query,
    )

    st.caption(f"Registros filtrados: {df_filtered.shape[0]} de {df.shape[0]}")

    # Visualizações principais
    st.subheader("Distribuições e Comparativos")

    vcol1, vcol2 = st.columns(2)
    with vcol1:
        st.plotly_chart(build_status_distribution(df_filtered), use_container_width=True)
    with vcol2:
        st.plotly_chart(build_hist_length(df_filtered, length_col), use_container_width=True)

    vcol3, vcol4 = st.columns(2)
    with vcol3:
        st.plotly_chart(build_box_by_status(df_filtered, length_col), use_container_width=True)
    with vcol4:
        st.plotly_chart(build_hist_by_status(df_filtered, length_col), use_container_width=True)

    vcol5, vcol6 = st.columns(2)
    with vcol5:
        st.plotly_chart(build_box_by_desativado(df_filtered, length_col), use_container_width=True)
    with vcol6:
        st.plotly_chart(build_hist_by_desativado(df_filtered, length_col), use_container_width=True)

    vcol7, _ = st.columns([2, 1])
    with vcol7:
        st.plotly_chart(build_box_status_desativado(df_filtered, length_col), use_container_width=True)

    # Estatísticas descritivas
    st.subheader("Estatísticas Descritivas por Grupo")
    stats_status, stats_desativado, stats_combined = stats_by_groups(df_filtered, length_col)
    stab1, stab2 = st.columns(2)
    with stab1:
        st.markdown("Estatísticas por Status")
        st.dataframe(stats_status, use_container_width=True)
    with stab2:
        st.markdown("Estatísticas por Desativação (S/N)")
        st.dataframe(stats_desativado, use_container_width=True)

    st.markdown("Estatísticas por Status e Desativação")
    st.dataframe(stats_combined, use_container_width=True)
    import json

    # Adicione esta função utilitária para tornar DataFrames compatíveis com Arrow/Streamlit:
    def arrow_safe_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Converte colunas de dtype 'object' e tipos mistos para formatos compatíveis com PyArrow,
        evitando erros em st.dataframe/to_parquet.
        - Converte colunas com listas/dicts/tuplas para strings (JSON).
        - Tenta converter objetos numéricos para float/int.
        - Demais objetos viram strings.
        """
        df = df.copy()

        def is_non_scalar(v):
            return isinstance(v, (list, dict, set, tuple))

        for col in df.columns:
            s = df[col]
            if pd.api.types.is_object_dtype(s):
                # Se houver qualquer valor não escalar (lista/dict/tupla), serialize para string
                if s.apply(is_non_scalar).any():
                    df[col] = s.apply(lambda v: json.dumps(v, ensure_ascii=False) if is_non_scalar(v) else ("" if pd.isna(v) else str(v)))
                    continue

                # Tenta converter para numérico quando possível
                numeric_try = pd.to_numeric(s, errors="coerce")
                if numeric_try.notna().sum() == s.notna().sum():
                    # Todos valores não-nulos eram numéricos -> manter como numérico
                    df[col] = numeric_try
                else:
                    # Caso contrário, força string
                    df[col] = s.astype(str)
            elif pd.api.types.is_string_dtype(s):
                df[col] = s.astype(str)
            # dtypes numéricos/booleanos/datetime já são compatíveis

        return df

    # Qualidade de Dados e inconsistências
    st.subheader("Qualidade de Dados")
    st.markdown("Registros 'Desmanchadas' com DESATIVADOSN diferente de 'Y'")
    st.dataframe(arrow_safe_df(inco_desmanchadas_N_df), use_container_width=True, hide_index=True)

    st.markdown("Registros 'Ativo' com DESATIVADOSN = 'Y'")
    st.dataframe(arrow_safe_df(inco_ativo_Y_df), use_container_width=True, hide_index=True)

    # Tabela de dados filtrados
    st.subheader("Dados (Filtrados)")
    show_cols = [
        "CODFACA", "STATUS", "STATUS_CODE", "STATUS_LABEL", "DESATIVADOSN",
        "COMPLAMINA_raw_mm", "COMPLAMINA_raw_m", "COMPLAMINA", "COMPLAMINA_m"
    ]
    existing_cols = [c for c in show_cols if c in df_filtered.columns]
    st.dataframe(arrow_safe_df(df_filtered[existing_cols]), use_container_width=True, hide_index=True)

    # Downloads
    st.subheader("Exportar")
    csv_bytes = df_filtered[existing_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Baixar CSV (filtrado)",
        data=csv_bytes,
        file_name="tb_facas_filtrado.csv",
        mime="text/csv",
    )
    try:
        import pyarrow as pa  # noqa
        import pyarrow.parquet as pq  # noqa
        parquet_buf = io.BytesIO()
        df_filtered[existing_cols].to_parquet(parquet_buf, index=False)
        st.download_button(
            label="Baixar Parquet (filtrado)",
            data=parquet_buf.getvalue(),
            file_name="tb_facas_filtrado.parquet",
            mime="application/octet-stream",
        )
    except Exception:
        st.caption("PyArrow não disponível. Instale 'pyarrow' para exportar em Parquet.")


if __name__ == "__main__":
    main()