# 📊 Dashboards Module

## Propósito
**Dashboards interativos** construídos com Streamlit para análise e monitoramento.

## Estrutura

```
dashboards/
├── dashboard_main.py          # Dashboard principal (multi-página)
├── dashboard_facas.py         # Dashboard de facas/lâminas
├── components/
│   └── ui.py                  # Componentes UI reutilizáveis
├── pages/                     # Páginas adicionais (futuro)
├── utils/                     # Utilitários específicos
└── config/                    # Configurações de dashboards
```

---

## Dashboards Disponíveis

### 📊 `dashboard_main.py`

Dashboard principal com múltiplas análises.

**Funcionalidades:**
- 📈 Análise temporal de produção
- 🏭 Performance de máquinas
- 📦 Análise de pedidos e itens
- ⏸️ Análise de paradas
- 🔪 Gestão de facas
- 👥 Análise de clientes (ABC)

**Executar:**
```bash
# Via Makefile
make app-main

# Ou diretamente
streamlit run src/dashboards/dashboard_main.py
```

**Estrutura interna:**
```python
import streamlit as st
from src.dashboards.components.ui import page_config, section_header, metric_card

# Configuração da página
page_config(
    page_title="Dashboard Principal",
    page_icon="📊",
    layout="wide"
)

# Sidebar para navegação
st.sidebar.title("Navegação")
page = st.sidebar.radio("Ir para", [
    "Overview",
    "Produção",
    "Máquinas",
    "Clientes",
    "Paradas"
])

# Renderizar página selecionada
if page == "Overview":
    render_overview()
elif page == "Produção":
    render_producao()
# ...
```

---

### 🔪 `dashboard_facas.py`

Dashboard especializado em análise de facas/lâminas.

**Funcionalidades:**
- 📊 Distribuição de status (NOVA, USADA, REFORMA)
- 📏 Análise de comprimentos
- 🔄 Histórico de trocas
- ⚠️ Alertas de manutenção
- 📈 Performance por faca

**Executar:**
```bash
# Via Makefile
make app-facas

# Ou diretamente
streamlit run src/dashboards/dashboard_facas.py
```

**Exemplo de análise:**
```python
import streamlit as st
import pandas as pd
from src.dashboards.components.ui import metric_card, insight_box
from src.viz.plots import plot_status_distribution, plot_histogram

st.title("🔪 Dashboard de Facas")

# Carregar dados
df_facas = pd.read_parquet('data/02 - trusted/tb_facas.parquet')

# Métricas principais
col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Total de Facas", len(df_facas))
with col2:
    novas = (df_facas['status'] == 'NOVA').sum()
    metric_card("Novas", novas)
with col3:
    usadas = (df_facas['status'] == 'USADA').sum()
    metric_card("Usadas", usadas)
with col4:
    reforma = (df_facas['status'] == 'REFORMA').sum()
    metric_card("Em Reforma", reforma)

# Gráfico de status
st.subheader("Distribuição de Status")
fig = plot_status_distribution(
    df_facas,
    status_col='status',
    label_col='cod_faca',
    title='Status das Facas'
)
st.plotly_chart(fig, use_container_width=True)

# Insight box
if reforma / len(df_facas) > 0.2:
    insight_box(
        "⚠️ Atenção",
        f"{reforma} facas ({reforma/len(df_facas)*100:.1f}%) em reforma. Considere aumentar estoque.",
        box_type="warning"
    )
```

---

## Componentes UI (`components/ui.py`)

### 📦 `page_config(page_title, page_icon="📊", layout="wide")`

Configura página do Streamlit.

**Exemplo:**
```python
from src.dashboards.components.ui import page_config

page_config(
    page_title="Dashboard de Produção",
    page_icon="🏭",
    layout="wide"
)
```

---

### 📊 `metric_card(label, value, help_text=None)`

Cria card de métrica estilizado.

**Exemplo:**
```python
from src.dashboards.components.ui import metric_card

metric_card(
    label="Produção Total",
    value="125.4k unidades",
    help_text="Produção acumulada no mês"
)
```

---

### 💡 `insight_box(title, content, box_type="info")`

Caixa de insight/alerta.

**Tipos:** `"info"`, `"warning"`, `"success"`, `"error"`

**Exemplo:**
```python
from src.dashboards.components.ui import insight_box

# Info
insight_box(
    "💡 Insight",
    "Máquina MAQ001 teve aumento de 15% na produtividade.",
    box_type="info"
)

# Warning
insight_box(
    "⚠️ Atenção",
    "Paradas aumentaram 30% em relação ao mês anterior.",
    box_type="warning"
)

# Success
insight_box(
    "✅ Sucesso",
    "Meta mensal atingida (105% do planejado).",
    box_type="success"
)

# Error
insight_box(
    "❌ Erro",
    "Falha na conexão com banco de dados Oracle.",
    box_type="error"
)
```

---

### 📝 `section_header(text, level=2)`

Cria cabeçalho de seção estilizado.

**Exemplo:**
```python
from src.dashboards.components.ui import section_header

section_header("Análise de Produção", level=1)
section_header("Distribuição Temporal", level=2)
section_header("Detalhes por Máquina", level=3)
```

---

### 🎨 `apply_custom_css()`

Aplica CSS customizado ao dashboard.

**Exemplo:**
```python
from src.dashboards.components.ui import apply_custom_css

apply_custom_css()
```

---

## Exemplo Dashboard Completo

```python
import streamlit as st
import pandas as pd
from src.dashboards.components.ui import (
    page_config,
    section_header,
    metric_card,
    insight_box,
    apply_custom_css
)
from src.viz.plots import (
    plot_time_series,
    plot_box_by_category,
    plot_pareto
)
from src.data.conn_oracle import oracle_connection

# ========================================
# CONFIGURAÇÃO
# ========================================
page_config(
    page_title="Dashboard de Produção",
    page_icon="🏭",
    layout="wide"
)
apply_custom_css()

# ========================================
# SIDEBAR - FILTROS
# ========================================
st.sidebar.title("Filtros")

# Filtro de data
date_range = st.sidebar.date_input(
    "Período",
    value=(pd.Timestamp.now() - pd.Timedelta(days=30), pd.Timestamp.now())
)

# Filtro de máquina
with oracle_connection('trusted') as conn:
    df_maquinas = pd.read_sql("SELECT DISTINCT cod_maquina FROM tb_maquinas ORDER BY cod_maquina", conn)

maquinas = st.sidebar.multiselect(
    "Máquinas",
    options=df_maquinas['cod_maquina'].tolist(),
    default=df_maquinas['cod_maquina'].tolist()[:5]
)

# ========================================
# CARREGAR DADOS
# ========================================
@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_data(start_date, end_date, maquinas_filter):
    with oracle_connection('trusted') as conn:
        query = f"""
            SELECT *
            FROM tb_tarefcon
            WHERE dt_inicio BETWEEN :start_date AND :end_date
            AND cod_maquina IN ({','.join([f"'{m}'" for m in maquinas_filter])})
        """
        df = pd.read_sql(query, conn, params={'start_date': start_date, 'end_date': end_date})
    return df

df = load_data(date_range[0], date_range[1], maquinas)

# ========================================
# HEADER
# ========================================
st.title("🏭 Dashboard de Produção")
st.markdown(f"Período: **{date_range[0]}** a **{date_range[1]}**")

# ========================================
# MÉTRICAS PRINCIPAIS
# ========================================
section_header("📊 Visão Geral", level=2)

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_producao = df['quantidade'].sum()
    metric_card("Produção Total", f"{total_producao:,.0f}", "Unidades produzidas")

with col2:
    media_dia = df.groupby('dt_inicio')['quantidade'].sum().mean()
    metric_card("Média Diária", f"{media_dia:,.0f}", "Unidades/dia")

with col3:
    num_maquinas = df['cod_maquina'].nunique()
    metric_card("Máquinas Ativas", num_maquinas)

with col4:
    eficiencia = (total_producao / (num_maquinas * len(df['dt_inicio'].unique()) * 1000)) * 100
    metric_card("Eficiência", f"{eficiencia:.1f}%", "vs capacidade teórica")

# ========================================
# SÉRIE TEMPORAL
# ========================================
section_header("📈 Evolução Temporal", level=2)

df_daily = df.groupby('dt_inicio')['quantidade'].sum().reset_index()
fig_ts = plot_time_series(
    df_daily,
    x_col='dt_inicio',
    y_col='quantidade',
    title='Produção Diária'
)
st.plotly_chart(fig_ts, use_container_width=True)

# ========================================
# ANÁLISE POR MÁQUINA
# ========================================
section_header("🏭 Performance por Máquina", level=2)

col1, col2 = st.columns(2)

with col1:
    # Box plot
    fig_box = plot_box_by_category(
        df,
        category_col='cod_maquina',
        value_col='quantidade',
        title='Distribuição de Produção'
    )
    st.plotly_chart(fig_box, use_container_width=True)

with col2:
    # Pareto
    maq_prod = df.groupby('cod_maquina')['quantidade'].sum().sort_values(ascending=False)
    fig_pareto = plot_pareto(
        maq_prod,
        title='Análise ABC de Máquinas',
        cumsum_lines=[80, 95]
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

# ========================================
# INSIGHTS AUTOMÁTICOS
# ========================================
section_header("💡 Insights", level=2)

# Top performer
top_maquina = maq_prod.idxmax()
top_valor = maq_prod.max()
insight_box(
    "🏆 Top Performer",
    f"Máquina **{top_maquina}** produziu {top_valor:,.0f} unidades ({top_valor/total_producao*100:.1f}% do total).",
    box_type="success"
)

# Alertas
media_maquina = maq_prod.mean()
baixo_desempenho = maq_prod[maq_prod < media_maquina * 0.7]
if len(baixo_desempenho) > 0:
    insight_box(
        "⚠️ Atenção",
        f"{len(baixo_desempenho)} máquinas com produção <70% da média: {', '.join(baixo_desempenho.index.tolist())}",
        box_type="warning"
    )

# ========================================
# TABELA DETALHADA
# ========================================
section_header("📋 Detalhes", level=2)

with st.expander("Ver dados brutos"):
    st.dataframe(
        df[['dt_inicio', 'cod_maquina', 'quantidade', 'tempo_parada']].head(100),
        use_container_width=True
    )

# ========================================
# DOWNLOAD
# ========================================
st.download_button(
    label="📥 Baixar dados (CSV)",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name=f"producao_{date_range[0]}_{date_range[1]}.csv",
    mime="text/csv"
)
```

---

## Boas Práticas

### 🎨 Design
- ✅ Layout wide para aproveitar espaço
- ✅ Usar colunas (`st.columns()`) para organizar
- ✅ Cores consistentes (usar paleta da empresa)
- ✅ Ícones para identificação visual
- ✅ Tooltips (`help_text`) para explicar métricas

### ⚡ Performance
- ✅ `@st.cache_data` para queries pesadas
- ✅ Limitar dados carregados (filtros de data)
- ✅ Amostrar gráficos com muitos pontos
- ✅ Lazy loading (carregar só quando necessário)

### 📊 Análise
- ✅ Insights automáticos (não só gráficos)
- ✅ Comparações (período anterior, meta)
- ✅ Alertas visuais (cores para status)
- ✅ Drill-down (detalhes ao clicar)

### 🔒 Segurança
- ✅ Nunca expor credenciais no código
- ✅ Validar inputs do usuário
- ✅ Usar st.secrets para configurações sensíveis
- ✅ Limitar acesso (autenticação se necessário)

---

## Deploy

### Streamlit Cloud

1. Push para GitHub
2. Conectar em [share.streamlit.io](https://share.streamlit.io)
3. Configurar secrets (`.streamlit/secrets.toml`)
4. Deploy automático

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "src/dashboards/dashboard_main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t dashboard-producao .
docker run -p 8501:8501 dashboard-producao
```

---

## Troubleshooting

### Erro: `StreamlitAPIException: set_page_config() must be called first`
**Solução:** Chamar `page_config()` antes de qualquer outro comando Streamlit

### Dashboard lento
**Solução:**
- Adicionar `@st.cache_data` nas queries
- Limitar período de dados
- Amostrar dados grandes
- Usar Parquet ao invés de CSV

### Erro de conexão com banco
**Solução:**
- Verificar `.env` configurado
- Testar conexão fora do Streamlit
- Adicionar timeout em queries
- Usar try/except para capturar erros

### Gráficos não aparecem
**Solução:**
- Verificar se `st.plotly_chart()` está sendo chamado
- Usar `use_container_width=True`
- Verificar se figura tem dados: `print(fig.data)`
