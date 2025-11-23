# 📊 Visualization Module

## Propósito
Funções reutilizáveis de **visualização** usando Plotly.

## Módulo Principal

### `plots.py`
Biblioteca de gráficos interativos para análise exploratória e dashboards.

---

## Gráficos Disponíveis

### 📊 `plot_status_distribution(df, status_col, label_col, title)`

Gráfico de barras para distribuição de status.

**Uso típico:** Distribuição de status de facas, pedidos, máquinas.

**Exemplo:**
```python
from src.viz.plots import plot_status_distribution

df_facas = pd.read_parquet('data/02 - trusted/tb_facas.parquet')
fig = plot_status_distribution(
    df_facas,
    status_col='status',
    label_col='cod_faca',
    title='Distribuição de Status das Facas'
)
fig.show()
```

---

### 📈 `plot_histogram(df, column, title, nbins=50, marginal=None)`

Histograma interativo com opção de marginal plot.

**Marginal options:** `'rug'`, `'box'`, `'violin'`, `None`

**Exemplo:**
```python
from src.viz.plots import plot_histogram

df_tarefcon = pd.read_parquet('data/02 - trusted/tb_tarefcon.parquet')

# Histograma simples
fig = plot_histogram(df_tarefcon, 'quantidade', 'Distribuição de Quantidade')
fig.show()

# Com box plot marginal
fig = plot_histogram(
    df_tarefcon,
    'quantidade',
    'Distribuição de Quantidade',
    marginal='box'
)
fig.show()
```

---

### 📦 `plot_box_by_category(df, category_col, value_col, title)`

Box plot por categoria para comparar distribuições.

**Uso típico:** Comparar produção por máquina, paradas por tipo, etc.

**Exemplo:**
```python
from src.viz.plots import plot_box_by_category

df_tarefcon = pd.read_parquet('data/02 - trusted/tb_tarefcon.parquet')
fig = plot_box_by_category(
    df_tarefcon,
    category_col='cod_maquina',
    value_col='quantidade',
    title='Distribuição de Quantidade por Máquina'
)
fig.show()
```

---

### 📉 `plot_time_series(df, x_col, y_col, title, color_col=None)`

Gráfico de série temporal.

**Exemplo:**
```python
from src.viz.plots import plot_time_series

df_tarefcon = pd.read_parquet('data/02 - trusted/tb_tarefcon.parquet')

# Série temporal simples
fig = plot_time_series(
    df_tarefcon,
    x_col='dt_inicio',
    y_col='quantidade',
    title='Produção ao Longo do Tempo'
)
fig.show()

# Com cor por categoria
fig = plot_time_series(
    df_tarefcon,
    x_col='dt_inicio',
    y_col='quantidade',
    title='Produção por Máquina',
    color_col='cod_maquina'
)
fig.show()
```

---

### 📊 `plot_pareto(values, title, top_n=50, cumsum_lines=[80, 95])`

Gráfico de Pareto (80/20 analysis).

**Uso típico:** Análise ABC de clientes, produtos, causas de paradas.

**Exemplo:**
```python
from src.viz.plots import plot_pareto

# Análise de clientes por quantidade
clientes_qtd = df.groupby('cod_cliente')['quantidade'].sum().sort_values(ascending=False)

fig = plot_pareto(
    clientes_qtd,
    title='Análise ABC de Clientes',
    top_n=50,
    cumsum_lines=[80, 95]  # Linhas de 80% e 95%
)
fig.show()
```

**Interpretação:**
- **Classe A:** Até 80% (poucos clientes, alta contribuição)
- **Classe B:** 80-95% (clientes intermediários)
- **Classe C:** 95-100% (muitos clientes, baixa contribuição)

---

### 🥧 `plot_pie(values, names, title, hole=0.4)`

Gráfico de pizza (ou donut se `hole > 0`).

**Exemplo:**
```python
from src.viz.plots import plot_pie

# Distribuição de status
status_counts = df_facas['status'].value_counts()

fig = plot_pie(
    status_counts.values,
    status_counts.index,
    title='Distribuição de Status das Facas',
    hole=0.4  # Donut chart
)
fig.show()
```

---

### 🌐 `plot_3d_scatter(df, x_col, y_col, z_col, color_col, sample_size=1000)`

Scatter plot 3D interativo.

**Uso típico:** Visualizar relações entre 3+ variáveis.

**Exemplo:**
```python
from src.viz.plots import plot_3d_scatter

fig = plot_3d_scatter(
    df_tarefcon,
    x_col='quantidade',
    y_col='duracao_minutos',
    z_col='tempo_parada',
    color_col='cod_maquina',
    sample_size=5000
)
fig.show()
```

---

### 🔥 `plot_heatmap(df, x_col, y_col, z_col, title, agg_func='mean')`

Heatmap de agregação.

**Exemplo:**
```python
from src.viz.plots import plot_heatmap

# Quantidade média por mês e máquina
fig = plot_heatmap(
    df_tarefcon,
    x_col='month',
    y_col='cod_maquina',
    z_col='quantidade',
    title='Produção Média por Mês e Máquina',
    agg_func='mean'
)
fig.show()
```

---

### 📊 `plot_correlation_matrix(df, title='Matriz de Correlação')`

Matriz de correlação de variáveis numéricas.

**Exemplo:**
```python
from src.viz.plots import plot_correlation_matrix

fig = plot_correlation_matrix(df_features, title='Correlação entre Features')
fig.show()
```

---

## Composição de Gráficos

### Subplots

```python
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from src.viz.plots import plot_histogram, plot_box_by_category

# Criar figura com 1 linha, 2 colunas
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=['Histograma', 'Box Plot']
)

# Adicionar gráficos
fig1 = plot_histogram(df, 'quantidade', 'Distribuição')
fig2 = plot_box_by_category(df, 'cod_maquina', 'quantidade', 'Por Máquina')

for trace in fig1.data:
    fig.add_trace(trace, row=1, col=1)

for trace in fig2.data:
    fig.add_trace(trace, row=1, col=2)

fig.update_layout(height=400, title_text="Dashboard de Produção")
fig.show()
```

---

## Customização

### Cores

```python
import plotly.express as px

# Usar paleta de cores
fig = px.bar(df, x='categoria', y='valor', color='categoria',
             color_discrete_sequence=px.colors.qualitative.Set2)
```

### Templates

```python
# Templates disponíveis: plotly, plotly_white, plotly_dark, ggplot2, seaborn, simple_white
fig.update_layout(template='plotly_white')
```

### Exportar

```python
# Salvar como HTML
fig.write_html('grafico.html')

# Salvar como imagem (requer kaleido)
fig.write_image('grafico.png', width=1200, height=600)

# Salvar como PDF
fig.write_image('grafico.pdf')
```

---

## Exemplo Dashboard Completo

```python
import pandas as pd
from src.viz.plots import (
    plot_time_series,
    plot_box_by_category,
    plot_pareto,
    plot_correlation_matrix
)
from plotly.subplots import make_subplots

# Carregar dados
df = pd.read_parquet('data/03 - ml/production_features.parquet')

# Criar figura com subplots
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=[
        'Produção ao Longo do Tempo',
        'Distribuição por Máquina',
        'Análise ABC de Clientes',
        'Correlação de Features'
    ],
    specs=[
        [{"type": "scatter"}, {"type": "box"}],
        [{"type": "bar"}, {"type": "heatmap"}]
    ]
)

# 1. Série temporal
fig_ts = plot_time_series(df, 'dt_inicio', 'quantidade', 'Produção')
for trace in fig_ts.data:
    fig.add_trace(trace, row=1, col=1)

# 2. Box plot
fig_box = plot_box_by_category(df, 'cod_maquina', 'quantidade', 'Por Máquina')
for trace in fig_box.data:
    fig.add_trace(trace, row=1, col=2)

# 3. Pareto
clientes = df.groupby('cod_cliente')['quantidade'].sum().sort_values(ascending=False)
fig_pareto = plot_pareto(clientes, 'ABC Clientes', top_n=30)
for trace in fig_pareto.data:
    fig.add_trace(trace, row=2, col=1)

# 4. Correlação
fig_corr = plot_correlation_matrix(df[['quantidade', 'quantidade_lag_1', 'quantidade_rolling_7d_mean']])
for trace in fig_corr.data:
    fig.add_trace(trace, row=2, col=2)

# Layout
fig.update_layout(
    height=800,
    title_text="Dashboard de Produção - Visão Geral",
    showlegend=False
)

fig.show()
```

---

## Boas Práticas

### 🎨 Design
- ✅ Usar títulos descritivos
- ✅ Adicionar labels nos eixos
- ✅ Escolher cores acessíveis (considerar daltonismo)
- ✅ Limitar número de categorias (max 10-15 no gráfico)
- ✅ Usar hover_data para detalhes adicionais

### 📊 Análise
- ✅ Começar com overview (distribuições, médias)
- ✅ Drill-down em anomalias
- ✅ Comparar períodos (mês a mês, ano a ano)
- ✅ Correlacionar variáveis antes de modelar

### ⚡ Performance
- ✅ Amostrar dados grandes (`sample_size` parâmetro)
- ✅ Agregar antes de plotar (não plotar milhões de pontos)
- ✅ Usar Plotly ao invés de Matplotlib para interatividade
- ✅ Salvar figuras prontas em HTML

---

## Troubleshooting

### Gráfico não aparece
**Solução:** Usar `fig.show()` ou salvar como HTML

### Erro: `ValueError: array length mismatch`
**Solução:** Verificar se x e y têm o mesmo tamanho

### Performance lenta
**Solução:**
- Reduzir `sample_size`
- Agregar dados antes de plotar
- Usar `scattergl` ao invés de `scatter` para muitos pontos

### Cores não distinguíveis
**Solução:** Usar `color_discrete_sequence` com paleta apropriada
