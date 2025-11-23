# 🔬 Analysis Module

## Propósito
Funções de **processamento e análise de dados** para limpeza, transformação e análise exploratória.

## Módulo Principal

### `data_processing.py`
Utilitários para transformação e análise de DataFrames.

---

## Funções Disponíveis

### 🧹 `clean_numeric_and_categorical(df, numeric_threshold=0.9, inplace=False)`

Separa e limpa colunas numéricas e categóricas automaticamente.

**Lógica:**
- Colunas com > 90% valores únicos → numérica
- Colunas com ≤ 90% valores únicos → categórica
- Exclui IDs (cod_*, id_*)

**Retorno:**
- `df_clean`: DataFrame limpo
- `numeric_cols`: Lista de colunas numéricas
- `categorical_cols`: Lista de colunas categóricas

**Exemplo:**
```python
from src.analysis.data_processing import clean_numeric_and_categorical

df_raw = pd.read_parquet('data/01 - raw/tb_clientes.parquet')

df_clean, num_cols, cat_cols = clean_numeric_and_categorical(df_raw)

print(f"✅ Numéricas: {num_cols}")
print(f"✅ Categóricas: {cat_cols}")

# Salvar na camada trusted
df_clean.to_parquet('data/02 - trusted/tb_clientes.parquet')
```

**Transformações aplicadas:**

**Numéricas:**
- Remove outliers (IQR method)
- Converte para `float64`
- Preenche NaN com mediana

**Categóricas:**
- Remove espaços extras (`str.strip()`)
- Padroniza para uppercase
- Preenche NaN com `'DESCONHECIDO'`

---

### 🔍 `get_common_numeric_columns(df1, df2, exclude_ids=None)`

Identifica colunas numéricas comuns entre dois DataFrames.

**Uso típico:** Encontrar colunas para merge ou comparação.

**Exemplo:**
```python
from src.analysis.data_processing import get_common_numeric_columns

df_pedidos = pd.read_parquet('data/02 - trusted/tb_pedidos.parquet')
df_itens = pd.read_parquet('data/02 - trusted/tb_itens.parquet')

common_cols = get_common_numeric_columns(
    df_pedidos,
    df_itens,
    exclude_ids=['cod_pedido', 'cod_item']
)

print(f"Colunas comuns: {common_cols}")
# Exemplo: ['quantidade', 'valor_unitario']
```

---

### 📊 `calculate_differences(df_left, df_right, join_key, value_columns, id_columns=None)`

Calcula diferenças entre valores de dois DataFrames.

**Uso típico:** Comparar pedidos vs catálogo, orçado vs realizado.

**Retorno:**
- DataFrame com colunas `{col}_left`, `{col}_right`, `{col}_diff`, `{col}_diff_pct`

**Exemplo:**
```python
from src.analysis.data_processing import calculate_differences

# Comparar pedidos vs catálogo de itens
df_diff = calculate_differences(
    df_left=df_pedidos,
    df_right=df_itens,
    join_key='cod_item',
    value_columns=['quantidade', 'preco_unitario'],
    id_columns=['cod_pedido', 'cod_cliente']
)

# Resultado:
# - quantidade_left (do pedido)
# - quantidade_right (do catálogo)
# - quantidade_diff (left - right)
# - quantidade_diff_pct ((left - right) / right * 100)

# Filtrar itens com diferença > 10%
df_diff_significativa = df_diff[df_diff['quantidade_diff_pct'].abs() > 10]

print(f"❌ {len(df_diff_significativa)} itens com diferença > 10%")
df_diff_significativa.to_parquet('data/04 - refined/pedidos_itens_diff.parquet')
```

---

### 📅 `create_temporal_aggregation(df, date_col, freq='M', agg_col=None, agg_func='count')`

Agrega dados por período temporal.

**Frequências disponíveis:**
- `'D'` → Diário
- `'W'` → Semanal
- `'M'` → Mensal
- `'Q'` → Trimestral
- `'Y'` → Anual

**Funções de agregação:**
- `'count'`, `'sum'`, `'mean'`, `'median'`, `'min'`, `'max'`, `'std'`

**Exemplo:**
```python
from src.analysis.data_processing import create_temporal_aggregation

df_tarefcon = pd.read_parquet('data/02 - trusted/tb_tarefcon.parquet')

# Agregação mensal de quantidade
df_monthly = create_temporal_aggregation(
    df_tarefcon,
    date_col='dt_inicio',
    freq='M',
    agg_col='quantidade',
    agg_func='sum'
)

print(df_monthly.head())
# dt_inicio  quantidade
# 2024-01    15000
# 2024-02    18500
# 2024-03    21000

# Salvar na camada refined
df_monthly.to_parquet('data/04 - refined/producao_mensal.parquet')
```

**Múltiplas agregações:**
```python
# Agrupar por mês e máquina com múltiplas métricas
df_monthly_multi = df_tarefcon.groupby([
    pd.Grouper(key='dt_inicio', freq='M'),
    'cod_maquina'
]).agg({
    'quantidade': ['sum', 'mean', 'count'],
    'tempo_parada': 'sum'
}).reset_index()

df_monthly_multi.to_parquet('data/04 - refined/kpis_producao_mensal.parquet')
```

---

### 📈 `abc_classification(values, thresholds=(80, 95))`

Classifica itens em categorias ABC (Pareto).

**Retorno:**
- DataFrame com colunas: `value`, `pct`, `cumsum_pct`, `class`

**Classes:**
- **A:** Até 80% do total (alta importância)
- **B:** 80-95% do total (importância média)
- **C:** 95-100% do total (baixa importância)

**Exemplo:**
```python
from src.analysis.data_processing import abc_classification

# Classificar clientes por quantidade
clientes_qtd = df.groupby('cod_cliente')['quantidade'].sum().sort_values(ascending=False)

df_abc = abc_classification(clientes_qtd, thresholds=(80, 95))

print(df_abc.groupby('class')['value'].agg(['count', 'sum']))
#        count      sum
# class
# A         15   800000  (15 clientes = 80% da quantidade)
# B         35   150000  (35 clientes = 15% da quantidade)
# C        150    50000  (150 clientes = 5% da quantidade)

# Salvar classificação
df_abc.to_parquet('data/04 - refined/abc_clientes.parquet')
```

**Visualizar:**
```python
from src.viz.plots import plot_pareto

fig = plot_pareto(clientes_qtd, title='Análise ABC de Clientes', cumsum_lines=[80, 95])
fig.show()
```

---

### 🔗 `create_pivot_table(df, index, columns, values, aggfunc='sum')`

Cria tabela dinâmica (pivot table).

**Exemplo:**
```python
from src.analysis.data_processing import create_pivot_table

# Quantidade por máquina e mês
pivot = create_pivot_table(
    df_tarefcon,
    index='cod_maquina',
    columns='month',
    values='quantidade',
    aggfunc='sum'
)

print(pivot)
#              1      2      3      4      5
# cod_maquina
# MAQ001      1500   1800   2100   1900   2200
# MAQ002      1200   1400   1600   1500   1700

# Visualizar heatmap
from src.viz.plots import plot_heatmap
fig = px.imshow(pivot, title='Produção por Máquina e Mês', text_auto=True)
fig.show()
```

---

### 📉 `detect_outliers(df, column, method='iqr', threshold=1.5)`

Detecta outliers em coluna numérica.

**Métodos:**
- `'iqr'` → Interquartile Range (padrão)
- `'zscore'` → Z-Score (desvios padrão)
- `'isolation_forest'` → Isolation Forest (ML)

**Exemplo:**
```python
from src.analysis.data_processing import detect_outliers

# Detectar outliers em quantidade
outliers_mask = detect_outliers(
    df_tarefcon,
    column='quantidade',
    method='iqr',
    threshold=1.5  # 1.5 * IQR
)

df_outliers = df_tarefcon[outliers_mask]
print(f"❌ {len(df_outliers)} outliers detectados")

# Visualizar
import plotly.express as px
fig = px.box(df_tarefcon, y='quantidade', points='outliers')
fig.show()

# Remover outliers
df_clean = df_tarefcon[~outliers_mask]
df_clean.to_parquet('data/02 - trusted/tb_tarefcon_clean.parquet')
```

---

## Pipeline de Limpeza Completo

```python
import pandas as pd
from src.analysis.data_processing import (
    clean_numeric_and_categorical,
    detect_outliers,
    create_temporal_aggregation
)
from src.logger import logger

# ========================================
# 1. CARREGAR DADOS BRUTOS
# ========================================
logger.info("📥 Carregando dados brutos...")
df_raw = pd.read_parquet('data/01 - raw/tb_tarefcon.parquet')
logger.info(f"✅ {len(df_raw)} registros carregados")

# ========================================
# 2. LIMPEZA INICIAL
# ========================================
logger.info("🧹 Limpando dados...")

# Remover duplicados
df = df_raw.drop_duplicates()
logger.info(f"❌ {len(df_raw) - len(df)} duplicados removidos")

# Separar e limpar numéricas/categóricas
df, num_cols, cat_cols = clean_numeric_and_categorical(df)
logger.info(f"✅ {len(num_cols)} numéricas, {len(cat_cols)} categóricas")

# ========================================
# 3. DETECTAR E REMOVER OUTLIERS
# ========================================
logger.info("🔍 Detectando outliers...")
outliers_mask = detect_outliers(df, 'quantidade', method='iqr')
logger.info(f"❌ {outliers_mask.sum()} outliers detectados")

# Opção 1: Remover outliers
df_clean = df[~outliers_mask]

# Opção 2: Substituir por limites (winsorizing)
# Q1 = df['quantidade'].quantile(0.25)
# Q3 = df['quantidade'].quantile(0.75)
# IQR = Q3 - Q1
# lower = Q1 - 1.5 * IQR
# upper = Q3 + 1.5 * IQR
# df['quantidade'] = df['quantidade'].clip(lower, upper)

# ========================================
# 4. VALIDAR QUALIDADE
# ========================================
from src.data.data_quality import check_data_quality

quality = check_data_quality(df_clean)
logger.info(f"📊 Missing: {quality['missing_pct']:.2f}%")
logger.info(f"📊 Duplicados: {quality['duplicates']}")

# ========================================
# 5. SALVAR NA CAMADA TRUSTED
# ========================================
logger.info("💾 Salvando dados limpos...")
df_clean.to_parquet('data/02 - trusted/tb_tarefcon.parquet')
logger.info(f"✅ {len(df_clean)} registros salvos")

# ========================================
# 6. CRIAR AGREGAÇÕES (REFINED)
# ========================================
logger.info("📈 Criando agregações...")

# Agregação mensal
df_monthly = create_temporal_aggregation(
    df_clean,
    date_col='dt_inicio',
    freq='M',
    agg_col='quantidade',
    agg_func='sum'
)
df_monthly.to_parquet('data/04 - refined/producao_mensal.parquet')

logger.info("✅ Pipeline de limpeza concluído!")
```

---

## Boas Práticas

### 🧹 Limpeza
- ✅ Sempre validar dados antes e depois
- ✅ Documentar decisões (remover vs imputar)
- ✅ Preservar dados brutos (01 - raw)
- ✅ Versionar transformações (scripts/data_processing.py)

### 📊 Análise
- ✅ Começar com `.info()`, `.describe()`, `.isna().sum()`
- ✅ Visualizar distribuições antes de limpar
- ✅ Documentar outliers (por que removeu?)
- ✅ Validar integridade referencial (foreign keys)

### ⚡ Performance
- ✅ Usar `.query()` ao invés de indexação booleana
- ✅ Processar em chunks para grandes volumes
- ✅ Usar categorias para strings repetidas (`df['col'].astype('category')`)
- ✅ Salvar em Parquet (comprimido, mais rápido)

---

## Troubleshooting

### Erro: `ValueError: could not convert string to float`
**Solução:** Limpar caracteres especiais antes de converter: `df['col'].str.replace(',', '').astype(float)`

### Erro: `KeyError: column not found`
**Solução:** Verificar se coluna existe: `if 'col' in df.columns:`

### Performance lenta em `groupby`
**Solução:**
- Converter colunas categóricas: `.astype('category')`
- Filtrar dados antes de agrupar
- Usar `.agg()` ao invés de múltiplos `.apply()`

### Muitos outliers detectados
**Solução:**
- Revisar threshold (tentar 2.0 ou 3.0 ao invés de 1.5)
- Usar método alternativo (zscore ao invés de IQR)
- Investigar se outliers são legítimos (erros vs valores reais)
