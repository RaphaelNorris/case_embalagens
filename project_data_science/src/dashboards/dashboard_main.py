# app2.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Set, Tuple, Optional
import datetime

# Configuração da página
st.set_page_config(
    page_title="Adami - Análise de Embalagens",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para melhor estilização
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2563EB;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #3B82F6;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }
    .insight-box {
        background-color: #EFF6FF;
        border-left: 5px solid #3B82F6;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 5px;
        padding: 1rem;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #4B5563;
    }
</style>
""", unsafe_allow_html=True)

# Funções auxiliares
@st.cache_data
def carregar_dados():
    """Carrega e armazena em cache os dados"""
    try:
        df_itens = pd.read_parquet('../data/02 - trusted/parquet/tb_itens.parquet')
        df_pedidos = pd.read_parquet('../data/02 - trusted/parquet/tb_pedidos.parquet')
        df_clientes = pd.read_parquet('../data/02 - trusted/parquet/tb_clientes.parquet')
        df_facas = pd.read_parquet('../data/02 - trusted/parquet/tb_facas.parquet')
        return df_itens, df_pedidos, df_clientes, df_facas
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None, None, None, None

def limpar_numericos_e_categoricos(df: pd.DataFrame,
                                  threshold_numerico: float = 0.9,
                                  inplace: bool = False) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """Limpa e categoriza colunas como numéricas ou categóricas"""
    if not inplace:
        df = df.copy()

    df = df.replace(r'^\s*$', np.nan, regex=True)

    # Começar com colunas já numéricas
    colunas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    outras_colunas = [c for c in df.columns if c not in colunas_numericas]

    colunas_categoricas = []

    # Tentar coerção para colunas não numéricas
    for col in outras_colunas:
        coercao = pd.to_numeric(df[col], errors='coerce')
        prop_numerica = coercao.notna().sum() / len(df)
        if prop_numerica >= threshold_numerico:
            df[col] = coercao
            colunas_numericas.append(col)
        else:
            colunas_categoricas.append(col)

    # Preencher valores
    if colunas_numericas:
        df[colunas_numericas] = df[colunas_numericas].fillna(0)
    if colunas_categoricas:
        df[colunas_categoricas] = df[colunas_categoricas].fillna('NA')

    return df, colunas_numericas, colunas_categoricas

def obter_colunas_numericas_comuns(df_pedidos: pd.DataFrame, df_itens: pd.DataFrame) -> List[str]:
    """Identifica colunas comuns que são numéricas em ambos os DataFrames"""
    comum = set(df_pedidos.columns).intersection(df_itens.columns)
    colunas_numericas = []
    for col in comum:
        s1 = pd.to_numeric(df_pedidos[col], errors='coerce')
        s2 = pd.to_numeric(df_itens[col], errors='coerce')
        if s1.notna().any() and s2.notna().any():
            colunas_numericas.append(col)
    # Remover chaves de texto que podem ser convertidas inadvertidamente
    for k in ['ID_ITEM', 'ID_PEDIDO', 'ID_IDCLIENTE']:
        if k in colunas_numericas:
            colunas_numericas.remove(k)
    return sorted(colunas_numericas)

def construir_tabela_diferencas(df_pedidos: pd.DataFrame, df_itens: pd.DataFrame, 
                    colunas_id: Optional[List[str]] = None, 
                    limite_itens: Optional[int] = None) -> pd.DataFrame:
    """Constrói uma tabela de diferenças entre pedidos e itens"""
    if colunas_id is None:
        colunas_id = [c for c in ['ID_PEDIDO', 'ID_ITEM', 'ID_IDCLIENTE'] if c in df_pedidos.columns]

    # Garantir que ID_ITEM seja comparável
    if 'ID_ITEM' in df_pedidos.columns:
        df_pedidos = df_pedidos.copy()
        df_pedidos['ID_ITEM'] = df_pedidos['ID_ITEM'].astype(str)
    if 'ID_ITEM' in df_itens.columns:
        df_itens = df_itens.copy()
        df_itens['ID_ITEM'] = df_itens['ID_ITEM'].astype(str)

    # Selecionar colunas numéricas comuns
    colunas_num_comuns = obter_colunas_numericas_comuns(df_pedidos, df_itens)
    if not colunas_num_comuns:
        return pd.DataFrame()

    # Limitar itens (opcional)
    if limite_itens is not None and 'ID_ITEM' in df_pedidos.columns:
        itens_unicos = df_pedidos['ID_ITEM'].dropna().unique()
        itens_selecionados = set(itens_unicos[:limite_itens])
        df_pedidos = df_pedidos[df_pedidos['ID_ITEM'].isin(itens_selecionados)]

    # Subconjuntos com colunas necessárias
    cols_pedidos = list(set(colunas_id + colunas_num_comuns))
    cols_itens = list(set(['ID_ITEM'] + colunas_num_comuns))

    dfp = df_pedidos[cols_pedidos].copy()
    dfi = df_itens[cols_itens].copy().drop_duplicates('ID_ITEM')

    # Coerção para numérico para colunas comuns
    for col in colunas_num_comuns:
        dfp[col] = pd.to_numeric(dfp[col], errors='coerce')
        dfi[col] = pd.to_numeric(dfi[col], errors='coerce')

    # Mesclar por ID_ITEM
    if 'ID_ITEM' not in dfp.columns:
        return pd.DataFrame()
    dfm = dfp.merge(dfi, on='ID_ITEM', how='left', suffixes=('_pedido', '_item'))

    # Calcular diferenças
    out = dfm[colunas_id].copy()
    for col in colunas_num_comuns:
        col_pedido = f"{col}_pedido"
        col_item = f"{col}_item"

        # Se os nomes não foram sufixados, ajustar:
        if col_pedido not in dfm.columns and col in dfp.columns:
            col_pedido = col
        if col_item not in dfm.columns and col in dfi.columns:
            col_item = col

        # Diferença absoluta
        diff = dfm[col_pedido] - dfm[col_item]

        # Diferença percentual com proteção contra divisão por zero
        base = dfm[col_item].replace(0, np.nan)
        diff_pct = (diff / base) * 100

        out[f"{col}_diff"] = diff
        out[f"{col}_diff_pct"] = diff_pct

    return out

# Estrutura principal do aplicativo
def main():
    # Carregar dados
    df_itens, df_pedidos, df_clientes, df_facas = carregar_dados()
    
    if df_itens is None or df_pedidos is None:
        st.warning("Por favor, verifique os caminhos dos dados e tente novamente.")
        return
    
    # Limpar e preparar dados
    df_itens_limpo, itens_cols_num, itens_cols_cat = limpar_numericos_e_categoricos(df_itens)
    df_pedidos_limpo, pedidos_cols_num, pedidos_cols_cat = limpar_numericos_e_categoricos(df_pedidos)
    
    # Converter colunas ID para string
    colunas_id = [c for c in df_pedidos_limpo.columns if c.upper().startswith('ID_') or c.upper() in ['ID_ITEM', 'ID_PEDIDO']]
    for col in colunas_id:
        if col in df_pedidos_limpo.columns:
            df_pedidos_limpo[col] = df_pedidos_limpo[col].astype(str)
    
    # Converter colunas de data para datetime
    colunas_data = [c for c in df_pedidos_limpo.columns if 'DT_' in c.upper()]
    for col in colunas_data:
        if col in df_pedidos_limpo.columns:
            df_pedidos_limpo[col] = pd.to_datetime(df_pedidos_limpo[col], errors='coerce')
    
    # Cabeçalho
    st.markdown('<div class="main-header">Dashboard de Análise de Embalagens Adami</div>', unsafe_allow_html=True)
    
    # Barra lateral
    st.sidebar.image("https://via.placeholder.com/150x80?text=Logo+Adami", use_column_width=True)
    st.sidebar.title("Navegação")
    
    pagina = st.sidebar.radio(
        "Selecione a Página",
        ["Visão Geral", "Análise de Produtos", "Análise de Pedidos", "Análise de Clientes", "Análise Comparativa", "Análise de Facas"]
    )
    
    # Seção de filtros na barra lateral
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filtros")
    
    # Filtro de data se tivermos colunas de data
    filtro_data = None
    if colunas_data:
        coluna_data_principal = next((col for col in colunas_data if 'PEDIDO' in col.upper()), colunas_data[0])
        data_min = df_pedidos_limpo[coluna_data_principal].min().date()
        data_max = df_pedidos_limpo[coluna_data_principal].max().date()
        
        filtro_data = st.sidebar.date_input(
            f"Filtrar por {coluna_data_principal}",
            value=(data_min, data_max),
            min_value=data_min,
            max_value=data_max
        )
    
    # Filtro de cliente
    if 'ID_IDCLIENTE' in df_pedidos_limpo.columns:
        clientes_principais = df_pedidos_limpo['ID_IDCLIENTE'].value_counts().head(20).index.tolist()
        clientes_selecionados = st.sidebar.multiselect(
            "Filtrar por Cliente",
            options=["Todos"] + clientes_principais,
            default="Todos"
        )
    
    # Aplicar filtros aos dados
    pedidos_filtrados = df_pedidos_limpo.copy()
    
    if filtro_data and len(filtro_data) == 2 and coluna_data_principal in pedidos_filtrados.columns:
        data_inicio, data_fim = filtro_data
        pedidos_filtrados = pedidos_filtrados[
            (pedidos_filtrados[coluna_data_principal].dt.date >= data_inicio) & 
            (pedidos_filtrados[coluna_data_principal].dt.date <= data_fim)
        ]
    
    if 'ID_IDCLIENTE' in pedidos_filtrados.columns and clientes_selecionados and "Todos" not in clientes_selecionados:
        pedidos_filtrados = pedidos_filtrados[pedidos_filtrados['ID_IDCLIENTE'].isin(clientes_selecionados)]
    
    # Conteúdo da página com base na seleção
    if pagina == "Visão Geral":
        exibir_visao_geral(df_itens_limpo, pedidos_filtrados)
    elif pagina == "Análise de Produtos":
        exibir_analise_produtos(df_itens_limpo)
    elif pagina == "Análise de Pedidos":
        exibir_analise_pedidos(pedidos_filtrados)
    elif pagina == "Análise de Clientes":
        exibir_analise_clientes(pedidos_filtrados, df_clientes)
    elif pagina == "Análise de Facas":
        exibir_analise_facas(df_facas)
    else:  # Análise Comparativa
        exibir_analise_comparativa(df_itens_limpo, pedidos_filtrados)
    
    # Rodapé
    st.markdown("---")
    st.markdown("© 2023 Adami - Análise de Embalagens | Dados atualizados em: " + 
                datetime.datetime.now().strftime("%d/%m/%Y"))

def exibir_visao_geral(df_itens, df_pedidos):
    """Exibe o dashboard de visão geral com métricas principais"""
    st.markdown('<div class="sub-header">Visão Geral do Negócio</div>', unsafe_allow_html=True)
    
    # Métricas principais em colunas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(df_itens):,}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total de Produtos</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(df_pedidos):,}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total de Pedidos</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        if 'ID_IDCLIENTE' in df_pedidos.columns:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{df_pedidos["ID_IDCLIENTE"].nunique():,}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Clientes Únicos</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">N/D</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Clientes Únicos</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        if 'QT_QUANTIDADEPEDIDA' in df_pedidos.columns:
            total_qtd = df_pedidos['QT_QUANTIDADEPEDIDA'].sum()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{total_qtd:,.0f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Quantidade Total Pedida</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">N/D</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Quantidade Total</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Gráfico de série temporal se tivermos colunas de data
    colunas_data = [c for c in df_pedidos.columns if 'DT_' in c.upper()]
    if colunas_data:
        st.markdown('<div class="section-header">Tendências de Pedidos</div>', unsafe_allow_html=True)
        
        coluna_data_principal = next((col for col in colunas_data if 'PEDIDO' in col.upper()), colunas_data[0])
        
        # Criar série temporal
        df_pedidos['ano_mes'] = df_pedidos[coluna_data_principal].dt.to_period('M')
        pedidos_por_mes = df_pedidos.groupby('ano_mes').size().reset_index(name='contagem')
        pedidos_por_mes['ano_mes_str'] = pedidos_por_mes['ano_mes'].astype(str)
        
        fig = px.line(
            pedidos_por_mes, 
            x='ano_mes_str', 
            y='contagem',
            markers=True,
            title=f'Volume Mensal de Pedidos',
            labels={'ano_mes_str': 'Mês', 'contagem': 'Número de Pedidos'}
        )
        fig.update_layout(xaxis_tickangle=45, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Distribuição de produtos e clientes
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">Distribuição de Produtos</div>', unsafe_allow_html=True)
        
        # Verificar se temos dados de dimensão
        if all(col in df_itens.columns for col in ['VL_LARGURAINTERNA', 'VL_COMPRIMENTOINTERNO', 'VL_ALTURAINTERNA']):
            # Calcular volume e criar categorias de tamanho
            df_itens['VOLUME'] = df_itens['VL_LARGURAINTERNA'] * df_itens['VL_COMPRIMENTOINTERNO'] * df_itens['VL_ALTURAINTERNA']
            df_itens['CATEGORIA_TAMANHO'] = pd.qcut(df_itens['VOLUME'], 3, labels=['Pequeno', 'Médio', 'Grande'])
            
            contagem_tamanhos = df_itens['CATEGORIA_TAMANHO'].value_counts()
            
            fig = px.pie(
                values=contagem_tamanhos.values,
                names=contagem_tamanhos.index,
                title='Distribuição de Produtos por Tamanho',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados de dimensão não disponíveis para análise de distribuição de produtos.")
    
    with col2:
        st.markdown('<div class="section-header">Concentração de Clientes</div>', unsafe_allow_html=True)
        
        if 'ID_IDCLIENTE' in df_pedidos.columns:
            # Concentração de clientes (Pareto)
            pedidos_por_cliente = df_pedidos.groupby('ID_IDCLIENTE').size().sort_values(ascending=False)
            pct_cumulativo = (pedidos_por_cliente.cumsum() / pedidos_por_cliente.sum() * 100)
            
            # Criar um DataFrame para os 20 principais clientes
            principais_clientes = pedidos_por_cliente.head(20).reset_index()
            principais_clientes.columns = ['ID_IDCLIENTE', 'Pedidos']
            principais_clientes['% Cumulativo'] = pct_cumulativo.loc[principais_clientes['ID_IDCLIENTE']].values
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Bar(
                    x=principais_clientes['ID_IDCLIENTE'],
                    y=principais_clientes['Pedidos'],
                    name='Pedidos'
                ),
                secondary_y=False
            )
            
            fig.add_trace(
                go.Scatter(
                    x=principais_clientes['ID_IDCLIENTE'],
                    y=principais_clientes['% Cumulativo'],
                    name='% Cumulativo',
                    mode='lines+markers'
                ),
                secondary_y=True
            )
            
            fig.update_layout(
                title='Top 20 Clientes por Volume de Pedidos',
                xaxis_title='ID do Cliente',
                height=400
            )
            
            fig.update_yaxes(title_text='Número de Pedidos', secondary_y=False)
            fig.update_yaxes(title_text='% Cumulativo', secondary_y=True)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados de cliente não disponíveis para análise de concentração.")
    
    # Insights principais
    st.markdown('<div class="section-header">Insights Principais do Negócio</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("**Eficiência de Produtos**")
        
        if 'VL_AREALIQUIDAPECA' in df_itens.columns and 'VL_AREABRUTAPECA' in df_itens.columns:
            df_itens['APROVEITAMENTO_perc'] = (df_itens['VL_AREALIQUIDAPECA'] / df_itens['VL_AREABRUTAPECA'] * 100).clip(0, 100)
            eficiencia_media = df_itens['APROVEITAMENTO_perc'].mean()
            baixa_eficiencia = (df_itens['APROVEITAMENTO_perc'] < 85).mean() * 100
            
            st.markdown(f"Aproveitamento médio de material: **{eficiencia_media:.1f}%**")
            st.markdown(f"Produtos com baixa eficiência (<85%): **{baixa_eficiencia:.1f}%**")
            
            if baixa_eficiencia > 20:
                st.markdown("⚠️ **Ação necessária**: Alto percentual de produtos com baixa eficiência de material.")
            else:
                st.markdown("✅ Bom aproveitamento de material em todo o portfólio de produtos.")
        else:
            st.markdown("Dados de aproveitamento de material não disponíveis.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("**Risco de Concentração de Clientes**")
        
        if 'ID_IDCLIENTE' in df_pedidos.columns:
            pedidos_por_cliente = df_pedidos.groupby('ID_IDCLIENTE').size()
            pct_principal_cliente = pedidos_por_cliente.max() / pedidos_por_cliente.sum() * 100
            pct_top5 = pedidos_por_cliente.nlargest(5).sum() / pedidos_por_cliente.sum() * 100
            
            st.markdown(f"Concentração do cliente principal: **{pct_principal_cliente:.1f}%**")
            st.markdown(f"Concentração dos 5 principais clientes: **{pct_top5:.1f}%**")
            
            if pct_principal_cliente > 30:
                st.markdown("⚠️ **Alto risco**: Dependência significativa do cliente principal.")
            elif pct_top5 > 60:
                st.markdown("⚠️ **Risco moderado**: Alta concentração nos 5 principais clientes.")
            else:
                st.markdown("✅ Base de clientes bem diversificada.")
        else:
            st.markdown("Dados de concentração de clientes não disponíveis.")
        
        st.markdown('</div>', unsafe_allow_html=True)

def exibir_analise_produtos(df_itens):
    """Exibe o dashboard de análise de produtos"""
    st.markdown('<div class="sub-header">Análise de Produtos</div>', unsafe_allow_html=True)
    
    # Análise de dimensões de produtos
    st.markdown('<div class="section-header">Dimensões dos Produtos</div>', unsafe_allow_html=True)
    
    dims = ['VL_LARGURAINTERNA', 'VL_COMPRIMENTOINTERNO', 'VL_ALTURAINTERNA']
    if all(dim in df_itens.columns for dim in dims):
        # Calcular volume
        df_itens['VOLUME'] = df_itens['VL_LARGURAINTERNA'] * df_itens['VL_COMPRIMENTOINTERNO'] * df_itens['VL_ALTURAINTERNA']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Estatísticas de dimensão
            st.markdown("**Estatísticas de Dimensão**")
            
            stats_df = pd.DataFrame({
                'Dimensão': ['Largura', 'Comprimento', 'Altura', 'Volume'],
                'Mín': [
                    df_itens['VL_LARGURAINTERNA'].min(),
                    df_itens['VL_COMPRIMENTOINTERNO'].min(),
                    df_itens['VL_ALTURAINTERNA'].min(),
                    df_itens['VOLUME'].min()
                ],
                'Máx': [
                    df_itens['VL_LARGURAINTERNA'].max(),
                    df_itens['VL_COMPRIMENTOINTERNO'].max(),
                    df_itens['VL_ALTURAINTERNA'].max(),
                    df_itens['VOLUME'].max()
                ],
                'Média': [
                    df_itens['VL_LARGURAINTERNA'].mean(),
                    df_itens['VL_COMPRIMENTOINTERNO'].mean(),
                    df_itens['VL_ALTURAINTERNA'].mean(),
                    df_itens['VOLUME'].mean()
                ],
                'Mediana': [
                    df_itens['VL_LARGURAINTERNA'].median(),
                    df_itens['VL_COMPRIMENTOINTERNO'].median(),
                    df_itens['VL_ALTURAINTERNA'].median(),
                    df_itens['VOLUME'].median()
                ]
            })
            
            st.dataframe(stats_df.round(2), hide_index=True)
        
        with col2:
            # Distribuição de tamanho
            df_itens['CATEGORIA_TAMANHO'] = pd.qcut(df_itens['VOLUME'], 3, labels=['Pequeno', 'Médio', 'Grande'])
            contagem_tamanhos = df_itens['CATEGORIA_TAMANHO'].value_counts()
            
            fig = px.pie(
                values=contagem_tamanhos.values,
                names=contagem_tamanhos.index,
                title='Distribuição de Produtos por Tamanho',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Relações de dimensão
        st.markdown("**Relações de Dimensão**")
        
        fig = px.scatter_3d(
            df_itens.sample(min(1000, len(df_itens))),
            x='VL_LARGURAINTERNA',
            y='VL_COMPRIMENTOINTERNO',
            z='VL_ALTURAINTERNA',
            color='CATEGORIA_TAMANHO',
            title='Visualização 3D das Dimensões dos Produtos',
            labels={
                'VL_LARGURAINTERNA': 'Largura',
                'VL_COMPRIMENTOINTERNO': 'Comprimento',
                'VL_ALTURAINTERNA': 'Altura'
            }
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Dados de dimensão de produtos não disponíveis.")
    
    # Análise de aproveitamento de material
    st.markdown('<div class="section-header">Aproveitamento de Material</div>', unsafe_allow_html=True)
    
    if 'VL_AREALIQUIDAPECA' in df_itens.columns and 'VL_AREABRUTAPECA' in df_itens.columns:
        df_itens['APROVEITAMENTO_perc'] = (df_itens['VL_AREALIQUIDAPECA'] / df_itens['VL_AREABRUTAPECA'] * 100).clip(0, 100)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Estatísticas de aproveitamento
            st.markdown("**Estatísticas de Aproveitamento de Material**")
            
            stats_util = df_itens['APROVEITAMENTO_perc'].describe()
            st.dataframe(pd.DataFrame({
                'Estatística': ['Média', 'Mediana', 'Mínimo', 'Máximo', 'Desvio Padrão'],
                'Valor': [
                    f"{stats_util['mean']:.2f}%",
                    f"{stats_util['50%']:.2f}%",
                    f"{stats_util['min']:.2f}%",
                    f"{stats_util['max']:.2f}%",
                    f"{stats_util['std']:.2f}%"
                ]
            }), hide_index=True)
        
        with col2:
            # Distribuição de aproveitamento
            fig = px.histogram(
                df_itens,
                x='APROVEITAMENTO_perc',
                nbins=20,
                title='Distribuição do Aproveitamento de Material',
                labels={'APROVEITAMENTO_perc': 'Aproveitamento de Material (%)'}
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Aproveitamento por categoria de tamanho
        if 'CATEGORIA_TAMANHO' in df_itens.columns:
            st.markdown("**Aproveitamento de Material por Tamanho do Produto**")
            
            util_por_tamanho = df_itens.groupby('CATEGORIA_TAMANHO')['APROVEITAMENTO_perc'].mean().reset_index()
            
            fig = px.bar(
                util_por_tamanho,
                x='CATEGORIA_TAMANHO',
                y='APROVEITAMENTO_perc',
                title='Aproveitamento Médio de Material por Tamanho do Produto',
                labels={
                    'CATEGORIA_TAMANHO': 'Tamanho do Produto',
                    'APROVEITAMENTO_perc': 'Aproveitamento Médio de Material (%)'
                }
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Dados de aproveitamento de material não disponíveis.")
    
    # Análise de flags de processo
    st.markdown('<div class="section-header">Análise de Processo de Produção</div>', unsafe_allow_html=True)
    
    flags = ['FL_REFILADO', 'FL_AMARRADO', 'FL_PALETIZADO', 'FL_ESPELHO', 'FL_FILME']
    flags_disponiveis = [flag for flag in flags if flag in df_itens.columns]
    
    if flags_disponiveis:
        # Distribuição de flags de processo
        dados_flag = []
        for flag in flags_disponiveis:
            contagem_sim = (df_itens[flag] == 1).sum()
            contagem_nao = (df_itens[flag] == 0).sum()
            dados_flag.append({
                'Processo': flag.replace('FL_', ''),
                'Sim': contagem_sim,
                'Não': contagem_nao,
                'Sim_pct': contagem_sim / len(df_itens) * 100
            })
        
        df_flag = pd.DataFrame(dados_flag)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Tabela de flags de processo
            st.markdown("**Distribuição de Flags de Processo**")
            
            df_exibicao = df_flag[['Processo', 'Sim', 'Não', 'Sim_pct']].copy()
            df_exibicao['Sim_pct'] = df_exibicao['Sim_pct'].round(2).astype(str) + '%'
            df_exibicao.columns = ['Processo', 'Contagem Sim', 'Contagem Não', 'Percentual Sim']
            
            st.dataframe(df_exibicao, hide_index=True)
        
        with col2:
            # Gráfico de flags de processo
            fig = px.bar(
                df_flag,
                x='Processo',
                y='Sim_pct',
                title='Percentual de Produtos com Flags de Processo',
                labels={'Processo': 'Processo', 'Sim_pct': 'Percentual (%)'}
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Dados de flag de processo não disponíveis.")
    
    # Análise de paletização
    st.markdown('<div class="section-header">Análise de Paletização</div>', unsafe_allow_html=True)
    
    cols_palet = ['QT_PECASPORPACOTE', 'QT_PACOTESPORPALETE', 'QT_PECASPORPALETE']
    cols_palet_disponiveis = [col for col in cols_palet if col in df_itens.columns]
    
    if cols_palet_disponiveis:
        col1, col2 = st.columns(2)
        
        with col1:
            # Estatísticas de paletização
            st.markdown("**Estatísticas de Paletização**")
            
            stats_palet = []
            for col in cols_palet_disponiveis:
                stats = df_itens[col].describe()
                stats_palet.append({
                    'Métrica': col.replace('QT_PECAS', 'Peças').replace('QT_PACOTES', 'Pacotes').replace('POR', ' por '), 'Média': stats['mean'], 'Mediana': stats['50%'], 'Mínimo': stats['min'], 'Máximo': stats['max'] })
            df_stats_palet = pd.DataFrame(stats_palet)
            st.dataframe(df_stats_palet.round(2), hide_index=True)
        
        with col2:
            # Distribuição de peças por palete
            if 'QT_PECASPORPALETE' in cols_palet_disponiveis:
                fig = px.histogram(
                    df_itens,
                    x='QT_PECASPORPALETE',
                    nbins=20,
                    title='Distribuição de Peças por Palete',
                    labels={'QT_PECASPORPALETE': 'Peças por Palete'}
                )
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Dados de paletização não disponíveis.")
def exibir_analise_pedidos(df_pedidos):
    """Exibe o dashboard de análise de pedidos"""
    st.markdown('<div class="sub-header">Análise de Pedidos</div>', unsafe_allow_html=True)
    # Métricas de volume de pedidos
    st.markdown('<div class="section-header">Volume de Pedidos</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(df_pedidos):,}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total de Pedidos</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if 'ID_ITEM' in df_pedidos.columns:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{df_pedidos["ID_ITEM"].nunique():,}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Produtos Únicos Pedidos</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">N/D</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Produtos Únicos</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        if 'QT_QUANTIDADEPEDIDA' in df_pedidos.columns:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{df_pedidos["QT_QUANTIDADEPEDIDA"].sum():,.0f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Quantidade Total Pedida</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">N/D</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Quantidade Total</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Análise de série temporal
    colunas_data = [c for c in df_pedidos.columns if 'DT_' in c.upper()]
    if colunas_data:
        st.markdown('<div class="section-header">Tendências de Pedidos</div>', unsafe_allow_html=True)

        # Selecionar coluna de data para análise
        coluna_data = st.selectbox(
            "Selecione o campo de data para análise de tendência:",
            colunas_data
        )

        # Criar série temporal por mês
        df_pedidos['ano_mes'] = df_pedidos[coluna_data].dt.to_period('M')
        pedidos_por_mes = df_pedidos.groupby('ano_mes').size().reset_index(name='contagem')
        pedidos_por_mes['ano_mes_str'] = pedidos_por_mes['ano_mes'].astype(str)

        # Criar série temporal por dia da semana
        df_pedidos['dia_semana'] = df_pedidos[coluna_data].dt.day_name()
        ordem_dias = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
        pedidos_por_dia = df_pedidos.groupby('dia_semana').size().reindex(ordem_dias).reset_index(name='contagem')

        col1, col2 = st.columns(2)

        with col1:
            # Tendência mensal
            fig = px.line(
                pedidos_por_mes,
                x='ano_mes_str',
                y='contagem',
                markers=True,
                title=f'Volume Mensal de Pedidos',
                labels={'ano_mes_str': 'Mês', 'contagem': 'Número de Pedidos'}
            )
            fig.update_layout(xaxis_tickangle=45, height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Distribuição por dia da semana
            fig = px.bar(
                pedidos_por_dia,
                x='dia_semana',
                y='contagem',
                title='Distribuição de Pedidos por Dia da Semana',
                labels={'dia_semana': 'Dia da Semana', 'contagem': 'Número de Pedidos'}
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        # Análise de sazonalidade
        st.markdown("**Análise de Sazonalidade**")

        # Criar agregação apenas por mês para sazonalidade
        df_pedidos['mes'] = df_pedidos[coluna_data].dt.month
        pedidos_por_mes_apenas = df_pedidos.groupby('mes').size().reset_index(name='contagem')
        pedidos_por_mes_apenas['nome_mes'] = pedidos_por_mes_apenas['mes'].apply(lambda x: datetime.date(2000, x, 1).strftime('%B'))

        fig = px.bar(
            pedidos_por_mes_apenas.sort_values('mes'),
            x='nome_mes',
            y='contagem',
            title='Padrão Sazonal: Pedidos por Mês',
            labels={'nome_mes': 'Mês', 'contagem': 'Número de Pedidos'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Informações de data não disponíveis para análise de tendência.")

    # Análise de status de pedido
    st.markdown('<div class="section-header">Análise de Status de Pedido</div>', unsafe_allow_html=True)

    colunas_status = [col for col in df_pedidos.columns if 'ST_' in col.upper()]
    if colunas_status:
        # Selecionar coluna de status para análise
        coluna_status = st.selectbox(
            "Selecione o campo de status para análise:",
            colunas_status
        )

        contagem_status = df_pedidos[coluna_status].value_counts()

        col1, col2 = st.columns(2)

        with col1:
            # Tabela de distribuição de status
            st.markdown("**Distribuição de Status de Pedido**")

            df_status = pd.DataFrame({
                'Status': contagem_status.index,
                'Contagem': contagem_status.values,
                'Percentual': (contagem_status.values / contagem_status.sum() * 100).round(2)
            })

            st.dataframe(df_status, hide_index=True)

        with col2:
            # Gráfico de distribuição de status
            fig = px.pie(
                values=contagem_status.values,
                names=contagem_status.index,
                title='Distribuição de Status de Pedido',
                hole=0.4
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        # Status ao longo do tempo se tivermos dados de data
        if colunas_data:
            st.markdown("**Evolução de Status ao Longo do Tempo**")

            coluna_data_principal = next((col for col in colunas_data if 'PEDIDO' in col.upper()), colunas_data[0])
            df_pedidos['ano_mes'] = df_pedidos[coluna_data_principal].dt.to_period('M')
            df_pedidos['ano_mes_str'] = df_pedidos['ano_mes'].astype(str)

            status_por_mes = df_pedidos.groupby(['ano_mes_str', coluna_status]).size().reset_index(name='contagem')

            fig = px.bar(
                status_por_mes,
                x='ano_mes_str',
                y='contagem',
                color=coluna_status,
                title='Evolução de Status de Pedido ao Longo do Tempo',
                labels={'ano_mes_str': 'Mês', 'contagem': 'Número de Pedidos'}
            )
            fig.update_layout(xaxis_tickangle=45, height=500)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Informações de status não disponíveis para análise.")

    # Análise de quantidade de pedido
    st.markdown('<div class="section-header">Análise de Quantidade de Pedido</div>', unsafe_allow_html=True)

    if 'QT_QUANTIDADEPEDIDA' in df_pedidos.columns:
        col1, col2 = st.columns(2)

        with col1:
            # Estatísticas de quantidade
            st.markdown("**Estatísticas de Quantidade de Pedido**")

            stats_qtd = df_pedidos['QT_QUANTIDADEPEDIDA'].describe()
            st.dataframe(pd.DataFrame({
                'Estatística': ['Média', 'Mediana', 'Mínimo', 'Máximo', 'Desvio Padrão'],
                'Valor': [
                    f"{stats_qtd['mean']:.2f}",
                    f"{stats_qtd['50%']:.2f}",
                    f"{stats_qtd['min']:.2f}",
                    f"{stats_qtd['max']:.2f}",
                    f"{stats_qtd['std']:.2f}"
                ]
            }), hide_index=True)

        with col2:
            # Distribuição de quantidade
            fig = px.histogram(
                df_pedidos,
                x='QT_QUANTIDADEPEDIDA',
                nbins=20,
                title='Distribuição de Quantidades de Pedido',
                labels={'QT_QUANTIDADEPEDIDA': 'Quantidade Pedida'}
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        # Principais produtos por quantidade
        if 'ID_ITEM' in df_pedidos.columns:
            st.markdown("**Principais Produtos por Quantidade Pedida**")

            qtd_por_produto = df_pedidos.groupby('ID_ITEM')['QT_QUANTIDADEPEDIDA'].sum().sort_values(ascending=False)

            fig = px.bar(
                x=qtd_por_produto.index[:15],
                y=qtd_por_produto.values[:15],
                title='Top 15 Produtos por Quantidade Total Pedida',
                labels={'x': 'ID do Produto', 'y': 'Quantidade Total'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Dados de quantidade de pedido não disponíveis para análise.")

def exibir_analise_clientes(df_pedidos, df_clientes): 
    """Exibe o dashboard de análise de clientes""" 
    st.markdown('Análise de Clientes', unsafe_allow_html=True)  
    if 'ID_IDCLIENTE' not in df_pedidos.columns:
        st.warning("Informações de ID de cliente não disponíveis no conjunto de dados.")
        return

    # Métricas de cliente
    st.markdown('<div class="section-header">Visão Geral de Clientes</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{df_pedidos["ID_IDCLIENTE"].nunique():,}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total de Clientes</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        media_pedidos = len(df_pedidos) / df_pedidos["ID_IDCLIENTE"].nunique()
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{media_pedidos:.1f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Média de Pedidos por Cliente</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        if 'QT_QUANTIDADEPEDIDA' in df_pedidos.columns:
            media_qtd = df_pedidos['QT_QUANTIDADEPEDIDA'].sum() / df_pedidos["ID_IDCLIENTE"].nunique()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{media_qtd:.1f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Média de Quantidade por Cliente</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">N/D</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Média de Quantidade por Cliente</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Análise de concentração de clientes
    st.markdown('<div class="section-header">Concentração de Clientes</div>', unsafe_allow_html=True)

    # Pedidos por cliente
    pedidos_por_cliente = df_pedidos.groupby('ID_IDCLIENTE').size().sort_values(ascending=False)

    # Calcular percentuais cumulativos
    total_pedidos = pedidos_por_cliente.sum()
    pct_pedidos_por_cliente = pedidos_por_cliente / total_pedidos * 100
    pct_cumulativo = pct_pedidos_por_cliente.cumsum()

    # Criar classificação ABC
    classe_cliente = pd.DataFrame({
        'pedidos': pedidos_por_cliente,
        'percentual': pct_pedidos_por_cliente,
        'cumulativo': pct_cumulativo
    })

    classe_cliente['classe'] = 'C'
    classe_cliente.loc[classe_cliente['cumulativo'] <= 80, 'classe'] = 'A'
    classe_cliente.loc[(classe_cliente['cumulativo'] > 80) & (classe_cliente['cumulativo'] <= 95), 'classe'] = 'B'

    # Contar clientes por classe
    clientes_por_classe = classe_cliente['classe'].value_counts().reindex(['A', 'B', 'C'])

    col1, col2 = st.columns(2)

    with col1:
        # Tabela de análise ABC
        st.markdown("**Análise ABC de Clientes**")
        
        abc_df = pd.DataFrame({
            'Classe': ['A', 'B', 'C'],
            'Clientes': [
                clientes_por_classe['A'],
                clientes_por_classe['B'],
                clientes_por_classe['C']
            ],
            'Percentual': [
                clientes_por_classe['A'] / len(classe_cliente) * 100,
                clientes_por_classe['B'] / len(classe_cliente) * 100,
                clientes_por_classe['C'] / len(classe_cliente) * 100
            ],
            'Pedidos %': [80, 15, 5]
        })
        
        abc_df['Percentual'] = abc_df['Percentual'].round(2).astype(str) + '%'
        abc_df['Pedidos %'] = abc_df['Pedidos %'].astype(str) + '%'
        
        st.dataframe(abc_df, hide_index=True)

    with col2:
        # Gráfico de análise ABC
        fig = px.pie(
            values=[clientes_por_classe['A'], clientes_por_classe['B'], clientes_por_classe['C']],
            names=['A', 'B', 'C'],
            title='Distribuição de Clientes por Classe ABC',
            hole=0.4
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    # Gráfico de Pareto
    st.markdown("**Análise de Pareto de Clientes**")

    # Criar um DataFrame para os 50 principais clientes
    principais_clientes = classe_cliente.head(50).reset_index()
    principais_clientes.columns = ['ID_IDCLIENTE', 'Pedidos', 'Percentual', 'Cumulativo', 'Classe']

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=principais_clientes['ID_IDCLIENTE'],
            y=principais_clientes['Pedidos'],
            name='Pedidos',
            marker_color=principais_clientes['Classe'].map({'A': '#1E40AF', 'B': '#60A5FA', 'C': '#BFDBFE'})
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=principais_clientes['ID_IDCLIENTE'],
            y=principais_clientes['Cumulativo'],
            name='% Cumulativo',
            mode='lines+markers',
            line=dict(color='red', width=2)
        ),
        secondary_y=True
    )

    # Adicionar linhas de referência para 80% e 95%
    fig.add_shape(
        type="line",
        x0=principais_clientes['ID_IDCLIENTE'].iloc[0],
        y0=80,
        x1=principais_clientes['ID_IDCLIENTE'].iloc[-1],
        y1=80,
        line=dict(color="green", width=2, dash="dash"),
        yref='y2'
    )

    fig.add_shape(
        type="line",
        x0=principais_clientes['ID_IDCLIENTE'].iloc[0],
        y0=95,
        x1=principais_clientes['ID_IDCLIENTE'].iloc[-1],
        y1=95,
        line=dict(color="orange", width=2, dash="dash"),
        yref='y2'
    )

    fig.update_layout(
        title='Top 50 Clientes - Análise de Pareto',
        xaxis_title='ID do Cliente',
        height=500,
        legend=dict(x=0.01, y=0.99)
    )

    fig.update_yaxes(title_text='Número de Pedidos', secondary_y=False)
    fig.update_yaxes(title_text='% Cumulativo', secondary_y=True, range=[0, 100])

    st.plotly_chart(fig, use_container_width=True)

    # Padrões de pedido de clientes
    st.markdown('<div class="section-header">Padrões de Pedido de Clientes</div>', unsafe_allow_html=True)

    # Selecionar principais clientes para análise detalhada
    top_n_clientes = min(20, df_pedidos['ID_IDCLIENTE'].nunique())
    lista_principais_clientes = pedidos_por_cliente.head(top_n_clientes).index.tolist()

    cliente_selecionado = st.selectbox(
        "Selecione um cliente para análise detalhada:",
        ["Todos"] + lista_principais_clientes
    )

    if cliente_selecionado != "Todos":
        pedidos_cliente = df_pedidos[df_pedidos['ID_IDCLIENTE'] == cliente_selecionado]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(pedidos_cliente):,}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total de Pedidos</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            if 'ID_ITEM' in pedidos_cliente.columns:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{pedidos_cliente["ID_ITEM"].nunique():,}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Produtos Únicos</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-value">N/D</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Produtos Únicos</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            if 'QT_QUANTIDADEPEDIDA' in pedidos_cliente.columns:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{pedidos_cliente["QT_QUANTIDADEPEDIDA"].sum():,.0f}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Quantidade Total</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-value">N/D</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Quantidade Total</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Série temporal para cliente se tivermos dados de data
        colunas_data = [c for c in pedidos_cliente.columns if 'DT_' in c.upper()]
        if colunas_data:
            coluna_data_principal = next((col for col in colunas_data if 'PEDIDO' in col.upper()), colunas_data[0])
            
            pedidos_cliente['ano_mes'] = pedidos_cliente[coluna_data_principal].dt.to_period('M')
            pedidos_por_mes = pedidos_cliente.groupby('ano_mes').size().reset_index(name='contagem')
            pedidos_por_mes['ano_mes_str'] = pedidos_por_mes['ano_mes'].astype(str)
            
            fig = px.line(
                pedidos_por_mes, 
                x='ano_mes_str', 
                y='contagem',
                markers=True,
                title=f'Volume Mensal de Pedidos para o Cliente {cliente_selecionado}',
                labels={'ano_mes_str': 'Mês', 'contagem': 'Número de Pedidos'}
            )
            fig.update_layout(xaxis_tickangle=45, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Principais produtos para este cliente
        if 'ID_ITEM' in pedidos_cliente.columns:
            st.markdown("**Principais Produtos para o Cliente Selecionado**")
            
            contagem_produtos = pedidos_cliente['ID_ITEM'].value_counts().head(10)
            
            fig = px.bar(
                x=contagem_produtos.index,
                y=contagem_produtos.values,
                title=f'Top 10 Produtos para o Cliente {cliente_selecionado}',
                labels={'x': 'ID do Produto', 'y': 'Número de Pedidos'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    else:
        # Distribuição de frequência de pedidos de clientes
        st.markdown("**Distribuição de Frequência de Pedidos de Clientes**")
        
        # Criar bins de frequência
        freq_pedidos = pedidos_por_cliente.reset_index()
        freq_pedidos.columns = ['ID_IDCLIENTE', 'ContagemPedidos']
        
        # Criar categorias de frequência
        bins = [0, 1, 5, 10, 20, 50, 100, 1000, float('inf')]
        labels = ['1', '2-5', '6-10', '11-20', '21-50', '51-100', '101-1000', '1000+']
        freq_pedidos['BinFrequencia'] = pd.cut(freq_pedidos['ContagemPedidos'], bins=bins, labels=labels)
        
        contagem_freq = freq_pedidos['BinFrequencia'].value_counts().sort_index()
        
        fig = px.bar(
            x=contagem_freq.index,
            y=contagem_freq.values,
            title='Distribuição de Clientes por Frequência de Pedidos',
            labels={'x': 'Número de Pedidos', 'y': 'Número de Clientes'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Análise de recência de cliente se tivermos dados de data
        colunas_data = [c for c in df_pedidos.columns if 'DT_' in c.upper()]
        if colunas_data:
            st.markdown("**Análise de Recência de Clientes**")
            
            coluna_data_principal = next((col for col in colunas_data if 'PEDIDO' in col.upper()), colunas_data[0])
            
            # Obter a data do pedido mais recente para cada cliente
            ultimo_pedido_cliente = df_pedidos.groupby('ID_IDCLIENTE')[coluna_data_principal].max().reset_index()
            
            # Calcular dias desde o último pedido
            data_max = ultimo_pedido_cliente[coluna_data_principal].max()
            ultimo_pedido_cliente['DiasDesdePedido'] = (data_max - ultimo_pedido_cliente[coluna_data_principal]).dt.days
            
            # Criar bins de recência
            bins = [0, 30, 90, 180, 365, float('inf')]
            labels = ['< 30 dias', '30-90 dias', '90-180 dias', '180-365 dias', '> 365 dias']
            ultimo_pedido_cliente['BinRecencia'] = pd.cut(ultimo_pedido_cliente['DiasDesdePedido'], bins=bins, labels=labels)
            
            contagem_recencia = ultimo_pedido_cliente['BinRecencia'].value_counts().sort_index()
            
            fig = px.bar(
                x=contagem_recencia.index,
                y=contagem_recencia.values,
                title='Distribuição de Clientes por Recência',
                labels={'x': 'Tempo Desde o Último Pedido', 'y': 'Número de Clientes'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)    


def exibir_analise_facas(df_facas): 
    """Exibe o dashboard de análise de facas""" 
    st.markdown('Análise de Facas', unsafe_allow_html=True)
    # Verificar se temos os dados necessários
    if df_facas is None:
        st.warning("Dados de facas não disponíveis.")
        return

    # Métricas principais
    st.markdown('<div class="section-header">Visão Geral de Facas</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(df_facas):,}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Total de Facas</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if 'ST_STATUS' in df_facas.columns:
            facas_ativas = df_facas[df_facas['ST_STATUS'] != '5.0'].shape[0]
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{facas_ativas:,}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Facas Ativas</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">N/D</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Facas Ativas</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        if 'FL_DESATIVADOSN' in df_facas.columns:
            facas_desativadas = df_facas[df_facas['FL_DESATIVADOSN'] == 'Y'].shape[0]
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{facas_desativadas:,}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Facas Desativadas</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-value">N/D</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Facas Desativadas</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Análise de status
    if 'ST_STATUS' in df_facas.columns:
        st.markdown('<div class="section-header">Análise de Status de Facas</div>', unsafe_allow_html=True)
        
        # Mapeamento de status para descrições mais amigáveis
        status_map = {
            '1.0': 'Ativo',
            '2.0': 'Em Manutenção',
            '3.0': 'Reservado',
            '4.0': 'Indisponível',
            '5.0': 'Desmobilizado'
        }
        
        # Adicionar coluna com rótulos de status
        df_facas['STATUS_LABEL'] = df_facas['ST_STATUS'].map(status_map)
        
        # Contagem de status
        contagem_status = df_facas['STATUS_LABEL'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Tabela de status
            st.markdown("**Distribuição de Status de Facas**")
            
            df_status = pd.DataFrame({
                'Status': contagem_status.index,
                'Contagem': contagem_status.values,
                'Percentual': (contagem_status.values / contagem_status.sum() * 100).round(2)
            })
            
            st.dataframe(df_status, hide_index=True)
        
        with col2:
            # Gráfico de status
            fig = px.pie(
                values=contagem_status.values,
                names=contagem_status.index,
                title='Distribuição de Status de Facas',
                hole=0.4
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

    # Análise de comprimento de lâmina
    if 'VL_COMPLAMINA' in df_facas.columns:
        st.markdown('<div class="section-header">Análise de Comprimento de Lâmina</div>', unsafe_allow_html=True)
        
        # Estatísticas de comprimento
        stats_comp = df_facas['VL_COMPLAMINA'].describe()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Tabela de estatísticas
            st.markdown("**Estatísticas de Comprimento de Lâmina**")
            
            st.dataframe(pd.DataFrame({
                'Estatística': ['Média', 'Mediana', 'Mínimo', 'Máximo', 'Desvio Padrão'],
                'Valor (mm)': [
                    f"{stats_comp['mean']:.2f}",
                    f"{stats_comp['50%']:.2f}",
                    f"{stats_comp['min']:.2f}",
                    f"{stats_comp['max']:.2f}",
                    f"{stats_comp['std']:.2f}"
                ]
            }), hide_index=True)
        
        with col2:
            # Histograma de comprimento
            fig = px.histogram(
                df_facas,
                x='VL_COMPLAMINA',
                nbins=20,
                title='Distribuição de Comprimento de Lâmina',
                labels={'VL_COMPLAMINA': 'Comprimento da Lâmina (mm)'}
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        # Comprimento por status
        if 'STATUS_LABEL' in df_facas.columns:
            st.markdown("**Comprimento de Lâmina por Status**")
            
            fig = px.box(
                df_facas,
                x='STATUS_LABEL',
                y='VL_COMPLAMINA',
                title='Distribuição de Comprimento de Lâmina por Status',
                labels={'STATUS_LABEL': 'Status', 'VL_COMPLAMINA': 'Comprimento da Lâmina (mm)'},
                color='STATUS_LABEL'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Comprimento por status e desativação
        if 'STATUS_LABEL' in df_facas.columns and 'FL_DESATIVADOSN' in df_facas.columns:
            st.markdown("**Comprimento de Lâmina por Status e Desativação**")
            
            fig = px.histogram(
                    df_facas,
                    x='VL_COMPLAMINA',
                    color='FL_DESATIVADOSN',
                    facet_col='STATUS_LABEL',
                    title='Distribuição de Comprimento de Lâmina por Status e Desativação',
                    labels={'VL_COMPLAMINA': 'Comprimento da Lâmina (mm)', 'FL_DESATIVADOSN': 'Desativado (S/N)', 'STATUS_LABEL': 'Status' }, 
                    color_discrete_map={'Y': 'red', 'N': 'blue'}, 
                    opacity=0.7, nbins=15 ) 
            
            fig.update_layout(height=500) 
            st.plotly_chart(fig, use_container_width=True)
        # Análise de inconsistências
        if 'ST_STATUS' in df_facas.columns and 'FL_DESATIVADOSN' in df_facas.columns:
            st.markdown('<div class="section-header">Análise de Inconsistências</div>', unsafe_allow_html=True)
            
            # Verificar inconsistências entre status e flag de desativação
            inconsistencias = df_facas[(df_facas['ST_STATUS'] == '5.0') & (df_facas['FL_DESATIVADOSN'] == 'N')]
            
            if len(inconsistencias) > 0:
                st.warning(f"Encontradas {len(inconsistencias)} facas com status 'Desmobilizado' mas não marcadas como desativadas.")
                
                # Mostrar detalhes das inconsistências
                st.dataframe(inconsistencias, use_container_width=True)
            else:
                st.success("Não foram encontradas inconsistências entre status e flag de desativação.")       

def exibir_analise_comparativa(df_itens, df_pedidos): 
    """Exibe análise comparativa entre itens e pedidos""" 
    st.markdown('Análise Comparativa: Itens vs Pedidos', unsafe_allow_html=True)
    # Comparação de estrutura
    st.markdown('<div class="section-header">Comparação de Estrutura de Dados</div>', unsafe_allow_html=True)

    # Comparar colunas
    cols_itens = set(df_itens.columns)
    cols_pedidos = set(df_pedidos.columns)

    cols_comuns = cols_itens.intersection(cols_pedidos)
    exclusivas_itens = cols_itens - cols_pedidos
    exclusivas_pedidos = cols_pedidos - cols_itens

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(cols_comuns)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Colunas Comuns</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(exclusivas_itens)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Colunas Exclusivas de Itens</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(exclusivas_pedidos)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Colunas Exclusivas de Pedidos</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Visualizar distribuição de colunas
    fig = px.pie(
        values=[len(cols_comuns), len(exclusivas_itens), len(exclusivas_pedidos)],
        names=['Comuns', 'Exclusivas de Itens', 'Exclusivas de Pedidos'],
        title='Distribuição de Colunas Entre Itens e Pedidos',
        hole=0.4
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Mostrar listas de colunas
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Colunas Exclusivas de Itens**")
        st.write(sorted(exclusivas_itens))

    with col2:
        st.markdown("**Colunas Exclusivas de Pedidos**")
        st.write(sorted(exclusivas_pedidos))

    # Análise de cobertura de itens
    st.markdown('<div class="section-header">Análise de Cobertura de Itens</div>', unsafe_allow_html=True)

    if 'ID_ITEM' in df_itens.columns and 'ID_ITEM' in df_pedidos.columns:
        # Converter ID_ITEM para string em ambos os dataframes
        df_itens_item = df_itens['ID_ITEM'].astype(str)
        df_pedidos_item = df_pedidos['ID_ITEM'].astype(str)
        
        # Obter itens únicos em cada conjunto de dados
        itens_em_itens = set(df_itens_item.unique())
        itens_em_pedidos = set(df_pedidos_item.unique())
        
        # Calcular interseções
        itens_comuns = itens_em_itens.intersection(itens_em_pedidos)
        itens_apenas_em_itens = itens_em_itens - itens_em_pedidos
        itens_apenas_em_pedidos = itens_em_pedidos - itens_em_itens
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(itens_comuns):,}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Itens em Ambos</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(itens_apenas_em_itens):,}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Itens sem Pedidos</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(itens_apenas_em_pedidos):,}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Pedidos sem Registro de Item</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Visualizar cobertura de itens
        fig = px.bar(
            x=['Itens em Ambos', 'Itens sem Pedidos', 'Pedidos sem Registro de Item'],
            y=[len(itens_comuns), len(itens_apenas_em_itens), len(itens_apenas_em_pedidos)],
            title='Análise de Cobertura de Itens',
            labels={'x': 'Categoria', 'y': 'Contagem'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Coluna ID_ITEM não encontrada em ambos os conjuntos de dados para análise de cobertura.")

    # Comparação de valores para colunas comuns
    st.markdown('<div class="section-header">Comparação de Valores para Atributos Comuns</div>', unsafe_allow_html=True)

    # Obter colunas numéricas comuns
    colunas_numericas_comuns = obter_colunas_numericas_comuns(df_pedidos, df_itens)

    if colunas_numericas_comuns:
        st.markdown("**Colunas Numéricas Comuns**")
        st.write(colunas_numericas_comuns)
        
        # Calcular diferenças entre pedidos e itens
        tabela_diff = construir_tabela_diferencas(df_pedidos, df_itens, limite_itens=1000)
        
        if not tabela_diff.empty:
            # Calcular estatísticas sobre diferenças
            stats_diff = {}
            for col in colunas_numericas_comuns:
                col_diff = f"{col}_diff"
                col_diff_pct = f"{col}_diff_pct"
                
                if col_diff in tabela_diff.columns and col_diff_pct in tabela_diff.columns:
                    stats_diff[col] = {
                        'media_diff': tabela_diff[col_diff].mean(),
                        'media_diff_pct': tabela_diff[col_diff_pct].mean(),
                        'itens_com_diff': (tabela_diff[col_diff].abs() > 0.01).sum(),
                        'pct_itens_com_diff': (tabela_diff[col_diff].abs() > 0.01).mean() * 100
                    }
            
            if stats_diff:
                df_stats_diff = pd.DataFrame.from_dict(stats_diff, orient='index')
                
                # Exibir estatísticas
                st.markdown("**Estatísticas de Diferença**")
                
                df_exibicao = df_stats_diff.copy()
                df_exibicao['media_diff_pct'] = df_exibicao['media_diff_pct'].round(2).astype(str) + '%'
                df_exibicao['pct_itens_com_diff'] = df_exibicao['pct_itens_com_diff'].round(2).astype(str) + '%'
                df_exibicao.columns = ['Diferença Média', 'Diferença Média %', 'Itens com Diferença', 'Itens com Diferença %']
                
                st.dataframe(df_exibicao, use_container_width=True)
                
                # Visualizar diferenças
                st.markdown("**Percentual de Itens com Diferenças**")
                
                fig = px.bar(
                    x=df_stats_diff.index,
                    y=df_stats_diff['pct_itens_com_diff'],
                    title='Percentual de Itens com Diferenças Entre Pedidos e Catálogo',
                    labels={'x': 'Atributo', 'y': 'Itens com Diferença (%)'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Mostrar exemplos de diferenças
                st.markdown("**Exemplos de Itens com Diferenças Significativas**")
                
                # Encontrar itens com grandes diferenças
                diffs_significativas = tabela_diff[tabela_diff[f"{colunas_numericas_comuns[0]}_diff_pct"].abs() > 5]
                if not diffs_significativas.empty:
                    st.dataframe(diffs_significativas.head(10), use_container_width=True)
                else:
                    st.info("Não foram encontrados itens com diferenças significativas.")
            else:
                st.info("Não foi possível calcular estatísticas de diferença.")
        else:
            st.info("Não foi possível gerar dados de diferença.")
    else:
        st.info("Não foram encontradas colunas numéricas comuns para comparação de valores.")

    # Explicação do modelo conceitual
    st.markdown('<div class="section-header">Modelo Conceitual de Dados</div>', unsafe_allow_html=True)

    st.markdown("""
    ### Relação Entre Itens e Pedidos

    Com base na análise, podemos inferir o seguinte modelo conceitual:

    1. **Tabela de Itens (tb_itens)**
    - Contém o catálogo mestre de todos os produtos
    - Cada registro representa um produto único identificado por ID_ITEM
    - Armazena as características atuais/mais recentes de cada produto
    - Funciona como uma tabela de referência/catálogo

    2. **Tabela de Pedidos (tb_pedidos)**
    - Contém pedidos feitos por clientes
    - Cada registro representa um pedido específico para um item
    - Armazena as características do item no momento em que o pedido foi feito
    - Inclui informações adicionais como status do pedido, datas de entrega, quantidades

    3. **Relacionamento**
    - Um item pode ter zero, um ou vários pedidos
    - Cada pedido está associado a exatamente um item
    - As características do item podem mudar ao longo do tempo, mas o pedido mantém as características de quando foi feito

    ### Diferenças Principais

    1. **Temporalidade**: 
    - Itens: representa o estado atual do produto
    - Pedidos: representa o estado do produto no momento do pedido (histórico)

    2. **Informações Exclusivas**:
    - Pedidos: contém informações de transação (status, datas, quantidades)
    - Itens: contém informações técnicas e de produção atualizadas

    3. **Propósito**:
    - Itens: referência para produtos disponíveis
    - Pedidos: registro de transações comerciais e histórico
    """)   
        
if __name__ == "__main__":
    main()

     