"""
Throughput Regression App (m³/h)
================================

Streamlit interface focada em estimar o volume físico produzido por hora
nas linhas Flexo e Corte/Vinco, a partir das dimensões e parâmetros do pedido.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle
from pathlib import Path
import sys
from typing import Dict, Any, Optional
import json

# Add src to path for imports
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from pipelines.DS import inference, config
    PIPELINE_AVAILABLE = True
except ImportError as e:
    st.error(f"Pipeline não disponível: {str(e)}")
    PIPELINE_AVAILABLE = False

from openai_insights import (
    ProductivityInsightsGenerator,
    get_openai_insights_component,
    display_ai_insights,
    display_batch_ai_insights,
)

try:
    from app.data_analyzer import create_data_explorer_tab as _create_data_explorer_tab
except ImportError as import_error:
    _create_data_explorer_tab = None
    DATA_EXPLORER_AVAILABLE = False
    DATA_EXPLORER_IMPORT_ERROR = str(import_error)
else:
    DATA_EXPLORER_AVAILABLE = True
    DATA_EXPLORER_IMPORT_ERROR = ""

AUTH_USERS = {
    "adami": "adami123",
    "amcom": "amcom123",
}

# Page configuration
st.set_page_config(
    page_title="Regressão de Volume por Hora - Adami",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .prediction-high {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .prediction-low {
        background: linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .feature-importance {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .ai-insights {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .data-selector {
        background: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #1f1f1f;
        border: 1px solid #d7dbe0;
    }
    .pipeline-status {
        background: #e8f5e8;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .pipeline-error {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_pedidos_data():
    """Load pedidos data from parquet file."""
    try:
        data_path = Path(
            "/home/adami/Projeto_IA_AMCOM/project_data_science/data/raw/tb_pedidos.parquet"
        )
        if data_path.exists():
            df = pd.read_parquet(data_path)
            st.success(f"Dados carregados: {len(df):,} pedidos encontrados")
            return df
        else:
            st.error("Arquivo tb_pedidos.parquet não encontrado em data/processed/")
            return None
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None

@st.cache_resource
def load_trained_models():
    """Load trained models using the pipeline."""
    if not PIPELINE_AVAILABLE:
        st.error("Pipeline não disponível. Não é possível carregar modelos.")
        return {}

    models: Dict[str, Optional[Dict[str, Any]]] = {}
    project_root = Path(__file__).resolve().parents[2]
    search_dirs = [
        project_root / "src" / "model",
        project_root / "model",
        project_root / "models",
        Path("models"),
    ]

    for machine_type in ["flexo", "cv"]:
        candidate_paths = [
            directory / f"{machine_type}_model_artifacts.pkl"
            for directory in search_dirs
        ]
        model_path = next((p for p in candidate_paths if p.exists()), None)

        if model_path is None:
            st.error(
                f"Modelo {machine_type} não encontrado nos diretórios pesquisados."
            )
            st.info(
                f"Busquei em: {', '.join(str(p.parent) for p in candidate_paths)}"
            )
            models[machine_type] = None
            continue

        resolved_dir = model_path.parent
        if resolved_dir.name != "models":
            st.info(
                f"Modelo {machine_type} carregado de diretório alternativo: {resolved_dir}"
            )

        if model_path.exists():
            try:
                with open(model_path, "rb") as f:
                    artifacts = pickle.load(f)

                task_type = str(artifacts.get("task_type", "classification")).lower()
                if task_type != "regression":
                    st.warning(
                        f"Artefato {machine_type} encontrado, porém configurado para '{task_type}'. "
                        "Execute o pipeline em modo regressão para habilitar este app."
                    )
                    models[machine_type] = None
                    continue

                models[machine_type] = artifacts
                st.success(f"Modelo de regressão {machine_type} carregado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao carregar modelo {machine_type}: {str(e)}")
                models[machine_type] = None
        else:
            st.error(f"Modelo {machine_type} não encontrado em {model_path}")
            st.info(f"💡 Execute o pipeline de treinamento para criar o modelo {machine_type}")
            models[machine_type] = None

    return models

def filter_data_by_machine_type(df: pd.DataFrame, machine_type: str) -> pd.DataFrame:
    """Filter data by machine type based on business rules."""
    if df is None or df.empty:
        return pd.DataFrame()

    if machine_type == "flexo":
        # Flexo: pedidos com mais cores, sem vincos ou com vincos mínimos
        flexo_filter = (
            (df['QT_NRCORES'] >= 2) |  # Flexo geralmente tem 2+ cores
            (df['TX_COMPOSICAO'].str.contains('KRAFT|DUPLEX', case=False, na=False))
        )
        return df[flexo_filter]

    elif machine_type == "cv":
        # CV: pedidos com vincos ou características de corte e vinco
        cv_filter = (
            (df['VL_VINCOLARG1'] > 0) |
            (df['VL_VINCOLARG2'] > 0) |
            (df['VL_VINCOLARG3'] > 0) |
            (df['VL_VINCOCOMP1'] > 0) |
            (df['VL_VINCOCOMP2'] > 0) |
            (df['VL_VINCOCOMP3'] > 0) |
            (df['VL_VINCOCOMP4'] > 0) |
            (df['VL_VINCOCOMP5'] > 0) |
            (df['TX_COMPOSICAO'].str.contains('ONDULADO|MICRO', case=False, na=False))
        )
        return df[cv_filter]

    return df

def create_sample_data_from_real(df: pd.DataFrame, machine_type: str, n_samples: int = 5) -> pd.DataFrame:
    """Create sample data from real pedidos data."""
    if df is None or df.empty:
        st.error("Nenhum dado disponível para criar amostras")
        return pd.DataFrame()

    # Filter by machine type
    filtered_df = filter_data_by_machine_type(df, machine_type)

    if filtered_df.empty:
        st.warning(f"Nenhum pedido encontrado para {machine_type}. Usando amostra geral.")
        filtered_df = df.sample(n=min(100, len(df)), random_state=42)

    # Sample random records
    if len(filtered_df) >= n_samples:
        sample_df = filtered_df.sample(n=n_samples, random_state=42)
    else:
        sample_df = filtered_df.copy()

    # Create CD_OP column if it doesn't exist
    if 'CD_OP' not in sample_df.columns:
        sample_df = sample_df.copy()
        sample_df['CD_OP'] = sample_df['CD_PEDIDO'].astype(str) + '/' + sample_df['CD_ITEM'].astype(str)

    return sample_df

def get_unique_values_from_data(df: pd.DataFrame, column: str, limit: int = 50) -> list:
    """Get unique values from a column in the dataframe."""
    if df is None or df.empty or column not in df.columns:
        return []

    unique_vals = df[column].dropna().unique().tolist()
    # Limit the number of options to avoid overwhelming the UI
    if len(unique_vals) > limit:
        # Get the most common values
        value_counts = df[column].value_counts().head(limit)
        unique_vals = value_counts.index.tolist()

    return sorted(unique_vals) if unique_vals else []

def create_pedido_selector(df: pd.DataFrame, machine_type: str):
    """Create a selector for existing pedidos."""
    if df is None or df.empty:
        st.warning("Nenhum dado disponível para seleção")
        return None

    # Filter by machine type
    filtered_df = filter_data_by_machine_type(df, machine_type)

    if filtered_df.empty:
        st.warning(f"Nenhum pedido encontrado para máquinas do tipo {machine_type}")
        filtered_df = df.sample(n=min(1000, len(df)), random_state=42)  # Use sample of all data as fallback

    st.markdown("""
    <div class="data-selector">
        <h4>Selecionar Pedido Existente</h4>
        <p>Escolha um pedido da base de dados para gerar a estimativa</p>
    </div>
    """, unsafe_allow_html=True)

    # Create CD_OP if it doesn't exist
    if 'CD_OP' not in filtered_df.columns:
        filtered_df = filtered_df.copy()
        filtered_df['CD_OP'] = filtered_df['CD_PEDIDO'].astype(str) + '/' + filtered_df['CD_ITEM'].astype(str)

    # Create selection options (limit to avoid performance issues)
    pedido_options = filtered_df['CD_OP'].unique()[:1000].tolist()  # Limit to 1000 options

    selected_pedido = st.selectbox(
        "Selecione um Pedido (CD_OP)",
        options=pedido_options,
        help="Escolha um código de operação da lista"
    )

    if selected_pedido:
        # Get the selected row
        selected_row = filtered_df[filtered_df['CD_OP'] == selected_pedido].iloc[0]

        # Display pedido details
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Código do Pedido", selected_row.get('CD_PEDIDO', 'N/A'))
            st.metric("Comprimento", f"{selected_row.get('VL_COMPRIMENTO', 0):.1f} mm")

        with col2:
            st.metric("Código do Item", selected_row.get('CD_ITEM', 'N/A'))
            st.metric("Largura", f"{selected_row.get('VL_LARGURA', 0):.1f} mm")

        with col3:
            st.metric("Quantidade", f"{selected_row.get('QT_PEDIDA', 0):.0f}")
            st.metric("Gramatura", f"{selected_row.get('VL_GRAMATURA', 0):.1f}")

        with col4:
            st.metric("Nº Cores", f"{selected_row.get('QT_NRCORES', 0):.0f}")
            st.metric("Composição", selected_row.get('TX_COMPOSICAO', 'N/A'))

        return selected_row.to_frame().T

    return None

def create_complete_input_data(user_inputs: dict) -> pd.DataFrame:
    """Create a complete DataFrame with all required columns for the pipeline."""

    # Current timestamp for IDs and dates
    current_date = pd.Timestamp.now()

    # Extract user inputs
    vl_comprimento = user_inputs['vl_comprimento']
    vl_largura = user_inputs['vl_largura']
    vl_gramatura = user_inputs['vl_gramatura']
    vl_comp_interno = user_inputs['vl_comp_interno']
    vl_larg_interna = user_inputs['vl_larg_interna']
    vl_altura_interna = user_inputs['vl_altura_interna']
    tx_composicao = user_inputs['tx_composicao']
    tx_tipoabnt = user_inputs['tx_tipoabnt']
    fl_teste = user_inputs['fl_teste']
    qt_pedida = user_inputs['qt_pedida']
    qt_arranjo = user_inputs['qt_arranjo']
    qt_nrcores = user_inputs['qt_nrcores']
    vl_multcomp = user_inputs['vl_multcomp']
    vl_multlarg = user_inputs['vl_multlarg']
    vl_refugo = user_inputs['vl_refugo']

    # Automatic calculations
    vl_comppeca = vl_comp_interno
    vl_largpeca = vl_larg_interna
    vl_arealiquidapeca = vl_comppeca * vl_largpeca
    vl_pesopeca = (vl_gramatura * vl_arealiquidapeca) / 1000000.0 / 1000.0
    vl_pesocaixa = vl_pesopeca
    vl_consumo_cor = qt_nrcores * 10.0 * (vl_arealiquidapeca / 1000000.0)

    # Create complete DataFrame with ALL required columns
    input_data = pd.DataFrame({
        # Identificação
        'CD_OP': [f"PRED_{current_date.strftime('%Y%m%d%H%M%S')}"],
        'CD_PEDIDO': [f"PRED_{current_date.strftime('%Y%m%d')}"],
        'CD_ITEM': ["1"],
        'ID_CLIENTE': ["CLIENTE_PRED"],
        'CD_PALETE': ["PALETE_001"],
        'CD_TIPOFT2': ["TIPO_001"],
        'CD_REFERENCIA': ["REF_001"],
        'CD_ESPELHO': ["ESP_001"],
        'CD_FILME': ["FILME_001"],
        'CD_FACA': ["FACA_001"],

        # Datas (necessárias para process_pedidos)
        'DT_ENTREGA2': [current_date],
        'DT_ENTREGAORIGINAL': [current_date],

        # Flags (valores padrão seguros)
        'FL_AMARRADO': ["N"],
        'FL_CHAPA': ["N"],
        'FL_EXIGELAUDO': ["S" if fl_teste == "Sim" else "N"],
        'FL_PALETIZADO': ["S"],
        'FL_REFILADO': ["N"],
        'FL_RESINAINTERNA': ["N"],
        'FL_SUSPENSO': ["N"],
        'FL_TIPOENTREGA': ["NORMAL"],
        'FL_SUSPOUCANCEL': ["0"],  # ← ADICIONADO PARA CORRIGIR O ERRO

        # Status
        'ST_PEDIDO': ["ATIVO"],
        'TX_DESCRSTATUSPEDIDO': ["ATIVO"],
        'TX_DESCRTIPODOPEDIDO': ["NORMAL"],
        'TX_DESCTIPOENTREGA': ["NORMAL"],

        # Características principais (do usuário)
        'TX_TIPOABNT': [tx_tipoabnt],
        'TX_COMPOSICAO': [tx_composicao],

        # Quantidades
        'QT_ARRANJO': [qt_arranjo],
        'QT_COBBINTMAXIMO': [1000.0],
        'QT_NRCORES': [qt_nrcores],
        'QT_PEDIDA': [qt_pedida],
        'QT_PEDIDAMAX': [qt_pedida * 1.1],
        'QT_PEDIDAMIN': [qt_pedida * 0.9],
        'QT_PROLONGLAP': [0.0],
        'QT_PECASPORPACOTE': [100.0],
        'QT_PECASPORPALETE': [1000.0],
        'QT_UNIDADESPORPALETE': [10.0],
        'QT_PACOTESPORPALETE': [10.0],

        # Dimensões principais (do usuário)
        'VL_COMPRIMENTO': [vl_comprimento],
        'VL_LARGURA': [vl_largura],
        'VL_GRAMATURA': [vl_gramatura],
        'VL_COMPRIMENTOINTERNO': [vl_comp_interno],
        'VL_LARGURAINTERNA': [vl_larg_interna],
        'VL_ALTURAINTERNA': [vl_altura_interna],
        'VL_MULTCOMP': [vl_multcomp],
        'VL_MULTLARG': [vl_multlarg],

        # Dimensões calculadas
        'VL_COMPPECA': [vl_comppeca],
        'VL_LARGPECA': [vl_largpeca],
        'VL_AREALIQUIDAPECA': [vl_arealiquidapeca],
        'VL_PESOPECA': [vl_pesopeca],
        'VL_PESOCAIXA': [vl_pesocaixa],

        # Outras dimensões (valores padrão)
        'VL_LAPINTERNO': [0.0],
        'VL_LAPNOCOMP': [0.0],
        'VL_ALTURAINTERNA_REAL': [vl_altura_interna],
        'VL_REFUGOCLIENTE': [vl_refugo],
        'VL_AREABRUTAPECA': [vl_arealiquidapeca * 1.1],
        'VL_AREABRUTACHAPA': [vl_comprimento * vl_largura],
        'VL_AREALIQUIDACHAPA': [vl_comp_interno * vl_larg_interna],
        'VL_VOLUMEFECHADOPEDIDO': [vl_arealiquidapeca * vl_altura_interna * qt_pedida / 1000000000.0],
        'VL_VOLUMEPACOTEFECHADOM3': [0.1],
        'VL_VOLUMEPALETEFECHADOM3': [1.0],
        'VL_COLUNAMINIMO': [100.0],
        'VL_COMPRESSAO': [0.0],
        'VL_REFILOLARGURA': [0.0],
        'VL_REFILOCOMPRIMENTO': [0.0],
        'VL_PACOTESLARGURA': [vl_largura],
        'VL_PACOTESCOMPRIMENTO': [vl_comprimento],
        'VL_PACOTESALTURA': [vl_altura_interna],
        'VL_COMPPACOTE': [vl_comprimento],
        'VL_LARGPACOTE': [vl_largura],
        'VL_ALTURAPACOTE': [vl_altura_interna],
        'VL_COMPPALETEFECHADO': [vl_comprimento],
        'VL_LARGPALETEFECHADO': [vl_largura],
        'VL_ALTURAPALETEFECHADO': [vl_altura_interna * 10],
        'VL_AREABRUTAPECACOMREFILOS': [vl_arealiquidapeca * 1.1],
        'VL_LAP': [0.0],

        # Consumo de cores (calculado)
        'QT_CONSUMOCOR1': [vl_consumo_cor if qt_nrcores >= 1 else 0.0],
        'QT_CONSUMOCOR2': [vl_consumo_cor if qt_nrcores >= 2 else 0.0],
        'QT_CONSUMOCOR3': [vl_consumo_cor if qt_nrcores >= 3 else 0.0],
        'QT_CONSUMOCOR4': [vl_consumo_cor if qt_nrcores >= 4 else 0.0],

        # Vincos (valores padrão - sem vincos para este exemplo)
        'VL_VINCOLARG1': [0.0],
        'VL_VINCOLARG2': [0.0],
        'VL_VINCOLARG3': [0.0],
        'VL_VINCOCOMP1': [0.0],
        'VL_VINCOCOMP2': [0.0],
        'VL_VINCOCOMP3': [0.0],
        'VL_VINCOCOMP4': [0.0],
        'VL_VINCOCOMP5': [0.0],
    })

    return input_data

def display_prediction_results(
    results: pd.DataFrame,
    machine_type: str,
    input_features: Dict[str, Any] = None,
    insights_generator: Optional[ProductivityInsightsGenerator] = None
):
    """Display regression prediction results with optional AI insights."""
    for idx, row in results.iterrows():
        predicted_rate = row.get("pred_m3_por_hora", np.nan)
        predicted_boxes = row.get("pred_caixas_por_hora", np.nan)
        piece_volume = row.get("volume_peca_m3", np.nan)
        total_volume = row.get("volume_total_estimado_m3", np.nan)
        estimated_time = row.get("pred_tempo_horas", np.nan)
        requested_qty = row.get("QT_PEDIDA", np.nan)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            throughput_text = (
                f"{predicted_rate:,.2f} m³/h"
                if pd.notna(predicted_rate)
                else "sem estimativa"
            )
            st.markdown(
                f"""
                <div class="prediction-high">
                    <h2>{throughput_text}</h2>
                    <p>Volume físico processado por hora (estimativa)</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        metric_cols = st.columns(3)
        metric_cols[0].metric(
            "Caixas/h (estimado)",
            f"{predicted_boxes:,.0f}" if pd.notna(predicted_boxes) else "N/D",
        )
        metric_cols[1].metric(
            "Volume por peça (m³)",
            f"{piece_volume:,.4f}" if pd.notna(piece_volume) else "N/D",
        )
        metric_cols[2].metric(
            "Tempo estimado (h)",
            f"{estimated_time:,.2f}" if pd.notna(estimated_time) else "N/D",
        )

        extra_cols = st.columns(2)
        extra_cols[0].metric(
            "Volume total do pedido (m³)",
            f"{total_volume:,.2f}" if pd.notna(total_volume) else "N/D",
        )
        extra_cols[1].metric(
            "Quantidade pedida",
            f"{requested_qty:,.0f}" if pd.notna(requested_qty) else "N/D",
        )

        cluster_cols = [
            col for col in results.columns if col.startswith("PROB_CLUSTER_")
        ]

        top_features = None
        if "top_features" in results.columns and pd.notna(row.get("top_features")):
            st.subheader("Principais Fatores Influenciadores")
            try:
                if isinstance(row["top_features"], str):
                    top_features = eval(row["top_features"])
                else:
                    top_features = row["top_features"]

                if top_features and len(top_features) > 0:
                    features, values = zip(*top_features)

                    fig_features = px.bar(
                        x=list(values),
                        y=list(features),
                        orientation="h",
                        title="Top Features Mais Importantes",
                        labels={"x": "Impacto na Predição", "y": "Feature"},
                        color=list(values),
                        color_continuous_scale="RdBu",
                    )
                    fig_features.update_layout(height=400)
                    st.plotly_chart(fig_features, width="stretch")
            except Exception:
                st.info(
                    "Análise de importância das features não disponível para esta estimativa."
                )

        st.subheader("📌 Indicadores Operacionais")
        op_cols = st.columns(4)
        cluster_display = row.get("cluster_pred", "N/D")
        try:
            cluster_display = f"C{int(cluster_display)}"
        except (ValueError, TypeError):
            cluster_display = "N/D"

        area_chapa = None
        if pd.notna(row.get("VL_COMPRIMENTO", np.nan)) and pd.notna(
            row.get("VL_LARGURA", np.nan)
        ):
            area_chapa = row["VL_COMPRIMENTO"] * row["VL_LARGURA"]
        area_chapa_m2 = area_chapa / 1_000_000 if area_chapa else None

        area_peca = None
        if pd.notna(row.get("VL_COMPPECA", np.nan)) and pd.notna(
            row.get("VL_LARGPECA", np.nan)
        ):
            area_peca = row["VL_COMPPECA"] * row["VL_LARGPECA"]

        volume_interno = row.get("VOLUME_INTERNO", np.nan)
        if pd.isna(volume_interno):
            if (
                pd.notna(row.get("VL_COMPRIMENTOINTERNO", np.nan))
                and pd.notna(row.get("VL_LARGURAINTERNA", np.nan))
                and pd.notna(row.get("VL_ALTURAINTERNA", np.nan))
            ):
                volume_interno = (
                    row["VL_COMPRIMENTOINTERNO"]
                    * row["VL_LARGURAINTERNA"]
                    * row["VL_ALTURAINTERNA"]
                )

        pecas_chapa = row.get("PECAS_POR_CHAPA", np.nan)
        if pd.isna(pecas_chapa):
            if pd.notna(row.get("VL_MULTCOMP", np.nan)) and pd.notna(
                row.get("VL_MULTLARG", np.nan)
            ):
                pecas_chapa = row["VL_MULTCOMP"] * row["VL_MULTLARG"]

        op_cols[0].metric("Cluster", cluster_display)
        op_cols[1].metric(
            "Área da chapa (m²)",
            f"{area_chapa_m2:.2f}" if area_chapa_m2 else "N/D",
        )
        op_cols[2].metric(
            "Peças por chapa",
            f"{pecas_chapa:.0f}" if pd.notna(pecas_chapa) else "N/D",
        )
        op_cols[3].metric(
            "Volume interno (m³)",
            f"{volume_interno/1_000_000_000:.3f}"
            if volume_interno and volume_interno > 0
            else "N/D",
        )

        st.subheader("🔬 Visão Técnica das Variáveis-Chave")
        detail_cols = [
            "VL_COMPRIMENTO",
            "VL_LARGURA",
            "VL_ALTURAINTERNA",
            "VL_COMPPECA",
            "VL_LARGPECA",
            "VL_GRAMATURA",
            "QT_PEDIDA",
            "QT_NRCORES",
            "VL_REFUGOCLIENTE",
            "VL_CONSUMO_COR_TOTAL",
            "PERC_VAR_PEDIDA",
        ]
        detail_data = []
        for col in detail_cols:
            if col in row.index and pd.notna(row[col]):
                detail_data.append({"Variável": col, "Valor": row[col]})
        if area_peca:
            detail_data.append({"Variável": "Área da peça (mm²)", "Valor": area_peca})

        if detail_data:
            detail_df = pd.DataFrame(detail_data)
            st.table(detail_df.set_index("Variável"))

        # AI Insights if available
        if insights_generator and input_features:
            prediction_data = {
                "pred_m3_por_hora": float(predicted_rate)
                if pd.notna(predicted_rate)
                else None,
                "pred_caixas_por_hora": float(predicted_boxes)
                if pd.notna(predicted_boxes)
                else None,
                "volume_peca_m3": float(piece_volume)
                if pd.notna(piece_volume)
                else None,
                "volume_total_estimado_m3": float(total_volume)
                if pd.notna(total_volume)
                else None,
                "pred_tempo_horas": float(estimated_time)
                if pd.notna(estimated_time)
                else None,
                "qt_pedida": float(requested_qty)
                if pd.notna(requested_qty)
                else None,
            }

            for col in cluster_cols:
                prediction_data[col] = row[col]

            display_ai_insights(
                insights_generator,
                prediction_data,
                machine_type,
                input_features,
                top_features,
            )

def ensure_authentication() -> bool:
    """Simple authentication gate using predefined users."""
    if "auth_user" in st.session_state:
        user = st.session_state["auth_user"]
        st.sidebar.success(f"Usuário autenticado: {user.upper()}")
        if st.sidebar.button("Sair"):
            del st.session_state["auth_user"]
            st.experimental_rerun()
        return True

    st.sidebar.markdown("### Acesso Restrito")
    with st.sidebar.form("login_form"):
        username = st.selectbox("Usuário", list(AUTH_USERS.keys()))
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

    if submitted:
        expected = AUTH_USERS.get(username)
        if expected and password == expected:
            st.session_state["auth_user"] = username
            st.toast(f"Bem-vindo, {username.upper()}!")
            st.rerun()
        else:
            st.sidebar.error("Usuário ou senha inválidos")
            st.write("Login falhou para o usuário:", username)

    st.info("Faça login para acessar o estimador.")
    return False

def main():
    # Header
    st.markdown(
        '<h1 class="main-header">Regressão de Volume por Hora - Adami</h1>',
        unsafe_allow_html=True,
    )

    # Check pipeline availability
    if not PIPELINE_AVAILABLE:
        st.error("Pipeline não disponível. Verifique a instalação.")
        return

    # Authentication
    if not ensure_authentication():
        return

    # Load data and models
    pedidos_df = load_pedidos_data()
    models = load_trained_models()

    # Main navigation
    main_tab1, main_tab2, main_tab3 = st.tabs(["Estimativas", "Explorar Dados", "Guia do Aplicativo"])

    with main_tab2:
        # Data explorer
        if pedidos_df is not None:
            if DATA_EXPLORER_AVAILABLE and _create_data_explorer_tab:
                try:
                    _create_data_explorer_tab(pedidos_df)
                except Exception as explorer_error:
                    st.warning(
                        f"Explorador de dados encontrou um problema: {explorer_error}"
                    )
                    st.write(f"**Total de registros:** {len(pedidos_df):,}")
                    st.write(f"**Colunas:** {len(pedidos_df.columns)}")
                    st.dataframe(pedidos_df.head())
            else:
                st.info("Explorador de dados não disponível. Mostrando informações básicas.")
                if DATA_EXPLORER_IMPORT_ERROR:
                    st.caption(f"Motivo: {DATA_EXPLORER_IMPORT_ERROR}")
                st.write(f"**Total de registros:** {len(pedidos_df):,}")
                st.write(f"**Colunas:** {len(pedidos_df.columns)}")
                st.dataframe(pedidos_df.head())
        else:
            st.error("Dados não disponíveis para exploração")

    with main_tab3:
        st.subheader("Como utilizar o Regressor de Volume por Hora")
        st.markdown(
            """
            1. **Login**: entre com um dos usuários configurados (ex.: `adami` ou `amcom`) e a senha correspondente.
            2. **Escolha o modelo**: selecione Flexo ou CV no menu lateral; o app confirma que o artefato foi carregado.
            3. **Defina o método de entrada**:
               - *Formulário Interativo*: informe dimensões, gramatura, cores e refugo; demais campos são calculados automaticamente.
               - *Upload CSV*: envie arquivo no formato de `src/pipelines/DS/input_models.csv`; cada linha gera uma estimativa.
               - *Selecionar Pedido Existente*: filtre pedidos reais para testar com dados históricos.
               - *Dados de Exemplo*: utiliza amostras reais já carregadas na base.
            4. **Executar estimativa**: clique no botão principal. O resultado mostra throughput previsto em m³/h, conversão estimada para caixas/h e tempo necessário para concluir o pedido.
            5. **IA Insights (opcional)**: ative na barra lateral, forneça a API key e receba recomendações textuais automáticas com base nas estimativas de volume.

            Boas práticas:
            - Use a aba “Explorar Dados” para entender a distribuição das variáveis antes de testar cenários.
            - Ao operar em rede interna, garanta que apenas usuários autorizados tenham acesso ao endereço do app.
            """,
        )

        st.markdown("### Formato esperado para upload CSV")
        st.write(
            "O CSV deve seguir o mesmo layout de `src/pipelines/DS/input_models.csv`. "
            "Os campos principais (todos em letras maiúsculas) são:"
        )
        csv_columns = [
            ("CD_PEDIDO / CD_ITEM", "Identificador do pedido e item; usados para gerar CD_OP."),
            ("TX_TIPOABNT, TX_COMPOSICAO", "Tipo de papel/ABNT do produto."),
            ("QT_ARRANJO", "Número de peças por arranjo na chapa."),
            ("QT_COBBINTMAXIMO", "Limite de teste Cobb interno (valor numérico)."),
            ("QT_PEDIDA", "Quantidade total solicitada."),
            ("QT_PROLONGLAP", "Quantidade de prolongamento de lap (se houver)."),
            ("VL_GRAMATURA", "Gramatura do papel em g/m²."),
            ("VL_COMPRIMENTO, VL_LARGURA, VL_ALTURAINTERNA", "Dimensões externas da chapa/caixa em mm."),
            ("VL_REFUGOCLIENTE", "Percentual ou valor de refugo previsto."),
            ("VL_PESOPECA / VL_PESOCAIXA", "Pesos estimados da peça e da caixa."),
            ("VL_AREALIQUIDAPECA / VL_AREALIQUIDACHAPA", "Áreas líquidas em mm²."),
            ("VL_COLUNAMINIMO / VL_COMPRESSAO", "Especificações de coluna e compressão."),
            ("VL_REFILOLARGURA / VL_REFILOCOMPRIMENTO", "Refilos nas direções largura/comprimento."),
            ("VL_LARGURAINTERNA / VL_COMPRIMENTOINTERNO / VL_ALTURAINTERNA_REAL", "Dimensões internas reais."),
            ("VL_LARGPECA / VL_COMPPECA", "Dimensões da peça final."),
            ("QT_CONSUMOCOR1..4", "Consumo estimado de tinta por cor (kg)."),
            ("VL_VINCOLARG1..3 / VL_VINCOCOMP1..5", "Medidas de vinco em largura e comprimento."),
            ("FL_AMARRADO, FL_CHAPA, FL_EXIGELAUDO, FL_REFILADO, FL_RESINAINTERNA", "Flags binárias (Sim/Não ou 1/0)."),
        ]
        for col, desc in csv_columns:
            st.markdown(f"- **{col}**: {desc}")

        st.markdown(
            """
            Exemplos completos podem ser encontrados em `src/pipelines/DS/input_models.csv`.
            Certifique-se de incluir `CD_PEDIDO` e `CD_ITEM`, pois o sistema gera `CD_OP` a partir deles.
            """
        )
        template_path = (
            Path(__file__).resolve().parents[2] / "src" / "pipelines" / "DS" / "input_models.csv"
        )
        if template_path.exists():
            template_bytes = template_path.read_bytes()
            st.download_button(
                label="Baixar modelo CSV (input_models.csv)",
                data=template_bytes,
                file_name="input_models_template.csv",
                mime="text/csv",
            )
        else:
            st.info(
                "Modelo CSV original não encontrado no servidor. Solicite o arquivo de exemplo ao time de dados."
            )

    with main_tab1:
        # Sidebar
        st.sidebar.title("Configurações")

        # Machine type selection
        machine_type = st.sidebar.selectbox(
            "Tipo",
            options=["flexo", "cv"],
            format_func=lambda x: "Flexo" if x == "flexo" else "Corte e Vinco",
            help="Selecione o tipo de máquina para estimativa"
        )

        # Check if model is available
        if models.get(machine_type) is None:
            st.error(f"Modelo para {machine_type} não encontrado. Execute o treinamento primeiro.")
            return

        st.sidebar.success(f"Modelo {machine_type} carregado com sucesso!")

        # Data info
        if pedidos_df is not None:
            filtered_data = filter_data_by_machine_type(pedidos_df, machine_type)
            st.sidebar.info(f"{len(filtered_data):,} pedidos disponíveis para {machine_type}")

            # Show data statistics
            with st.sidebar.expander("Estatísticas dos Dados"):
                st.write(f"**Total de pedidos:** {len(pedidos_df):,}")
                st.write(f"**Pedidos {machine_type}:** {len(filtered_data):,}")
                if not filtered_data.empty:
                    st.write(f"**Período:** {filtered_data['DT_ENTREGA2'].min().strftime('%Y-%m-%d')} a {filtered_data['DT_ENTREGA2'].max().strftime('%Y-%m-%d')}")
        else:
            st.sidebar.warning("Dados não carregados")

        # OpenAI Insights Configuration
        enable_insights, api_key = get_openai_insights_component()

        # Initialize insights generator if enabled
        insights_generator = None
        if enable_insights and api_key:
            try:
                insights_generator = ProductivityInsightsGenerator(api_key)
                st.sidebar.success("IA Insights ativado!")
            except Exception as e:
                st.sidebar.error(f"Erro ao configurar IA: {str(e)}")

        # Input method selection
        input_methods = ["Formulário Interativo", "Upload CSV", "Selecionar Pedido Existente", "Dados de Exemplo"]
        input_method = st.sidebar.radio(
            "Método de Entrada",
            input_methods,
            help="Escolha como fornecer os dados para estimativa"
        )

        # Main content area
        col1, col2 = st.columns([2, 1])

        with col2:
            st.markdown(
                """
                ### Informações do Modelo
                """
            )

            model_info = models[machine_type]
            metrics = model_info.get("metrics", {})

            if metrics:
                r2_value = metrics.get("r2")
                mae_value = metrics.get("mae")
                rmse_value = metrics.get("rmse")

                if r2_value is not None:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <h4>R² (ajuste)</h4>
                            <h2>{r2_value:.3f}</h2>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                if mae_value is not None:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <h4>MAE (m³/h)</h4>
                            <h2>{mae_value:,.0f}</h2>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                if rmse_value is not None:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <h4>RMSE (m³/h)</h4>
                            <h2>{rmse_value:,.0f}</h2>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # AI Insights Status
            if enable_insights:
                st.markdown("""
                <div class="ai-insights">
                    <h4>IA Insights Ativo</h4>
                    <p>Análises inteligentes serão geradas automaticamente</p>
                </div>
                """, unsafe_allow_html=True)

        with col1:
            if input_method == "Selecionar Pedido Existente":
                st.subheader("Selecionar Pedido da Base de Dados")

                selected_data = create_pedido_selector(pedidos_df, machine_type)

                if selected_data is not None:
                    if st.button("Estimar Produção com Pedido Selecionado", width="stretch"):
                        try:
                            with st.spinner("Calculando estimativa..."):
                                results = inference.predict_orders(selected_data, models[machine_type])

                            st.success("Estimativa realizada com sucesso!")

                            # Prepare input features for AI insights
                            input_features = {}
                            feature_cols = ['VL_COMPRIMENTO', 'VL_LARGURA', 'VL_GRAMATURA', 'QT_NRCORES', 'QT_PEDIDA', 'TX_COMPOSICAO', 'TX_TIPOABNT', 'FL_EXIGELAUDO']
                            for col in feature_cols:
                                if col in selected_data.columns:
                                    input_features[col] = selected_data[col].iloc[0]

                            display_prediction_results(
                                results,
                                machine_type,
                                input_features,
                                insights_generator
                            )

                        except Exception as e:
                            st.error(f"Erro na estimativa: {str(e)}")
                            with st.expander("Detalhes do Erro"):
                                import traceback
                                st.code(traceback.format_exc())

            elif input_method == "Formulário Interativo":
                st.subheader("Estimativa de Volume por Hora")
                st.markdown("Preencha as informações do produto para estimar m³/h, caixas/h e o tempo necessário para concluir o pedido.")

                # Get unique values from real data for dropdowns
                composicao_options = get_unique_values_from_data(pedidos_df, 'TX_COMPOSICAO')
                if not composicao_options:
                    composicao_options = ["KRAFT", "DUPLEX", "TRIPLEX", "ONDULADO", "MICRO"]

                tipoabnt_options = get_unique_values_from_data(pedidos_df, 'TX_TIPOABNT')
                if not tipoabnt_options:
                    tipoabnt_options = ["TIPO_A", "TIPO_B", "TIPO_C"]

                # Create form for manual input
                with st.form("prediction_form"):
                    st.markdown("### Dimensões da Caixa")
                    col_form1, col_form2, col_form3 = st.columns(3)

                    with col_form1:
                        vl_comprimento = st.number_input(
                            "Comprimento da Chapa (mm)",
                            min_value=0.0,
                            max_value=2000.0,
                            value=0.0,
                            help="Comprimento total da chapa de papelão"
                        )
                        vl_largura = st.number_input(
                            "Largura da Chapa (mm)",
                            min_value=0.0,
                            max_value=1500.0,
                            value=0.0,
                            help="Largura total da chapa de papelão"
                        )

                    with col_form2:
                        vl_comp_interno = st.number_input(
                            "Comprimento Interno (mm)",
                            min_value=0.0,
                            max_value=1900.0,
                            value=0.0,
                            help="Comprimento interno da caixa montada"
                        )
                        vl_larg_interna = st.number_input(
                            "Largura Interna (mm)",
                            min_value=0.0,
                            max_value=1400.0,
                            value=0.0,
                            help="Largura interna da caixa montada"
                        )

                    with col_form3:
                        vl_altura_interna = st.number_input(
                            "Altura Interna (mm)",
                            min_value=0.0,
                            max_value=500.0,
                            value=0.0,
                            help="Altura interna da caixa montada"
                        )
                        vl_gramatura = st.number_input(
                            "Gramatura (g/m²)",
                            min_value=0.0,
                            max_value=800.0,
                            value=0.0,
                            help="Peso do papelão por metro quadrado"
                        )

                    st.markdown("### Características do Produto")
                    col_char1, col_char2, col_char3 = st.columns(3)

                    with col_char1:
                        tx_composicao = st.selectbox(
                            "Tipo de Papelão",
                            composicao_options,
                            help="Tipo de composição do papelão",
                        )
                        tx_tipoabnt = st.selectbox(
                            "Tipo ABNT",
                            tipoabnt_options,
                            help="Classificação ABNT do produto",
                        )

                    with col_char2:
                        fl_teste = st.selectbox(
                            "Exige Teste de Laboratório?",
                            ["Não", "Sim"],
                            help="Se o produto precisa de laudo técnico",
                        )
                        qt_pedida = st.number_input(
                            "Quantidade (unidades)",
                            min_value=0,
                            max_value=100000,
                            value=0,
                            help="Quantidade total de peças do pedido",
                        )

                    with col_char3:
                        qt_arranjo = st.number_input(
                            "Arranjo",
                            min_value=0,
                            max_value=10,
                            value=0,
                            help="Número de peças por arranjo na chapa",
                        )
                        qt_nrcores = st.number_input(
                            "Número de Cores",
                            min_value=0,
                            max_value=8,
                            value=0,
                            help="Quantidade de cores na impressão",
                        )

                    st.markdown("### Configuração de Produção")
                    col_prod1, col_prod2, col_prod3 = st.columns(3)

                    with col_prod1:
                        vl_multcomp = st.number_input(
                            "Peças no Comprimento",
                            min_value=0,
                            max_value=20,
                            value=0,
                            help="Quantas peças cabem no comprimento da chapa",
                        )

                    with col_prod2:
                        vl_multlarg = st.number_input(
                            "Peças na Largura",
                            min_value=0,
                            max_value=20,
                            value=0,
                            help="Quantas peças cabem na largura da chapa",
                        )

                    with col_prod3:
                        vl_refugo = st.number_input(
                            "Refugo Cliente (%)",
                            min_value=0.0,
                            max_value=50.0,
                            value=0.0,
                            help="Percentual de refugo aceito pelo cliente",
                        )

                    # Show calculated values
                    st.markdown("### Valores Calculados Automaticamente")
                    col_calc1, col_calc2, col_calc3, col_calc4 = st.columns(4)

                    # Calculations
                    vl_comppeca = vl_comp_interno
                    vl_largpeca = vl_larg_interna
                    vl_arealiquidapeca = vl_comppeca * vl_largpeca
                    vl_pesopeca = (
                        (vl_gramatura * vl_arealiquidapeca) / 1000000.0 / 1000.0
                    )
                    vl_consumo_cor = (
                        qt_nrcores * 10.0 * (vl_arealiquidapeca / 1000000.0)
                    )

                    with col_calc1:
                        st.metric("Área da Peça (mm²)", f"{vl_arealiquidapeca:,.0f}")

                    with col_calc2:
                        st.metric("Peso da Peça (kg)", f"{vl_pesopeca:.4f}")

                    with col_calc3:
                        st.metric("Peças por Chapa", f"{vl_multcomp * vl_multlarg}")

                    with col_calc4:
                        st.metric("Consumo Tinta (kg)", f"{vl_consumo_cor:.4f}")

                    submitted = st.form_submit_button(
                        "Estimar m³/h", width="stretch"
                    )

                    if submitted:
                        # Prepare user inputs
                        user_inputs = {
                            "vl_comprimento": vl_comprimento,
                            "vl_largura": vl_largura,
                            "vl_gramatura": vl_gramatura,
                            "vl_comp_interno": vl_comp_interno,
                            "vl_larg_interna": vl_larg_interna,
                            "vl_altura_interna": vl_altura_interna,
                            "tx_composicao": tx_composicao,
                            "tx_tipoabnt": tx_tipoabnt,
                            "fl_teste": fl_teste,
                            "qt_pedida": qt_pedida,
                            "qt_arranjo": qt_arranjo,
                            "qt_nrcores": qt_nrcores,
                            "vl_multcomp": vl_multcomp,
                            "vl_multlarg": vl_multlarg,
                            "vl_refugo": vl_refugo,
                        }

                        # Create complete input data
                        input_data = create_complete_input_data(user_inputs)

                        # Prepare input features for AI insights
                        input_features = {
                            "VL_COMPRIMENTO": vl_comprimento,
                            "VL_LARGURA": vl_largura,
                            "VL_GRAMATURA": vl_gramatura,
                            "QT_NRCORES": qt_nrcores,
                            "QT_PEDIDA": qt_pedida,
                            "TX_COMPOSICAO": tx_composicao,
                            "TX_TIPOABNT": tx_tipoabnt,
                            "FL_EXIGELAUDO": fl_teste,
                        }

                        # Make estimation
                        try:
                            with st.spinner("Calculando estimativa..."):
                                results = inference.predict_orders(
                                    input_data, models[machine_type]
                                )

                            st.success("Estimativa realizada com sucesso!")
                            display_prediction_results(
                                results,
                                machine_type,
                                input_features,
                                insights_generator,
                            )

                        except Exception as e:
                            st.error(f"Erro na estimativa: {str(e)}")
                            st.error("Verifique se o modelo foi treinado corretamente.")
                            with st.expander("Detalhes do Erro"):
                                import traceback

                                st.code(traceback.format_exc())

            elif input_method == "Upload CSV":
                st.subheader("Upload de Arquivo CSV")

                uploaded_file = st.file_uploader(
                    "Escolha um arquivo CSV",
                    type=["csv"],
                    help="Upload um arquivo CSV com os dados dos pedidos",
                )

                if uploaded_file is not None:
                    try:
                        df = pd.read_csv(uploaded_file)
                        st.success(
                            f"Arquivo carregado com sucesso! {len(df)} registros encontrados."
                        )

                        # Show preview
                        st.subheader("Prévia dos Dados")
                        st.dataframe(df.head())

                        if st.button("Gerar Estimativas", width="stretch"):
                            with st.spinner("Processando estimativas..."):
                                try:
                                    results = inference.predict_orders(
                                        df, models[machine_type]
                                    )
                                except Exception as e:
                                    st.error(
                                        f"Erro ao processar estimativas: {str(e)}"
                                    )
                                    with st.expander("Detalhes do Erro"):
                                        import traceback

                                        st.code(traceback.format_exc())
                                    return

                            st.success("Estimativas geradas com sucesso!")

                            # Show summary
                            st.subheader("Resumo das Estimativas")
                            col_sum1, col_sum2, col_sum3 = st.columns(3)

                            total_orders = len(results)
                            col_sum1.metric("Total de Pedidos", total_orders)

                            avg_rate = results.get(
                                "pred_m3_por_hora", pd.Series(dtype=float)
                            ).mean()
                            col_sum2.metric(
                                "Média (m³/h)",
                                f"{avg_rate:,.2f}" if pd.notna(avg_rate) else "N/D",
                            )

                            if "pred_tempo_horas" in results.columns:
                                total_hours = results["pred_tempo_horas"].sum()
                                col_sum3.metric(
                                    "Tempo projetado (h)",
                                    f"{total_hours:,.2f}",
                                )
                            else:
                                total_volume = results.get("volume_total_estimado_m3")
                                total_volume_val = (
                                    total_volume.sum()
                                    if isinstance(total_volume, pd.Series)
                                    else np.nan
                                )
                                col_sum3.metric(
                                    "Volume acumulado (m³)",
                                    f"{total_volume_val:,.1f}"
                                    if pd.notna(total_volume_val)
                                    else "N/D",
                                )

                            if {
                                "cluster_pred",
                                "pred_m3_por_hora",
                            }.issubset(results.columns):
                                st.markdown("### Throughput médio por Cluster")
                                cluster_summary = (
                                    results.groupby("cluster_pred")["pred_m3_por_hora"]
                                    .agg(["mean", "count"])
                                    .reset_index()
                                )
                                fig_cluster = px.bar(
                                    cluster_summary,
                                    x="cluster_pred",
                                    y="mean",
                                    hover_data={"count": True},
                                    labels={
                                        "cluster_pred": "Cluster",
                                        "mean": "m³/h médios",
                                        "count": "Pedidos",
                                    },
                                    title="Distribuição de m³/h por cluster",
                                )
                                st.plotly_chart(fig_cluster, width="stretch")

                            if {
                                "pred_m3_por_hora",
                                "VL_GRAMATURA",
                                "VL_COMPRIMENTO",
                                "VL_LARGURA",
                            }.issubset(results.columns):
                                st.markdown("### Relação com Variáveis Geométricas")
                                geom_tabs = st.tabs(
                                    ["Gramatura", "Comprimento", "Largura"]
                                )
                                geom_map = {
                                    "Gramatura": "VL_GRAMATURA",
                                    "Comprimento": "VL_COMPRIMENTO",
                                    "Largura": "VL_LARGURA",
                                }
                                for tab, label in zip(geom_tabs, geom_map.keys()):
                                    with tab:
                                        col_name = geom_map[label]
                                        fig_scatter = px.scatter(
                                            results,
                                            x=col_name,
                                            y="pred_m3_por_hora",
                                            labels={
                                                col_name: label,
                                                "pred_m3_por_hora": "m³/h",
                                            },
                                            title=f"{label} vs m³/h",
                                        )
                                        st.plotly_chart(
                                            fig_scatter, width="stretch"
                                        )

                            # AI Insights for batch if available
                            if insights_generator:
                                display_batch_ai_insights(
                                    insights_generator, results, machine_type
                                )

                            # Results table
                            st.subheader("Resultados Detalhados")
                            st.dataframe(results)

                            # Download results
                            csv = results.to_csv(index=False)
                            st.download_button(
                                label="💾 Download Resultados CSV",
                                data=csv,
                                file_name=f"estimativas_{machine_type}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                            )

                    except Exception as e:
                        st.error(f"Erro ao processar arquivo: {str(e)}")

            else:  # Dados de Exemplo
                st.subheader("Dados de Exemplo")

                # Try to use real data first, fallback to dummy data
                if pedidos_df is not None:
                    sample_data = create_sample_data_from_real(pedidos_df, machine_type)
                    st.info("Usando dados reais da base de pedidos")
                else:
                    st.error("Dados não disponíveis para criar exemplos")
                    return

                st.dataframe(sample_data)

                if st.button(
                    "Testar com Dados de Exemplo", width="stretch"
                ):
                    try:
                        with st.spinner("Calculando estimativa com dados de exemplo..."):
                            results = inference.predict_orders(
                                sample_data, models[machine_type]
                            )

                        st.success("Estimativa realizada com sucesso!")

                        # Prepare sample input features for AI insights
                        sample_input_features = {}
                        feature_cols = [
                            "VL_COMPRIMENTO",
                            "VL_LARGURA",
                            "VL_GRAMATURA",
                            "QT_NRCORES",
                            "QT_PEDIDA",
                            "TX_COMPOSICAO",
                            "TX_TIPOABNT",
                            "FL_EXIGELAUDO",
                        ]
                        for col in feature_cols:
                            if col in sample_data.columns:
                                sample_input_features[col] = sample_data[col].iloc[0]

                        display_prediction_results(
                            results,
                            machine_type,
                            sample_input_features,
                            insights_generator,
                        )

                    except Exception as e:
                        st.error(f"Erro na estimativa: {str(e)}")
                        with st.expander("Detalhes do Erro"):
                            import traceback

                            st.code(traceback.format_exc())

    # Footer
    st.markdown("---")
    current_user = st.session_state.get("auth_user", "desconhecido")
    st.markdown(
        """
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>Regressor de Volume por Hora Adami</p>
        <p>Desenvolvido pelo time de IA da AMCOM para a Adami.</p>
        <p><small>Dados carregados de tb_pedidos.parquet - {}</small></p>
        <p><small>Usuário autenticado: {}</small></p>
    </div>
    """.format(
            f"{len(pedidos_df):,} registros"
            if pedidos_df is not None
            else "Dados não disponíveis",
            current_user.upper(),
        ),
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
